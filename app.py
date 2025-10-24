# predictive_app/app.py
import os
import json
from pathlib import Path
from typing import Any, Dict

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError

from predictive_app.schema import PredictRequest, PredictResponse

# ---------------------------------------------------------
# Carga del "predictor" (lo hace tu compañero)
# Debe exponer al menos:
#   - predict_one(features_dict: dict) -> float
#   - load_meta() -> dict con {"version","trained_at","metrics","features":[...]}
# Opcionalmente:
#   - get_model_version() -> str
# ---------------------------------------------------------
try:
    from predictor import predict_one, load_meta  # type: ignore
    _PREDICTOR_AVAILABLE = True
except Exception as e:
    # Modo MOCK si aún no está el predictor real
    _PREDICTOR_AVAILABLE = False
    _MOCK_ERR = str(e)

    def predict_one(features_dict: Dict[str, Any]) -> float:  # type: ignore
        # Devuelve un valor fijo para probar el cableado
        return 12345.0

    def load_meta() -> Dict[str, Any]:  # type: ignore
        # Meta mínima para pruebas sin modelo real
        return {
            "version": "mock",
            "trained_at": "N/A",
            "metrics": {},
            # Lista de features esperadas por el modelo (ajústala a las definitivas)
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
                # Si tenéis 12 exactas, añadid aquí la(s) restante(s), por ejemplo:
                # "anios_desde_graduacion", "gpa"
            ],
        }

# ---------------------------------------------------------
# Flask app y CORS
# ---------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONT_ORIGIN", "http://localhost:5173")}})

# Cache de metadatos para no releer en cada request
_META_CACHE: Dict[str, Any] | None = None


def get_meta() -> Dict[str, Any]:
    global _META_CACHE
    if _META_CACHE is None:
        _META_CACHE = load_meta()
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
        # Añade aquí si vuestro modelo usa más columnas (debe estar también en metadata["features"])
        # "anios_desde_graduacion": req.anios_desde_graduacion,
        # "gpa": req.gpa,
        # ...
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
    return body, 200


@app.get("/model/info")
def model_info():
    try:
        meta = get_meta()
        return {
            "version": meta.get("version", "unknown"),
            "trained_at": meta.get("trained_at", "unknown"),
            "metrics": meta.get("metrics", {}),
            "features": meta.get("features", []),
        }, 200
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
    return resp.model_dump(), 200


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
