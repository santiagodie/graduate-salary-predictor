"""
app/__init__.py - Inicialización de la aplicación Flask
"""

import warnings
from flask import Flask
from flask_cors import CORS

# Suprimir advertencias de compatibilidad de versiones de sklearn
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')


def create_app(config_name='default'):
    """
    Factory de aplicación Flask
    """
    from config import get_config

    # Crear aplicación Flask
    app = Flask(__name__)

    # Cargar configuración
    app_config = get_config()
    app.config.from_object(app_config)
    app.secret_key = app_config.SECRET_KEY

    # Configurar CORS para desarrollo con frontend separado
    CORS(app, resources={
        r"/api/*": {"origins": app_config.FRONT_ORIGIN}
    })

    # Registrar blueprints
    from app.routes import views, api
    app.register_blueprint(views)
    app.register_blueprint(api)

    # Inicializar cache de estadísticas del modelo
    with app.app_context():
        try:
            from app.models.predictor import _PREDICTOR_AVAILABLE
            if _PREDICTOR_AVAILABLE:
                print("[INFO] Calculando estadísticas con el modelo...")
                from app.utils.helpers import calculate_average_salaries_from_model
                calculate_average_salaries_from_model()
        except Exception as e:
            print(f"[WARNING] No se pudieron calcular estadísticas: {e}")

    return app
