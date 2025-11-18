"""
Script de prueba para verificar que el modelo carga correctamente
"""
import pickle
import warnings
from pathlib import Path

# Suprimir advertencias de incompatibilidad de versiones de sklearn
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

print("=" * 60)
print("PRUEBA DE CARGA DEL MODELO")
print("=" * 60)

# 1. Verificar que el archivo existe
modelo_path = Path(__file__).parent.parent / 'data' / 'modelo_entrenado.pkl'
print(f"\n1. Verificando archivo:")
print(f"   Ruta: {modelo_path}")
print(f"   Existe: {modelo_path.exists()}")

if modelo_path.exists():
    print(f"   Tamanio: {modelo_path.stat().st_size / (1024*1024):.2f} MB")
else:
    print("   [ERROR] El archivo no existe!")
    exit(1)

# 2. Intentar cargar el modelo
print(f"\n2. Intentando cargar el modelo con pickle...")
try:
    with open(modelo_path, 'rb') as file:
        modelo = pickle.load(file)
    print(f"   [OK] Modelo cargado exitosamente!")
    print(f"   Tipo: {type(modelo)}")
    if hasattr(modelo, '__class__'):
        print(f"   Clase: {modelo.__class__.__name__}")
except Exception as e:
    print(f"   [ERROR] al cargar: {e}")
    print(f"\n   NOTA: Si el error menciona 'sklearn', necesitas instalar:")
    print(f"         pip install scikit-learn pandas")
    exit(1)

# 3. Verificar si tiene el método predict
print(f"\n3. Verificando metodo predict:")
if hasattr(modelo, 'predict'):
    print(f"   [OK] El modelo tiene metodo predict()")
else:
    print(f"   [ERROR] El modelo NO tiene metodo predict()")

# 4. Intentar usar el predictor.py
print(f"\n4. Probando predictor.py:")
try:
    from predictor import predict_one, MODEL

    if MODEL is not None:
        print(f"   [OK] Predictor cargo el modelo correctamente")
        print(f"   Tipo de MODEL: {type(MODEL)}")
    else:
        print(f"   [ERROR] Predictor no cargo el modelo (MODEL = None)")
except Exception as e:
    print(f"   [ERROR] Error importando predictor: {e}")

print("\n" + "=" * 60)
print("FIN DE LA PRUEBA")
print("=" * 60)
