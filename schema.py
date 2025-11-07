# define las reglas de lo que tu API considera un “payload válido”.

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import unicodedata
import re

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
# Helpers
# -----------------------------
def _norm(s: Optional[str]) -> Optional[str]:
    """Normaliza texto: strip, lowercase, eliminar tildes y puntuación redundante."""
    if s is None:
        return None
    s2 = str(s).strip().lower()
    s2 = unicodedata.normalize("NFKD", s2).encode("ascii", "ignore").decode("ascii")
    s2 = re.sub(r"[^\w\s]", " ", s2)  # reemplaza puntuación por espacio
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2


def _build_canon_map(values):
    """Devuelve dict normalizado -> canonical (original)"""
    return { _norm(v): v for v in values }


# Precompute mapas canónicos normalizados
_CANON_PAISES = _build_canon_map(PAISES)
_CANON_GENEROS = _build_canon_map(GENEROS)
_CANON_TITULACIONES = _build_canon_map(TITULACIONES)
_CANON_CAMPOS = _build_canon_map(CAMPOS_ESTUDIO_CANON.keys())
_CANON_NIVELES = _build_canon_map(NIVELES_INGLES_CANON.keys())
_CANON_SITUACIONES = _build_canon_map(SITUACIONES_LABORALES)
_CANON_RANKING = _build_canon_map(RANKING_UNI)
_CANON_REGIONES = _build_canon_map(REGIONES_ESTUDIO)


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
    def _clean_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        return v or None

    # país
    @field_validator("pais")
    def _validate_pais(cls, v: str) -> str:
        v_norm = _norm(v)
        # normalizar algunos alias frecuentes
        alias = {
            "pakistan": "pakistán",
            "eeuu": "usa",
            "estados unidos": "usa"
        }
        if v_norm in alias:
            target = alias[v_norm]
            return target
        if v_norm in _CANON_PAISES:
            return _CANON_PAISES[v_norm]
        raise ValueError(f"pais debe ser uno de: {sorted(PAISES)}")

    # género
    @field_validator("genero")
    def _validate_genero(cls, v: str) -> str:
        v_norm = _norm(v)
        if v_norm in _CANON_GENEROS:
            return _CANON_GENEROS[v_norm]
        raise ValueError(f"genero debe ser uno de: {sorted(GENEROS)}")

    # titulación
    @field_validator("titulacion")
    def _validate_titulacion(cls, v: str) -> str:
        v_norm = _norm(v)
        # normalización de variantes
        if v_norm in {"master", "mastere", "mastero", "maestria", "mastre"}:
            return "master"
        if v_norm in {"phd", "ph d", "ph.d", "doctorado"}:
            return "phd"
        if v_norm in _CANON_TITULACIONES:
            return _CANON_TITULACIONES[v_norm]
        raise ValueError(f"titulacion debe ser uno de: {sorted(TITULACIONES)}")

    # campo de estudio
    @field_validator("campo_estudio")
    def _validate_campo_estudio(cls, v: str) -> str:
        v_norm = _norm(v)
        # aceptar variantes como "s social", "s.sociales", etc.
        if v_norm in {"s social", "s social es", "s sociales", "s social es"}:
            return "s_sociales"
        if v_norm in _CANON_CAMPOS:
            canon = _CANON_CAMPOS[v_norm]
            # devolver la forma canon (en el mapa CAMPOS_ESTUDIO_CANON)
            return CAMPOS_ESTUDIO_CANON.get(canon, canon)
        raise ValueError(
            "campo_estudio no válido. Usa uno de: "
            f"{sorted(set(CAMPOS_ESTUDIO_CANON.values()))} (admite 'Ing', 'S.Sociales', etc.)"
        )

    # nivel de inglés
    @field_validator("nivel_ingles")
    def _validate_nivel_ingles(cls, v: str) -> str:
        v_norm = _norm(v)
        if v_norm in _CANON_NIVELES:
            return NIVELES_INGLES_CANON.get(_CANON_NIVELES[v_norm], _CANON_NIVELES[v_norm])
        raise ValueError(f"nivel_ingles debe ser uno de: {sorted(set(NIVELES_INGLES_CANON.values()))}")

    # situación laboral
    @field_validator("situacion_laboral")
    def _validate_situacion_laboral(cls, v: str) -> str:
        v_norm = _norm(v)
        if v_norm in _CANON_SITUACIONES:
            return _CANON_SITUACIONES[v_norm]
        raise ValueError(f"situacion_laboral debe ser uno de: {sorted(SITUACIONES_LABORALES)}")

    # ranking de universidad
    @field_validator("universidad_ranking")
    def _validate_universidad_ranking(cls, v: str) -> str:
        v_norm = _norm(v)
        if v_norm in _CANON_RANKING:
            return _CANON_RANKING[v_norm]
        raise ValueError(f"universidad_ranking debe ser uno de: {sorted(RANKING_UNI)}")

    # región de estudio
    @field_validator("region_estudio")
    def _validate_region_estudio(cls, v: str) -> str:
        v_norm = _norm(v)
        alias = {
            "eeuu": "usa",
            "estados unidos": "usa",
        }
        if v_norm in alias:
            return alias[v_norm]
        if v_norm in _CANON_REGIONES:
            return _CANON_REGIONES[v_norm]
        raise ValueError(f"region_estudio debe ser uno de: {sorted(REGIONES_ESTUDIO)}")


# -----------------------------
# Modelo de respuesta
# -----------------------------
class PredictResponse(BaseModel):
    salary_pred: float
    model_version: str
