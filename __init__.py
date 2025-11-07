# model/__init__.py
"""
Model Package - Módulo de predicción ML
========================================

Contiene el modelo entrenado y la lógica de inferencia.

Módulos:
    - predictor: Funciones de predicción y preprocesamiento

Archivos:
    - model.pkl: Modelo serializado de scikit-learn
    - scaler.pkl: (Opcional) Scaler para normalización
    - metadata.json: (Opcional) Metadatos del modelo
"""

__version__ = "1.0.0"

from model.predictor import (
    predict_one,
    load_meta,
    get_model_version,
    validate_input_data,
    COLUMN_ORDER,
    ENCODING_MAPS,
)

# Información del modelo
MODEL_TYPE = "Regression"
TARGET_VARIABLE = "salary"

__all__ = [
    # Versión
    "__version__",
    
    # Constantes
    "MODEL_TYPE",
    "TARGET_VARIABLE",
    "COLUMN_ORDER",
    "ENCODING_MAPS",
    
    # Funciones principales
    "predict_one",
    "load_meta",
    "get_model_version",
    "validate_input_data",
]