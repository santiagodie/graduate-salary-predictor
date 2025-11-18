import pickle
import numpy as np
import pandas as pd
import os

# --- CONFIGURACIÓN ---
NOMBRE_DE_TU_ARCHIVO = 'modelo_entrenado.pkl'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_COMPLETA = os.path.join(BASE_DIR, NOMBRE_DE_TU_ARCHIVO)

print(f"Buscando el archivo en: {RUTA_COMPLETA}\n")

try:
    with open(RUTA_COMPLETA, 'rb') as f:
        model = pickle.load(f)

    print("--- ¡Modelo cargado con éxito! ---")
    print(f"El tipo de modelo es: {type(model)}\n")

    # --- EXTRACCIÓN DE NOMBRES Y PORCENTAJES ---

    # 1. Obtener el modelo final (RandomForest)
    # Suponemos que es el último paso
    final_model = model.steps[-1][1]
    
    # 2. Obtener los porcentajes de ese modelo
    importances = final_model.feature_importances_
    percentages = (importances / importances.sum() * 100).round(2)

    # 3. Obtener los nombres de las características del preprocesador
    # Suponemos que es el primer paso
    preprocessor = model.steps[0][1]
    
    # Usar .get_feature_names_out() para obtener la lista de todas las columnas
    # (incluyendo las creadas por OneHotEncoder)
    try:
        feature_names = preprocessor.get_feature_names_out()
        print("Nombres de características extraídos con éxito.")
    except Exception as e:
        print(f"Error al obtener nombres de características: {e}")
        print("Asegúrate de que tu versión de Scikit-learn (1.7.2) es compatible con la que entrenó el modelo (1.4.2).")
        print("Si falla, es posible que el preprocesador no sea el primer paso. ¡Pero inténtalo primero!")
        feature_names = [f"feature_{i}" for i in range(len(percentages))] # Nombres genéricos si falla

    # 4. Unir todo en un DataFrame de Pandas
    if len(feature_names) == len(percentages):
        print("\n--- IMPORTANCIA DE CADA CARACTERÍSTICA ---")
        
        # Ocultar advertencia de versión inconsistente para la legibilidad
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # Crear el DataFrame
        df_importances = pd.DataFrame({
            'Feature': feature_names,
            'Percentage': percentages
        })

        # Ordenar por importancia y mostrar
        df_importances = df_importances.sort_values(by='Percentage', ascending=False)
        
        # Configurar pandas para mostrar todas las filas
        pd.set_option('display.max_rows', None)
        
        print(df_importances)
        
        print("\n--- FIN DEL REPORTE ---")

    else:
        print(f"Error: El número de nombres ({len(feature_names)}) no coincide con el número de importancias ({len(percentages)}).")


except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta esperada.")
except Exception as e:
    print(f"Ocurrió un error: {e}")