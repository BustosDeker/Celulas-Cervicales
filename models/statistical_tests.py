"""
Módulo de Pruebas Estadísticas para SiPakMed-AI
Implementa pruebas estadísticas robustas para comparar modelos
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from app_config.settings import DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RESULTS_DIR = Path("data/statistical_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_cross_validation_results():
    """Cargar resultados de validación cruzada"""
    cv_path = Path("data/cross_validation_results/cv_all_models.json")
    if cv_path.exists():
        with open(cv_path, 'r') as f:
            return json.load(f)
    return None


def prepare_data_for_tests(cv_results):
    """Preparar datos para pruebas estadísticas"""
    data = []
    for model_name, results in cv_results.items():
        fold_results = results['fold_results']
        for fold in fold_results:
            data.append({
                'model': model_name,
                'accuracy': fold['accuracy'],
                'f1': fold['f1_macro'],
                'mcc': fold['mcc']
            })
    return pd.DataFrame(data)


def perform_shapiro_wilk(df, metric='accuracy'):
    """Prueba de Shapiro-Wilk para normalidad"""
    results = {}
    for model in df['model'].unique():
        values = df[df['model'] == model][metric].values
        stat, p_value = stats.shapiro(values)
        results[model] = {
            'statistic': float(stat),
            'p_value': float(p_value),
            'normal': bool(p_value > 0.05)
        }
        logger.info(f"Shapiro-Wilk para {model} ( {metric} ): W={stat:.4f}, p={p_value:.4f}")
    return results


def perform_levene_test(df, metric='accuracy'):
    """Prueba de Levene para homogeneidad de varianzas"""
    groups = [df[df['model'] == model][metric].values for model in df['model'].unique()]
    stat, p_value = stats.levene(*groups)
    logger.info(f"Levene Test ( {metric} ): W={stat:.4f}, p={p_value:.4f}")
    return {'statistic': float(stat), 'p_value': float(p_value), 'equal_variances': bool(p_value > 0.05)}


def perform_anova(df, metric='accuracy'):
    """ANOVA de una vía"""
    groups = [df[df['model'] == model][metric].values for model in df['model'].unique()]
    f_stat, p_value = stats.f_oneway(*groups)
    logger.info(f"ANOVA ( {metric} ): F={f_stat:.4f}, p={p_value:.4f}")
    return {'f_statistic': float(f_stat), 'p_value': float(p_value), 'significant': bool(p_value < 0.05)}


def perform_kruskal_wallis(df, metric='accuracy'):
    """Prueba de Kruskal-Wallis (no paramétrica)"""
    groups = [df[df['model'] == model][metric].values for model in df['model'].unique()]
    h_stat, p_value = stats.kruskal(*groups)
    logger.info(f"Kruskal-Wallis ( {metric} ): H={h_stat:.4f}, p={p_value:.4f}")
    return {'h_statistic': float(h_stat), 'p_value': float(p_value), 'significant': bool(p_value < 0.05)}


def perform_tukey_hsd(df, metric='accuracy'):
    """Prueba post-hoc de Tukey HSD"""
    tukey = pairwise_tukeyhsd(endog=df[metric], groups=df['model'], alpha=0.05)
    logger.info(f"Tukey HSD ( {metric} ):\n{tukey.summary()}")
    return tukey


def perform_mcnemar_test(predictions_dict):
    """
    Prueba de McNemar para comparar dos modelos (matrices de confusión 2x2)
    predictions_dict: {model1: {labels: [], preds: []}, model2: {labels: [], preds: []}}
    """
    from sklearn.metrics import confusion_matrix
    
    model_names = list(predictions_dict.keys())
    results = {}
    
    for i in range(len(model_names)):
        for j in range(i+1, len(model_names)):
            m1, m2 = model_names[i], model_names[j]
            
            # Obtener predicciones correctas/incorrectas
            correct1 = np.array(predictions_dict[m1]['labels']) == np.array(predictions_dict[m1]['preds'])
            correct2 = np.array(predictions_dict[m2]['labels']) == np.array(predictions_dict[m2]['preds'])
            
            # Tabla 2x2
            a = np.sum(correct1 & correct2)  # Ambos correctos
            b = np.sum(correct1 & ~correct2)  # Solo m1 correcto
            c = np.sum(~correct1 & correct2)  # Solo m2 correcto
            d = np.sum(~correct1 & ~correct2)  # Ambos incorrectos
            
            # Prueba de McNemar
            stat, p_value = stats.mcnemar([[a, b], [c, d]], exact=True)
            
            results[f"{m1}_vs_{m2}"] = {
                'a': int(a), 'b': int(b), 'c': int(c), 'd': int(d),
                'statistic': float(stat), 'p_value': float(p_value),
                'significant': p_value < 0.05
            }
            logger.info(f"McNemar {m1} vs {m2}: stat={stat:.4f}, p={p_value:.4f}")
    
    return results


def plot_statistical_results(df, metric='accuracy', save_dir=RESULTS_DIR):
    """Plotear resultados estadísticos"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Boxplot
    sns.boxplot(data=df, x='model', y=metric, ax=axes[0], palette='viridis')
    axes[0].set_title(f'Distribución de {metric.upper()} por Modelo', fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Violín plot
    sns.violinplot(data=df, x='model', y=metric, ax=axes[1], palette='viridis')
    axes[1].set_title(f'Distribución de {metric.upper()} (Violín)', fontweight='bold')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_dir / f'statistical_{metric}.png', dpi=120, bbox_inches='tight')
    plt.close()
    logger.info(f"Gráficos estadísticos para {metric} guardados")


def run_all_statistical_tests(cv_results=None):
    """Ejecutar todas las pruebas estadísticas"""
    if cv_results is None:
        cv_results = load_cross_validation_results()
    
    if cv_results is None:
        logger.warning("No hay resultados de CV disponibles, usando datos de demostración")
        # Datos de demostración
        cv_results = {
            "MobileNetV2": {"fold_results": [{"accuracy": 84, "f1_macro": 0.83, "mcc": 0.80}] * 5},
            "ResNet50": {"fold_results": [{"accuracy": 93, "f1_macro": 0.93, "mcc": 0.90}] * 5},
            "EfficientNetB0": {"fold_results": [{"accuracy": 86, "f1_macro": 0.85, "mcc": 0.82}] * 5},
            "HybridEnsemble": {"fold_results": [{"accuracy": 94, "f1_macro": 0.94, "mcc": 0.93}] * 5},
            "HybridMultiscale": {"fold_results": [{"accuracy": 91, "f1_macro": 0.91, "mcc": 0.91}] * 5}
        }
    
    df = prepare_data_for_tests(cv_results)
    
    results = {}
    
    for metric in ['accuracy', 'f1', 'mcc']:
        logger.info(f"\n{'='*50}")
        logger.info(f"PRUEBAS PARA MÉTRICA: {metric.upper()}")
        logger.info(f"{'='*50}")
        
        results[metric] = {
            'shapiro_wilk': perform_shapiro_wilk(df, metric),
            'levene': perform_levene_test(df, metric),
            'anova': perform_anova(df, metric),
            'kruskal_wallis': perform_kruskal_wallis(df, metric),
            'tukey_hsd': None  # Guardar después como texto
        }
        
        # Tukey HSD
        if results[metric]['anova']['significant'] or results[metric]['kruskal_wallis']['significant']:
            tukey = perform_tukey_hsd(df, metric)
            results[metric]['tukey_hsd'] = tukey.summary().as_text()
        
        plot_statistical_results(df, metric)
    
    # Guardar resultados
    with open(RESULTS_DIR / 'statistical_tests_results.json', 'w') as f:
        json.dump(results, f, indent=4, default=str)
    
    # Guardar dataframe
    df.to_csv(RESULTS_DIR / 'statistical_data.csv', index=False)
    
    logger.info("\n✅ Pruebas estadísticas completadas!")
    return results, df


if __name__ == "__main__":
    run_all_statistical_tests()
