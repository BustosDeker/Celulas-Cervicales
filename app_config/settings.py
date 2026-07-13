"""
Configuración de la aplicación SiPakMed-AI
"""

import os
from pathlib import Path
import streamlit as st

# Rutas base
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
TRANSLATIONS_DIR = DATA_DIR / "translations"
TRAINING_RESULTS_DIR = DATA_DIR / "training_results"
COMPARISON_RESULTS_DIR = DATA_DIR / "comparison_results"
ASSETS_DIR = BASE_DIR / "assets"

# Configuración de UI
UI_CONFIG = {
    "page_title": "SiPakMed-AI - Clasificador de Células Cervicales",
    "page_icon": "🔬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "supported_formats": ["png", "jpg", "jpeg", "PNG", "JPG", "JPEG"]
}

# Configuración de modelos
MODEL_CONFIG = {
    "class_names": ["dyskeratotic", "koilocytotic", "metaplastic", "parabasal", "superficial_intermediate"],
    "image_size": (224, 224),
    "models": {
        "MobileNetV2": {
            "file": "mobilenetv2.h5",
            "type": "keras",
            "accuracy": 92.5
        },
        "ResNet50": {
            "file": "resnet50.h5",
            "type": "keras",
            "accuracy": 93.1
        },
        "EfficientNetB0": {
            "file": "efficientnetb0.h5",
            "type": "keras",
            "accuracy": 94.2
        },
        "HybridEnsembleCNN": {
            "file": "hybrid_ensemble.pth",
            "type": "pytorch",
            "accuracy": 95.8
        },
        "HybridMultiScaleCNN": {
            "file": "hybrid_multiscale.pth",
            "type": "pytorch",
            "accuracy": 96.3
        }
    }
}


def initialize_app():
    """
    Inicializa la configuración de la aplicación Streamlit
    """
    # Configurar la página
    st.set_page_config(
        page_title=UI_CONFIG["page_title"],
        page_icon=UI_CONFIG["page_icon"],
        layout=UI_CONFIG["layout"],
        initial_sidebar_state=UI_CONFIG["initial_sidebar_state"]
    )
    
    # Inicializar estado de sesión
    if "language" not in st.session_state:
        st.session_state.language = "es"
    
    if "models_loaded" not in st.session_state:
        st.session_state.models_loaded = False
    
    if "current_image" not in st.session_state:
        st.session_state.current_image = None
    
    if "predictions" not in st.session_state:
        st.session_state.predictions = None
    
    # Crear directorios necesarios
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(TRANSLATIONS_DIR, exist_ok=True)
    os.makedirs(TRAINING_RESULTS_DIR, exist_ok=True)
    os.makedirs(COMPARISON_RESULTS_DIR, exist_ok=True)
