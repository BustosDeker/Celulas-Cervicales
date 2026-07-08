"""
Generador de reportes PDF
"""

import os
from datetime import datetime
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def create_probability_graphs(predictions):
    """Crea gráficos de distribución de probabilidades para cada modelo"""
    class_names = ["Células Superficiales", "Células Intermedias", 
                   "Células Parabasales", "Células Koilocíticas", 
                   "Células Displásicas"]
    colors_list = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181']
    images = []
    
    for model_name, pred in predictions.items():
        probabilities = pred.get('probabilities', [0]*5)
        
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(class_names, probabilities, color=colors_list)
        ax.set_title(f'{model_name} - Distribución de Probabilidades')
        ax.set_ylabel('Probabilidad')
        ax.set_ylim([0, 1])
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        images.append(buf)
        plt.close()
    
    return images


def create_consensus_graph(predictions):
    """Crea un gráfico de pastel para el consenso entre modelos"""
    class_counts = {}
    total_models = len(predictions)
    
    for pred in predictions.values():
        cls = pred.get('class_friendly', pred.get('class', 'N/A'))
        class_counts[cls] = class_counts.get(cls, 0) + 1
    
    fig, ax = plt.subplots(figsize=(5, 5))
    colors_list = ['#00D25B', '#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
    ax.pie(class_counts.values(), labels=class_counts.keys(), 
           autopct='%1.1f%%', colors=colors_list[:len(class_counts)],
           startangle=90)
    ax.set_title('Consenso entre Modelos')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()
    return buf


def generate_pdf_report(predictions, image_info, patient_info, t=None, model_comparison=None, probability_fig=None, consensus_fig=None, original_image=None, enhanced_image=None, hybrid_training_info=None, hybrid_comparison_data=None):
    """
    Genera un reporte PDF completo y detallado
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=portrait(letter), rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        story = []
        styles = getSampleStyleSheet()
        
        # Define custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], textColor=colors.blue, fontSize=22, spaceAfter=30, alignment=1)
        heading2 = ParagraphStyle('Heading2Custom', parent=styles['Heading2'], spaceBefore=20, spaceAfter=12)
        
        # Portada y Metadatos
        story.append(Paragraph("Reporte de Análisis de Células Cervicales", title_style))
        story.append(Paragraph("Sistema SiPakMed-AI", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Fecha y Hora del Análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        if patient_info and patient_info.get('name'):
            story.append(Paragraph(f"Paciente: {patient_info['name']}", styles['Normal']))
        if patient_info and patient_info.get('id'):
            story.append(Paragraph(f"ID de Paciente: {patient_info['id']}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Análisis de la Imagen
        story.append(Paragraph("1. Análisis de la Imagen", heading2))
        if isinstance(image_info, dict):
            image_table_data = [
                ["Nombre del Archivo", str(image_info.get('filename', 'N/A'))],
                ["Dimensiones", str(image_info.get('size', 'N/A'))],
                ["Formato", str(image_info.get('format', 'N/A'))],
                ["Modo", str(image_info.get('mode', 'N/A'))]
            ]
            image_table = Table(image_table_data)
            image_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(image_table)
        story.append(Spacer(1, 20))
        
        # Imágenes
        story.append(Paragraph("2. Imágenes Analizadas", heading2))
        col_widths = [3*inch, 3*inch]
        image_content = []
        
        if original_image:
            img_buffer1 = BytesIO()
            try:
                original_image.save(img_buffer1, format='PNG')
                img_buffer1.seek(0)
                img1 = Image(img_buffer1, width=2.8*inch, height=2.3*inch)
                if enhanced_image:
                    img_buffer2 = BytesIO()
                    enhanced_image.save(img_buffer2, format='PNG')
                    img_buffer2.seek(0)
                    img2 = Image(img_buffer2, width=2.8*inch, height=2.3*inch)
                    image_content = [
                        [Paragraph("Imagen Original", styles['Heading3']), Paragraph("Imagen Mejorada (CLAHE)", styles['Heading3'])],
                        [img1, img2]
                    ]
                else:
                    image_content = [[Paragraph("Imagen Original", styles['Heading3']), ''], [img1, '']]
            except Exception as e:
                logger.error(f"Error al agregar imágenes: {e}")
        
        if image_content:
            img_table = Table(image_content, colWidths=col_widths)
            story.append(img_table)
        
        story.append(PageBreak())
        
        # Resultados de Predicción
        story.append(Paragraph("3. Resultados de Predicción", heading2))
        if predictions:
            # Tabla de predicciones
            data = [["Modelo", "Clase Predicha", "Confianza (%)", "Tipo de Modelo"]]
            for model_name, pred in predictions.items():
                class_name = pred.get('class_friendly', pred.get('predicted_class', 'N/A'))
                confidence = pred.get('confidence', 0)
                model_type = "Híbrido" if any(h in model_name for h in ['Hybrid', 'Ensemble', 'Multiscale']) else "Clásico"
                data.append([model_name, str(class_name), f"{confidence:.2f}", model_type])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(table)
            
            # Resumen de predicciones
            story.append(Spacer(1, 20))
            story.append(Paragraph("Resumen del Análisis", styles['Heading3']))
            
            total_models = len(predictions)
            avg_confidence = sum(p.get('confidence', 0) for p in predictions.values()) / total_models
            class_counts = {}
            for pred in predictions.values():
                cls = pred.get('class_friendly', pred.get('predicted_class', 'N/A'))
                class_counts[cls] = class_counts.get(cls, 0) + 1
            most_common = max(class_counts.items(), key=lambda x: x[1]) if class_counts else ("N/A", 0)
            
            summary_data = [
                ["Total de Modelos", str(total_models)],
                ["Confianza Promedio", f"{avg_confidence:.2f}%"],
                ["Clase con Mayor Consenso", f"{most_common[0]}"],
                ["Votos para la Clase Principal", f"{most_common[1]} de {total_models}"]
            ]
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(summary_table)
            
            # Probabilidades por clase para cada modelo
            story.append(Spacer(1, 20))
            story.append(Paragraph("Distribución de Probabilidades", styles['Heading3']))
            
            # Agregar gráficos de probabilidades
            try:
                prob_graphs = create_probability_graphs(predictions)
                for img_buf in prob_graphs:
                    img = Image(img_buf, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 12))
            except Exception as e:
                logger.error(f"Error creando gráficos de probabilidades: {e}")
            
            # Agregar texto de probabilidades
            for model_name, pred in predictions.items():
                story.append(Paragraph(f"{model_name}:", styles['Heading4']))
                probs = pred.get('probabilities', [])
                if probs:
                    class_names = ["Células Superficiales", "Células Intermedias", "Células Parabasales", "Células Koilocíticas", "Células Displásicas"]
                    prob_text = ""
                    for i, cls in enumerate(class_names):
                        if i < len(probs):
                            prob_text += f"• {cls}: {probs[i]*100:.2f}%  "
                    story.append(Paragraph(prob_text, styles['Normal']))
            
            # Agregar gráfico de consenso
            story.append(Spacer(1, 20))
            story.append(Paragraph("Consenso entre Modelos", styles['Heading3']))
            try:
                consensus_graph = create_consensus_graph(predictions)
                img = Image(consensus_graph, width=5*inch, height=5*inch)
                story.append(img)
            except Exception as e:
                logger.error(f"Error creando gráfico de consenso: {e}")
        
        story.append(PageBreak())
        
        # Interpretación Clínica y Métricas del Sistema
        story.append(Paragraph("4. Interpretación y Información del Sistema", heading2))
        
        system_data = [
            ["Modelos Disponibles", "5 (3 clásicas + 2 híbridas)"],
            ["Precisión del Sistema", "84-93%"],
            ["Clases de Células", "5"],
            ["Modo de Procesamiento", "CPU/GPU"]
        ]
        system_table = Table(system_data)
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.green),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        story.append(system_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        return pdf_content
    except Exception as e:
        logger.error(f"Error en generate_pdf_report: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def create_download_link(pdf_content, filename="reporte_sipakmed.pdf"):
    """
    Crea un enlace de descarga para el PDF
    """
    try:
        import base64
        b64 = base64.b64encode(pdf_content).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Descargar Reporte PDF</a>'
        return href
    except Exception as e:
        logger.error(f"Error en create_download_link: {e}")
        return "<p>No se pudo crear el enlace de descarga.</p>"
