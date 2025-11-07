# model/predictor.py

import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
import unicodedata

# --------------------------------------------------------------------------
# --- 1. CONFIGURACIÓN Y CARGA DEL MODELO ---
# --------------------------------------------------------------------------

# Rutas de archivos
MODEL_FILE = Path(__file__).parent / 'model.pkl'
META_FILE = Path(__file__).parent / 'metadata.json'

# 2. ORDEN EXACTO DE LAS COLUMNAS (FEATURES) que el modelo espera
# Basado en tu schema.py y formulario
COLUMN_ORDER = [
    'edad',
    'pais',
    'genero',
    'titulacion',
    'anios_desde_titulo',  # Años desde obtención del título
    'campo_estudio',
    'nivel_ingles',
    'universidad_ranking',
    'region_estudio',
    'nota_media',
    'practicas',  # bool convertido a 0/1
    'situacion_laboral'
]

# Mapeos para codificación categórica (deben coincidir con el entrenamiento)
# IMPORTANTE: Ajusta estos valores según cómo entrenaste el modelo
ENCODING_MAPS = {
    'pais': {
        'brasil': 0, 'china': 1, 'españa': 2, 'pakistan': 3,
        'usa': 4, 'india': 5, 'vietnam': 6, 'nigeria': 7
    },
    'genero': {
        'hombre': 0, 'mujer': 1, 'otro': 2
    },
    'titulacion': {
        'fp': 0, 'grado': 1, 'master': 2, 'phd': 3
    },
    'campo_estudio': {
        'artes': 0, 'ing': 1, 'it': 2, 'salud': 3,
        's_sociales': 4, 'empresa': 5
    },
    'nivel_ingles': {
        'basico': 0, 'intermedio': 1, 'avanzado': 2, 'fluido': 3
    },
    'universidad_ranking': {
        'bajo': 0, 'medio': 1, 'alto': 2
    },
    'region_estudio': {
        'australia': 0, 'europa': 1, 'usa': 2
    },
    'situacion_laboral': {
        'estudiando': 0, 'desempleado': 1, 'empleado': 2
    }
}

# Variables globales
MODEL = None
SCALER = None
METADATA = None

# --------------------------------------------------------------------------
# --- Utilidades internas ---
# --------------------------------------------------------------------------


def _normalize_str(value: Any) -> str:
    """
    Normaliza cadenas: none-safe, strip, lower y elimina acentos.
    """
    if value is None:
        return ""
    s = str(value).strip().lower()
    # eliminar acentos/diacríticos para robustez
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s


def _build_normalized_map(encoding_map: Dict[str, int]) -> Dict[str, int]:
    """
    Construye un mapa con claves normalizadas para permitir coincidencias más flexibles.
    """
    return { _normalize_str(k): v for k, v in encoding_map.items() }


# --------------------------------------------------------------------------
# --- CARGA INICIAL ---
# --------------------------------------------------------------------------


def _load_model():
    """Carga el modelo una única vez al iniciar."""
    global MODEL, SCALER, METADATA

    try:
        if MODEL_FILE.exists():
            MODEL = joblib.load(MODEL_FILE)
            print(f"[OK] Modelo predictivo cargado exitosamente desde {MODEL_FILE}")
        else:
            raise FileNotFoundError(f"{MODEL_FILE} no existe")

        # Si usaste un scaler, cárgalo aquí
        scaler_path = MODEL_FILE.parent / 'scaler.pkl'
        if scaler_path.exists():
            SCALER = joblib.load(scaler_path)
            print(f"[OK] Scaler cargado desde {scaler_path}")

        # Cargar metadata si existe
        if META_FILE.exists():
            with open(META_FILE, 'r', encoding='utf-8') as f:
                METADATA = json.load(f)
            print(f"[OK] Metadata cargada desde {META_FILE}")
        else:
            # Crear metadata por defecto
            METADATA = {
                "version": "1.0.0",
                "trained_at": datetime.now().isoformat(),
                "metrics": {},
                "features": COLUMN_ORDER
            }

    except FileNotFoundError as fnf:
        # Modo mock: no detener la importación de la librería
        MODEL = None
        SCALER = None
        METADATA = {
            "version": "mock",
            "trained_at": "N/A",
            "metrics": {},
            "features": COLUMN_ORDER
        }
        print(f"[WARNING] Archivo del modelo no encontrado en {MODEL_FILE}: {fnf}")
        print("          El sistema funcionará en modo MOCK para desarrollo")
    except Exception as e:
        MODEL = None
        SCALER = None
        METADATA = {
            "version": "error",
            "trained_at": "N/A",
            "metrics": {"load_error": str(e)},
            "features": COLUMN_ORDER
        }
        print(f"[ERROR] Error al cargar el modelo: {e}")


# Cargar al importar el módulo
_load_model()

# --------------------------------------------------------------------------
# --- 2. FUNCIONES DE PREPROCESAMIENTO ---
# --------------------------------------------------------------------------


def _encode_categorical(value: Any, feature_name: str) -> int:
    """
    Codifica una variable categórica a su valor numérico.
    Soporta coincidencias insensibles a mayúsculas y sin acentos.
    """
    encoding_map = ENCODING_MAPS.get(feature_name)
    if encoding_map is None:
        raise ValueError(f"No existe mapa de codificación para '{feature_name}'")

    norm_map = _build_normalized_map(encoding_map)
    norm_value = _normalize_str(value)

    if norm_value in norm_map:
        return norm_map[norm_value]

    # Intentar convertir directamente si el usuario envía un entero válido
    try:
        maybe_int = int(value)
        if maybe_int in encoding_map.values():
            return maybe_int
    except Exception:
        pass

    allowed = list(encoding_map.keys())
    raise ValueError(
        f"Valor '{value}' no válido para '{feature_name}'. "
        f"Valores permitidos: {allowed}"
    )


def _preprocess_features(input_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Preprocesa los datos de entrada:
    1. Convierte categóricas a numéricas
    2. Convierte booleanos a 0/1
    3. Asegura el orden correcto de columnas
    """
    processed = {}

    for feature in COLUMN_ORDER:
        if feature not in input_data:
            raise ValueError(f"Falta la feature requerida: '{feature}'")

        value = input_data[feature]

        # Procesar según el tipo de feature
        if feature in ENCODING_MAPS:
            # Variable categórica -> codificar
            processed[feature] = _encode_categorical(value, feature)

        elif feature == 'practicas':
            # Booleano -> convertir a 0/1. Acepta True/False, 'true'/'false', 1/0
            if isinstance(value, bool):
                processed[feature] = 1 if value else 0
            else:
                s = _normalize_str(value)
                if s in ("1", "true", "yes", "si", "sí"):
                    processed[feature] = 1
                elif s in ("0", "false", "no"):
                    processed[feature] = 0
                else:
                    # fallback: intentar cast int
                    try:
                        processed[feature] = int(value)
                    except Exception:
                        raise ValueError(f"Valor no válido para 'practicas': {value}")

        elif feature in ['edad', 'anios_desde_titulo', 'nota_media']:
            # Variables numéricas -> asegurar tipo float
            try:
                processed[feature] = float(value)
            except Exception:
                raise ValueError(f"Feature numérica '{feature}' debe ser convertible a float. Valor: {value}")

        else:
            # Por defecto, mantener el valor tal cual (pero normalizamos strings)
            if isinstance(value, str):
                processed[feature] = value.strip()
            else:
                processed[feature] = value

    # Crear DataFrame con el orden correcto
    df = pd.DataFrame([processed], columns=COLUMN_ORDER)

    return df


def _apply_scaling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica escalado si se usó durante el entrenamiento.
    """
    if SCALER is None:
        return df

    # Identificar columnas numéricas que deben ser escaladas
    numeric_cols = ['edad', 'anios_desde_titulo', 'nota_media']

    # Crear copia para no modificar el original
    df_scaled = df.copy()

    # Determinar columnas a escalar
    try:
        if hasattr(SCALER, 'feature_names_in_'):
            cols_to_scale = [c for c in SCALER.feature_names_in_ if c in df.columns]
        else:
            cols_to_scale = [c for c in numeric_cols if c in df.columns]

        if cols_to_scale:
            # SCALER.transform espera una matriz 2D
            df_scaled[cols_to_scale] = SCALER.transform(df[cols_to_scale])
    except Exception as e:
        # No fallar la predicción por problemas del scaler; emitir aviso y devolver df sin cambios
        print(f"[WARNING] Error aplicando scaler: {e}")
        return df

    return df_scaled


# --------------------------------------------------------------------------
# --- 3. FUNCIÓN PRINCIPAL DE PREDICCIÓN (usada por app.py) ---
# --------------------------------------------------------------------------


def predict_one(features_dict: Dict[str, Any]) -> float:
    """
    Función principal que usa app.py para hacer predicciones.

    Args:
        features_dict: Diccionario con todas las features necesarias

    Returns:
        float: Predicción del salario
    """
    # Verificación inicial
    if MODEL is None:
        # Modo MOCK para desarrollo: heurística simple
        print("[WARNING] Usando predicción MOCK (modelo no cargado)")
        edad = features_dict.get('edad', 25)
        try:
            edad_val = float(edad)
        except Exception:
            edad_val = 25.0
        return 45000.0 + (edad_val * 500.0)

    # 1. Preprocesar features
    try:
        df = _preprocess_features(features_dict)
    except ValueError as e:
        raise ValueError(f"Error en preprocesamiento: {e}")

    # 2. Aplicar escalado si corresponde
    df_final = _apply_scaling(df)

    # 3. Realizar predicción
    try:
        prediction = MODEL.predict(df_final)[0]
    except Exception as e:
        raise Exception(f"Error al ejecutar predicción del modelo: {e}")

    # 4. Devolver resultado
    return float(prediction)


# --------------------------------------------------------------------------
# --- 4. FUNCIÓN DE METADATA (usada por app.py) ---
# --------------------------------------------------------------------------


def load_meta() -> Dict[str, Any]:
    """
    Devuelve metadata del modelo para el endpoint /model/info
    """
    if METADATA is not None:
        return METADATA

    # Metadata por defecto si no se pudo cargar
    return {
        "version": "1.0.0-mock",
        "trained_at": "N/A",
        "metrics": {
            "note": "Modelo no cargado, usando valores mock"
        },
        "features": COLUMN_ORDER
    }


def get_model_version() -> str:
    """Devuelve la versión del modelo."""
    meta = load_meta()
    return meta.get("version", "unknown")


# --------------------------------------------------------------------------
# --- 5. FUNCIÓN LEGACY (para compatibilidad) ---
# --------------------------------------------------------------------------


def preprocess_and_predict(input_data: dict) -> float:
    """
    Función legacy - redirige a predict_one para mantener compatibilidad.
    """
    return predict_one(input_data)


# --------------------------------------------------------------------------
# --- 6. UTILIDADES DE VALIDACIÓN ---
# --------------------------------------------------------------------------


def validate_input_data(data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Valida que los datos de entrada sean correctos.

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Verificar features requeridas
    for feature in COLUMN_ORDER:
        if feature not in data:
            errors.append(f"Falta feature requerida: '{feature}'")

    # Validar rangos numéricos
    if 'edad' in data:
        try:
            edad = float(data['edad'])
            if not (16 <= edad <= 80):
                errors.append(f"Edad fuera de rango (16-80): {edad}")
        except Exception:
            errors.append(f"Edad debe ser numérica: {data['edad']}")

    if 'nota_media' in data:
        try:
            nota = float(data['nota_media'])
            if not (0 <= nota <= 10):
                errors.append(f"Nota media fuera de rango (0-10): {nota}")
        except Exception:
            errors.append(f"Nota media debe ser numérica: {data['nota_media']}")

    if 'anios_desde_titulo' in data:
        try:
            anios = float(data['anios_desde_titulo'])
            if not (0 <= anios <= 40):
                errors.append(f"Años desde título fuera de rango (0-40): {anios}")
        except Exception:
            errors.append(f"Años desde título debe ser numérico: {data['anios_desde_titulo']}")

    # Validar valores categóricos
    for feature, encoding_map in ENCODING_MAPS.items():
        if feature in data:
            val = data[feature]
            norm_val = _normalize_str(val)
            norm_map = _build_normalized_map(encoding_map)
            if norm_val not in norm_map and str(val) not in map(str, encoding_map.values()):
                errors.append(
                    f"Valor '{val}' no válido para '{feature}'. "
                    f"Permitidos: {list(encoding_map.keys())}"
                )

    return len(errors) == 0, errors


# --------------------------------------------------------------------------
# --- TESTING ---
# --------------------------------------------------------------------------

if __name__ == "__main__":
    # Datos de prueba
    test_data = {
        'edad': 28.0,
        'pais': 'españa',
        'genero': 'mujer',
        'titulacion': 'master',
        'anios_desde_titulo': 3.0,
        'campo_estudio': 'it',
        'nivel_ingles': 'avanzado',
        'universidad_ranking': 'alto',
        'region_estudio': 'europa',
        'nota_media': 8.5,
        'practicas': True,
        'situacion_laboral': 'empleado'
    }

    print("\n" + "="*60)
    print("PRUEBA DEL PREDICTOR")
    print("="*60)

    # Validar datos
    is_valid, errors = validate_input_data(test_data)
    if not is_valid:
        print("\n[ERROR] Errores de validación:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n[OK] Datos válidos")

    # Hacer predicción
    try:
        salary_pred = predict_one(test_data)
        print(f"\n[PREDICCION] Salario estimado: {salary_pred:,.2f} EUR")
        print(f"\n[METADATA] Información del modelo:")
        meta = load_meta()
        print(f"  - Versión: {meta['version']}")
        print(f"  - Features: {len(meta['features'])}")
    except Exception as e:
        print(f"\n[ERROR] Error en predicción: {e}")

    print("\n" + "="*60)