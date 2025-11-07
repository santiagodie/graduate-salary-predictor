"""
app.py - 
Combina:
- Renderizado de templates HTML (frontend integrado)
- API REST con validación Pydantic
- Soporte para modelo ML real o mock
- Sistema de comparaciones y estadísticas
"""

import os
import json
import random
import time
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from pydantic import BaseModel, Field, ValidationError, validator

# =============================================================================
# CONFIGURACIÓN Y MODELOS PYDANTIC
# =============================================================================

class PredictRequest(BaseModel):
    """Modelo de validación para requests de predicción"""
    # Datos personales
    nombre: Optional[str] = None
    edad: float = Field(..., ge=18, le=100, description="Edad del graduado")
    pais: str = Field(..., description="País de origen")
    genero: str = Field(..., description="Género")
    
    # Datos de formación
    titulacion: str = Field(..., description="Nivel de titulación")
    aniosDesdeObtencion: float = Field(..., ge=0, le=50, description="Años desde graduación")
    campoEstudio: str = Field(..., description="Campo de estudio")
    nivelIngles: str = Field(..., description="Nivel de inglés")
    universidadRanking: str = Field(..., description="Ranking de universidad")
    regionEstudio: str = Field(..., description="Región de estudio")
    notaMedia: float = Field(..., ge=0, le=10, description="Nota media")
    practicas: bool = Field(default=False, description="Realizó prácticas")
    situacionLaboral: str = Field(..., description="Situación laboral actual")
    
    @validator('pais')
    def validate_pais(cls, v):
        valid = ['Brasil', 'China', 'España', 'Pakistán', 'USA', 'India', 'Vietnam', 'Nigeria']
        if v not in valid:
            raise ValueError(f'País debe ser uno de: {valid}')
        return v
    
    @validator('genero')
    def validate_genero(cls, v):
        valid = ['Hombre', 'Mujer', 'Otro']
        if v not in valid:
            raise ValueError(f'Género debe ser uno de: {valid}')
        return v
    
    @validator('titulacion')
    def validate_titulacion(cls, v):
        valid = ['Grado', 'Master', 'PHD', 'FP']
        if v not in valid:
            raise ValueError(f'Titulación debe ser uno de: {valid}')
        return v
    
    @validator('campoEstudio')
    def validate_campo(cls, v):
        valid = ['Artes', 'Ing', 'IT', 'Salud', 'S.Sociales', 'Empresa']
        if v not in valid:
            raise ValueError(f'Campo de estudio debe ser uno de: {valid}')
        return v
    
    @validator('nivelIngles')
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
    salary_range: Optional[Dict[str, float]] = Field(None, description="Rango salarial")


# =============================================================================
# CARGA DEL PREDICTOR (Real o Mock)
# =============================================================================

_PREDICTOR_AVAILABLE = False
_MOCK_ERR = None

try:
    from predictor import predict_one, load_meta
    _PREDICTOR_AVAILABLE = True
    print("✓ Predictor real cargado correctamente")
except Exception as e:
    _MOCK_ERR = str(e)
    print(f"⚠ Predictor no disponible, usando modo MOCK: {e}")
    
    def predict_one(features_dict: Dict[str, Any]) -> float:
        """Mock: calcula salario basado en reglas heurísticas"""
        base_salary = 30000
        
        # Multiplicadores por educación
        education_mult = {
            'Grado': 1.0, 'Master': 1.3, 'PHD': 1.8, 'FP': 0.9
        }
        base_salary *= education_mult.get(features_dict.get('titulacion'), 1.0)
        
        # Multiplicadores por país
        country_mult = {
            'USA': 1.5, 'España': 1.0, 'China': 1.1, 'India': 0.9,
            'Brasil': 0.85, 'Pakistán': 0.8, 'Vietnam': 0.85, 'Nigeria': 0.8
        }
        base_salary *= country_mult.get(features_dict.get('pais'), 1.0)
        
        # Multiplicadores por campo
        field_mult = {
            'IT': 1.3, 'Ing': 1.2, 'Empresa': 1.1, 'Salud': 1.05,
            'S.Sociales': 0.95, 'Artes': 0.9
        }
        base_salary *= field_mult.get(features_dict.get('campoEstudio'), 1.0)
        
        # Bonus por nivel de inglés
        english_bonus = {
            'Básico': 0, 'Intermedio': 2000, 'Avanzado': 5000, 'Fluido': 8000
        }
        base_salary += english_bonus.get(features_dict.get('nivelIngles'), 0)
        
        # Bonus por ranking
        ranking_bonus = {'Alto': 5000, 'Medio': 2000, 'Bajo': 0}
        base_salary += ranking_bonus.get(features_dict.get('universidadRanking'), 0)
        
        # Ajuste por experiencia
        years = float(features_dict.get('aniosDesdeObtencion', 0))
        base_salary += years * 1500
        
        # Ajuste por nota
        grade = float(features_dict.get('notaMedia', 5))
        if grade > 8:
            base_salary += 3000
        elif grade > 7:
            base_salary += 1500
        
        # Ajuste por prácticas
        if features_dict.get('practicas'):
            base_salary += 2000
        
        # Ajuste por situación laboral
        if features_dict.get('situacionLaboral') == 'Empleado':
            base_salary += 5000
        
        # Variabilidad
        salary = base_salary + random.randint(-3000, 3000)
        return max(20000, min(salary, 150000))
    
    def load_meta() -> Dict[str, Any]:
        """Mock: metadata del modelo"""
        return {
            "version": "mock-v1.0",
            "trained_at": datetime.now().isoformat(),
            "metrics": {
                "r2_score": 0.85,
                "rmse": 5000,
                "mae": 3500
            },
            "features": [
                "edad", "pais", "genero", "titulacion", "aniosDesdeObtencion",
                "campoEstudio", "nivelIngles", "universidadRanking", 
                "regionEstudio", "notaMedia", "practicas", "situacionLaboral"
            ]
        }


# =============================================================================
# FLASK APP
# =============================================================================

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_key_cambiar_en_produccion')

# Configurar CORS para desarrollo con frontend separado
CORS(app, resources={
    r"/api/*": {"origins": os.getenv("FRONT_ORIGIN", "http://localhost:5173")}
})

# Cache de metadata y predicciones
_META_CACHE: Optional[Dict[str, Any]] = None
predictions_db: Dict[str, Dict] = {}


# =============================================================================
# DATOS DE REFERENCIA
# =============================================================================

AVERAGE_DATA = {
    'salaries_by_country': {
        'Brasil': 28000, 'China': 35000, 'España': 32000, 
        'Pakistán': 25000, 'USA': 65000, 'India': 30000,
        'Vietnam': 27000, 'Nigeria': 26000
    },
    'salaries_by_education': {
        'Grado': 35000, 'Master': 45000, 'PHD': 65000, 'FP': 30000
    },
    'salaries_by_field': {
        'Artes': 32000, 'Ing': 55000, 'IT': 60000,
        'Salud': 45000, 'S.Sociales': 35000, 'Empresa': 50000
    },
    'average_age': 28,
    'average_years_experience': 3,
    'average_grade': 7.5
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_meta() -> Dict[str, Any]:
    """Obtiene metadata del modelo (con caché)"""
    global _META_CACHE
    if _META_CACHE is None:
        _META_CACHE = load_meta()
    return _META_CACHE


def calculate_percentile(value: float, min_val: float, max_val: float) -> int:
    """Calcula el percentil de un valor en un rango"""
    if max_val == min_val:
        return 50
    percentile = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, int(percentile)))


def build_comparisons(request_data: Dict[str, Any], salary: float) -> Dict[str, Any]:
    """Construye objeto de comparaciones para la respuesta"""
    return {
        'edad': {
            'user': request_data.get('edad', 25),
            'average': AVERAGE_DATA['average_age'],
            'percentile': calculate_percentile(request_data.get('edad', 25), 22, 35)
        },
        'pais': {
            'user': request_data.get('pais'),
            'average_salary': AVERAGE_DATA['salaries_by_country'].get(
                request_data.get('pais'), 35000
            ),
            'percentile': calculate_percentile(
                salary,
                AVERAGE_DATA['salaries_by_country'].get(request_data.get('pais'), 35000) - 5000,
                AVERAGE_DATA['salaries_by_country'].get(request_data.get('pais'), 35000) + 15000
            )
        },
        'genero': {
            'user': request_data.get('genero'),
            'distribution': {'Hombre': 55, 'Mujer': 40, 'Otro': 5}
        },
        'formacion': {
            'user': request_data.get('titulacion'),
            'average_salary': AVERAGE_DATA['salaries_by_education'].get(
                request_data.get('titulacion'), 40000
            )
        },
        'campoEstudio': {
            'user': request_data.get('campoEstudio'),
            'average_salary': AVERAGE_DATA['salaries_by_field'].get(
                request_data.get('campoEstudio'), 45000
            )
        },
        'aniosExperiencia': {
            'user': request_data.get('aniosDesdeObtencion', 0),
            'average': AVERAGE_DATA['average_years_experience']
        },
        'notaMedia': {
            'user': request_data.get('notaMedia', 7),
            'average': AVERAGE_DATA['average_grade']
        },
        'universidadRanking': {
            'user': request_data.get('universidadRanking'),
            'impact': {'Alto': '+15%', 'Medio': '+5%', 'Bajo': '0%'}
        },
        'regionEstudio': {
            'user': request_data.get('regionEstudio'),
            'average_by_region': {'USA': 60000, 'Europa': 38000, 'Australia': 45000}
        }
    }


# =============================================================================
# RUTAS DE PÁGINAS HTML (Frontend integrado)
# =============================================================================

@app.route('/')
def index():
    """Redirige a página de inicio"""
    return redirect(url_for('inicio'))


@app.route('/inicio')
def inicio():
    """Landing page principal"""
    return render_template('inicio.html')


@app.route('/inicio/info')
def info():
    """Página de información del modelo"""
    meta = get_meta()
    return render_template('info.html', model_info=meta)


@app.route('/formulario/<form_id>')
def formulario(form_id):
    """Página del formulario de predicción"""
    return render_template('formulario.html', form_id=form_id)


@app.route('/formulario/resultado/<form_id>')
def resultado(form_id):
    """Página de resultados de predicción"""
    # Obtener predicción de la base de datos
    prediction = predictions_db.get(form_id)
    
    if not prediction:
        # Si no existe, redirigir a error
        return redirect(url_for('error', exception='not_found'))
    
    return render_template('resultado.html', 
                         form_id=form_id, 
                         prediction=prediction)


@app.route('/error/<exception>')
def error(exception):
    """Página de manejo de errores"""
    error_messages = {
        '404': 'Página no encontrada',
        '500': 'Error interno del servidor',
        'timeout': 'Tiempo de espera agotado',
        'offline': 'Sin conexión a internet',
        'not_found': 'Predicción no encontrada',
        'validation_error': 'Error de validación de datos'
    }
    
    return render_template('error.html', 
                         error_code=exception,
                         error_message=error_messages.get(
                             exception, 'Error desconocido'
                         )), 400


# =============================================================================
# ENDPOINTS API REST
# =============================================================================

@app.route('/api/health')
def health():
    """Endpoint de health check"""
    status = "ok" if _PREDICTOR_AVAILABLE else "ok (mock)"
    body = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": get_meta().get("version", "unknown")
    }
    if not _PREDICTOR_AVAILABLE:
        body["note"] = "Predictor no cargado, usando modo mock"
        body["detail"] = _MOCK_ERR
    return jsonify(body), 200


@app.route('/api/model/info')
def model_info():
    """Información del modelo ML"""
    try:
        meta = get_meta()
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


@app.route('/api/predict', methods=['POST'])
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
        data = req.dict()
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
        features = {
            'edad': data['edad'],
            'pais': data['pais'],
            'genero': data['genero'],
            'titulacion': data['titulacion'],
            'aniosDesdeObtencion': data['aniosDesdeObtencion'],
            'campoEstudio': data['campoEstudio'],
            'nivelIngles': data['nivelIngles'],
            'universidadRanking': data['universidadRanking'],
            'regionEstudio': data['regionEstudio'],
            'notaMedia': data['notaMedia'],
            'practicas': data['practicas'],
            'situacionLaboral': data['situacionLaboral']
        }
    except KeyError as e:
        return jsonify({
            "error": "missing_field",
            "details": f"Campo requerido faltante: {e}"
        }), 400
    
    # 4. Realizar predicción
    try:
        salary = predict_one(features)
        salary = float(salary)
        model_version = get_meta().get("version", "unknown")
    except Exception as e:
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


@app.route('/api/statistics', methods=['POST'])
def get_statistics():
    """
    Obtener estadísticas filtradas para visualizaciones
    Body: { "pais": "España", "formacion": "Master", ... }
    """
    filters = request.json or {}
    
    base_stats = {
        'average_salary': 45000,
        'total_graduates': random.randint(800, 1200),
        'by_country': {},
        'by_education': {},
        'by_field': {}
    }
    
    # Aplicar filtros
    if filters.get('pais'):
        base_stats['average_salary'] = AVERAGE_DATA['salaries_by_country'].get(
            filters['pais'], 45000
        )
    
    if filters.get('formacion'):
        base_stats['average_salary'] = AVERAGE_DATA['salaries_by_education'].get(
            filters['formacion'], 45000
        )
    
    # Generar datos para gráficos con variabilidad
    for country, avg in AVERAGE_DATA['salaries_by_country'].items():
        base_stats['by_country'][country] = avg + random.randint(-2000, 2000)
    
    for edu, avg in AVERAGE_DATA['salaries_by_education'].items():
        base_stats['by_education'][edu] = avg + random.randint(-2000, 2000)
    
    for field, avg in AVERAGE_DATA['salaries_by_field'].items():
        base_stats['by_field'][field] = avg + random.randint(-2000, 2000)
    
    return jsonify(base_stats), 200


@app.route('/api/prediction/<form_id>')
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
# MANEJO DE ERRORES
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Manejo de 404"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "not_found", "path": request.path}), 404
    return redirect(url_for('error', exception='404'))


@app.errorhandler(500)
def server_error(error):
    """Manejo de 500"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "server_error", "details": str(error)}), 500
    return redirect(url_for('error', exception='500'))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    
    print("=" * 60)
    print("🚀 Iniciando Salary Prediction App")
    print("=" * 60)
    print(f"Puerto: {port}")
    print(f"Debug: {debug}")
    print(f"Predictor real: {'✓ Sí' if _PREDICTOR_AVAILABLE else '✗ No (mock)'}")
    print(f"Modelo: {get_meta().get('version', 'unknown')}")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )