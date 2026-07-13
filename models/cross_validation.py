"""
Módulo de Validación Cruzada para SiPakMed-AI
Implementa validación cruzada K-Fold configurable
"""

import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.metrics import (
    confusion_matrix, classification_report, accuracy_score,
    precision_score, recall_score, f1_score, matthews_corrcoef,
    roc_curve, auc, roc_auc_score
)
from pathlib import Path
from tqdm import tqdm
import json
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from app_config.settings import MODEL_CONFIG, DATA_DIR
from models.data_loader import get_data_loaders, get_class_weights, get_full_dataset
from models.hybrid_architectures import get_hybrid_model
import torchvision.models as models

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Usando dispositivo para CV: {device}")

RESULTS_DIR = Path("data/cross_validation_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = [
    'dyskeratotic',
    'koilocytotic',
    'metaplastic',
    'parabasal',
    'superficial_intermediate'
]
CLASS_NAMES_SHORT = ["Dysk", "Koil", "Metap", "Parab", "Sup-Interm"]


def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_pretrained_model(model_type, num_classes=5):
    if model_type == "MobileNetV2":
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V2)
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, num_classes)
    elif model_type == "ResNet50":
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
    elif model_type == "EfficientNetB0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, num_classes)
    else:
        raise ValueError(f"Modelo no soportado: {model_type}")
    return model


def train_one_epoch(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in tqdm(train_loader, desc="Entrenando Fold", leave=False):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    
    return running_loss / total, 100. * correct / total


def evaluate(model, val_loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_labels = []
    all_preds = []
    all_probs = []

    with torch.no_grad():
        for inputs, labels in tqdm(val_loader, desc="Evaluando Fold", leave=False):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(predicted.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    return (
        running_loss / total, 100. * correct / total,
        np.array(all_labels), np.array(all_preds), np.array(all_probs)
    )


def cross_validate_model(model_name, dataset_path, n_splits=5, num_epochs=20, batch_size=16):
    """
    Ejecuta validación cruzada para un modelo
    """
    set_seed(42)
    logger.info(f"\n{'='*60}")
    logger.info(f"VALIDACIÓN CRUZADA ({n_splits}-FOLD) PARA: {model_name}")
    logger.info(f"{'='*60}")
    
    # Obtener dataset completo
    full_dataset = get_full_dataset(dataset_path, image_size=224)
    targets = [full_dataset[i][1] for i in range(len(full_dataset))]
    
    # KFold estratificado
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    fold_results = []
    fold_histories = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(np.zeros(len(targets)), targets)):
        logger.info(f"\n--- Fold {fold + 1}/{n_splits} ---")
        
        # Crear dataloaders para este fold
        from torch.utils.data import Subset, DataLoader
        train_subset = Subset(full_dataset, train_idx)
        val_subset = Subset(full_dataset, val_idx)
        
        train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=0)
        val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=0)
        
        # Obtener class weights para este fold
        class_weights = get_class_weights(dataset_path).to(device)
        
        # Inicializar modelo
        if model_name.startswith("Hybrid"):
            model = get_hybrid_model(model_type=model_name.split('Hybrid')[1].lower(), num_classes=5)
        else:
            model = get_pretrained_model(model_name, num_classes=5)
        
        model = model.to(device)
        criterion = nn.CrossEntropyLoss(weight=class_weights)
        optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
        scheduler = ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5, verbose=False)
        
        best_val_acc = 0.0
        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        
        for epoch in range(num_epochs):
            train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc, _, _, _ = evaluate(model, val_loader, criterion, device)
            
            scheduler.step(val_loss)
            
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_acc'].append(train_acc)
            history['val_acc'].append(val_acc)
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_state = model.state_dict().copy()
        
        # Evaluar con el mejor modelo del fold
        model.load_state_dict(best_state)
        final_val_loss, final_val_acc, final_labels, final_preds, final_probs = evaluate(
            model, val_loader, criterion, device
        )
        
        # Calcular métricas
        fold_metrics = {
            'fold': fold + 1,
            'accuracy': final_val_acc,
            'precision_macro': precision_score(final_labels, final_preds, average='macro'),
            'recall_macro': recall_score(final_labels, final_preds, average='macro'),
            'f1_macro': f1_score(final_labels, final_preds, average='macro'),
            'mcc': matthews_corrcoef(final_labels, final_preds),
            'labels': final_labels.tolist(),
            'predictions': final_preds.tolist(),
            'probabilities': final_probs.tolist()
        }
        
        fold_results.append(fold_metrics)
        fold_histories.append(history)
        logger.info(f"Fold {fold+1} - Acc: {final_val_acc:.2f}%, MCC: {fold_metrics['mcc']:.4f}")
    
    # Calcular estadísticas agregadas
    metrics_df = pd.DataFrame(fold_results)
    aggregated_metrics = {
        'model': model_name,
        'n_splits': n_splits,
        'accuracy_mean': metrics_df['accuracy'].mean(),
        'accuracy_std': metrics_df['accuracy'].std(),
        'precision_mean': metrics_df['precision_macro'].mean(),
        'precision_std': metrics_df['precision_macro'].std(),
        'recall_mean': metrics_df['recall_macro'].mean(),
        'recall_std': metrics_df['recall_macro'].std(),
        'f1_mean': metrics_df['f1_macro'].mean(),
        'f1_std': metrics_df['f1_macro'].std(),
        'mcc_mean': metrics_df['mcc'].mean(),
        'mcc_std': metrics_df['mcc'].std(),
        'fold_results': fold_results
    }
    
    logger.info(f"\n{'='*60}")
    logger.info(f"RESULTADOS AGREGADOS PARA {model_name}")
    logger.info(f"{'='*60}")
    logger.info(f"Accuracy: {aggregated_metrics['accuracy_mean']:.2f} ± {aggregated_metrics['accuracy_std']:.2f}%")
    logger.info(f"F1: {aggregated_metrics['f1_mean']:.4f} ± {aggregated_metrics['f1_std']:.4f}")
    logger.info(f"MCC: {aggregated_metrics['mcc_mean']:.4f} ± {aggregated_metrics['mcc_std']:.4f}")
    
    # Guardar resultados
    with open(RESULTS_DIR / f'cv_results_{model_name}.json', 'w') as f:
        json.dump(aggregated_metrics, f, indent=4)
    
    # Plotear resultados de CV
    plot_cv_results(metrics_df, model_name, RESULTS_DIR)
    
    return aggregated_metrics


def plot_cv_results(metrics_df, model_name, save_dir):
    """Plotear resultados de validación cruzada"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Accuracy
    axes[0].bar(range(1, len(metrics_df)+1), metrics_df['accuracy'], color='#4ECDC4', alpha=0.8)
    axes[0].axhline(y=metrics_df['accuracy'].mean(), color='red', linestyle='--', label='Media')
    axes[0].set_title(f'Accuracy por Fold - {model_name}', fontweight='bold')
    axes[0].set_xlabel('Fold')
    axes[0].set_ylabel('Accuracy (%)')
    axes[0].set_ylim(70, 100)
    axes[0].legend()
    
    # F1
    axes[1].bar(range(1, len(metrics_df)+1), metrics_df['f1_macro'], color='#FF6B6B', alpha=0.8)
    axes[1].axhline(y=metrics_df['f1_macro'].mean(), color='red', linestyle='--', label='Media')
    axes[1].set_title(f'F1 Macro por Fold - {model_name}', fontweight='bold')
    axes[1].set_xlabel('Fold')
    axes[1].set_ylabel('F1 Score')
    axes[1].set_ylim(0.7, 1.0)
    axes[1].legend()
    
    # MCC
    axes[2].bar(range(1, len(metrics_df)+1), metrics_df['mcc'], color='#45B7D1', alpha=0.8)
    axes[2].axhline(y=metrics_df['mcc'].mean(), color='red', linestyle='--', label='Media')
    axes[2].set_title(f'MCC por Fold - {model_name}', fontweight='bold')
    axes[2].set_xlabel('Fold')
    axes[2].set_ylabel('MCC')
    axes[2].set_ylim(0.6, 1.0)
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(save_dir / f'cv_summary_{model_name}.png', dpi=120, bbox_inches='tight')
    plt.close()


def run_all_cross_validation(dataset_path, n_splits=5, num_epochs=20):
    """Ejecuta validación cruzada para todos los modelos"""
    all_results = {}
    
    models_to_test = ["MobileNetV2", "ResNet50", "EfficientNetB0", "HybridEnsemble", "HybridMultiscale"]
    
    for model_name in models_to_test:
        try:
            results = cross_validate_model(
                model_name, dataset_path,
                n_splits=n_splits, num_epochs=num_epochs
            )
            all_results[model_name] = results
        except Exception as e:
            logger.error(f"Error en CV para {model_name}: {e}")
    
    # Guardar resultados combinados
    with open(RESULTS_DIR / 'cv_all_models.json', 'w') as f:
        json.dump(all_results, f, indent=4)
    
    logger.info("\n✅ Validación cruzada completada para todos los modelos!")
    return all_results


if __name__ == "__main__":
    from app_config.settings import DATA_DIR
    run_all_cross_validation(
        dataset_path=DATA_DIR / "dataset",
        n_splits=5,
        num_epochs=20
    )
