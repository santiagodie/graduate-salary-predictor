# Como consultar desde el frotend a un modelo guardado en pickle usando scikit-learn en Python.

import pickle
import numpy as np
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
app = Flask(__name__)
# Cargar el modelo guardado en pickle
with open('modelo.pkl', 'rb') as f:
    modelo = pickle.load(f)
@app.route('/predict', methods=['POST'])
def predict():
    # Obtener los datos JSON enviados desde el frontend
    data = request.get_json()
    # Convertir los datos en un array numpy
    input_data = np.array(data['input']).reshape(1, -1)
    # Realizar la predicción usando el modelo cargado
    prediction = modelo.predict(input_data)
    # Devolver la predicción como respuesta JSON
    return jsonify({'prediction': prediction.tolist()})
if __name__ == '__main__':
    app.run(debug=True)
# Este código crea una API REST simple usando Flask que recibe datos de entrada en formato JSON,
# realiza una predicción con un modelo de scikit-learn cargado desde un archivo pickle
# y devuelve la predicción en formato JSON.

# Asegúrate de tener Flask y scikit-learn instalados en tu entorno de Python.
# Puedes instalar Flask usando pip:
# pip install Flask
# Y scikit-learn:
# pip install scikit-learn

# Guarda este código en un archivo llamado predictor.py y ejecuta el script.
# Luego, puedes enviar solicitudes POST a la ruta /predict con datos JSON para obtener predicciones
# desde tu modelo guardado en pickle.



