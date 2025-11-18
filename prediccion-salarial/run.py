"""
run.py - Punto de entrada principal de la aplicación
"""

import os
from app import create_app
from app.models.predictor import _PREDICTOR_AVAILABLE, load_meta

# Crear aplicación
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"

    print("=" * 60)
    print("Iniciando Salary Prediction App")
    print("=" * 60)
    print(f"Puerto: {port}")
    print(f"Debug: {debug}")
    print(f"Predictor real: {'SI' if _PREDICTOR_AVAILABLE else 'NO (mock)'}")
    print(f"Modelo: {load_meta().get('version', 'unknown')}")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
