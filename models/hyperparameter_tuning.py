"""
Módulo de Tunning de Hiperparámetros para SiPakMed-AI
Usa Optuna para optimizar hiperparámetros de los modelos
"""

import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import optuna
from optuna.trial import TrialState
from pathlib import Path
from tqdm import tqdm
import json


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from app_config.settings import MODEL_CONFIG, DATA_DIR
from models.data_loader import get_data_loaders, get_class_weights
from models.hybrid_architectures import get_hybrid_model
import torchvision.models as models

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Usando dispositivo para Tunning: {device}")

RESULTS_DIR = Path("data/hyperparameter_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


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

    for inputs, labels in tqdm(train_loader, desc="Entrenando", leave=False):
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


def validate(model, val_loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in tqdm(val_loader, desc="Validando", leave=False):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    return running_loss / total, 100. * correct / total


def objective(trial, model_name, dataset_path):
    """Función objetivo para Optuna"""
    set_seed(42)
    
    # Espacio de búsqueda de hiperparámetros
    lr = trial.suggest_float("lr", 1e-5, 1e-1, log=True)
    weight_decay = trial.suggest_float("weight_decay", 1e-6, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    optimizer_name = trial.suggest_categorical("optimizer", ["Adam", "AdamW", "SGD"])
    
    logger.info(f"Trial {trial.number}: lr={lr:.6f}, weight_decay={weight_decay:.6f}, batch_size={batch_size}, optimizer={optimizer_name}")
    
    # Cargar datos
    class_weights = get_class_weights(dataset_path).to(device)
    train_loader, val_loader = get_data_loaders(
        root_dir=dataset_path,
        batch_size=batch_size,
        image_size=224,
        num_workers=0
    )
    
    # Inicializar modelo
    if model_name.startswith("Hybrid"):
        model = get_hybrid_model(model_type=model_name.split('Hybrid')[1].lower(), num_classes=5)
    else:
        model = get_pretrained_model(model_name, num_classes=5)
    
    model = model.to(device)
    
    # Criterio y optimizador
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    if optimizer_name == "Adam":
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name == "AdamW":
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    else:  # SGD
        optimizer = optim.SGD(model.parameters(), lr=lr, weight_decay=weight_decay, momentum=0.9)
    
    scheduler = ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)
    
    best_val_acc = 0.0
    num_epochs = 15
    
    for epoch in range(num_epochs):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        scheduler.step(val_loss)
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
        
        # Reportar a Optuna para pruning
        trial.report(val_acc, epoch)
        
        # Pruning (parada temprana)
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()
    
    return best_val_acc


def tune_hyperparameters(model_name, dataset_path, n_trials=50):
    """Tunear hiperparámetros para un modelo"""
    set_seed(42)
    logger.info(f"\n{'='*60}")
    logger.info(f"INICIANDO TUNNING DE HIPERPARÁMETROS PARA: {model_name}")
    logger.info(f"{'='*60}")
    
    # Crear estudio Optuna
    study = optuna.create_study(
        direction="maximize",
        study_name=f"tuning_{model_name}",
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=5)
    )
    
    # Ejecutar optimización
    study.optimize(
        lambda trial: objective(trial, model_name, dataset_path),
        n_trials=n_trials,
        show_progress_bar=True
    )
    
    # Resultados
    logger.info(f"\n{'='*60}")
    logger.info(f"MEJORES HIPERPARÁMETROS PARA {model_name}")
    logger.info(f"{'='*60}")
    logger.info(f"Mejor Accuracy: {study.best_value:.2f}%")
    logger.info(f"Parámetros: {study.best_params}")
    
    # Guardar resultados
    results = {
        'model': model_name,
        'best_value': study.best_value,
        'best_params': study.best_params,
        'n_trials': n_trials,
        'all_trials': [
            {
                'number': t.number,
                'value': t.value,
                'params': t.params,
                'state': t.state.name
            }
            for t in study.trials
        ]
    }
    
    with open(RESULTS_DIR / f'tuning_results_{model_name}.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Plotear resultados
    plot_optuna_results(study, model_name, RESULTS_DIR)
    
    # Convert numpy types to native Python types
    results = convert_numpy_types(results)
    return study, results


def plot_optuna_results(study, model_name, save_dir):
    """Plotear resultados del tunning"""
    fig = plt.figure(figsize=(15, 5))
    
    # Plot 1: History
    ax1 = fig.add_subplot(1, 3, 1)
    optuna.visualization.matplotlib.plot_optimization_history(study, ax=ax1)
    ax1.set_title('Historial de Optimización', fontweight='bold')
    
    # Plot 2: Parameter importances
    ax2 = fig.add_subplot(1, 3, 2)
    try:
        optuna.visualization.matplotlib.plot_param_importances(study, ax=ax2)
        ax2.set_title('Importancia de Parámetros', fontweight='bold')
    except Exception:
        pass
    
    # Plot 3: Contour (si hay suficientes trials)
    ax3 = fig.add_subplot(1, 3, 3)
    try:
        params = list(study.best_params.keys())[:2]
        if len(params) >= 2:
            optuna.visualization.matplotlib.plot_contour(study, params=params, ax=ax3)
            ax3.set_title('Contorno de Parámetros', fontweight='bold')
    except Exception:
        pass
    
    plt.tight_layout()
    plt.savefig(save_dir / f'tuning_plots_{model_name}.png', dpi=120, bbox_inches='tight')
    plt.close()


def tune_all_models(dataset_path, n_trials=30):
    """Tunear hiperparámetros para todos los modelos"""
    all_results = {}
    
    models_to_tune = ["MobileNetV2", "ResNet50", "EfficientNetB0", "HybridEnsemble", "HybridMultiscale"]
    
    for model_name in models_to_tune:
        try:
            study, results = tune_hyperparameters(model_name, dataset_path, n_trials=n_trials)
            all_results[model_name] = results
        except Exception as e:
            logger.error(f"Error en tunning para {model_name}: {e}")
    
    # Guardar resultados combinados
    with open(RESULTS_DIR / 'tuning_all_models.json', 'w') as f:
        json.dump(all_results, f, indent=4)
    
    logger.info("\n✅ Tunning de hiperparámetros completado para todos los modelos!")
    return all_results


if __name__ == "__main__":
    from app_config.settings import DATA_DIR
    tune_all_models(
        dataset_path=DATA_DIR / "dataset",
        n_trials=30
    )
