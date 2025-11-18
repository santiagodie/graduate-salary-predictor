"""
api.py - Endpoints API REST
"""

import time
import random
from datetime import datetime
from typing import Dict
import pandas as pd

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.schema import PredictRequest
from app.models.predictor import predict_one, load_meta, MODEL, _PREDICTOR_AVAILABLE
from app.utils.helpers import (
    build_comparisons,
    get_stats_cache,
    translate_features_to_english,
    COUNTRY_MAP,
    GENDER_MAP,
    EDUCATION_MAP,
    FIELD_MAP
)

# Crear blueprint para la API
api = Blueprint('api', __name__, url_prefix='/api')

# Base de datos mock de predicciones
predictions_db: Dict = {}


@api.route('/health')
def health():
    """Endpoint de health check"""
    status = "ok" if _PREDICTOR_AVAILABLE else "ok (mock)"
    body = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": load_meta().get("version", "unknown")
    }
    if not _PREDICTOR_AVAILABLE:
        body["note"] = "Predictor no cargado, usando modo mock"
    return jsonify(body), 200


@api.route('/model/info')
def model_info():
    """Información del modelo ML"""
    try:
        meta = load_meta()
        return jsonify({
            "version": meta.get("version", "unknown"),
            "trained_at": meta.get("trained_at", "unknown"),
            "metrics": meta.get("metrics", {}),
            "features": meta.get("features", []),
            "predictor_available": _PREDICTOR_AVAILABLE
        }), 200
    except Exception as e:
        return jsonify({
            "error": "meta_error",
            "details": str(e)
        }), 500


@api.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint principal de predicción con validación Pydantic
    Acepta JSON y retorna predicción + comparaciones
    """
    # Simular tiempo de procesamiento
    time.sleep(1)

    # 1. Validación con Pydantic
    try:
        payload = request.get_json(force=True) or {}
        req = PredictRequest(**payload)
        data = req.model_dump()
    except ValidationError as ve:
        return jsonify({
            "error": "validation_error",
            "details": ve.errors()
        }), 422
    except Exception as e:
        return jsonify({
            "error": "bad_request",
            "details": str(e)
        }), 400

    # 2. Obtener form_id
    form_id = data.get('form_id', f"pred_{int(time.time())}")

    # 3. Preparar features para el modelo
    try:
        features = translate_features_to_english(data)
    except ValueError as e:
        return jsonify({
            "error": "missing_field",
            "details": str(e)
        }), 400

    # 4. Realizar predicción
    try:
        # El modelo espera un DataFrame con columnas en inglés
        df = pd.DataFrame([features])

        print(f"[INFO] Usando MODELO REAL para prediccion")
        print(f"[INFO] Columnas del DataFrame: {list(df.columns)}")
        print(f"[INFO] Valores: {df.iloc[0].to_dict()}")

        if MODEL is None:
            raise Exception("Modelo no cargado")

        # Predicción directa con el modelo
        salary = float(MODEL.predict(df)[0])
        print(f"[INFO] Prediccion realizada: {salary:.2f}")

        model_version = load_meta().get("version", "unknown")
    except Exception as e:
        print(f"[ERROR] Error en prediccion: {e}")
        print(f"[ERROR] Features enviadas: {features}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "prediction_error",
            "details": str(e)
        }), 500

    # 5. Construir respuesta completa
    result = {
        'salary': salary,
        'form_id': form_id,
        'model_version': model_version,
        'timestamp': datetime.now().isoformat(),
        'using_real_model': _PREDICTOR_AVAILABLE,
        'comparisons': build_comparisons(data, salary),
        'statistics': {
            'total_predictions': random.randint(1000, 5000),
            'confidence': random.randint(75, 95),
            'salary_range': {
                'min': salary - 5000,
                'max': salary + 8000
            }
        }
    }

    # 6. Guardar en base de datos mock
    predictions_db[form_id] = result

    return jsonify(result), 200


@api.route('/statistics', methods=['POST'])
def get_statistics():
    """
    Obtener estadísticas filtradas para visualizaciones usando el modelo real
    Body: { "pais": "España", "formacion": "Master", "genero": "Hombre", "campoEstudio": "IT" }
    Retorna salarios, edad media y nota media filtrados
    """
    filters = request.json or {}
    stats_cache = get_stats_cache()

    if MODEL is None:
        # Si no hay modelo, devolver cache con valores mock
        from app.utils.helpers import FIELD_AVERAGES
        field_key = filters.get('campoEstudio', 'IT')
        field_stats = FIELD_AVERAGES.get(field_key, {'age': 27, 'grade': 7.5})

        return jsonify({
            'average_salary': 45000,
            'total_graduates': random.randint(800, 1200),
            'by_country': stats_cache['by_country'].copy(),
            'by_education': stats_cache['by_education'].copy(),
            'by_field': stats_cache['by_field'].copy(),
            'average_age': field_stats['age'],
            'average_grade': field_stats['grade']
        }), 200

    print(f"[INFO] Calculando estadisticas con filtros: {filters}")

    # Perfil base (se sobrescribirá con filtros)
    base_profile = {
        'Age': 28.0,
        'Years_Since_Graduation': 3.0,
        'GPA_10': 7.5,
        'Internship_Experience': 1,
        'Gender': 'Male',
        'Education_Level': 'Bachelor',
        'Field_of_Study': 'Computer Science',
        'Language_Proficiency': 'Intermediate',
        'University_Ranking': 'Top 500',
        'Region_of_Study': 'Europe'
    }

    # Aplicar filtros al perfil base
    if filters.get('pais'):
        base_profile['Country_of_Origin'] = COUNTRY_MAP.get(filters['pais'].lower(), 'Spain')
    else:
        base_profile['Country_of_Origin'] = 'Spain'

    if filters.get('genero'):
        base_profile['Gender'] = GENDER_MAP.get(filters['genero'].lower(), 'Male')

    if filters.get('formacion'):
        base_profile['Education_Level'] = EDUCATION_MAP.get(filters['formacion'].lower(), 'Bachelor')

    if filters.get('campoEstudio'):
        base_profile['Field_of_Study'] = FIELD_MAP.get(filters['campoEstudio'].lower(), 'Computer Science')

    # Calcular estadísticas POR PAÍS con el perfil filtrado
    stats_by_country = {}
    countries = ['Brazil', 'China', 'Spain', 'Pakistan', 'USA', 'India', 'Vietnam', 'Nigeria']
    for country in countries:
        profile = base_profile.copy()
        profile['Country_of_Origin'] = country
        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            stats_by_country[country] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando {country}: {e}")
            stats_by_country[country] = stats_cache['by_country'].get(country, 50000)

    # Calcular estadísticas POR EDUCACIÓN con el perfil filtrado
    stats_by_education = {}
    education_levels = ['FP', 'Bachelor', 'Master', 'PhD']
    for edu in education_levels:
        profile = base_profile.copy()
        profile['Education_Level'] = edu
        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            stats_by_education[edu] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando {edu}: {e}")
            stats_by_education[edu] = stats_cache['by_education'].get(edu, 50000)

    # Calcular estadísticas POR CAMPO con el perfil filtrado
    stats_by_field = {}
    fields = ['Arts', 'Engineering', 'Computer Science', 'Health', 'Social Sciences', 'Business']
    for field in fields:
        profile = base_profile.copy()
        profile['Field_of_Study'] = field
        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            stats_by_field[field] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando {field}: {e}")
            stats_by_field[field] = stats_cache['by_field'].get(field, 50000)

    # Calcular estadísticas POR GÉNERO (para el gráfico de campo de estudio)
    stats_by_gender = {}
    genders = ['Male', 'Female']
    for gender in genders:
        profile = base_profile.copy()
        profile['Gender'] = gender
        try:
            df = pd.DataFrame([profile])
            salary = float(MODEL.predict(df)[0])
            stats_by_gender[gender] = salary
        except Exception as e:
            print(f"[ERROR] Error calculando {gender}: {e}")
            stats_by_gender[gender] = 50000

    # Calcular edad y nota media basadas en el campo de estudio
    from app.utils.helpers import FIELD_AVERAGES

    # Mapear el campo filtrado a la clave de FIELD_AVERAGES
    field_key = filters.get('campoEstudio', 'IT')
    field_stats = FIELD_AVERAGES.get(field_key, {'age': 27, 'grade': 7.5})

    average_age = field_stats['age']
    average_grade = field_stats['grade']

    print(f"[INFO] Estadisticas calculadas con filtros aplicados")
    print(f"[INFO] Edad media: {average_age}, Nota media: {average_grade}")

    return jsonify({
        'average_salary': sum(stats_by_country.values()) / len(stats_by_country),
        'total_graduates': random.randint(800, 1200),
        'by_country': stats_by_country,
        'by_education': stats_by_education,
        'by_field': stats_by_field,
        'by_gender': stats_by_gender,
        'average_age': average_age,
        'average_grade': average_grade
    }), 200


@api.route('/prediction/<form_id>')
def get_prediction(form_id):
    """Obtener predicción por ID"""
    prediction = predictions_db.get(form_id)

    if not prediction:
        return jsonify({
            "error": "not_found",
            "message": f"No se encontró predicción con ID: {form_id}"
        }), 404

    return jsonify(prediction), 200


# =============================================================================
# MANEJO DE ERRORES DE API
# =============================================================================

@api.errorhandler(404)
def api_not_found(error):
    """Manejo de 404 en API"""
    return jsonify({"error": "not_found", "path": request.path}), 404


@api.errorhandler(500)
def api_server_error(error):
    """Manejo de 500 en API"""
    return jsonify({"error": "server_error", "details": str(error)}), 500
