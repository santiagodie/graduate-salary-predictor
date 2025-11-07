# predictive_app/app.py
import os
from typing import Any, Dict, Optional, List

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError

from schema import PredictRequest, PredictResponse

# ---------------------------------------------------------
# Carga del "predictor" (lo hace tu compañero)
# Intentamos importar de varias ubicaciones para mayor robustez.
# Debe exponer al menos:
#   - predict_one(features_dict: dict) -> float
#   - load_meta() -> dict con {"version","trained_at","metrics","features":[...]}
# Opcionalmente:
#   - get_model_version() -> str
# ---------------------------------------------------------
_PREDICTOR_AVAILABLE = False
_MOCK_ERR: Optional[str] = None

try:
    # Preferir import desde la raíz si predictor.py está ahí
    from predictor import predict_one, load_meta  # type: ignore
    _PREDICTOR_AVAILABLE = True
except Exception as e_root:
    try:
        # Intentar como parte del paquete predictive_app
        from predictive_app.predictor import predict_one, load_meta  # type: ignore
        _PREDICTOR_AVAILABLE = True
    except Exception as e_pkg:
        # Modo MOCK si aún no está el predictor real
        _PREDICTOR_AVAILABLE = False
        _MOCK_ERR = f"root_err: {e_root}; pkg_err: {e_pkg}"

        def predict_one(features_dict: Dict[str, Any]) -> float:  # type: ignore
            # Devuelve un valor fijo para probar el cableado
            return 12345.0

        def load_meta() -> Dict[str, Any]:  # type: ignore
            # Meta mínima para pruebas sin modelo real
            return {
                "version": "mock",
                "trained_at": "N/A",
                "metrics": {},
                "features": [
                    "edad",
                    "pais",
                    "genero",
                    "titulacion",
                    "campo_estudio",
                    "nivel_ingles",
                    "situacion_laboral",
                    "universidad_ranking",
                    "region_estudio",
                ],
            }

# ---------------------------------------------------------
# Flask app y CORS
# ---------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONT_ORIGIN", "http://localhost:5173")}})

# Cache de metadatos para no releer en cada request
_META_CACHE: Optional[Dict[str, Any]] = None

# Columnas críticas que el schema expone / que usa build_ordered_features.
# Si la metadata del modelo no incluye todas estas, consideramos la meta inválida.
REQUIRED_FEATURES: List[str] = [
    "edad",
    "pais",
    "genero",
    "titulacion",
    "campo_estudio",
    "nivel_ingles",
    "situacion_laboral",
    "universidad_ranking",
    "region_estudio",
]


def _validate_meta_features(meta: Dict[str, Any]) -> None:
    """
    Lanza ValueError si metadata['features'] no contiene todas las columnas requeridas.
    """
    features = meta.get("features", [])
    if not isinstance(features, list):
        raise ValueError("metadata.features must be a list")
    missing = [f for f in REQUIRED_FEATURES if f not in features]
    if missing:
        raise ValueError(f"metadata.features missing required fields: {missing}")


def get_meta() -> Dict[str, Any]:
    """
    Devuelve metadata del predictor; cacheada en memoria.
    Si load_meta falla o no cumple con REQUIRED_FEATURES, lanza excepción.
    """
    global _META_CACHE
    if _META_CACHE is None:
        meta = load_meta()
        # Validar las features del meta antes de cachear
        _validate_meta_features(meta)
        _META_CACHE = meta
    return _META_CACHE


def build_ordered_features(req: PredictRequest) -> Dict[str, Any]:
    """
    Toma la request validada y devuelve un dict con el **orden de columnas**
    que declara el metadata["features"]. Si falta alguna, la pone a None.
    """
    meta = get_meta()
    feature_names = meta.get("features", [])
    # Mapeo 1:1 desde los campos canónicos del schema
    row = {
        "edad": req.edad,
        "pais": req.pais,
        "genero": req.genero,
        "titulacion": req.titulacion,
        "campo_estudio": req.campo_estudio,
        "nivel_ingles": req.nivel_ingles,
        "situacion_laboral": req.situacion_laboral,
        "universidad_ranking": req.universidad_ranking,
        "region_estudio": req.region_estudio,
    }
    # Ordenar y rellenar
    ordered = {f: row.get(f, None) for f in feature_names}
    return ordered


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@app.get("/health")
def health():
    status = "ok" if _PREDICTOR_AVAILABLE else "ok (mock)"
    body = {"status": status}
    if not _PREDICTOR_AVAILABLE:
        body["note"] = "predictor.py no cargado aún; usando modo mock"
        body["detail"] = _MOCK_ERR
    return jsonify(body), 200


@app.get("/model/info")
def model_info():
    try:
        meta = get_meta()
        return jsonify(
            {
                "version": meta.get("version", "unknown"),
                "trained_at": meta.get("trained_at", "unknown"),
                "metrics": meta.get("metrics", {}),
                "features": meta.get("features", []),
            }
        ), 200
    except Exception as e:
        return jsonify({"error": "meta_error", "details": str(e)}), 500


@app.post("/predict")
def predict():
    # 1) Validación Pydantic
    try:
        payload = request.get_json(force=True) or {}
        req = PredictRequest(**payload)
    except ValidationError as ve:
        # 422: datos no procesables (contrato incumplido)
        return jsonify({"error": "validation_error", "details": ve.errors()}), 422
    except Exception as e:
        return jsonify({"error": "bad_request", "details": str(e)}), 400

    # 2) Construcción de features en el orden oficial del modelo
    try:
        features = build_ordered_features(req)
    except Exception as e:
        return jsonify({"error": "feature_build_error", "details": str(e)}), 500

    # 3) Llamada al predictor
    try:
        y_hat = predict_one(features)
        # Intentar extraer la version desde meta (si existe)
        version = get_meta().get("version", "unknown")
    except Exception as e:
        return jsonify({"error": "prediction_error", "details": str(e)}), 500

    # 4) Respuesta
    resp = PredictResponse(salary_pred=float(y_hat), model_version=str(version))
    return jsonify(resp.model_dump()), 200


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
