"""
Componentes de UI para la aplicación
"""

import streamlit as st
from PIL import Image
from app_config.settings import MODEL_CONFIG


def load_custom_css():
    """
    Carga CSS personalizado compatible con Modo Claro y Oscuro
    """
    custom_css = """
    <style>
    /* ======= Variables CSS para ambos temas ======= */
    :root {
        --bg-main-light: #ffffff;
        --bg-main-dark: #0f172a;
        --text-main-light: #0f172a;
        --text-main-dark: #e2e8f0;
        
        --bg-sidebar-light: #f1f5f9;
        --bg-sidebar-dark: #1e293b;
        
        --text-heading-light: #1e293b;
        --text-heading-dark: #f1f5f9;
        
        --bg-metric-light: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        --bg-metric-dark: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        --border-metric-light: #cbd5e1;
        --border-metric-dark: #475569;
        
        --text-metric-label-light: #64748b;
        --text-metric-label-dark: #94a3b8;
        --text-metric-value-light: #1e293b;
        --text-metric-value-dark: #f8fafc;
        
        --bg-success-light: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        --bg-success-dark: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        --border-success-light: #10b981;
        --border-success-dark: #059669;
        --text-success-light: #065f46;
        --text-success-dark: #a7f3d0;
        
        --bg-warning-light: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        --bg-warning-dark: linear-gradient(135deg, #78350f 0%, #92400e 100%);
        --border-warning-light: #f59e0b;
        --border-warning-dark: #d97706;
        --text-warning-light: #78350f;
        --text-warning-dark: #fde68a;
        
        --bg-select-light: #f8fafc;
        --bg-select-dark: #334155;
        --border-select-light: #cbd5e1;
        --border-select-dark: #475569;
        --text-select-light: #1e293b;
        --text-select-dark: #f1f5f9;
        
        --bg-card-light: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        --bg-card-dark: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        --border-card-light: #cbd5e1;
        --border-card-dark: #334155;
        --text-card-model-light: #1e293b;
        --text-card-model-dark: #f8fafc;
        --text-card-class-light: #475569;
        --text-card-class-dark: #cbd5e1;
        
        --bg-uploader-light: #f8fafc;
        --bg-uploader-dark: #1e293b;
        --border-uploader-light: #cbd5e1;
        --border-uploader-dark: #475569;
        
        --bg-tabs-light: #f8fafc;
        --bg-tabs-dark: #1e293b;
        --text-tab-light: #64748b;
        --text-tab-dark: #94a3b8;
        
        --hr-color-light: #e2e8f0;
        --hr-color-dark: #334155;
    }
    
    /* ======= Estilos para Modo Claro (predeterminado) ======= */
    .main {
        background-color: var(--bg-main-light);
        color: var(--text-main-light);
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar-light);
        border-right: none;
        padding: 2rem 1.25rem;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-heading-light);
        font-weight: 700;
    }
    
    .stMetric {
        background: var(--bg-metric-light);
        border: 1px solid var(--border-metric-light);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .stMetric label {
        color: var(--text-metric-label-light) !important;
        font-weight: 600;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-metric-value-light) !important;
        font-size: 1.75rem !important;
        font-weight: 700;
    }
    
    .stSuccess {
        background: var(--bg-success-light);
        border: 1px solid var(--border-success-light);
        border-radius: 12px;
        color: var(--text-success-light);
    }
    
    .stWarning {
        background: var(--bg-warning-light);
        border: 1px solid var(--border-warning-light);
        border-radius: 12px;
        color: var(--text-warning-light);
    }
    
    .stSelectbox label,
    .stCheckbox label,
    .stTextInput label {
        color: var(--text-main-light) !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: var(--bg-select-light) !important;
        border-color: var(--border-select-light) !important;
        color: var(--text-select-light) !important;
    }
    
    .stCheckbox input:checked + div {
        background-color: #3b82f6 !important;
    }
    
    .result-card {
        background: var(--bg-card-light);
        border-radius: 20px;
        padding: 1.75rem 1.5rem;
        border: 2px solid var(--border-card-light);
        box-shadow: 0 12px 40px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
    }
    
    .card-model-name {
        color: var(--text-card-model-light);
        font-size: 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1.25rem;
    }
    
    .card-class-name {
        color: var(--text-card-class-light);
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 1.25rem;
    }
    
    [data-testid="stFileUploader"] {
        background-color: var(--bg-uploader-light);
        border: 2px dashed var(--border-uploader-light);
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--bg-tabs-light);
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--text-tab-light);
        border-radius: 8px;
        padding: 0.75rem 1.25rem;
        font-weight: 600;
    }
    
    hr {
        border-color: var(--hr-color-light);
    }
    
    /* ======= Estilos para Modo Oscuro (prefiere-color-scheme) ======= */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: var(--bg-main-dark);
            color: var(--text-main-dark);
        }
        
        [data-testid="stSidebar"] {
            background-color: var(--bg-sidebar-dark);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-heading-dark);
        }
        
        .stMetric {
            background: var(--bg-metric-dark);
            border: 1px solid var(--border-metric-dark);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        
        .stMetric label {
            color: var(--text-metric-label-dark) !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            color: var(--text-metric-value-dark) !important;
        }
        
        .stSuccess {
            background: var(--bg-success-dark);
            border: 1px solid var(--border-success-dark);
            color: var(--text-success-dark);
        }
        
        .stWarning {
            background: var(--bg-warning-dark);
            border: 1px solid var(--border-warning-dark);
            color: var(--text-warning-dark);
        }
        
        .stSelectbox label,
        .stCheckbox label,
        .stTextInput label {
            color: var(--text-main-dark) !important;
        }
        
        .stSelectbox div[data-baseweb="select"] {
            background-color: var(--bg-select-dark) !important;
            border-color: var(--border-select-dark) !important;
            color: var(--text-select-dark) !important;
        }
        
        .result-card {
            background: var(--bg-card-dark);
            border: 2px solid var(--border-card-dark);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }
        
        .card-model-name {
            color: var(--text-card-model-dark);
        }
        
        .card-class-name {
            color: var(--text-card-class-dark);
        }
        
        [data-testid="stFileUploader"] {
            background-color: var(--bg-uploader-dark);
            border: 2px dashed var(--border-uploader-dark);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--bg-tabs-dark);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-tab-dark);
        }
        
        hr {
            border-color: var(--hr-color-dark);
        }
    }
    
    /* ======= Estilos comunes para ambos temas ======= */
    .card-confidence-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
        line-height: 1;
    }
    
    .card-risk-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 700;
        border: 2px solid;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #6366f1;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        box-shadow: 0 8px 24px rgba(59,130,246,0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(59,130,246,0.4);
    }
    
    .result-card:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: #6366f1;
        box-shadow: 0 20px 60px rgba(99,102,241,0.25);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def display_header(title=None, subtitle=None, t=None):
    """
    Muestra el encabezado principal compatible con ambos temas
    """
    st.markdown("""
    <style>
    .header-container {
        text-align: center;
        padding: 2rem;
        margin-bottom: 2rem;
        border-radius: 24px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border: 2px solid #cbd5e1;
    }
    .header-title {
        margin: 0 0 0.5rem 0;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header-subtitle {
        margin: 0;
        color: #64748b;
        font-size: 1.25rem;
    }
    @media (prefers-color-scheme: dark) {
        .header-container {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 2px solid #475569;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }
        .header-subtitle {
            color: #94a3b8;
        }
    }
    </style>
    <div class="header-container">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🔬</div>
        <h1 class="header-title">Clasificador de Células Cervicales</h1>
        <p class="header-subtitle">Sistema de análisis automatizado con IA</p>
    </div>
    """, unsafe_allow_html=True)


def display_metrics_row(metrics_data, t=None):
    """
    Muestra la fila de métricas
    """
    cols = st.columns(len(metrics_data))
    for i, (label, value, help_text) in enumerate(metrics_data):
        with cols[i]:
            st.metric(label=label, value=value, help=help_text)


def display_system_ready_message(t=None):
    """
    Muestra el mensaje de sistema listo
    """
    st.success(
        f"✅ {t('system_ready') if t else 'Sistema Listo'}! "
        f"{t('ai_system') if t else 'Sistema de Inteligencia Artificial'} preparado para analizar imágenes."
    )


def display_waiting_message(t=None):
    """
    Muestra el mensaje de espera
    """
    st.info(
        f"📷 {t('upload_instruction') if t else 'Por favor, sube una imagen de células cervicales para comenzar el análisis.'}"
    )


def display_image_info(image_info, t=None):
    """
    Muestra información de la imagen cargada
    """
    st.markdown("### Información de la Imagen")
    if isinstance(image_info, dict):
        if 'filename' in image_info:
            st.write(f"**Archivo:** {image_info['filename']}")
        if 'size' in image_info:
            st.write(f"**Dimensiones:** {image_info['size']}")
        if 'format' in image_info:
            st.write(f"**Formato:** {image_info['format']}")
        if 'mode' in image_info:
            st.write(f"**Modo:** {image_info['mode']}")


def display_model_results_cards(predictions, clinical_info=None, t=None):
    """
    Muestra tarjetas con resultados por modelo - Estilo compatible con ambos temas
    """
    if not predictions:
        return
    
    # Header with nice styling
    st.markdown("""
    <style>
    .results-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 2px solid #cbd5e1;
    }
    .results-header h2 {
        margin: 0;
        color: #1e293b;
    }
    @media (prefers-color-scheme: dark) {
        .results-header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 2px solid #475569;
        }
        .results-header h2 {
            color: #f1f5f9;
        }
    }
    </style>
    <div class="results-header">
        <h2>📊 Resultados del Análisis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Model color gradients (matching the image's style)
    model_colors = [
        ("#22c55e", "#16a34a"),    # Green
        ("#6366f1", "#4f46e5"),    # Indigo
        ("#10b981", "#059669"),    # Emerald
        ("#8b5cf6", "#7c3aed"),    # Violet
        ("#34d399", "#10b981")     # Green 2
    ]
    
    # Use responsive columns
    num_models = len(predictions)
    if num_models <= 4:
        cols = st.columns(num_models)
    else:
        cols = st.columns(5)
    
    for i, (model_name, pred) in enumerate(predictions.items()):
        class_name = pred.get('class_friendly', pred.get('predicted_class', 'N/A'))
        confidence = pred.get('confidence', 0)
        
        # Get color gradient for this model
        color1, color2 = model_colors[i % len(model_colors)]
        
        # Get clinical risk info
        risk_text = "Normal"
        risk_color = "#22c55e"
        risk_border = "#22c55e"
        if clinical_info:
            class_key = pred.get("class_name")
            if class_key in clinical_info:
                risk = clinical_info[class_key].get('riesgo', 'Normal').lower()
                risk_text = clinical_info[class_key].get('riesgo', 'Normal')
                if 'alto' in risk:
                    risk_color = "#ef4444"
                    risk_border = "#dc2626"
                elif 'bajo' in risk or 'medio' in risk:
                    risk_color = "#eab308"
                    risk_border = "#ca8a04"
        
        with cols[i % len(cols)]:
            # Build the card HTML without comments to avoid issues
            card_html = f'<div class="result-card">'
            card_html += f'<div style="background: linear-gradient(135deg, {color1} 0%, {color2} 100%); margin: -1.75rem -1.5rem 1.5rem -1.5rem; padding: 1rem; border-radius: 18px 18px 0 0;">'
            card_html += f'<div class="card-model-name">{model_name}</div>'
            card_html += '</div>'
            card_html += f'<div class="card-confidence-value" style="color: {color1};">{confidence:.1f}%</div>'
            card_html += f'<div class="card-class-name">{class_name}</div>'
            card_html += f'<div class="card-risk-badge" style="background-color: {risk_color}20; border: 2px solid {risk_border}; color: {risk_color}; display: inline-block; padding: 0.5rem 1.25rem; border-radius: 9999px; font-weight: 700;">● {risk_text}</div>'
            card_html += '</div>'
            st.markdown(card_html, unsafe_allow_html=True)


def display_error_message(t=None, message=None):
    """
    Muestra un mensaje de error
    """
    if message:
        st.error(f"❌ {message}")
    else:
        st.error(f"❌ {t('model_error') if t else 'Error al cargar los modelos'}")


def display_footer(t=None):
    """
    Muestra el pie de página
    """
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>SiPakMed-AI - Sistema de Análisis de Células Cervicales</p>
        </div>
        """,
        unsafe_allow_html=True
    )
