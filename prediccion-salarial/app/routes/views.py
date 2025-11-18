"""
views.py - Rutas para renderizado de páginas HTML
"""

from flask import Blueprint, render_template, redirect, url_for, request
from app.models.predictor import load_meta

# Crear blueprint para las vistas
views = Blueprint('views', __name__)

# Base de datos mock de predicciones (compartida con API)
from app.routes.api import predictions_db


@views.route('/')
def index():
    """Redirige a página de inicio"""
    return redirect(url_for('views.inicio'))


@views.route('/inicio')
def inicio():
    """Landing page principal"""
    return render_template('inicio.html')


@views.route('/inicio/info')
def info():
    """Página de información del modelo"""
    meta = load_meta()
    return render_template('info.html', model_info=meta)


@views.route('/formulario/<form_id>')
def formulario(form_id):
    """Página del formulario de predicción"""
    return render_template('formulario.html', form_id=form_id)


@views.route('/formulario/resultado/<form_id>')
def resultado(form_id):
    """Página de resultados de predicción"""
    # Obtener predicción de la base de datos
    prediction = predictions_db.get(form_id)

    if not prediction:
        # Si no existe, redirigir a error
        return redirect(url_for('views.error', exception='not_found'))

    return render_template('resultado.html',
                         form_id=form_id,
                         prediction=prediction)


@views.route('/error/<exception>')
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

    # Mapear el código de error al status HTTP correcto
    status_codes = {
        '404': 404,
        '500': 500,
        'timeout': 408,  # Request Timeout
        'offline': 503,  # Service Unavailable
        'not_found': 404,
        'validation_error': 422  # Unprocessable Entity
    }

    status_code = status_codes.get(exception, 400)

    return render_template('error.html',
                         error_code=exception,
                         error_message=error_messages.get(
                             exception, 'Error desconocido'
                         )), status_code


# =============================================================================
# MANEJO DE ERRORES
# =============================================================================

@views.app_errorhandler(404)
def not_found(error):
    """Manejo de 404"""
    if request.path.startswith('/api/'):
        # Los errores de API los maneja el blueprint de API
        return error
    return redirect(url_for('views.error', exception='404'))


@views.app_errorhandler(500)
def server_error(error):
    """Manejo de 500"""
    if request.path.startswith('/api/'):
        # Los errores de API los maneja el blueprint de API
        return error
    return redirect(url_for('views.error', exception='500'))
