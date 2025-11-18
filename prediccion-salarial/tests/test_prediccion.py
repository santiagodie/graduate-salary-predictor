"""
Script para probar si el backend está usando el modelo real
Ejecuta este script mientras app.py está corriendo
"""
import requests
import json

# URL del servidor (ajusta si es necesario)
BASE_URL = "http://localhost:5000"

print("=" * 70)
print("PRUEBA DE PREDICCIÓN - Verificar si usa modelo real o mock")
print("=" * 70)

# 1. Verificar health check
print("\n1. Verificando estado del servidor...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    health = response.json()
    print(f"   Status: {health['status']}")
    print(f"   Version: {health.get('version', 'N/A')}")

    if health['status'] == 'ok (mock)':
        print("\n   [WARNING] El servidor esta en modo MOCK")
        print(f"   Razon: {health.get('detail', 'N/A')}")
    else:
        print("\n   [OK] El servidor tiene predictor disponible")
except Exception as e:
    print(f"   [ERROR] Error: {e}")
    exit(1)

# 2. Verificar info del modelo
print("\n2. Verificando información del modelo...")
try:
    response = requests.get(f"{BASE_URL}/api/model/info")
    model_info = response.json()
    print(f"   Version: {model_info.get('version', 'N/A')}")
    print(f"   Predictor disponible: {model_info.get('predictor_available', False)}")

    if not model_info.get('predictor_available', False):
        print("\n   [WARNING] El predictor NO esta disponible - usando MOCK")
    else:
        print("\n   [OK] Predictor REAL disponible")
except Exception as e:
    print(f"   [ERROR] Error: {e}")

# 3. Hacer una predicción de prueba
print("\n3. Haciendo predicción de prueba...")
print("   (Revisa la CONSOLA del servidor Flask para ver los logs)")

# Datos de prueba
test_data = {
    "nombre": "Test Usuario",
    "edad": 28,
    "pais": "España",
    "genero": "Hombre",
    "titulacion": "Master",
    "aniosDesdeObtencion": 3,
    "campoEstudio": "IT",
    "nivelIngles": "Avanzado",
    "universidadRanking": "Alto",
    "regionEstudio": "Europa",
    "notaMedia": 8.5,
    "practicas": True,
    "situacionLaboral": "Empleado"
}

print(f"\n   Datos enviados:")
print(f"   - País: {test_data['pais']}")
print(f"   - Titulación: {test_data['titulacion']}")
print(f"   - Campo: {test_data['campoEstudio']}")

try:
    response = requests.post(
        f"{BASE_URL}/api/predict",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"\n   [OK] Prediccion exitosa!")
        print(f"   Salario predicho: ${result['salary']:,.2f}")
        print(f"   Model version: {result['model_version']}")
        print(f"   Form ID: {result.get('form_id', 'N/A')}")

        # CLAVE: Verificar si usa modelo real
        using_real = result.get('using_real_model', False)
        if using_real:
            print(f"\n   [OK] [OK] [OK] USANDO MODELO REAL [OK] [OK] [OK]")
        else:
            print(f"\n   [WARNING] [WARNING] USANDO MOCK (no modelo real) [WARNING]")

        print("\n" + "=" * 70)
        print("IMPORTANTE: Revisa la CONSOLA donde corre 'python app.py'")
        print("=" * 70)
        print("\nDeberias ver UNO de estos mensajes:")
        print("\n[OK] SI USA EL MODELO REAL:")
        print("   [INFO] Usando MODELO REAL para prediccion")
        print("   [INFO] Features recibidas: [...]")
        print("   [INFO] Features preprocesadas correctamente")
        print("   [INFO] Prediccion realizada: XXXX.XX")

        print("\n[WARNING] SI USA EL MOCK:")
        print("   [WARNING] Usando prediccion MOCK (modelo no cargado)")

    else:
        print(f"\n   [ERROR] Error en la prediccion: {response.status_code}")
        print(f"   Respuesta: {response.text}")

except Exception as e:
    print(f"   [ERROR] Error: {e}")

print("\n" + "=" * 70)
