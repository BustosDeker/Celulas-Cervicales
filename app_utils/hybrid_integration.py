"""
Integración de modelos híbridos
"""

import logging

logger = logging.getLogger(__name__)


def get_hybrid_predictions(image, hybrid_models=None):
    """
    Obtiene predicciones de modelos híbridos
    """
    try:
        predictions = {}
        return predictions
    except Exception as e:
        logger.error(f"Error en get_hybrid_predictions: {e}")
        return {}


def is_hybrid_available():
    """
    Verifica si los modelos híbridos están disponibles
    """
    return False  # Por ahora, no hay modelos híbridos reales


def get_hybrid_model_info():
    """
    Obtiene información de modelos híbridos disponibles
    """
    try:
        from app_config.settings import MODEL_CONFIG
        hybrid_models = {
            k: v for k, v in MODEL_CONFIG["models"].items() if v["type"] == "pytorch"
        }
        return hybrid_models
    except Exception as e:
        logger.error(f"Error en get_hybrid_model_info: {e}")
        return {}


def display_hybrid_info_in_sidebar(t=None):
    """
    Muestra información de modelos híbridos en la barra lateral
    """
    import streamlit as st
    st.sidebar.markdown("### 🧠 Modelos Híbridos")
    st.sidebar.info("Modelos híbridos combinan CNN clásicas con arquitecturas avanzadas para mayor precisión.")
