#define las reglas de lo que tu API considera un “payload válido”.

# predictive_app/schema.py
from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
from typing import Optional, Literal


# -----------------------------
# Conjunto de dominios (canónicos)
# -----------------------------
PAISES = {
    "brasil", "china", "españa", "pakistán", "usa", "india", "vietnam", "nigeria"
}

GENEROS = {"hombre", "mujer", "otro"}

TITULACIONES = {"grado", "master", "phd", "fp"}

CAMPOS_ESTUDIO_CANON = {
    "artes": "artes",
    "ing": "ing",                # ingeniería abreviado "Ing"
    "it": "it",
    "salud": "salud",
    "s.sociales": "s_sociales",  # lo normalizamos a "s_sociales"
    "s_sociales": "s_sociales",
    "empresa": "empresa",
}

NIVELES_INGLES_CANON = {
    "básico": "basico",
    "basico": "basico",
    "intermedio": "intermedio",
    "avanzado": "avanzado",
    "fluido": "fluido",
}

SITUACIONES_LABORALES = {"estudiando", "desempleado", "empleado"}

RANKING_UNI = {"alto", "medio", "bajo"}

REGIONES_ESTUDIO = {"australia", "europa", "usa"}

# -----------------------------
# Modelo de petición
# -----------------------------
class PredictRequest(BaseModel):
    """
    Campos canónicos esperados por la API (snake_case, en castellano).
    'nombre' es opcional y NO se usa para el modelo (solo informativo).
    """
    model_config = ConfigDict(extra="forbid")  # rechaza campos desconocidos

    # --- Datos personales ---
    nombre: Optional[str] = Field(default=None, max_length=100)
    edad: float = Field(ge=16, le=80, description="Edad en años (double)")

    pais: str  # combobox (Brasil, China, España, Pakistán, USA, India, Vietnam, Nigeria)
    genero: str  # (Hombre, Mujer, Otro)

    # --- Datos de formación ---
    titulacion: str  # (Grado, Master, PHD, Fp)
    campo_estudio: str  # (Artes, Ing, IT, Salud, S.Sociales, Empresa)
    nivel_ingles: str  # (Intermedio, Avanzado, Básico, Fluido)

    situacion_laboral: str  # (Estudiando, Desempleado, empleado)

    universidad_ranking: str  # (Alto, Medio, Bajo)

    region_estudio: str  # (Australia, Europa, USA)

    # -------------------------
    # Validadores / Normalización
    # -------------------------

    # nombre opcional: limpiar espacios
    @field_validator("nombre")
    @classmethod
    def _clean_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        return v or None

    # país
    @field_validator("pais")
    @classmethod
    def _validate_pais(cls, v: str) -> str:
        v1 = v.strip().lower()
        # normalizar algunos alias frecuentes
        alias = {
            "pakistan": "pakistán",
            "eeuu": "usa",
            "estados unidos": "usa"
        }
        v1 = alias.get(v1, v1)
        if v1 not in PAISES:
            raise ValueError(f"pais debe ser uno de: {sorted(PAISES)}")
        return v1

    # género
    @field_validator("genero")
    @classmethod
    def _validate_genero(cls, v: str) -> str:
        v1 = v.strip().lower()
        if v1 not in GENEROS:
            raise ValueError(f"genero debe ser uno de: {sorted(GENEROS)}")
        return v1

    # titulación
    @field_validator("titulacion")
    @classmethod
    def _validate_titulacion(cls, v: str) -> str:
        v1 = v.strip().lower()
        # normalización de variantes
        if v1 in {"máster", "master"}:
            v1 = "master"
        if v1 in {"phd", "ph.d.", "doctorado"}:
            v1 = "phd"
        if v1 not in TITULACIONES:
            raise ValueError(f"titulacion debe ser uno de: {sorted(TITULACIONES)}")
        return v1

    # campo de estudio
    @field_validator("campo_estudio")
    @classmethod
    def _validate_campo_estudio(cls, v: str) -> str:
        v0 = v.strip()
        v1 = v0.lower()
        # normalizar abreviaturas y puntos
        if v1 == "s. sociales":
            v1 = "s.sociales"
        canon = CAMPOS_ESTUDIO_CANON.get(v1)
        if not canon:
            raise ValueError(
                "campo_estudio no válido. Usa uno de: "
                f"{sorted(set(CAMPOS_ESTUDIO_CANON.values()))} (admite 'Ing', 'S.Sociales', etc.)"
            )
        return canon

    # nivel de inglés
    @field_validator("nivel_ingles")
    @classmethod
    def _validate_nivel_ingles(cls, v: str) -> str:
        v1 = v.strip().lower()
        canon = NIVELES_INGLES_CANON.get(v1)
        if not canon:
            raise ValueError(f"nivel_ingles debe ser uno de: {sorted(set(NIVELES_INGLES_CANON.values()))}")
        return canon

    # situación laboral
    @field_validator("situacion_laboral")
    @classmethod
    def _validate_situacion_laboral(cls, v: str) -> str:
        v1 = v.strip().lower()
        if v1 not in SITUACIONES_LABORALES:
            raise ValueError(f"situacion_laboral debe ser uno de: {sorted(SITUACIONES_LABORALES)}")
        return v1

    # ranking de universidad
    @field_validator("universidad_ranking")
    @classmethod
    def _validate_universidad_ranking(cls, v: str) -> str:
        v1 = v.strip().lower()
        if v1 not in RANKING_UNI:
            raise ValueError(f"universidad_ranking debe ser uno de: {sorted(RANKING_UNI)}")
        return v1

    # región de estudio
    @field_validator("region_estudio")
    @classmethod
    def _validate_region_estudio(cls, v: str) -> str:
        v1 = v.strip().lower()
        alias = {
            "eeuu": "usa",
            "estados unidos": "usa",
        }
        v1 = alias.get(v1, v1)
        if v1 not in REGIONES_ESTUDIO:
            raise ValueError(f"region_estudio debe ser uno de: {sorted(REGIONES_ESTUDIO)}")
        return v1


# -----------------------------
# Modelo de respuesta
# -----------------------------
class PredictResponse(BaseModel):
    salary_pred: float
    model_version: str
