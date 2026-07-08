# 🔬 SiPakMed-AI: Sistema de Análisis de Células Cervicales

Aplicación de Streamlit para clasificar células cervicales usando modelos de deep learning (CNN clásicas y modelos híbridos).

## ✨ Características

- 🎨 **Tema oscuro moderno** con diseño minimalista y atractivo
- 📊 **Gráficos interactivos** (distribución de probabilidades, consenso entre modelos)
- 📄 **Generación de reportes PDF** con resultados visuales
- 🎯 **Mejora de imágenes** con CLAHE (preservando colores)
- 🧠 **5 modelos**: 3 CNN clásicas + 2 híbridos
- 🌍 **Idiomas**: Español / English

## 🚀 Cómo Desplegar en Streamlit Community Cloud

1. Ve a https://share.streamlit.io
2. Haz clic en **"New app"**
3. Selecciona tu repositorio: `BustosDeker/Celulas-Cervicales`
4. Selecciona la rama: `main`
5. Escribe la ruta del archivo principal: `app.py`
6. ¡Haz clic en **Deploy**!

## 📦 Instalación Local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/BustosDeker/Celulas-Cervicales.git
   cd Celulas-Cervicales
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la app:
   ```bash
   streamlit run app.py
   ```

## 📁 Estructura del Proyecto

```
SiPakMed-AI/
├── app.py                      # Aplicación Streamlit principal
├── app_config/                 # Configuración de la app
│   ├── __init__.py
│   └── settings.py
├── app_utils/                  # Utilidades
│   ├── __init__.py
│   ├── data_loader.py
│   ├── hybrid_integration.py
│   ├── ml_predictions.py
│   ├── pdf_generator.py
│   └── ui_components.py
├── models/                     # Modelos de ML
│   ├── __init__.py
│   ├── data_loader.py
│   └── hybrid_architectures.py
├── assets/                     # Recursos estáticos
│   ├── css/
│   ├── icons/
│   └── images/
├── data/                       # Datos y modelos entrenados
│   ├── comparison_results/
│   ├── dataset/
│   ├── models/
│   ├── training_results/
│   └── translations/
├── reports/                    # Reportes generados
│   └── pdf/
├── tests/                      # Tests
│   └── test_hybrid_setup.py
├── .streamlit/                 # Configuración de Streamlit
│   └── config.toml
├── .gitignore
├── requirements.txt
└── README.md
```

## 📋 Requisitos

- Python 3.9+
- Streamlit
- TensorFlow/PyTorch (según los modelos)
- OpenCV
- Matplotlib
- ReportLab

## 📝 Notas

- La aplicación está lista para ser desplegada en Streamlit Community Cloud!
- Asegúrate de configurar tu repositorio como **Público** para usar el plan gratuito.
- ¡Disfruta del tema oscuro y las tarjetas modernas! 🎉
