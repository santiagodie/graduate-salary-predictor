# 🎓 Sistema de Predicción Salarial para Graduados

Aplicación web minimalista para predecir salarios de graduados internacionales basada en su formación y experiencia.

## 🚀 Instalación Rápida (5 minutos)

### Requisitos Previos
- Python 3.7 o superior
- MAMP (opcional, para despliegue local)

### Pasos de Instalación

1. **Descargar el proyecto**
```bash
# Opción 1: Si tienes los archivos
# Simplemente descomprime en una carpeta

# Opción 2: Crear desde cero
mkdir prediccion-salarial
cd prediccion-salarial
```

2. **Instalar Flask** (única dependencia)
```bash
pip install flask

# O usando requirements.txt
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**
```bash
python app.py
```

4. **Abrir en el navegador**
```
http://localhost:5000
```

¡Listo! La aplicación ya está funcionando.

## 📁 Estructura del Proyecto

```
prediccion-salarial/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias (solo Flask)
├── templates/            # Plantillas HTML
│   ├── base.html         # Template base
│   ├── inicio.html       # Página de inicio
│   ├── info.html         # Información del modelo
│   ├── formulario.html   # Formulario de predicción
│   ├── resultado.html    # Resultados y gráficos
│   └── error.html        # Página de errores
└── static/              # Archivos estáticos
    ├── css/
    │   └── style.css     # Estilos personalizados
    └── js/
        └── app.js        # JavaScript del formulario
```

## 🌟 Características

- **Sin dependencias complejas**: Solo Flask
- **Sin npm/webpack**: Todo via CDN (Tailwind CSS, Chart.js)
- **Responsive**: Funciona en móvil y desktop
- **Multi-idioma**: Español, Inglés, Francés
- **Formulario dinámico**: 2 pasos con validación
- **Gráficos interactivos**: Comparaciones visuales
- **Datos persistentes**: SessionStorage para no perder información

## 🛠️ Configuración para MAMP

Si quieres usar MAMP en lugar de ejecutar Python directamente:

1. **Configurar Python en MAMP**
   - Asegúrate de que MAMP tenga Python instalado
   - Configura el puerto 5000 para la aplicación Flask

2. **Configurar Apache como proxy**
   
   Añade esto a `httpd.conf`:
   ```apache
   ProxyPass /prediccion http://localhost:5000
   ProxyPassReverse /prediccion http://localhost:5000
   ```

3. **Ejecutar Flask como servicio**
   ```bash
   # En la carpeta del proyecto
   python app.py --host=0.0.0.0 --port=5000
   ```

## 📊 Cómo Funciona

1. **Inicio**: Landing page con información general
2. **Formulario**: 
   - Paso 1: Datos personales (edad, país, género)
   - Paso 2: Datos de formación (titulación, experiencia, etc.)
3. **Procesamiento**: Algoritmo que calcula el salario basado en:
   - Nivel educativo (35%)
   - Experiencia (25%)
   - Ubicación (20%)
   - Competencias (15%)
   - Situación actual (5%)
4. **Resultados**: 
   - Salario estimado
   - Comparaciones con medias del sector
   - Gráficos interactivos

## 🔧 Personalización

### Modificar el algoritmo de predicción
Edita la función `predict()` en `app.py`:
```python
# Línea ~55 en app.py
def predict():
    # Modifica los multiplicadores y bonos aquí
```

### Cambiar colores/diseño
- Modifica las clases de Tailwind en los templates HTML
- Añade estilos personalizados en `static/css/style.css`

### Añadir idiomas
Edita el objeto `translations` en `static/js/app.js`:
```javascript
// Línea ~3 en app.js
const translations = {
    // Añade tu idioma aquí
}
```

## 🐛 Solución de Problemas

### Error: "Flask no encontrado"
```bash
pip install flask
```

### Puerto 5000 ocupado
Cambia el puerto en `app.py`:
```python
app.run(debug=True, port=8000)  # Usa otro puerto
```

### Los gráficos no se muestran
- Verifica conexión a internet (Chart.js se carga via CDN)
- Revisa la consola del navegador por errores

## 📝 Notas para el Desarrollo

- **Modo debug activo**: Los cambios se recargan automáticamente
- **Datos mock**: El modelo usa datos simulados, no ML real
- **Sin base de datos**: Todo en memoria (se pierde al reiniciar)
- **Sin autenticación**: Versión simplificada sin usuarios

## 🎯 Próximos Pasos (Opcional)

Si quieres expandir el proyecto:

1. **Añadir ML real**: Integrar scikit-learn o TensorFlow
2. **Base de datos**: SQLite para persistencia
3. **Autenticación**: Flask-Login para usuarios
4. **API REST completa**: Flask-RESTful
5. **Deployment**: Heroku, PythonAnywhere, o AWS

## 📄 Licencia

Proyecto académico - 4º año Ingeniería Informática

## 🤝 Soporte

Para problemas o preguntas, revisa:
1. La consola de Python por errores
2. La consola del navegador (F12)
3. Los logs en `app.py` (modo debug activo)

---

**Tiempo estimado de setup: 5 minutos** ⏱️

¡Disfruta prediciendo salarios! 🚀
