"""
config.py - Configuración de la aplicación Flask
"""

import os
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = DATA_DIR / "modelo_entrenado.pkl"
SCALER_PATH = DATA_DIR / "scaler.pkl"
METADATA_PATH = DATA_DIR / "metadata.json"


class Config:
    """Configuración base de la aplicación"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_cambiar_en_produccion')
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"

    # CORS
    FRONT_ORIGIN = os.getenv("FRONT_ORIGIN", "http://localhost:5173")

    # Server
    HOST = '0.0.0.0'
    PORT = int(os.getenv("PORT", "5000"))

    # Modelo ML
    MODEL_PATH = str(MODEL_PATH)
    SCALER_PATH = str(SCALER_PATH)
    METADATA_PATH = str(METADATA_PATH)


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False


# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
