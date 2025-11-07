"""
Paquete raíz del proyecto. Expone funciones y constantes del predictor
ubicado en predictor.py (archivo en la raíz del proyecto).
"""
__version__ = "1.0.0"

from predictor import (  # type: ignore
    predict_one,
    load_meta,
    get_model_version,
    validate_input_data,
    COLUMN_ORDER,
    ENCODING_MAPS,
)

MODEL_TYPE = "Regression"
TARGET_VARIABLE = "salary"

__all__ = [
    "__version__",
    "MODEL_TYPE",
    "TARGET_VARIABLE",
    "COLUMN_ORDER",
    "ENCODING_MAPS",
    "predict_one",
    "load_meta",
    "get_model_version",
    "validate_input_data",
]       