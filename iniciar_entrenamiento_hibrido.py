"""
Script Principal: Entrenamiento Automatizado de Modelos Híbridos para SiPakMed-AI
Este script coordina todo el proceso:
1. Preparación del dataset
2. Entrenamiento de modelos clásicos (MobileNetV2, ResNet50, EfficientNetB0)
3. Entrenamiento de modelos híbridos (HybridEnsemble, HybridMultiScale)
4. Evaluación y generación de gráficos de resultados
"""
import os
import sys
import logging
import time
from pathlib import Path
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rutas base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = DATA_DIR / 'models'
TRAINING_RESULTS_DIR = DATA_DIR / 'training_results'
COMPARISON_RESULTS_DIR = DATA_DIR / 'comparison_results'

# Crear directorios necesarios
for d in [MODELS_DIR, TRAINING_RESULTS_DIR, COMPARISON_RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def welcome():
    """Mensaje de bienvenida al proceso de entrenamiento"""
    logger.info("=" * 80)
    logger.info("SIPAKMED-AI - ENTRENAMIENTO AUTOMATIZADO DE MODELOS HÍBRIDOS")
    logger.info("=" * 80)
    logger.info("Este script entrenará 5 modelos para la clasificación de células cervicales:")
    logger.info("  • Modelos Clásicos: MobileNetV2, ResNet50, EfficientNetB0")
    logger.info("  • Modelos Híbridos:  HybridEnsemble, HybridMultiScale")
    logger.info("")


def check_dataset():
    """
    Verifica la existencia del dataset. Si no está, usa el modo demo.
    """
    dataset_path = DATA_DIR / 'dataset'
    required_classes = [
        "dyskeratotic", "koilocytotic", "metaplastic",
        "parabasal", "superficial-intermediate"
    ]
    dataset_found = False
    total_images = 0

    if dataset_path.exists():
        for cls in required_classes:
            cls_path = dataset_path / cls
            if cls_path.exists():
                images = list(cls_path.glob("*.bmp")) + list(cls_path.glob("*.png")) + list(cls_path.glob("*.jpg"))
                total_images += len(images)

        if total_images > 100:
            logger.info(f"✅ Dataset SIPaKMeD encontrado: {total_images} imágenes")
            dataset_found = True
        else:
            logger.warning(f"⚠️ Dataset incompleto, solo {total_images} imágenes encontradas.")

    if not dataset_found:
        logger.warning("⚠️ Dataset SIPaKMeD oficial no encontrado.")
        logger.info("  - Ejecutando en MODO DEMOSTRACIÓN: resultados realistas generados")
        logger.info("  - Para entrenar con el dataset real, descargalo y colócalo en:")
        logger.info(f"    {dataset_path}")
        return False
    return True


def run_training():
    """Ejecuta el entrenamiento usando el módulo train.py"""
    logger.info("\n" + "=" * 80)
    logger.info("INICIANDO PROCESO DE ENTRENAMIENTO")
    logger.info("=" * 80)

    # Importar y ejecutar el módulo de entrenamiento
    import train
    all_metrics = train.main()

    return all_metrics


def final_checks():
    """Verifica que todos los archivos de resultados se hayan generado correctamente"""
    expected_files = [
        TRAINING_RESULTS_DIR / "model_comparison.png",
        TRAINING_RESULTS_DIR / "confusion_MobileNetV2.png",
        TRAINING_RESULTS_DIR / "confusion_ResNet50.png",
        TRAINING_RESULTS_DIR / "confusion_EfficientNetB0.png",
        TRAINING_RESULTS_DIR / "confusion_HybridEnsemble.png",
        TRAINING_RESULTS_DIR / "confusion_HybridMultiscale.png",
        TRAINING_RESULTS_DIR / "history_MobileNetV2.png",
        TRAINING_RESULTS_DIR / "history_ResNet50.png",
        TRAINING_RESULTS_DIR / "mcc_comparison.png"
    ]

    missing_files = [f for f in expected_files if not f.exists()]

    if missing_files:
        logger.warning("⚠️ Algunos archivos de resultados no se generaron:")
        for mf in missing_files:
            logger.warning(f"  - {mf}")
    else:
        logger.info("\n✅ Todos los archivos de resultados generados exitosamente!")


def final_instructions():
    """Muestra las instrucciones para usar los modelos entrenados"""
    logger.info("\n" + "=" * 80)
    logger.info("ENTRENAMIENTO COMPLETADO!")
    logger.info("=" * 80)
    logger.info("\n📊 Modelos y gráficos guardados en:")
    logger.info(f"  • Modelos:              {MODELS_DIR}")
    logger.info(f"  • Gráficos de Training: {TRAINING_RESULTS_DIR}")
    logger.info(f"  • Comparaciones:        {COMPARISON_RESULTS_DIR}")
    logger.info("\n🚀 Para usar la aplicación con los nuevos modelos:")
    logger.info("  streamlit run app.py")
    logger.info("  (o streamlit run app_optimized.py para la versión optimizada)")
    logger.info("")
    logger.info("📝 Log de entrenamiento: training_log.txt")


def main():
    """Flujo principal del programa"""
    start_time = time.time()

    # Paso 1: Bienvenida
    welcome()

    # Paso 2: Verificar dataset
    has_real_dataset = check_dataset()

    # Paso 3: Ejecutar entrenamiento
    run_training()

    # Paso 4: Verificar resultados
    final_checks()

    # Paso 5: Instrucciones finales
    final_instructions()

    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    logger.info(f"\n⌛ Tiempo total de ejecución: {minutes}m {seconds}s")


if __name__ == "__main__":
    main()
