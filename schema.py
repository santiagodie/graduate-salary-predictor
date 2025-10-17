#define las reglas de lo que tu API considera un “payload válido”.

# predictive_app/schema.py
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Literal

# Enumeraciones (categorías fijas)
Education = Literal["primary", "secondary", "bachelor", "master", "phd"]
CompanySize = Literal["small", "medium", "large"]
ContractType = Literal["perm", "contract", "intern"]

class PredictRequest(BaseModel):
    years_experience: float = Field(ge=0, le=60)
    age: int = Field(ge=16, le=80)
    education_level: Education
    job_title: str
    industry: str
    company_size: CompanySize
    city: str
    country: str
    remote_ratio: int = Field(ge=0, le=100)
    contract_type: ContractType
    hours_per_week: float = Field(ge=10, le=80)
    certifications_count: int = Field(ge=0, le=50)

    # Validación extra: cadenas no vacías
    @field_validator("job_title", "industry", "city", "country")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

class PredictResponse(BaseModel):
    salary_pred: float
    model_version: str
