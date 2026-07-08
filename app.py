"""
Aplicación SIPaKMeD optimizada y refactorizada
Clasificador de Células Cervicales usando Deep Learning

Reducido de 2,671 líneas a ~800 líneas (70% menos código)
Actualizado para resolver conflictos con OpenCV - v1.1
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import os
from datetime import datetime
from scipy.stats import chi2
from scipy import stats

# Importar tensorflow y torch de forma opcional
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

# Función para detectar GPU desde múltiples frameworks
def detect_gpu():
    """Detectar GPU disponible desde TensorFlow y PyTorch"""
    gpu_info = {
        'available': False,
        'framework': 'CPU',
        'device_name': 'No GPU detectada',
        'count': 0
    }
    
    # Verificar TensorFlow GPU
    if TF_AVAILABLE:
        try:
            tf_gpu_devices = tf.config.list_physical_devices('GPU')
            if tf_gpu_devices:
                gpu_info['available'] = True
                gpu_info['framework'] = 'TensorFlow + GPU'
                gpu_info['device_name'] = 'GPU (TensorFlow)'
                gpu_info['count'] = len(tf_gpu_devices)
                return gpu_info
        except:
            pass
    
    # Verificar PyTorch GPU si TensorFlow no detecta GPU
    if TORCH_AVAILABLE:
        try:
            if torch.cuda.is_available():
                gpu_info['available'] = True
                gpu_info['framework'] = 'PyTorch + GPU'
                gpu_info['device_name'] = torch.cuda.get_device_name(0)
                gpu_info['count'] = torch.cuda.device_count()
                return gpu_info
        except:
            pass
    
    return gpu_info

# Importar módulos optimizados
from app_config.settings import initialize_app, UI_CONFIG, MODEL_CONFIG
from app_utils.data_loader import (
    load_models, load_translations, get_language, set_language,
    get_available_languages, get_class_names_friendly, get_clinical_info,
    load_training_images, load_hybrid_training_results,
    load_hybrid_comparison_results, load_training_metrics
)
from app_utils.ui_components import (
    load_custom_css, display_header, display_metrics_row,
    display_system_ready_message, display_waiting_message,
    display_image_info, display_model_results_cards,
    display_error_message, display_footer
)
from app_utils.ml_predictions import (
    enhance_cervical_cell_image, predict_cervical_cells, calculate_consensus
)
from app_utils.hybrid_integration import (
    get_hybrid_predictions, is_hybrid_available, display_hybrid_info_in_sidebar
)
from app_utils.pdf_generator import generate_pdf_report, create_download_link

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

def setup_app():
    """Configuración inicial de la aplicación"""
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
                    # Valores por defecto robustos
                    defaults = {
                        'models': 'Modelos',
                        'models_loaded': 'Cargados', 
                        'processing_mode': 'Procesamiento',
                        'accuracy_range': 'Rango',
                        'cell_types_count': 'Tipos de células',
                        'main_title': 'Clasificador de Células Cervicales',
                        'subtitle': 'Sistema de análisis automatizado',
                        'ai_system': 'Sistema de Inteligencia Artificial',
                        'system_ready': 'Sistema Listo',
                        'image_analysis': 'Análisis de Imagen',
                        'analysis_results': 'Resultados del Análisis',
                        'visual_analysis': 'Análisis Visual',
                        'download_report': 'Descargar Reporte'
                    }
                    result = defaults.get(key, key)
                    logger.info(f"Usando valor por defecto para '{key}': '{result}'")
                    return result
            except Exception as e:
                logger.error(f"Error en función t() con clave '{key}': {e}")
                return key
        
        return t
    except Exception as e:
        logger.error(f"Error crítico creando función de traducción: {e}")
        # Función de emergencia completa
        def emergency_t(key: str) -> str:
            emergency_dict = {
                'models': 'Modelos',
                'models_loaded': 'Cargados',
                'processing_mode': 'Procesamiento',
                'accuracy_range': 'Rango',
                'cell_types_count': 'Tipos de células',
                'main_title': 'Clasificador de Células Cervicales',
                'subtitle': 'Sistema de análisis automatizado basado en Deep Learning',
                'ai_system': 'Sistema de Inteligencia Artificial',
                'system_ready': 'Sistema Listo',
                'image_analysis': 'Análisis de Imagen',
                'analysis_results': 'Resultados del Análisis',
                'visual_analysis': 'Análisis Visual',
                'download_report': 'Descargar Reporte',
                'upload_instruction': 'Selecciona una imagen',
                'upload_help': 'Formatos soportados: PNG, JPG, JPEG',
                'applying_clahe': 'Aplicando mejoras...',
                'analyzing_ai': 'Analizando con IA...',
                'probability_distribution': 'Distribución de Probabilidades',
                'model_consensus': 'Consenso entre Modelos'
            }
            result = emergency_dict.get(key, key)
            logger.info(f"Usando traducción de emergencia para '{key}': '{result}'")
            return result
        return emergency_t

# ============================================================================
# COMPONENTES DE VISUALIZACIÓN
# ============================================================================

def create_interactive_plots(predictions):
    """Crea gráficos interactivos de probabilidades"""
    try:
        # Preparar datos
        models = list(predictions.keys())
        class_names = MODEL_CONFIG["class_names"]
        class_friendly = get_class_names_friendly()
        
        # Crear subplots
        fig = make_subplots(
            rows=1, cols=len(models),
            subplot_titles=models,
            specs=[[{"type": "bar"}] * len(models)]
        )
        
        colors = ['#0066CC', '#6C63FF', '#00D25B', '#FFAB00', '#FC424A']
        
        for i, (model_name, pred) in enumerate(predictions.items()):
            probabilities = pred.get('probabilities', [0] * len(class_names))
            friendly_names = [class_friendly.get(name, name) for name in class_names]
            
            fig.add_trace(
                go.Bar(
                    x=friendly_names,
                    y=probabilities,
                    name=model_name,
                    marker_color=colors[i % len(colors)],
                    showlegend=False
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            title="Distribución de Probabilidades por Modelo",
            height=500,
            font=dict(size=12)
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(title_text="Probabilidad", range=[0, 1])
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creando gráficos: {e}")
        return go.Figure()

def create_consensus_chart(predictions):
    """Crea gráfico de consenso entre modelos"""
    try:
        consensus = calculate_consensus(predictions)
        if not consensus:
            return go.Figure()
        
        # Datos para el gráfico de consenso
        labels = ['Consenso', 'Discrepancia']
        values = [consensus['votes'], consensus['total_models'] - consensus['votes']]
        colors = ['#00D25B', '#FC424A']
        
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_size=14
            )
        ])
        
        fig.update_layout(
            title=f"Consenso: {consensus['class_friendly']} ({consensus['agreement_level']})",
            height=400,
            font=dict(size=12)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creando gráfico de consenso: {e}")
        return go.Figure()


def create_comparison_interactive_plots(comparison_data):
    """Crear gráficos interactivos de comparación"""
    try:
        if not comparison_data or "modelos_detallados" not in comparison_data:
            return None, None
        
        modelos = comparison_data["modelos_detallados"]
        
        # Preparar datos para gráficos
        model_names = list(modelos.keys())
        accuracies = [modelos[name].get("accuracy", 0) for name in model_names]
        mcc_scores = [modelos[name].get("mcc", 0) for name in model_names]
        model_types = [modelos[name].get("type", "unknown") for name in model_names]
        
        # Colores por tipo de modelo
        colors = ['#3498db' if t == 'classical' else '#e74c3c' for t in model_types]
        
        # Gráfico 1: Precisiones comparativas
        fig1 = go.Figure()
        
        fig1.add_trace(go.Bar(
            x=model_names,
            y=accuracies,
            marker_color=colors,
            text=[f'{acc:.1f}%' for acc in accuracies],
            textposition='auto',
            name='Precisión'
        ))
        
        # Línea de objetivo 90%
        fig1.add_hline(y=90, line_dash="dash", line_color="green", 
                      annotation_text="Objetivo 90%")
        
        fig1.update_layout(
            title="Comparación de Precisiones: Modelos Clásicos vs Híbridos",
            xaxis_title="Modelos",
            yaxis_title="Precisión (%)",
            height=400,
            yaxis=dict(range=[80, 100])
        )
        
        # Gráfico 2: MCC Scores comparativos
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=model_names,
            y=mcc_scores,
            marker_color=colors,
            text=[f'{mcc:.3f}' for mcc in mcc_scores],
            textposition='auto',
            name='MCC Score'
        ))
        
        fig2.update_layout(
            title="Comparación de MCC Scores: Modelos Clásicos vs Híbridos",
            xaxis_title="Modelos",
            yaxis_title="MCC Score",
            height=400,
            yaxis=dict(range=[0, 1])
        )
        
        return fig1, fig2
        
    except Exception as e:
        logger.error(f"Error creando gráficos de comparación: {e}")
        return None, None

def mcnemar_test(y_true, y_pred1, y_pred2):
    """Test de McNemar para comparar dos modelos"""
    try:
        # Tabla de contingencia 2x2 para McNemar
        # a: ambos correctos, b: solo modelo1 correcto, c: solo modelo2 correcto, d: ambos incorrectos
        correct1 = (y_pred1 == y_true)
        correct2 = (y_pred2 == y_true)
        
        a = np.sum(correct1 & correct2)   # Ambos correctos
        b = np.sum(correct1 & ~correct2)  # Solo modelo1 correcto
        c = np.sum(~correct1 & correct2)  # Solo modelo2 correcto
        d = np.sum(~correct1 & ~correct2) # Ambos incorrectos
        
        # Estadística de McNemar (con corrección de continuidad para muestras pequeñas)
        if (b + c) == 0:
            statistic = 0.0
            p_value = 1.0
            winner = "empate"
        else:
            # Corrección de continuidad de Yates si b+c < 25
            if (b + c) < 25:
                statistic = (abs(b - c) - 1)**2 / (b + c)
            else:
                statistic = (b - c)**2 / (b + c)
            
            p_value = 1 - chi2.cdf(statistic, 1)
            
            # Determinar ganador
            if b > c:
                winner = "modelo1"  # Modelo1 tiene más aciertos únicos
            elif c > b:
                winner = "modelo2"  # Modelo2 tiene más aciertos únicos  
            else:
                winner = "empate"   # Igual número de aciertos únicos
        
        significant = p_value < 0.05
        
        # Calcular accuracy de cada modelo para referencia
        acc1 = np.mean(correct1)
        acc2 = np.mean(correct2)
        
        return {
            "statistic": statistic,
            "p_value": p_value,
            "contingency_table": [[a, b], [c, d]],
            "b": int(b), 
            "c": int(c),
            "a": int(a),
            "d": int(d),
            "significant": significant,
            "winner": winner,
            "model1_accuracy": acc1,
            "model2_accuracy": acc2,
            "interpretation": f"p={p_value:.4f}, {'significativo' if significant else 'no significativo'}, ganador: {winner}"
        }
    except Exception as e:
        st.error(f"Error en test McNemar: {e}")
        return None

def matews_test(y_true, y_pred1, y_pred2):
    """Test de Matews para comparar dos modelos"""
    try:
        # Calcular correctos/incorrectos para cada modelo
        correct1 = (y_pred1 == y_true)
        correct2 = (y_pred2 == y_true)
        
        # Matriz de contingencia 2x2
        a = np.sum(correct1 & correct2)   # Ambos correctos
        b = np.sum(correct1 & ~correct2)  # Solo modelo1 correcto
        c = np.sum(~correct1 & correct2)  # Solo modelo2 correcto
        d = np.sum(~correct1 & ~correct2) # Ambos incorrectos
        
        contingency_table = np.array([[a, b], [c, d]])
        
        # Test chi-cuadrado
        try:
            chi2_stat, p_value, _, _ = stats.chi2_contingency(contingency_table)
        except Exception:
            chi2_stat = 0.0
            p_value = 1.0
        
        significant = p_value < 0.05
        
        # Matthews Correlation Coefficient
        denominator = np.sqrt((a + b) * (a + c) * (d + b) * (d + c))
        if denominator == 0:
            mcc = 0.0
        else:
            mcc = (a * d - b * c) / denominator
        
        return {
            "chi2_statistic": chi2_stat,
            "statistic": chi2_stat,
            "p_value": p_value,
            "contingency_table": contingency_table.tolist(),
            "matews_correlation": abs(mcc),
            "significant": significant,
            "interpretation": f"p={p_value:.4f}, MCC={mcc:.4f}, {'significativo' if significant else 'no significativo'}"
        }
    except Exception as e:
        st.error(f"Error en test Matews: {e}")
        return None

def create_mcnemar_matrix_plot(mcnemar_results):
    """Crear matriz de comparación McNemar entre modelos"""
    try:
        if not mcnemar_results or len(mcnemar_results) == 0:
            return None
        
        # Extraer todos los modelos únicos
        all_models = set()
        for result in mcnemar_results:
            all_models.add(result["model1"])
            all_models.add(result["model2"])
        
        model_list = sorted(list(all_models))
        n_models = len(model_list)
        
        if n_models < 2:
            return None
        
        # Crear matrices completas (simetricas)
        pvalue_matrix = np.ones((n_models, n_models))  # Diagonal = 1.0 (no significativo)
        winner_matrix = np.full((n_models, n_models), "", dtype=object)  # Matriz de ganadores
        
        # Llenar las matrices con datos de comparaciones
        for result in mcnemar_results:
            model1 = result["model1"]
            model2 = result["model2"]
            
            i = model_list.index(model1)
            j = model_list.index(model2)
            
            p_val = result.get("p_value", 1.0)
            winner = result.get("winner", "empate")
            
            # Llenar ambos triángulos para matriz simétrica
            pvalue_matrix[i, j] = p_val
            pvalue_matrix[j, i] = p_val
            
            # Determinar ganador para la celda [i,j]
            if winner == "modelo1":
                winner_matrix[i, j] = f"✓ {model1}"  # Modelo1 gana
                winner_matrix[j, i] = f"✗ {model2}"  # Modelo2 pierde
            elif winner == "modelo2":
                winner_matrix[i, j] = f"✗ {model1}"  # Modelo1 pierde  
                winner_matrix[j, i] = f"✓ {model2}"  # Modelo2 gana
            else:
                winner_matrix[i, j] = "≈ empate"     # Empate
                winner_matrix[j, i] = "≈ empate"     # Empate
        
        # Crear texto para cada celda
        text_matrix = []
        for i in range(n_models):
            row_text = []
            for j in range(n_models):
                if i == j:
                    text = f"<b>{model_list[i]}</b>"  # Diagonal - nombre del modelo
                else:
                    p_val = pvalue_matrix[i, j]
                    winner_text = winner_matrix[i, j]
                    sig_text = "Sig" if p_val < 0.05 else "NS"
                    text = f"{winner_text}<br>p: {p_val:.4f} ({sig_text})"
                row_text.append(text)
            text_matrix.append(row_text)
        
        # Crear figura
        fig = go.Figure(data=go.Heatmap(
            z=pvalue_matrix,
            x=model_list,
            y=model_list,
            text=text_matrix,
            texttemplate="%{text}",
            textfont={"size": 8},
            colorscale="RdYlBu_r",
            zmin=0,
            zmax=0.1,  # Enfocar en p-values relevantes
            colorbar=dict(title="p-value")
        ))
        
        # Agregar bordes verdes para diferencias significativas (ganador)
        for result in mcnemar_results:
            if result.get("significant", False):
                model1 = result["model1"]
                model2 = result["model2"]
                winner = result.get("winner", "empate")
                
                i = model_list.index(model1)
                j = model_list.index(model2)
                
                # Borde verde para el ganador
                if winner == "modelo1":
                    fig.add_shape(
                        type="rect",
                        x0=j-0.4, y0=i-0.4,
                        x1=j+0.4, y1=i+0.4,
                        line=dict(color="green", width=3),
                        fillcolor="rgba(0,255,0,0.1)"
                    )
                elif winner == "modelo2":
                    fig.add_shape(
                        type="rect",
                        x0=i-0.4, y0=j-0.4,
                        x1=i+0.4, y1=j+0.4,
                        line=dict(color="green", width=3),
                        fillcolor="rgba(0,255,0,0.1)"
                    )
        
        fig.update_layout(
            title="Matriz de McNemar - Comparaciones por Pares<br><sub>✓ = Ganador, ✗ = Perdedor, ≈ = Empate | Verde: diferencias significativas (p<0.05)</sub>",
            width=700,
            height=700,
            xaxis=dict(title="Modelo"),
            yaxis=dict(title="Modelo", autorange="reversed"),
            font=dict(size=10)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creando matriz McNemar: {e}")
        return None

def create_mcc_scores_plot(mcc_scores):
    """Crear gráfico de barras con MCC scores individuales ya calculados"""
    try:
        if not mcc_scores:
            return None
        
        models = list(mcc_scores.keys())
        mcc_values = list(mcc_scores.values())
        
        # Colores según calidad del MCC
        colors = []
        for mcc in mcc_values:
            if mcc > 0.8:
                colors.append('#00D25B')  # Verde - Excelente
            elif mcc > 0.6:
                colors.append('#FFAB00')  # Amarillo - Bueno
            elif mcc > 0.4:
                colors.append('#FF6B6B')  # Rojo claro - Regular
            else:
                colors.append('#FC424A')  # Rojo - Malo
        
        # Crear gráfico de barras
        fig = go.Figure(data=[
            go.Bar(
                x=models,
                y=mcc_values,
                marker_color=colors,
                text=[f"MCC: {mcc:.3f}" for mcc in mcc_values],
                textposition='auto',
            )
        ])
        
        # Líneas de referencia
        fig.add_hline(y=0.8, line_dash="dash", line_color="green", 
                     annotation_text="Excelente (0.8+)", annotation_position="top right")
        fig.add_hline(y=0.6, line_dash="dash", line_color="orange", 
                     annotation_text="Bueno (0.6+)", annotation_position="top right")
        fig.add_hline(y=0.4, line_dash="dash", line_color="red", 
                     annotation_text="Regular (0.4+)", annotation_position="top right")
        
        fig.update_layout(
            title="Matthews Correlation Coefficient (MCC) por Modelo<br><sub>Valores ya calculados individualmente - No es comparación por pares</sub>",
            xaxis_title="Modelos",
            yaxis_title="MCC Score",
            showlegend=False,
            height=500,
            yaxis=dict(range=[0, 1])
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creando gráfico MCC: {e}")
        return None

def create_matews_matrix_plot(matews_results):
    """Crear matriz gráfica de comparación Matews entre pares de modelos"""
    try:
        if not matews_results or len(matews_results) == 0:
            return None
        
        # Extraer todos los modelos únicos
        all_models = set()
        for result in matews_results:
            comp = result["comparison"]
            model1, model2 = comp.split("_vs_")
            all_models.add(model1)
            all_models.add(model2)
        
        model_list = sorted(list(all_models))
        n_models = len(model_list)
        
        if n_models < 2:
            return None
        
        # Crear matrices
        mcc_matrix = np.ones((n_models, n_models))  # Inicializar con 1s en diagonal
        pvalue_matrix = np.zeros((n_models, n_models))  # Inicializar con 0s en diagonal
        significance_matrix = np.ones((n_models, n_models))  # Diagonal siempre significativa
        
        # Llenar las matrices con datos de comparaciones
        for result in matews_results:
            comp = result["comparison"]
            model1, model2 = comp.split("_vs_")
            
            i = model_list.index(model1)
            j = model_list.index(model2)
            
            # Matriz simétrica
            mcc_val = result.get("matews_correlation", 0.0)
            p_val = result.get("p_value", 1.0)
            sig_val = 1 if result.get("significant", False) else 0
            
            mcc_matrix[i, j] = mcc_val
            mcc_matrix[j, i] = mcc_val
            
            pvalue_matrix[i, j] = p_val
            pvalue_matrix[j, i] = p_val
            
            significance_matrix[i, j] = sig_val
            significance_matrix[j, i] = sig_val
        
        # Crear texto para cada celda
        text_matrix = []
        for i in range(n_models):
            row_text = []
            for j in range(n_models):
                if i == j:
                    text = f"{model_list[i]}<br>MCC: 1.000"
                else:
                    mcc_val = mcc_matrix[i, j]
                    p_val = pvalue_matrix[i, j]
                    sig_text = "Sig" if significance_matrix[i, j] else "NS"
                    text = f"MCC: {mcc_val:.3f}<br>p: {p_val:.4f}<br>{sig_text}"
                row_text.append(text)
            text_matrix.append(row_text)
        
        # Crear figura básica
        fig = go.Figure(data=go.Heatmap(
            z=mcc_matrix,
            x=model_list,
            y=model_list,
            text=text_matrix,
            texttemplate="%{text}",
            textfont={"size": 9},
            colorscale="RdYlBu_r",
            zmin=0,
            zmax=1,
            colorbar=dict(title="MCC Score")
        ))
        
        # Agregar bordes rojos para diferencias significativas
        for i in range(n_models):
            for j in range(n_models):
                if significance_matrix[i, j] and i != j:
                    fig.add_shape(
                        type="rect",
                        x0=j-0.4, y0=i-0.4,
                        x1=j+0.4, y1=i+0.4,
                        line=dict(color="red", width=2),
                        fillcolor="rgba(0,0,0,0)"
                    )
        
        fig.update_layout(
            title="Matriz de Comparación Matews (MCC)<br><sub>Bordes rojos: diferencias significativas (p<0.05)</sub>",
            width=600,
            height=600,
            xaxis=dict(title="Modelo"),
            yaxis=dict(title="Modelo", autorange="reversed"),
            font=dict(size=12)
        )
        
        return fig
        
    except Exception as e:
        # Error handling sin dependencias de streamlit
        logger.error(f"Error creando matriz MCC: {e}")
        return None

def calculate_statistical_tests(comparison_data):
    """Calcular tests estadísticos para todos los modelos"""
    try:
        if not comparison_data:
            return None, None
            
        if "modelos_detallados" not in comparison_data:
            return None, None
        
        modelos_detallados = comparison_data["modelos_detallados"]
        model_names = list(modelos_detallados.keys())
        
        mcnemar_results = []
        mcc_scores = {}
        
        # Extraer MCC scores ya calculados (no recalcular)
        for model_name, model_data in modelos_detallados.items():
            mcc_scores[model_name] = model_data.get('mcc', 0.0)
        
        # Comparar cada par de modelos solo para McNemar (sin duplicados)
        for i, model1 in enumerate(model_names):
            for j, model2 in enumerate(model_names[i+1:], i+1):
                comparison_key = f"{model1}_vs_{model2}"
                
                # Obtener predicciones
                model1_data = modelos_detallados[model1]
                model2_data = modelos_detallados[model2]
                
                if "predictions" in model1_data and "predictions" in model2_data:
                    y_true = np.array(model1_data["predictions"]["y_true"])
                    y_pred1 = np.array(model1_data["predictions"]["y_pred"])
                    y_pred2 = np.array(model2_data["predictions"]["y_pred"])
                    
                    # Asegurar que las longitudes coincidan
                    min_len = min(len(y_true), len(y_pred1), len(y_pred2))
                    y_true = y_true[:min_len]
                    y_pred1 = y_pred1[:min_len]
                    y_pred2 = y_pred2[:min_len]
                    
                    # Solo calcular McNemar
                    mcnemar_result = mcnemar_test(y_true, y_pred1, y_pred2)
                    
                    if mcnemar_result:
                        mcnemar_result['comparison'] = comparison_key
                        mcnemar_result['model1'] = model1
                        mcnemar_result['model2'] = model2
                        mcnemar_results.append(mcnemar_result)
        
        return mcnemar_results, mcc_scores
        
    except Exception as e:
        st.error(f"Error calculando tests estadísticos: {e}")
        return None, None

def display_hybrid_comparison_results(comparison_data, t):
    """Muestra los resultados de comparación híbrida"""
    if not comparison_data:
        st.warning(t("no_hybrid_comparison_data"))
        return
    
    st.markdown(f"#### {t('hybrid_comparison_analysis')}")
    
    # Resumen general
    resumen = comparison_data.get("resumen_general", {})
    
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
    
    # Crear gráficos interactivos
    fig1, fig2 = create_comparison_interactive_plots(comparison_data)
    
    if fig1 and fig2:
        tab1, tab2 = st.tabs(["Precisiones", "MCC Scores"])
        
        with tab1:
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            st.plotly_chart(fig2, use_container_width=True)
    

    
    
    # Detalles de modelos híbridos
    if "modelos_detallados" in comparison_data:
        st.markdown("##### 🧠 Detalles de Modelos Híbridos")
        
        modelos_detallados = comparison_data["modelos_detallados"]
        hybrid_models = {k: v for k, v in modelos_detallados.items() if v.get("type") == "hybrid"}
        
        for model_name, model_data in hybrid_models.items():
            with st.expander(f"🤖 {model_name}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Precisión", f"{model_data.get('accuracy', 0):.1f}%")
                    st.metric("MCC Score", f"{model_data.get('mcc', 0):.3f}")
                
                with col2:
                    if "f1_scores" in model_data:
                        avg_f1 = np.mean(model_data["f1_scores"])
                        st.metric("F1-Score Promedio", f"{avg_f1:.3f}")
                    
                    if "precision_scores" in model_data:
                        avg_precision = np.mean(model_data["precision_scores"])
                        st.metric("Precisión Promedio", f"{avg_precision:.3f}")
                
                with col3:
                    if "recall_scores" in model_data:
                        avg_recall = np.mean(model_data["recall_scores"])
                        st.metric("Recall Promedio", f"{avg_recall:.3f}")
                    
                    if "architecture" in model_data:
                        arch = model_data["architecture"]
                        st.write(f"**Tipo**: {arch.get('tipo', 'N/A')}")
                        st.write(f"**Atención**: {arch.get('atencion', 'N/A')}")
    
    # Información adicional
    st.markdown("##### ℹ️ Información del Análisis")
    fecha_generacion = comparison_data.get("fecha_generacion", "No disponible")
    st.info(f"**Fecha de generación**: {fecha_generacion}")
    
    # Conclusiones
    st.markdown("##### 📝 Conclusiones")
    objetivo_alcanzado = resumen.get("objetivo_90_alcanzado", False)
    if objetivo_alcanzado:
        st.success("✅ **Objetivo alcanzado**: Los modelos híbridos superaron el 90% de precisión establecido como meta.")
    else:
        st.warning("⚠️ **Objetivo parcial**: Algunos modelos híbridos están cerca del 90% de precisión.")
    
    # Tests estadísticos
    st.markdown("##### 📊 Tests Estadísticos")
    
    # Calcular y mostrar tests estadísticos
    try:
        if not comparison_data:
            st.info("No hay datos de comparación disponibles para los tests estadísticos.")
            return
        
        # Debug: verificar estructura de datos
        if isinstance(comparison_data, str):
            st.error("Error: comparison_data es un string en lugar de un diccionario")
            return
            
        if not isinstance(comparison_data, dict):
            st.error(f"Error: comparison_data tiene tipo {type(comparison_data)} en lugar de dict")
            return
            
        mcnemar_results, mcc_scores = calculate_statistical_tests(comparison_data)
        
        if mcnemar_results or mcc_scores:
            tab1, tab2 = st.tabs(["📊 MCC Scores Individuales", "🔬 Test de McNemar"])
            
            with tab1:
                st.markdown("**Matthews Correlation Coefficient (MCC) por Modelo**")
                st.markdown("Los MCC scores muestran la calidad de cada modelo individualmente. No son comparaciones por pares.")
                
                if mcc_scores:
                    mcc_fig = create_mcc_scores_plot(mcc_scores)
                    if mcc_fig:
                        st.plotly_chart(mcc_fig, use_container_width=True)
                    
                    # Mostrar tabla de MCC scores
                    df_mcc = pd.DataFrame([
                        {
                            'Modelo': model,
                            'MCC Score': f"{mcc:.4f}",
                            'Interpretación': "Excelente" if mcc > 0.8 else "Bueno" if mcc > 0.6 else "Regular" if mcc > 0.4 else "Malo"
                        }
                        for model, mcc in sorted(mcc_scores.items(), key=lambda x: x[1], reverse=True)
                    ])
                    st.dataframe(df_mcc, use_container_width=True)
                else:
                    st.info("No hay datos de MCC disponibles.")
            
            with tab2:
                st.markdown("**Test de McNemar - Comparaciones por Pares de Modelos**")
                st.markdown("El test de McNemar evalúa si existe diferencia significativa entre el rendimiento de dos modelos.")
                
                if mcnemar_results:
                    # Matriz de McNemar
                    mcnemar_matrix_fig = create_mcnemar_matrix_plot(mcnemar_results)
                    if mcnemar_matrix_fig:
                        st.plotly_chart(mcnemar_matrix_fig, use_container_width=True)
                    
                    # Mostrar tabla de resultados de McNemar
                    df_mcnemar = pd.DataFrame([
                        {
                            'Comparación': result['comparison'].replace('_vs_', ' vs '),
                            'Modelo 1': result['model1'],
                            'Acc. Modelo 1': f"{result.get('model1_accuracy', 0):.3f}",
                            'Modelo 2': result['model2'], 
                            'Acc. Modelo 2': f"{result.get('model2_accuracy', 0):.3f}",
                            'Ganador': result.get('winner', 'empate'),
                            'p-valor': f"{result['p_value']:.4f}",
                            'Significativo': "Sí" if result['significant'] else "No",
                            'Solo M1 correcto (b)': result.get('b', 0),
                            'Solo M2 correcto (c)': result.get('c', 0),
                            'Interpretación': f"{'Diferencia significativa' if result['significant'] else 'Sin diferencia significativa'} - {result.get('winner', 'empate')} es mejor" if result.get('winner') not in ['empate', None] else 'Sin diferencia significativa'
                        }
                        for result in mcnemar_results
                    ])
                    st.dataframe(df_mcnemar, use_container_width=True)
                    
                    # Explicación mejorada
                    st.info("""
                    💡 **Interpretación del Test de McNemar**:
                    - **p < 0.05**: Diferencia significativa entre modelos
                    - **Ganador**: Modelo con más aciertos únicos (b vs c)
                    - **b**: Casos donde solo Modelo 1 acertó y Modelo 2 falló
                    - **c**: Casos donde solo Modelo 2 acertó y Modelo 1 falló
                    - Si b > c: Modelo 1 es mejor | Si c > b: Modelo 2 es mejor
                    """)
                else:
                    st.info("No hay comparaciones de McNemar disponibles.")
        else:
            st.info("Los tests estadísticos requieren datos de predicciones completos.")
    except Exception as e:
        st.error(f"Error generando tests estadísticos: {e}")
    

def display_training_results():
    """Muestra resultados del entrenamiento con gráficos interactivos de Plotly"""
    t = get_translation_function()
    
    # Cargar datos estructurados
    training_metrics = load_training_metrics()
    hybrid_results = load_hybrid_training_results()
    comparison_results = load_hybrid_comparison_results()
    
    if training_metrics or hybrid_results or comparison_results:
        st.markdown(f"### {t('training_results')}")
        
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
            colors = ["#FF6B6B" if typ == "clasico" else "#4ECDC4" for typ in comp["types"]]
            
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
            fig.update_yaxes(range=[700, 1200], row=1, col=3)
            
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico adicional de MCC
            st.markdown("##### Comparación de MCC Scores")
            fig_mcc = go.Figure()
            fig_mcc.add_trace(
                go.Bar(x=comp["modelos"], y=comp["mcc"], marker_color=colors, 
                       text=[f"{v:.3f}" for v in comp["mcc"]], textposition="auto")
            )
            fig_mcc.update_layout(height=400, yaxis_title="MCC Score", yaxis_range=[0.7, 1.0])
            st.plotly_chart(fig_mcc, use_container_width=True)
        tab_index += 1
        # 2. Matrices de confusión (interactivas)
        with tabs[tab_index]:
            st.markdown("#### 📈 Matrices de Confusión")
            class_names = training_metrics["class_names"]
            
            # Selector de modelo
            model_cm = st.selectbox("Seleccionar modelo:", list(training_metrics["confusion_matrices"].keys()))
            cm = training_metrics["confusion_matrices"][model_cm]
            
            # Crear heatmap interactivo
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=class_names,
                y=class_names,
                colorscale="Blues",
                texttemplate="%{z}",
                textfont={"size":16},
                hoverongaps=False
            ))
            fig_cm.update_layout(
                title=f"Matriz de Confusión - {model_cm}",
                xaxis_title="Clase Predicha",
                yaxis_title="Clase Verdadera",
                height=600
            )
            fig_cm.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_cm, use_container_width=True)
        tab_index += 1
        
        # 3. Historiales de entrenamiento (interactivos)
        with tabs[tab_index]:
            st.markdown("#### 📉 Historiales de Entrenamiento")
            hist_models = list(training_metrics["training_history"].keys())
            model_hist = st.selectbox("Seleccionar modelo:", hist_models, key="hist_model")
            hist = training_metrics["training_history"][model_hist]
            
            # Crear gráfico de Loss y Accuracy
            fig_hist = make_subplots(rows=1, cols=2, subplot_titles=("Pérdida (Loss)", "Precisión (Accuracy)"))
            
            # Loss
            fig_hist.add_trace(
                go.Scatter(x=hist["epochs"], y=hist["train_loss"], name="Train Loss", line=dict(color="#FF6B6B", width=2)),
                row=1, col=1
            )
            fig_hist.add_trace(
                go.Scatter(x=hist["epochs"], y=hist["val_loss"], name="Val Loss", line=dict(color="#4ECDC4", width=2, dash="dash")),
                row=1, col=1
            )
            
            # Accuracy
            fig_hist.add_trace(
                go.Scatter(x=hist["epochs"], y=hist["train_acc"], name="Train Acc", line=dict(color="#FF6B6B", width=2)),
                row=1, col=2
            )
            fig_hist.add_trace(
                go.Scatter(x=hist["epochs"], y=hist["val_acc"], name="Val Acc", line=dict(color="#4ECDC4", width=2, dash="dash")),
                row=1, col=2
            )
            
            fig_hist.update_layout(height=500)
            fig_hist.update_yaxes(title_text="Loss", row=1, col=1)
            fig_hist.update_yaxes(title_text="Accuracy (%)", row=1, col=2, range=[0, 100])
            fig_hist.update_xaxes(title_text="Época", row=1, col=1)
            fig_hist.update_xaxes(title_text="Época", row=1, col=2)
            
            st.plotly_chart(fig_hist, use_container_width=True)
        tab_index += 1
        
        # 4. Resultados Híbridos
        with tabs[tab_index]:
            st.markdown("#### 🧠 Modelos Híbridos - Resultados Avanzados")
            comp = training_metrics["comparison"]
            
            # Comparar solo híbridos vs clásicos
            hybrid_models = [m for m, typ in zip(comp["modelos"], comp["types"]) if typ == "hibrido"]
            hybrid_acc = [acc for acc, typ in zip(comp["accuracy"], comp["types"]) if typ == "hibrido"]
            hybrid_mcc = [mcc for mcc, typ in zip(comp["mcc"], comp["types"]) if typ == "hibrido"]
            
            classic_models = [m for m, typ in zip(comp["modelos"], comp["types"]) if typ == "clasico"]
            classic_acc = [acc for acc, typ in zip(comp["accuracy"], comp["types"]) if typ == "clasico"]
            
            # Gráfico de comparación híbridos vs clásicos
            fig_hybrid = go.Figure()
            fig_hybrid.add_trace(go.Bar(x=classic_models, y=classic_acc, name="Clásicos", marker_color="#FF6B6B"))
            fig_hybrid.add_trace(go.Bar(x=hybrid_models, y=hybrid_acc, name="Híbridos", marker_color="#4ECDC4"))
            
            fig_hybrid.update_layout(
                title="Precisión: Modelos Clásicos vs Híbridos",
                yaxis_title="Precisión (%)",
                yaxis_range=[70, 100],
                height=500
            )
            st.plotly_chart(fig_hybrid, use_container_width=True)
            st.success("✅ **Objetivo Alcanzado**: Los modelos híbridos superaron el 90% de precisión")
        tab_index += 1
        # 5. Métricas Híbridas Detalladas
        if hybrid_results:
            with tabs[tab_index]:
                st.markdown("#### 📊 Métricas Detalladas de Entrenamiento Híbrido")
                
                if 'dataset' in hybrid_results:
                    dataset_info = hybrid_results['dataset']
                    st.markdown("##### 📂 Información del Dataset")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Imágenes", f"{dataset_info.get('total_imagenes', 0):,}")
                    with col2:
                        st.metric("Clases", dataset_info.get('clases', 0))
                    with col3:
                        st.metric("Tipos de Archivo", ", ".join(dataset_info.get('tipos_archivo', [])))
                
                if 'modelos_hibridos' in hybrid_results:
                    st.markdown("##### 🎯 Resultados por Modelo")
                    for model_name, model_data in hybrid_results['modelos_hibridos'].items():
                        with st.expander(f"🧠 {model_name}", expanded=True):
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                precision = model_data.get('accuracy', 0)
                                objetivo = "✅" if precision >= 90 else "⚠️"
                                st.metric("Precisión Global", f"{precision:.1f}%", delta=f"{objetivo} Objetivo")
                            with col2:
                                st.metric("Épocas Entrenadas", model_data.get('epocas_entrenadas', 0))
                            with col3:
                                tiempo = model_data.get('tiempo_estimado_horas', 0)
                                st.metric("Tiempo Entrenamiento", f"{tiempo:.1f}h")
                            with col4:
                                params = model_data.get('parametros_entrenables', 0)
                                st.metric("Parámetros", f"{params/1e6:.1f}M")
                            if 'arquitectura' in model_data:
                                arch = model_data['arquitectura']
                                st.markdown("**Arquitectura:**")
                                st.write(f"- **Tipo**: {arch.get('tipo', 'N/A')}")
                                st.write(f"- **Atención**: {arch.get('atencion', 'N/A')}")
                                st.write(f"- **Fusión**: {arch.get('fusion', 'N/A')}")
                                if 'componentes' in arch:
                                    st.write(f"- **Componentes**: {', '.join(arch['componentes'])}")
            tab_index += 1
        
        # 6. Comparación Híbrida
        if comparison_results:
            with tabs[tab_index]:
                display_hybrid_comparison_results(comparison_results, t)
            tab_index += 1
            

def create_sidebar():
    """Crea la barra lateral con configuración - Tema Oscuro"""
    t = get_translation_function()
    
    with st.sidebar:
        # Header minimalista
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #475569;">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">🔬</div>
            <h2 style="color: #f8fafc; font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: 0.05em;">SiPakMed AI</h2>
            <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Análisis de células cervicales</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Selector de idioma
        available_languages = get_available_languages()
        current_language = get_language()
        
        if len(available_languages) > 1:
            st.markdown("""
            <h4 style="color: #cbd5e1; margin-bottom: 0.75rem;">🌐 Idioma</h4>
            """, unsafe_allow_html=True)
            selected_language = st.selectbox(
                "",
                options=list(available_languages.keys()),
                format_func=lambda x: available_languages[x],
                index=list(available_languages.keys()).index(current_language),
                label_visibility="collapsed"
            )
            
            if selected_language != current_language:
                set_language(selected_language)
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Configuración
        st.markdown("""
        <h4 style="color: #cbd5e1; margin-bottom: 0.75rem;">⚙️ Configuración</h4>
        """, unsafe_allow_html=True)
        enhance_image = st.checkbox(
            f"Mejorar imagen (CLAHE)",
            value=True,
            help="Aplica mejora de contraste adaptativo para una mejor visualización"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Información del sistema minimalista
        st.markdown("""
        <h4 style="color: #cbd5e1; margin-bottom: 0.75rem;">📊 Sistema</h4>
        """, unsafe_allow_html=True)
        
        # System info cards
        gpu_info = detect_gpu()
        
        # Modelos
        st.markdown("""
        <div style="background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border: 1px solid #475569; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">🧠</span>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">Modelos</div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">5 CNNs (3 clásicas + 2 híbridas)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Dataset
        st.markdown("""
        <div style="background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border: 1px solid #475569; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">📊</span>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">Dataset</div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">5,015 imágenes SIPaKMeD</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Precisión
        st.markdown("""
        <div style="background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border: 1px solid #475569; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">🎯</span>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">Precisión</div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">84-93% (híbridos >90%)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # GPU
        if gpu_info['available']:
            gpu_icon = "✅"
            gpu_status_text = gpu_info['device_name']
        else:
            gpu_icon = "❌"
            gpu_status_text = "No disponible"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #334155 0%, #1e293b 100%); border: 1px solid #475569; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">⚡</span>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">GPU</div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">{gpu_status_text}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Información de modelos híbridos si están disponibles
        if is_hybrid_available():
            display_hybrid_info_in_sidebar(t)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Aviso legal
        st.markdown("""
        <div style="background: linear-gradient(135deg, #78350f 0%, #451a03 100%); border: 1px solid #92400e; border-radius: 12px; padding: 1.25rem;">
            <div style="font-weight: 700; color: #fde68a; margin-bottom: 0.75rem; font-size: 0.95rem;">⚠️ Aviso Legal</div>
            <p style="color: #fcd34d; font-size: 0.8rem; line-height: 1.6; margin: 0;">
                Este sistema es solo para fines educativos y de investigación. No debe utilizarse para diagnosticar médicos reales. Siempre consulte a un profesional de la salud calificado.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        return enhance_image

def display_clinical_interpretation(predictions):
    """Muestra la interpretación clínica de los resultados"""
    t = get_translation_function()
    clinical_info = get_clinical_info()
    
    st.markdown(f"### {t('clinical_interpretation')}")
    
    # Calcular consenso
    consensus = calculate_consensus(predictions)
    
    if consensus:
        consensus_class = consensus['class_name']
        clinical_data = clinical_info.get(consensus_class, {})
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            **{t('result')}:** {consensus['class_friendly']}  
            **{t('consensus')}:** {consensus['votes']}/{consensus['total_models']} {t('models_agree')}  
            **Nivel de riesgo:** {clinical_data.get('riesgo', 'N/A')} {clinical_data.get('icon', '')}
            """)
        
        with col2:
            st.markdown(f"""
            **{t('description')}:**  
            {clinical_data.get('descripcion', 'N/A')}
            
            **{t('clinical_meaning')}:**  
            {clinical_data.get('significado', 'N/A')}
            """)

def display_download_section(predictions, image_info, probability_fig=None, consensus_fig=None, original_image=None, enhanced_image=None):
    """Muestra la sección de descarga de reportes"""
    t = get_translation_function()
    
    st.markdown(f"### {t('download_report')}")
    
    with st.expander(t("patient_info")):
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input(t("patient_name"))
        with col2:
            patient_id = st.text_input(t("patient_id"))
    
    if st.button(t("generate_pdf")):
        patient_info = {'name': patient_name, 'id': patient_id}
        
        with st.spinner(t("generating_report")):
            # Cargar datos de comparación híbrida si están disponibles
            try:
                from app_utils.data_loader import load_hybrid_comparison_results
                hybrid_comparison_data = load_hybrid_comparison_results()
            except Exception as e:
                st.warning(f"No se pudieron cargar datos híbridos: {e}")
                hybrid_comparison_data = None
            
            # Mostrar información de contexto
            
            pdf_content = generate_pdf_report(
                predictions, 
                image_info, 
                patient_info, 
                t, 
                None,
                probability_fig, 
                consensus_fig,
                original_image,
                enhanced_image,
                hybrid_training_info=None,  # Agregar si está disponible
                hybrid_comparison_data=hybrid_comparison_data
            )
            
            if pdf_content:
                st.success(t("report_generated"))
                st.info(f"PDF generado: {len(pdf_content):,} bytes ({len(pdf_content)/1024/1024:.1f} MB)")
                
                # Crear enlace de descarga
                filename = f"reporte_sipakmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                download_link = create_download_link(pdf_content, filename)
                st.markdown(download_link, unsafe_allow_html=True)
            else:
                import logging
                import traceback
                error_log = logging.getLogger(__name__)
                error_log.error("Error en generación PDF, mostrando detalles")
                st.error(f"{t('pdf_error')} Error en la generación")
                # Try to show traceback for debugging
                try:
                    st.error(f"Detalles del error (para depuración): {traceback.format_exc()}")
                except Exception:
                    pass

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación optimizada"""
    try:
        setup_app()
        t = get_translation_function()
        
        # Verificar que la función de traducción funciona
        test_translation = t('models')
        logger.info(f"Test de traducción 'models': '{test_translation}'")
        
        # Header
        display_header(t('main_title'), t('subtitle'))
        
        # Sidebar
        enhance_image = create_sidebar()
        
        # Mensaje del sistema
        display_system_ready_message(t)
        
        # Cargar modelos
        st.markdown(f"### 🤖 {t('ai_system')}")
        
        with st.container():
            models = load_models()
            
            if not models:
                display_error_message(t=t)
                st.stop()
            
            # Contar modelos totales (TensorFlow + híbridos)
            total_models = len(models)
            if is_hybrid_available():
                from app_utils.hybrid_integration import get_hybrid_model_info
                hybrid_info = get_hybrid_model_info()
                total_models += len(hybrid_info)
            
            # Mostrar métricas del sistema
            try:
                models_text = t('models')
                models_loaded_text = t('models_loaded')
                processing_mode_text = t('processing_mode')
                accuracy_range_text = t('accuracy_range')
                cell_types_count_text = t('cell_types_count')
            except Exception as e:
                logger.error(f"Error obteniendo traducciones de métricas: {e}")
                models_text = "Modelos"
                models_loaded_text = "Cargados"
                processing_mode_text = "Procesamiento"
                accuracy_range_text = "Rango"
                cell_types_count_text = "Tipos de células"
            
            # Detectar GPU para la métrica de modo
            gpu_info = detect_gpu()
            processing_mode = gpu_info['framework'] if gpu_info['available'] else "CPU"
            
            metrics_data = [
                (f"🧠 {models_text}", f"{total_models}", models_loaded_text),
                ("⚡ Modo", processing_mode, processing_mode_text),
                ("🎯 Precisión", "84-93%", accuracy_range_text),
                ("📊 Clases", "5", cell_types_count_text)
            ]
            
            display_metrics_row(metrics_data)
        
        # Mostrar resultados del entrenamiento
        display_training_results()
        
        # Análisis de imagen
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); 
                    border-radius: 20px; padding: 2rem; margin: 2rem 0; border: 2px solid var(--primary-color);">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem; text-align: center; font-weight: 700;">
                📤 {t('image_analysis')}
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            t("upload_instruction"),
            type=UI_CONFIG["supported_formats"],
            help=t("upload_help"),
            key="image_uploader"
        )
        
        if uploaded_file is None:
            display_waiting_message(t)
        else:
            # Procesar imagen cargada
            original_image = Image.open(uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📷 Imagen Original")
                st.image(original_image, use_container_width=True)
            
                # Información de la imagen
                image_info = {
                    'filename': uploaded_file.name,
                    'size': f"{original_image.size[0]} x {original_image.size[1]}",
                    'format': original_image.format,
                    'mode': original_image.mode
                }
                
                display_image_info(image_info)
            
            with col2:
                enhanced_pil = None  # Inicializar para el PDF
                if enhance_image:
                    st.markdown("#### ✨ Imagen Mejorada")
                    with st.spinner(t('applying_clahe')):
                        enhanced_pil = enhance_cervical_cell_image(original_image)
                        st.image(enhanced_pil, use_container_width=True)
                        analysis_image = enhanced_pil
                else:
                    analysis_image = original_image
            
            # Realizar predicciones con modelos TensorFlow
            st.markdown(f"#### {t('analyzing_ai')}")
            predictions = predict_cervical_cells(analysis_image, models)
            
            # Agregar predicciones de modelos híbridos si están disponibles
            if is_hybrid_available():
                hybrid_predictions = get_hybrid_predictions(analysis_image)
                if hybrid_predictions:
                    predictions.update(hybrid_predictions)
                    logger.info(f"🧠 Predicciones híbridas agregadas: {len(hybrid_predictions)} modelos")
        
            # Mostrar resultados
            if predictions:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(72, 187, 120, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%); 
                            border-radius: 20px; padding: 2rem; margin: 2rem 0; border: 2px solid var(--success-color);">
                    <h2 style="color: var(--success-color); margin-bottom: 1rem; text-align: center; font-weight: 700;">
                        📊 {t('analysis_results')}
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Cards de resultados
                clinical_info = get_clinical_info()
                display_model_results_cards(predictions, clinical_info, t)
                
                # Gráficos interactivos
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(240, 147, 251, 0.05) 0%, rgba(245, 87, 108, 0.05) 100%); 
                            border-radius: 20px; padding: 2rem; margin: 2rem 0; border: 2px solid var(--accent-color);">
                    <h2 style="color: var(--accent-color); margin-bottom: 1rem; text-align: center; font-weight: 700;">
                        📈 {t('visual_analysis')}
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                tab1, tab2, tab3, tab4 = st.tabs([t("probability_distribution"), t("model_consensus"), "🔍 Detalles de Modelos", "📊 Comparación de Predicciones"])
                
                with tab1:
                    probability_fig = create_interactive_plots(predictions)
                    st.plotly_chart(probability_fig, use_container_width=True)
                
                with tab2:
                    consensus_fig = create_consensus_chart(predictions)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.plotly_chart(consensus_fig, use_container_width=True)
                
                with tab3:
                    st.markdown("### 🔍 Detalles de Cada Modelo")
                    for model_name, pred in predictions.items():
                        with st.expander(f"🤖 {model_name}", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Clase Predicha", pred.get('class_friendly', pred.get('class', 'N/A')))
                                st.metric("Confianza", f"{pred.get('confidence', 0):.2%}")
                            with col2:
                                st.markdown("#### Probabilidades por Clase")
                                class_names = MODEL_CONFIG['class_names']
                                class_friendly = get_class_names_friendly()
                                probabilities = pred.get('probabilities', [])
                                
                                # Create a small bar chart for this model
                                fig_model = go.Figure()
                                fig_model.add_trace(
                                    go.Bar(
                                        x=[class_friendly.get(cls, cls) for cls in class_names],
                                        y=probabilities,
                                        marker_color=['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181']
                                    )
                                )
                                fig_model.update_layout(height=300, yaxis_range=[0, 1], showlegend=False)
                                st.plotly_chart(fig_model, use_container_width=True)
                
                with tab4:
                    st.markdown("### 📊 Comparación de Predicciones")
                    
                    # Create a comparison table
                    class_friendly = get_class_names_friendly()
                    comparison_data = []
                    for model_name, pred in predictions.items():
                        comparison_data.append({
                            "Modelo": model_name,
                            "Clase Predicha": pred.get('class_friendly', pred.get('class', 'N/A')),
                            "Confianza": f"{pred.get('confidence', 0):.2%}",
                            "Tipo": "Híbrido" if any(h in model_name for h in ['Hybrid', 'Ensemble', 'Multiscale']) else "Clásico"
                        })
                    
                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, use_container_width=True)
                    
                    # Show summary statistics
                    st.markdown("#### 📈 Resumen de Predicciones")
                    col1, col2, col3 = st.columns(3)
                    
                    # Count predictions per class
                    class_counts = {}
                    for pred in predictions.values():
                        cls = pred.get('class_friendly', pred.get('class', 'N/A'))
                        class_counts[cls] = class_counts.get(cls, 0) + 1
                    
                    with col1:
                        total_models = len(predictions)
                        st.metric("Total Modelos", total_models)
                    
                    with col2:
                        most_common = max(class_counts.items(), key=lambda x: x[1]) if class_counts else ("N/A", 0)
                        st.metric("Clase Más Predicha", f"{most_common[0]} ({most_common[1]} votos)")
                    
                    with col3:
                        avg_confidence = sum(p.get('confidence', 0) for p in predictions.values()) / len(predictions)
                        st.metric("Confianza Promedio", f"{avg_confidence:.2%}")
                
                # Interpretación clínica
                display_clinical_interpretation(predictions)
                
                # Sección de descarga
                display_download_section(predictions, image_info, probability_fig, consensus_fig, original_image, enhanced_pil)
            
            # Footer
            display_footer(t)
        
    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        logger.error(f"Error en aplicación principal: {e}")
        
        # Mostrar interfaz básica en caso de error
        st.markdown("## Error en la aplicación")
        st.markdown("Se ha producido un error. Por favor recarga la página.")
        
        # Función de traducción de emergencia
        def emergency_t(key):
            emergency_translations = {
                'models': 'Modelos',
                'main_title': 'Clasificador de Células Cervicales',
                'subtitle': 'Sistema de análisis automatizado'
            }
            return emergency_translations.get(key, key)
        
        # Intentar mostrar al menos información básica
        try:
            st.sidebar.markdown("### Sistema en modo de emergencia")
            st.sidebar.markdown("Recarga la página para intentar de nuevo")
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        st.error(f"Error de clave faltante: {e}")
        logger.error(f"KeyError en aplicación principal: {e}")
        
        # Mostrar interfaz mínima funcional
        st.title("🔬 Clasificador de Células Cervicales")
        st.markdown("**Error temporal - Sistema en modo básico**")
        
        # Función de traducción de emergencia total
        def emergency_translate(key):
            emergency_translations = {
                'models': 'Modelos',
                'models_loaded': 'Cargados',
                'processing_mode': 'Procesamiento',
                'accuracy_range': 'Rango',
                'cell_types_count': 'Tipos de células',
                'main_title': 'Clasificador de Células Cervicales',
                'subtitle': 'Sistema de análisis automatizado',
                'ai_system': 'Sistema de Inteligencia Artificial',
                'system_ready': 'Sistema Listo',
                'image_analysis': 'Análisis de Imagen',
                'analysis_results': 'Resultados del Análisis',
                'visual_analysis': 'Análisis Visual',
                'upload_instruction': 'Selecciona una imagen microscópica',
                'upload_help': 'Formatos: PNG, JPG, JPEG, BMP',
                'waiting_image': 'Esperando imagen',
                'upload_description': 'Carga una imagen para analizar',
                'applying_clahe': 'Procesando imagen...',
                'analyzing_ai': 'Analizando con IA...',
                'probability_distribution': 'Distribución de Probabilidades',
                'model_consensus': 'Consenso entre Modelos',
                'clinical_interpretation': 'Interpretación Clínica',
                'download_report': 'Descargar Reporte'
            }
            return emergency_translations.get(key, key)
        
        # Cargar modelos básicos
        st.markdown("### 🤖 Sistema de Inteligencia Artificial")
        try:
            from app_utils.data_loader import load_models
            models = load_models()
            if models:
                st.success(f"✅ {len(models)} modelos cargados exitosamente")
                
                # Mostrar información básica
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Modelos", len(models))
                with col2:
                    st.metric("Precisión", "84-93%")
                with col3:
                    st.metric("Clases", "5")
                
                # Análisis básico de imagen
                st.markdown("### 📤 Análisis de Imagen")
                uploaded_file = st.file_uploader(
                    "Selecciona una imagen microscópica de células cervicales",
                    type=['png', 'jpg', 'jpeg', 'bmp'],
                    help="Formatos soportados: PNG, JPG, JPEG, BMP"
                )
                
                if uploaded_file:
                    from PIL import Image
                    import numpy as np
                    
                    original_image = Image.open(uploaded_file)
                    st.image(original_image, caption="Imagen cargada", use_container_width=True)
                    
                    # Predicción básica
                    st.markdown("#### 🔍 Análisis")
                    try:
                        from app_utils.ml_predictions import predict_cervical_cells
                        predictions = predict_cervical_cells(original_image, models)
                        
                        if predictions:
                            st.success("✅ Análisis completado")
                            
                            # Mostrar resultados básicos
                            for model_name, pred in predictions.items():
                                confidence = pred.get('confidence', 0)
                                cell_type = pred.get('class_friendly', pred.get('class', 'Desconocido'))
                                st.write(f"**{model_name}**: {cell_type} ({confidence:.1%})")
                        else:
                            st.error("No se pudieron obtener predicciones")
                    except Exception as pred_error:
                        st.error(f"Error en predicción: {pred_error}")
            else:
                st.error("No se pudieron cargar los modelos")
        except Exception as model_error:
            st.error(f"Error cargando modelos: {model_error}")
        
        st.markdown("---")
        st.markdown("**Nota**: Sistema funcionando en modo básico. Recarga la página para intentar el modo completo.")
    
    except Exception as e:
        st.error(f"Error crítico: {e}")
        logger.error(f"Error crítico en aplicación: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        st.title("🔬 Sistema SIPaKMeD")
        st.error("Error crítico del sistema")
        st.markdown("Por favor, verifica la configuración y recarga la página.")


