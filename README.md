# Predictor de Sueldos

**Trabajo Final 2025-2026**

**Asignatura:** Profesión de Ingeniero Informático

**Universidad de La Rioja**

## Integrantes del Grupo

- Isaac Terés
- Jon Jiménez
- Alberto Hidalgo
- Santiago Die

## Descripción del Proyecto

Sistema de predicción salarial desarrollado con Flask y Machine Learning que permite estimar salarios basándose en diferentes características profesionales y demográficas. El proyecto implementa algoritmos de aprendizaje automático para proporcionar predicciones precisas y una interfaz web intuitiva para interactuar con el modelo.

## Tecnologías Utilizadas

### Backend
- **Flask 3.0.0** - Framework web de Python
- **Flask-CORS** - Manejo de CORS para API REST
- **Pydantic** - Validación de datos

### Frontend
- **HTML5** - Estructura de las páginas web
- **Tailwind CSS** - Framework CSS para diseño responsive y moderno
- **JavaScript (Vanilla)** - Interactividad y lógica del cliente
- **Chart.js** - Librería para visualización de datos y gráficos
- **Jinja2** - Motor de plantillas integrado con Flask

### Machine Learning y Procesamiento de Datos
- **Scikit-learn** - Algoritmos de machine learning
- **Pandas** - Análisis y manipulación de datos

### Adicionales
- **Requests** - Cliente HTTP para Python

## Estructura del Proyecto

```
Predictor_sueldos/
│
├── prediccion-salarial/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/          # Modelos de ML y datos
│   │   ├── routes/          # Endpoints de la API
│   │   ├── static/          # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── templates/       # Plantillas HTML
│   │   └── utils/           # Funciones auxiliares
│   │
│   ├── data/                # Datasets y archivos de datos
│   ├── tests/               # Tests unitarios y de integración
│   ├── config.py            # Configuración de la aplicación
│   ├── run.py               # Punto de entrada de la aplicación
│   └── requirements.txt     # Dependencias del proyecto
│
└── README.md
```

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/Predictor_sueldos.git
   cd Predictor_sueldos/prediccion-salarial
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate

   # En Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

### Ejecutar tests

```bash
python -m pytest tests/
```

## Funcionalidades

### Características Principales
- **Predicción de salarios** basada en Machine Learning
- **Interfaz web moderna y responsive** con diseño adaptativo
- **Visualización de datos** mediante gráficos interactivos (Chart.js)
- **Historial de predicciones** con almacenamiento local
- **Soporte multiidioma** (Español, Inglés, Francés)
- **Conversión de divisas** (USD, EUR, GBP)
- **API REST** para integración con otros sistemas
- **Validación de datos** de entrada robusta
- **Sistema de navegación intuitivo** con múltiples vistas:
  - Página de inicio
  - Formulario de predicción
  - Resultados detallados
  - Página de información
  - Manejo de errores personalizado

## Desarrollo

### Configuración de Desarrollo

El archivo `config.py` contiene las configuraciones necesarias para el entorno de desarrollo y producción.


---

**Universidad de La Rioja - 2025/2026**
