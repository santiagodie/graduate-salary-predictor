#define las reglas de lo que tu API considera un “payload válido”.

# predictive_app/schema.py
from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
from typing import Literal, Optional

# --- Enums "base" (ajusta si el CSV trae otros valores) ---
Education = Literal["high_school", "associate", "bachelor", "master", "phd", "postdoc"]
Gender = Literal["male", "female", "other", "prefer_not_to_say"]
LangCEFR = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
LangAlt = Literal["basic", "intermediate", "advanced", "fluent", "native"]
EmpStatus = Literal[
    "employed_full_time", "employed_part_time", "self_employed",
    "unemployed", "further_study", "intern"
]

# Si finalmente usáis bandas para ranking, cambia a enum
class PredictRequest(BaseModel):
    # Categóricas "flexibles" por ahora (se cierran con metadata en producción)
    country_of_origin: str
    field_of_study: str
    region_of_study: str

    # Categóricas cerradas
    education_level: Education
    language_proficiency: str  # aceptamos CEFR o 5-niveles y normalizamos abajo
    gender: Gender
    employment_status: EmpStatus

    # Numéricas
    university_ranking: int = Field(ge=1, le=5000)
    age: int = Field(ge=16, le=80)
    years_since_graduation: int = Field(ge=0, le=40)
    gpa: float = Field(ge=0, le=10)  # aceptamos 0–10 y luego normalizamos a 0–4
    internship_experience: str  # "yes" | "no"  (o mapea desde bool/int)
    
    model_config = ConfigDict(extra="forbid")  # rechaza campos desconocidos

    # --- Validaciones de strings no vacíos ---
    @field_validator("country_of_origin", "field_of_study", "region_of_study")
    @classmethod
    def non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must be a non-empty string")
        if len(v) > 64:
            raise ValueError("value too long")
        return v

    # --- Normalización de language_proficiency ---
    @field_validator("language_proficiency")
    @classmethod
    def normalize_language(cls, v: str) -> str:
        v0 = v.strip()
        # aceptar CEFR tal cual
        if v0 in {"A1","A2","B1","B2","C1","C2"}:
            return v0
        # mapear 5 niveles comunes a CEFR aproximada
        m = {
            "basic": "A2",
            "intermediate": "B2",
            "advanced": "C1",
            "fluent": "C1",
            "native": "C2",
        }
        v1 = v0.lower()
        if v1 in m:
            return m[v1]
        raise ValueError("language_proficiency must be CEFR (A1–C2) or one of basic/intermediate/advanced/fluent/native")

    # --- Internship "yes/no" -> booleano textual consistente ---
    @field_validator("internship_experience")
    @classmethod
    def normalize_internship(cls, v: str) -> str:
        v1 = v.strip().lower()
        if v1 in {"yes", "no"}:
            return v1
        if v1 in {"true","1"}:
            return "yes"
        if v1 in {"false","0"}:
            return "no"
        raise ValueError("internship_experience must be 'yes' or 'no'")

    # --- Reglas cruzadas: edad vs años desde graduación ---
    @field_validator("years_since_graduation")
    @classmethod
    def check_age_relation(cls, ysg: int, info):
        # Pydantic v2: acceder al modelo parcial con info.data
        age = info.data.get("age", None)
        if age is not None and ysg > (age - 16):
            raise ValueError("years_since_graduation inconsistent with age")
        return ysg

class PredictResponse(BaseModel):
    salary_pred: float
    model_version: str

