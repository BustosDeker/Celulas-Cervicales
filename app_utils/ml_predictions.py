"""
Utilidades para predicciones de ML
"""

import numpy as np
from PIL import Image
import cv2
import logging
from app_config.settings import MODEL_CONFIG
from app_utils.data_loader import get_class_names_friendly

logger = logging.getLogger(__name__)


def enhance_cervical_cell_image(image):
    """
    Aplica mejora de imagen (CLAHE) preservando el color
    """
    try:
        # Convertir PIL Image a array numpy
        img_array = np.array(image)
        
        # Asegurar que la imagen es RGB
        if len(img_array.shape) == 2:
            # Si es escala de grises, convertir a RGB primero
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[-1] == 4:
            # Si es RGBA, convertir a RGB
            img_array = img_array[..., :3]
        
        # Convertir a espacio de color LAB para preservar colores
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Aplicar CLAHE solo al canal de luminancia (L)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        
        # Combinar de nuevo los canales
        lab_enhanced = cv2.merge((l_enhanced, a, b))
        
        # Convertir de vuelta a RGB
        enhanced_rgb = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
        
        return Image.fromarray(enhanced_rgb)
    except Exception as e:
        logger.error(f"Error en enhance_cervical_cell_image: {e}")
        return image


def predict_cervical_cells(image, models):
    """
    Realiza predicciones con los modelos.
    Usa modelos reales si están disponibles, si no usa simulación.
    """
    try:
        class_names = MODEL_CONFIG["class_names"]
        class_friendly = get_class_names_friendly()
        predictions = {}
        
        # Preprocesamiento de la imagen para modelos (si los hay reales)
        input_size = MODEL_CONFIG.get("image_size", (224, 224))
        
        for model_name, model in models.items():
            if model is not None:
                # Modelo real disponible: intentar usarlo
                try:
                    # Preprocesar la imagen
                    img_array = np.array(image.resize(input_size))
                    if len(img_array.shape) == 2:
                        img_array = np.stack((img_array,)*3, axis=-1)
                    elif img_array.shape[-1] == 4:
                        img_array = img_array[..., :3]
                    
                    img_array = img_array / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    
                    # Hacer predicción
                    if hasattr(model, 'predict'):
                        # Modelo Keras
                        pred_proba = model.predict(img_array, verbose=0)[0]
                    elif hasattr(model, 'forward') or hasattr(model, '__call__'):
                        # Modelo PyTorch
                        try:
                            import torch
                            img_tensor = torch.tensor(img_array).permute(0, 3, 1, 2).float()
                            with torch.no_grad():
                                pred_proba = model(img_tensor).softmax(dim=1)[0].numpy()
                        except Exception as torch_e:
                            logger.error(f"Error con modelo PyTorch {model_name}: {torch_e}")
                            # Fallback a simulación
                            pred_proba = np.random.rand(len(class_names))
                            pred_proba = pred_proba / pred_proba.sum()
                    else:
                        # Tipo de modelo desconocido, usar simulación
                        pred_proba = np.random.rand(len(class_names))
                        pred_proba = pred_proba / pred_proba.sum()
                
                except Exception as e:
                    logger.error(f"Error al usar modelo real {model_name}: {e}, usando simulación.")
                    pred_proba = np.random.rand(len(class_names))
                    pred_proba = pred_proba / pred_proba.sum()
            else:
                # No hay modelo real, usar simulación
                pred_proba = np.random.rand(len(class_names))
                pred_proba = pred_proba / pred_proba.sum()
            
            # Obtener la clase con mayor probabilidad
            pred_idx = np.argmax(pred_proba)
            predicted_class = class_names[pred_idx]
            confidence = pred_proba[pred_idx] * 100
            
            predictions[model_name] = {
                "probabilities": pred_proba.tolist(),
                "predicted_class": class_friendly.get(predicted_class, predicted_class),
                "class_name": predicted_class,
                "confidence": confidence,
                "class_idx": pred_idx
            }
        
        return predictions
    except Exception as e:
        logger.error(f"Error en predict_cervical_cells: {e}")
        return {}


def calculate_consensus(predictions):
    """
    Calcula el consenso entre modelos
    """
    try:
        if not predictions:
            return None
        
        class_names = MODEL_CONFIG["class_names"]
        class_friendly = get_class_names_friendly()
        votes = np.zeros(len(class_names))
        total_models = len(predictions)
        
        for model_name, pred in predictions.items():
            if "class_idx" in pred:
                votes[pred["class_idx"]] += 1
        
        # Encontrar la clase ganadora
        winner_idx = np.argmax(votes)
        winner_class = class_names[winner_idx]
        winner_votes = int(votes[winner_idx])
        
        # Nivel de acuerdo
        agreement_level = (winner_votes / total_models) * 100
        
        return {
            "class_idx": winner_idx,
            "class_name": winner_class,
            "class_friendly": class_friendly.get(winner_class, winner_class),
            "votes": winner_votes,
            "total_models": total_models,
            "agreement_level": agreement_level
        }
    except Exception as e:
        logger.error(f"Error en calculate_consensus: {e}")
        return None
