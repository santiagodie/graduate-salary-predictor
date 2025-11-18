"""
Módulo de modelos
"""

from app.models.predictor import (
    predict_one,
    load_meta,
    MODEL,
    _PREDICTOR_AVAILABLE
)

from app.models.schema import (
    PredictRequest,
    PredictResponse
)

__all__ = [
    'predict_one',
    'load_meta',
    'MODEL',
    '_PREDICTOR_AVAILABLE',
    'PredictRequest',
    'PredictResponse'
]
