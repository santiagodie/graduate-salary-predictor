"""
helpers.py - Funciones auxiliares y utilidades
"""

from typing import Dict, Any
from datetime import datetime


# =============================================================================
# DATOS DE REFERENCIA
# =============================================================================

AVERAGE_DATA = {
    'salaries_by_country': {},  # Se calculará dinámicamente
    'salaries_by_education': {},  # Se calculará dinámicamente
    'salaries_by_field': {},  # Se calculará dinámicamente
    'average_age': 28,
    'average_years_experience': 3,
    'average_grade': 7.5
}

# Cache para predicciones de estadísticas
_STATS_CACHE = {
    'by_country': {},
    'by_education': {},
    'by_field': {},
    'last_updated': None
}


# =============================================================================
# MAPEOS ESPAÑOL <-> INGLÉS
# =============================================================================

COUNTRY_MAP = {
    'brasil': 'Brazil', 'china': 'China', 'españa': 'Spain',
    'pakistán': 'Pakistan', 'usa': 'USA', 'india': 'India',
    'vietnam': 'Vietnam', 'nigeria': 'Nigeria'
}

GENDER_MAP = {
    'hombre': 'Male', 'mujer': 'Female', 'otro': 'Other'
}

EDUCATION_MAP = {
    'fp': 'FP', 'grado': 'Bachelor', 'master': 'Master', 'phd': 'PhD'
}

FIELD_MAP = {
    'artes': 'Arts', 'ing': 'Engineering', 'it': 'Computer Science',
    'salud': 'Health', 's.sociales': 'Social Sciences', 's sociales': 'Social Sciences',
    'empresa': 'Business'
}

LANGUAGE_MAP = {
    'básico': 'Basic', 'basico': 'Basic',
    'intermedio': 'Intermediate',
    'avanzado': 'Advanced',
    'fluido': 'Fluent'
}

RANKING_MAP = {
    'alto': 'Top 100', 'medio': 'Top 500', 'bajo': 'Unranked'
}

REGION_MAP = {
    'australia': 'Australia', 'europa': 'Europe', 'usa': 'USA'
}

# Medias de edad y nota por campo de estudio
FIELD_AVERAGES = {
    'Artes': {'age': 26, 'grade': 7.2},
    'Ing': {'age': 27, 'grade': 7.8},
    'IT': {'age': 25, 'grade': 7.5},
    'Salud': {'age': 28, 'grade': 8.0},
    'S.Sociales': {'age': 27, 'grade': 7.3},
    'Empresa': {'age': 26, 'grade': 7.6}
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def calculate_percentile(value: float, min_val: float, max_val: float) -> int:
    """Calcula el percentil de un valor en un rango"""
    if max_val == min_val:
        return 50
    percentile = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, int(percentile)))


def build_comparisons(request_data: Dict[str, Any], salary: float) -> Dict[str, Any]:
    """Construye objeto de comparaciones para la respuesta usando valores reales del modelo"""

    # Obtener valores del cache o usar defaults
    country_eng = COUNTRY_MAP.get(request_data.get('pais', '').lower(), 'Spain')
    education_eng = EDUCATION_MAP.get(request_data.get('titulacion', '').lower(), 'Bachelor')
    field_eng = FIELD_MAP.get(request_data.get('campo_estudio', '').lower(), 'Computer Science')

    country_avg = _STATS_CACHE['by_country'].get(country_eng, 35000)
    education_avg = _STATS_CACHE['by_education'].get(education_eng, 40000)
    field_avg = _STATS_CACHE['by_field'].get(field_eng, 40000)
    # Obtener campo de estudio del usuario
    user_field = request_data.get('campo_estudio', 'IT')
    field_stats = FIELD_AVERAGES.get(user_field, {'age': 27, 'grade': 7.5})

    return {
        'edad': {
            'user': request_data.get('edad', 25),
            'average': field_stats['age'],
            'field': user_field,
            'percentile': calculate_percentile(request_data.get('edad', 25), 22, 35)
        },
        'pais': {
            'user': request_data.get('pais'),
            'average_salary': country_avg,
            'percentile': calculate_percentile(
                salary,
                country_avg - 5000,
                country_avg + 15000
            )
        },
        'genero': {
            'user': request_data.get('genero'),
            'distribution': {'Hombre': 55, 'Mujer': 40, 'Otro': 5}
        },
        'formacion': {
            'user': request_data.get('titulacion'),
            'average_salary': education_avg
        },
        'campoEstudio': {
            'user': user_field,
            'average_salary': field_avg
        },
        'notaMedia': {
            'user': request_data.get('nota_media', 7),
            'average': field_stats['grade'],
            'field': user_field
        },
        'universidadRanking': {
            'user': request_data.get('universidad_ranking'),
            'impact': {'Alto': '+15%', 'Medio': '+5%', 'Bajo': '0%'}
        },
        'regionEstudio': {
            'user': request_data.get('region_estudio'),
            'average_by_region': {'USA': 60000, 'Europa': 38000, 'Australia': 45000}
        }
    }


def calculate_average_salaries_from_model():
    """
    Calcula salarios promedio usando el modelo real para diferentes categorías.
    Esto se hace una vez al inicio y se cachea.
    """
    import pandas as pd
    from app.models.predictor import MODEL

    if MODEL is None:
        print("[WARNING] Modelo no disponible, no se pueden calcular estadisticas reales")
        return

    print("[INFO] Calculando estadisticas reales con el modelo...")

    # Perfil base "promedio" para hacer comparaciones
    base_profile = {
        'Age': 28.0,
        'Years_Since_Graduation': 3.0,
        'GPA_10': 7.5,
        'Internship_Experience': 1
    }

    # Calcular salarios por país
    countries = ['Brazil', 'China', 'Spain', 'Pakistan', 'USA', 'India', 'Vietnam', 'Nigeria']
    for country in countries:
        profile = base_profile.copy()
        profile.update({
            'Country_of_Origin': country,
            'Gender': 'Male',
            'Education_Level': 'Bachelor',
            'Field_of_Study': 'Computer Science',
            'Language_Proficiency': 'Intermediate',
            'University_Ranking': 'Top 500',
            'Region_of_Study': 'Europe'
        })

        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            _STATS_CACHE['by_country'][country] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando salario para {country}: {e}")

    # Calcular salarios por educación
    education_levels = ['FP', 'Bachelor', 'Master', 'PhD']
    for edu in education_levels:
        profile = base_profile.copy()
        profile.update({
            'Country_of_Origin': 'Spain',
            'Gender': 'Male',
            'Education_Level': edu,
            'Field_of_Study': 'Computer Science',
            'Language_Proficiency': 'Intermediate',
            'University_Ranking': 'Top 500',
            'Region_of_Study': 'Europe'
        })

        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            _STATS_CACHE['by_education'][edu] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando salario para {edu}: {e}")

    # Calcular salarios por campo de estudio
    fields = ['Arts', 'Engineering', 'Computer Science', 'Health', 'Social Sciences', 'Business']
    for field in fields:
        profile = base_profile.copy()
        profile.update({
            'Country_of_Origin': 'Spain',
            'Gender': 'Male',
            'Education_Level': 'Bachelor',
            'Field_of_Study': field,
            'Language_Proficiency': 'Intermediate',
            'University_Ranking': 'Top 500',
            'Region_of_Study': 'Europe'
        })

        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            _STATS_CACHE['by_field'][field] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando salario para {field}: {e}")

    _STATS_CACHE['last_updated'] = datetime.now().isoformat()

    print(f"[INFO] Estadisticas calculadas:")
    print(f"       - Paises: {len(_STATS_CACHE['by_country'])} valores")
    print(f"       - Educacion: {len(_STATS_CACHE['by_education'])} valores")
    print(f"       - Campos: {len(_STATS_CACHE['by_field'])} valores")


def get_stats_cache():
    """Retorna el cache de estadísticas"""
    return _STATS_CACHE

def translate_features_to_english(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traduce los campos del español al inglés para el modelo ML
    """
    try:
        pais_lower = data['pais'].lower()
        genero_lower = data['genero'].lower()
        titulacion_lower = data['titulacion'].lower()
        campo_lower = data['campo_estudio'].lower().replace('.', ' ')
        ingles_lower = data['nivel_ingles'].lower()
        ranking_lower = data['universidad_ranking'].lower()
        region_lower = data['region_estudio'].lower()

        features = {
            'Age': float(data['edad']),
            'Country_of_Origin': COUNTRY_MAP.get(pais_lower, data['pais']),
            'Gender': GENDER_MAP.get(genero_lower, data['genero']),
            'Education_Level': EDUCATION_MAP.get(titulacion_lower, data['titulacion']),
            'Years_Since_Graduation': float(data['anios_desde_obtencion']),
            'Field_of_Study': FIELD_MAP.get(campo_lower, data['campo_estudio']),
            'Language_Proficiency': LANGUAGE_MAP.get(ingles_lower, data['nivel_ingles']),
            'University_Ranking': RANKING_MAP.get(ranking_lower, 'Unranked'),
            'Region_of_Study': REGION_MAP.get(region_lower, data['region_estudio']),
            'GPA_10': float(data['nota_media']),
            'Internship_Experience': 1 if data['practicas'] else 0,
        }
        return features
    except KeyError as e:
        raise ValueError(f"Campo requerido faltante: {e}")
