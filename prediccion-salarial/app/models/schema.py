"""
schema.py - Validación con Pydantic v2
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class PredictRequest(BaseModel):
    """Modelo de validación para requests de predicción"""
    
    model_config = ConfigDict(populate_by_name=True)  # Permite usar aliases
    
    # Datos personales
    nombre: Optional[str] = None
    edad: float = Field(..., ge=18, le=100, description="Edad del graduado")
    pais: str = Field(..., description="País de origen")
    genero: str = Field(..., description="Género")
    
    # Datos de formación con aliases para camelCase
    titulacion: str = Field(..., description="Nivel de titulación")
    anios_desde_obtencion: float = Field(default=2.0, ge=0, le=50, description="Años desde graduación", 
                                         alias="aniosDesdeObtencion")
    campo_estudio: str = Field(..., description="Campo de estudio", alias="campoEstudio")
    nivel_ingles: str = Field(..., description="Nivel de inglés", alias="nivelIngles")
    universidad_ranking: str = Field(..., description="Ranking de universidad", 
                                     alias="universidadRanking")
    region_estudio: str = Field(..., description="Región de estudio", alias="regionEstudio")
    nota_media: float = Field(..., ge=0, le=10, description="Nota media", alias="notaMedia")
    practicas: bool = Field(default=False, description="Realizó prácticas")

    @field_validator('pais')
    @classmethod
    def validate_pais(cls, v):
        valid = ['Brasil', 'China', 'España', 'Pakistán', 'USA', 'India', 'Vietnam', 'Nigeria']
        if v not in valid:
            raise ValueError(f'País debe ser uno de: {valid}')
        return v

    @field_validator('genero')
    @classmethod
    def validate_genero(cls, v):
        valid = ['Hombre', 'Mujer', 'Otro']
        if v not in valid:
            raise ValueError(f'Género debe ser uno de: {valid}')
        return v

    @field_validator('titulacion')
    @classmethod
    def validate_titulacion(cls, v):
        valid = ['Grado', 'Master', 'PHD', 'FP']
        if v not in valid:
            raise ValueError(f'Titulación debe ser uno de: {valid}')
        return v

    @field_validator('campo_estudio')
    @classmethod
    def validate_campo(cls, v):
        valid = ['Artes', 'Ing', 'IT', 'Salud', 'S.Sociales', 'Empresa']
        if v not in valid:
            raise ValueError(f'Campo de estudio debe ser uno de: {valid}')
        return v

    @field_validator('nivel_ingles')
    @classmethod
    def validate_ingles(cls, v):
        valid = ['Básico', 'Intermedio', 'Avanzado', 'Fluido']
        if v not in valid:
            raise ValueError(f'Nivel de inglés debe ser uno de: {valid}')
        return v


class PredictResponse(BaseModel):
    """Modelo de respuesta de predicción"""
    salary: float = Field(..., description="Salario predicho")
    model_version: str = Field(..., description="Versión del modelo")
    confidence: Optional[float] = Field(None, description="Confianza de la predicción")
    salary_range: Optional[dict] = Field(None, description="Rango salarial")
