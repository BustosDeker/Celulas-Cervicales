"""
Aplicación Streamlit para ENTRENAMIENTO de modelos SiPakMed-AI
"""
import streamlit as st
import logging
import os
from datetime import datetime

# Importar módulos
from app_config.settings import initialize_app
from app_utils.data_loader import (
    load_translations, get_language, set_language,
    load_hybrid_training_results,
    load_hybrid_comparison_results, load_training_metrics
)
from app_utils.ui_components import load_custom_css, display_header
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar la aplicación
initialize_app()
load_custom_css()

def get_translation_function():
    """Obtiene la función de traducción para el idioma actual"""
    try:
        logger.info("Iniciando carga de función de traducción...")
        current_language = get_language()
        logger.info(f"Idioma seleccionado: {current_language}")
        translations = load_translations(current_language)
        logger.info(f"Traducciones cargadas: {len(translations) if translations else 0} claves")
        
        def t(key: str) -> str:
            try:
                if translations and isinstance(translations, dict) and key in translations:
                    return str(translations.get(key, key))
                else:
                    defaults = {
                        "models": "Modelos",
                        "training_results": "Resultados de Entrenamiento",
                        "general_comparison": "Comparación General",
                        "confusion_matrices": "Matrices de Confusión",
                        "training_histories": "Historiales de Entrenamiento",
                        "hybrid_comparison_analysis": "Análisis de Comparación Híbrida"
                    }
                    return defaults.get(key, key)
            except Exception as e:
                logger.error(f"Error en función t() con clave '{key}': {e}")
                return key
        return t
    except Exception as e:
        logger.error(f"Error crítico creando función de traducción: {e}")
        def emergency_t(key: str) -> str:
            return key
        return emergency_t

t = get_translation_function()

# Mostrar cabecera
display_header(t)

# Sidebar
st.sidebar.title("SiPakMed-AI - Entrenamiento")
st.sidebar.markdown("### Configuración")

# Selector de idioma en sidebar
available_languages = {"es": "Español", "en": "English"}
current_lang = get_language()
selected_lang = st.sidebar.selectbox(
    "Idioma / Language",
    options=list(available_languages.keys()),
    format_func=lambda x: available_languages[x],
    index=list(available_languages.keys()).index(current_lang) if current_lang in available_languages else 0
)
if selected_lang != current_lang:
    set_language(selected_lang)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Esta aplicación se usa exclusivamente para ver y gestionar el entrenamiento de modelos.")

# Contenido principal
st.title(f"🔬 {t('training_results')}")

# Cargar datos
training_metrics = load_training_metrics()
hybrid_results = load_hybrid_training_results()
comparison_results = load_hybrid_comparison_results()

if training_metrics or hybrid_results or comparison_results:
    # Tabs para diferentes secciones
    tab_labels = []
    tab_labels.append(t('general_comparison'))
    tab_labels.append(t('confusion_matrices'))
    tab_labels.append(t('training_histories'))
    tab_labels.append("🧠 Resultados Híbridos")
    if hybrid_results:
        tab_labels.append("📊 Métricas Híbridas")
    if comparison_results:
        tab_labels.append("🔬 Comparación Híbrida")
    
    tabs = st.tabs(tab_labels)
    tab_index = 0
    
    # 1. Comparación general (gráfico interactivo)
    with tabs[tab_index]:
        st.markdown("#### 📊 Comparación General de Modelos")
        comp = training_metrics["comparison"]
        
        # Crear subplots para los tres gráficos
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=("Precisión por Modelo (%)", "Pérdida de Validación", "Tiempo de Entrenamiento (seg)"),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )
        
        # Color por tipo de modelo
        colors = ["#FF6B6B" if typ == "clásico" or typ == "clasico" else "#4ECDC4" for typ in comp["types"]]
        
        # Gráfico 1: Precisión
        fig.add_trace(
            go.Bar(x=comp["modelos"], y=comp["accuracy"], marker_color=colors, name="Precisión", 
                   text=[f"{v:.1f}%" for v in comp["accuracy"]], textposition="auto"),
            row=1, col=1
        )
        fig.update_yaxes(range=[70, 100], row=1, col=1)
        
        # Gráfico 2: Val Loss
        fig.add_trace(
            go.Bar(x=comp["modelos"], y=comp["val_loss"], marker_color=colors, name="Val Loss",
                   text=[f"{v:.3f}" for v in comp["val_loss"]], textposition="auto"),
            row=1, col=2
        )
        fig.update_yaxes(range=[1.0, 1.8], row=1, col=2)
        
        # Gráfico 3: Tiempo de entrenamiento
        fig.add_trace(
            go.Bar(x=comp["modelos"], y=comp["train_time"], marker_color=colors, name="Tiempo",
                   text=[f"{v}" for v in comp["train_time"]], textposition="auto"),
            row=1, col=3
        )
        
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico adicional de MCC
        st.markdown("##### Comparación de MCC Scores")
        fig_mcc = go.Figure()
        fig_mcc.add_trace(
            go.Bar(x=comp["modelos"], y=comp["mcc"], marker_color=colors,
                   text=[f"{v:.3f}" for v in comp["mcc"]], textposition="auto")
        )
        fig_mcc.update_layout(title="MCC por Modelo", height=400)
        fig_mcc.update_yaxes(range=[0.7, 1.0])
        st.plotly_chart(fig_mcc, use_container_width=True)
    tab_index +=1
    
    # 2. Matrices de confusión
    with tabs[tab_index]:
        st.markdown("#### 📈 Matrices de Confusión")
        if "confusion_matrices" in training_metrics:
            cm_data = training_metrics["confusion_matrices"]
            class_names_short = ["Dysk", "Koil", "Metap", "Parab", "Sup-Interm"]
            
            # Mostrar matrices en columnas
            cols = st.columns(2)
            for idx, (model_name, cm) in enumerate(cm_data.items()):
                with cols[idx % 2]:
                    st.markdown(f"**{model_name}**")
                    fig_cm = go.Figure(data=go.Heatmap(
                        z=cm,
                        x=class_names_short,
                        y=class_names_short,
                        colorscale="Blues",
                        text=cm,
                        texttemplate="%{text}",
                        textfont={"size":12}
                    ))
                    fig_cm.update_layout(height=400)
                    st.plotly_chart(fig_cm, use_container_width=True)
    tab_index +=1
    
    # 3. Historiales de entrenamiento
    with tabs[tab_index]:
        st.markdown("#### 📉 Historiales de Entrenamiento")
        if "training_history" in training_metrics:
            th_data = training_metrics["training_history"]
            for model_name, history in th_data.items():
                st.markdown(f"**{model_name}**")
                fig_th = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("Pérdida", "Precisión")
                )
                fig_th.add_trace(
                    go.Scatter(x=history["epochs"], y=history["train_loss"], name="Train Loss", line=dict(color="#FF6B6B")),
                    row=1, col=1
                )
                fig_th.add_trace(
                    go.Scatter(x=history["epochs"], y=history["val_loss"], name="Val Loss", line=dict(color="#4ECDC4", dash="dash")),
                    row=1, col=1
                )
                fig_th.add_trace(
                    go.Scatter(x=history["epochs"], y=history["train_acc"], name="Train Acc", line=dict(color="#FF6B6B")),
                    row=1, col=2
                )
                fig_th.add_trace(
                    go.Scatter(x=history["epochs"], y=history["val_acc"], name="Val Acc", line=dict(color="#4ECDC4", dash="dash")),
                    row=1, col=2
                )
                fig_th.update_layout(height=400)
                fig_th.update_yaxes(range=[0, 100], row=1, col=2)
                st.plotly_chart(fig_th, use_container_width=True)
    tab_index +=1
    
    # 4. Resultados Híbridos
    with tabs[tab_index]:
        st.markdown("#### 🧠 Resultados de Modelos Híbridos")
        if hybrid_results:
            if "modelos_hibridos" in hybrid_results:
                for model_name, model_data in hybrid_results["modelos_hibridos"].items():
                    with st.expander(f"🤖 {model_name}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Precisión", f"{model_data.get('accuracy', 0):.1f}%")
                            st.metric("Épocas Entrenadas", model_data.get("epocas_entrenadas", 0))
                        with col2:
                            st.metric("Precisión Global", f"{model_data.get('precision_global', 0):.2f}")
                            st.metric("Tiempo Estimado", f"{model_data.get('tiempo_estimado_horas', 0)}h")
                        
                        if "arquitectura" in model_data:
                            arch = model_data["arquitectura"]
                            st.write(f"**Tipo**: {arch.get('tipo', 'N/A')}")
                            st.write(f"**Atención**: {arch.get('atencion', 'N/A')}")
                            st.write(f"**Fusión**: {arch.get('fusion', 'N/A')}")
    tab_index +=1
    
    # 5. Métricas Híbridas (si aplica)
    if tab_index < len(tabs) and hybrid_results:
        with tabs[tab_index]:
            st.markdown("#### 📊 Métricas Adicionales Híbridas")
            if "dataset" in hybrid_results:
                ds = hybrid_results["dataset"]
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Imágenes", ds.get("total_imagenes", 0))
                col2.metric("Clases", ds.get("clases", 0))
                col3.metric("Formatos", ", ".join(ds.get("tipos_archivo", [])))
    tab_index +=1
    
    # 6. Comparación Híbrida (si aplica)
    if tab_index < len(tabs) and comparison_results:
        with tabs[tab_index]:
            st.markdown(f"#### {t('hybrid_comparison_analysis')}")
            
            # Resumen general
            resumen = comparison_results.get("resumen_general", {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Modelos", 
                    resumen.get("total_modelos", 0),
                    help="Modelos analizados en total"
                )
            
            with col2:
                mejora_abs = resumen.get('mejora_absoluta', 0)
                mejora_rel = resumen.get('mejora_relativa', 0)
                st.metric(
                    "Mejora Híbridos", 
                    f"{mejora_abs:+.1f}%",
                    delta=f"{mejora_rel:+.1f}% relativa"
                )
            
            with col3:
                precision_hibridos = resumen.get("precision_media_hibridos", 0)
                objetivo_alcanzado = "Sí" if resumen.get("objetivo_90_alcanzado", False) else "No"
                st.metric(
                    "Precisión Híbridos", 
                    f"{precision_hibridos:.1f}%",
                    delta=f"Objetivo 90%: {objetivo_alcanzado}"
                )
            
            with col4:
                precision_clasicos = resumen.get("precision_media_clasicos", 0)
                st.metric(
                    "Precisión Clásicos", 
                    f"{precision_clasicos:.1f}%"
                )
            
            # Gráficos interactivos
            st.markdown("##### 📊 Visualizaciones Comparativas")
            if "modelos_detallados" in comparison_results:
                modelos_detallados = comparison_results["modelos_detallados"]
                model_names = list(modelos_detallados.keys())
                accuracies = [modelos_detallados[name].get("accuracy", 0) for name in model_names]
                mcc_scores = [modelos_detallados[name].get("mcc", 0) for name in model_names]
                model_types = [modelos_detallados[name].get("type", "unknown") for name in model_names]
                
                # Colores por tipo de modelo
                colors = ['#3498db' if t == 'clásico' or t == 'clasico' else '#e74c3c' for t in model_types]
                
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(
                    x=model_names, y=accuracies, marker_color=colors,
                    text=[f'{acc:.1f}%' for acc in accuracies], textposition='auto',
                    name='Precisión'
                ))
                fig1.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="Objetivo 90%")
                fig1.update_layout(title="Comparación de Precisiones", height=400)
                st.plotly_chart(fig1, use_container_width=True)
                
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=model_names, y=mcc_scores, marker_color=colors,
                    text=[f'{mcc:.3f}' for mcc in mcc_scores], textposition='auto',
                    name='MCC'
                ))
                fig2.update_layout(title="Comparación de MCC Scores", height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Información adicional
            st.markdown("##### ℹ️ Información del Análisis")
            fecha_generacion = comparison_results.get("fecha_generacion", "No disponible")
            st.info(f"**Fecha de generación**: {fecha_generacion}")
            
            # Conclusiones
            st.markdown("##### 📝 Conclusiones")
            objetivo_alcanzado = resumen.get("objetivo_90_alcanzado", False)
            if objetivo_alcanzado:
                st.success("✅ **Objetivo alcanzado**: Los modelos híbridos superaron el 90% de precisión establecido como meta.")
            else:
                st.warning("⚠️ **Objetivo parcial**: Algunos modelos híbridos están cerca del 90% de precisión.")

else:
    st.info("No hay datos de entrenamiento disponibles.")

# Footer
st.markdown("---")
st.markdown("SiPakMed-AI - Sistema de Análisis de Células Cervicales")
