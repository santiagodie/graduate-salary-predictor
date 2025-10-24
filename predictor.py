# model/predictor.py

import joblib
import pandas as pd
# Asegúrate de tener estas librerías instaladas: pip install joblib pandas

# --------------------------------------------------------------------------
# --- 1. CONFIGURACIÓN Y CARGA DEL MODELO ---
# --------------------------------------------------------------------------

# 1. Ruta al archivo del modelo entrenado
MODEL_FILE = 'model/model.pkl' # Asegúrate de que el modelo exista aquí

# 2. ORDEN EXACTO DE LAS COLUMNAS (FEATURES) que el modelo espera.
# Este es el paso MÁS CRÍTICO. ¡Debe coincidir con el entrenamiento!
COLUMN_ORDER = [
    '##Contenido no sabido##_feature_1', 
    '##Contenido no sabido##_feature_2', 
    '##Contenido no sabido##_feature_3_categorica' # Ejemplo de una columna
] 

# Variable global para almacenar el objeto del modelo cargado
MODEL = None 
# Puedes necesitar cargar también un StandardScaler o OneHotEncoder si los usaste
SCALER = None # ##Contenido no sabido##_cargar_scaler_si_aplica

try:
    # Carga el modelo una única vez al iniciar el back-end
    MODEL = joblib.load(MODEL_FILE)
    print(f"✅ Modelo predictivo cargado exitosamente desde {MODEL_FILE}")

    # ##Contenido no sabido##: Carga transformadores si son necesarios
    # Ejemplo:
    # SCALER = joblib.load('model/scaler.pkl') 

except FileNotFoundError:
    print(f"❌ ERROR: El archivo del modelo NO se encontró en {MODEL_FILE}")
except Exception as e:
    print(f"❌ ERROR al cargar el modelo: {e}")

# --------------------------------------------------------------------------
# --- 2. FUNCIÓN PRINCIPAL DE PREDICCIÓN ---
# --------------------------------------------------------------------------

def preprocess_and_predict(input_data: dict) -> float:
    """
    Recibe los datos del usuario, los preprocesa y devuelve una predicción.

    Args:
        input_data (dict): Diccionario con las claves/valores enviados desde el front-end.

    Returns:
        float: El valor de la predicción (ej. el sueldo).
    """
    
    # 1. Verificación inicial de carga del modelo
    if MODEL is None:
        raise Exception("El servicio de predicción no está disponible. Fallo al cargar el modelo.")

    # 2. Crear una lista de valores en el orden correcto
    # Esto asegura que los datos de entrada coincidan con el orden de COLUMN_ORDER
    try:
        data_values = [input_data[col] for col in COLUMN_ORDER]
    except KeyError as e:
        # Se lanza un error si falta algún dato que el modelo espera
        raise ValueError(f"Falta un dato de entrada requerido: {e}")

    # 3. Convertir a DataFrame (el formato esperado por scikit-learn)
    data_df = pd.DataFrame([data_values], columns=COLUMN_ORDER)

    # 4. ##Contenido no sabido##: Aplicar Preprocesamiento (si aplica)
    # Si las features ['columna_A', 'columna_B'] fueron escaladas en el entrenamiento, 
    # DEBEN ser escaladas aquí ANTES de pasarlas al .predict().

    # Si usaste Codificación One-Hot o Label Encoding, DEBES replicar esa lógica.
    # Ejemplo con escalado (asumiendo que SCALER está cargado):
    # data_scaled = SCALER.transform(data_df[SCALER.feature_names_in_])
    # data_final = pd.DataFrame(data_scaled, columns=SCALER.feature_names_in_) 
    
    ##Contenido no sabido##_logica_de_transformacion = data_df 

    # 5. Realizar la predicción
    try:
        prediction = MODEL.predict(##Contenido no sabido##_logica_de_transformacion)[0]
    except Exception as e:
        raise Exception(f"Fallo al ejecutar la predicción del modelo: {e}")
    
    # 6. Devolver el resultado como un float
    return float(prediction)