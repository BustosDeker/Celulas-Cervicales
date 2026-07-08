"""
Test de configuración del sistema para modelos híbridos
Verifica GPU, PyTorch, TensorFlow y carga de arquitecturas
"""
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("SIPAKMED-AI: VERIFICACIÓN DE CONFIGURACIÓN HÍBRIDA")
    logger.info("=" * 60)

    checks = {}

    # Verificación 1: PyTorch y CUDA
    logger.info("\n[1/4] Verificando PyTorch...")
    try:
        import torch
        torch_version = torch.__version__
        checks["pytorch"] = {
            "status": "✅",
            "version": torch_version,
            "details": f"PyTorch {torch_version} instalado correctamente"
        }
        logger.info(f"✅ PyTorch {torch_version} encontrado")
        
        logger.info("  - Verificando GPU (CUDA)...")
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            checks["cuda"] = {
                "status": "✅",
                "details": f"GPU disponible: {gpu_name}",
                "name": gpu_name
            }
            logger.info(f"✅ GPU (CUDA) disponible: {gpu_name}")
        else:
            checks["cuda"] = {
                "status": "⚠️",
                "details": "GPU no disponible. Se usará CPU (más lento)."
            }
            logger.warning("⚠️ GPU (CUDA) no disponible. Se usará CPU.")
    except ImportError as e:
        checks["pytorch"] = {
            "status": "❌",
            "details": f"PyTorch no encontrado: {e}"
        }
        logger.error(f"❌ PyTorch no encontrado: {e}")
        sys.exit(1)

    # Verificación 2: TensorFlow (opcional para modelos clásicos)
    logger.info("\n[2/4] Verificando TensorFlow...")
    try:
        import tensorflow as tf
        tf_version = tf.__version__
        checks["tensorflow"] = {
            "status": "✅",
            "version": tf_version,
            "details": f"TensorFlow {tf_version} instalado"
        }
        logger.info(f"✅ TensorFlow {tf_version} encontrado")
    except ImportError:
        checks["tensorflow"] = {
            "status": "⚠️",
            "details": "TensorFlow no encontrado (solo modelos híbridos en PyTorch)"
        }
        logger.warning("⚠️ TensorFlow no encontrado (solo se usarán modelos de PyTorch)")

    # Verificación 3: Importar arquitecturas híbridas
    logger.info("\n[3/4] Cargando arquitecturas híbridas...")
    try:
        from models.hybrid_architectures import (
            get_hybrid_model, count_parameters,
            HybridEnsembleCNN, HybridMultiScaleCNN
        )
        checks["architectures"] = {
            "status": "✅",
            "details": "Arquitecturas híbridas importadas correctamente"
        }
        
        logger.info("✅ Archivo hybrid_architectures.py importado")
        
        # Instanciar modelos de prueba
        logger.info("  - Probando HybridEnsemble...")
        model_ensemble = get_hybrid_model("ensemble", num_classes=5, pretrained=False)
        params_ensemble = count_parameters(model_ensemble)
        logger.info(f"  ✅ HybridEnsemble: {params_ensemble:,} parámetros entrenables")
        
        logger.info("  - Probando HybridMultiScale...")
        model_multiscale = get_hybrid_model("multiscale", num_classes=5)
        params_multiscale = count_parameters(model_multiscale)
        logger.info(f"  ✅ HybridMultiScale: {params_multiscale:,} parámetros entrenables")
        
    except Exception as e:
        checks["architectures"] = {
            "status": "❌",
            "details": f"Error en arquitecturas: {e}"
        }
        logger.error(f"❌ Error al cargar arquitecturas: {e}", exc_info=True)
        sys.exit(1)

    # Verificación 4: Carga de datos
    logger.info("\n[4/4] Verificando módulos de datos...")
    try:
        from models.data_loader import get_data_loaders, SIPaKMeDDataset
        checks["dataloader"] = {
            "status": "✅",
            "details": "Módulo de carga de datos listo"
        }
        logger.info("✅ Módulo data_loader.py importado")
    except Exception as e:
        checks["dataloader"] = {
            "status": "⚠️",
            "details": f"DataLoader advertencia: {e}"
        }
        logger.warning(f"⚠️ DataLoader advertencia: {e}")

    # Imprimir resumen final
    logger.info("\n" + "="*60)
    logger.info("RESUMEN DE LA VERIFICACIÓN")
    logger.info("="*60)
    for check_name, check_data in checks.items():
        logger.info(f"{check_data['status']} {check_name.upper()}: {check_data['details']}")

    logger.info("\n" + "="*60)
    if all([v["status"] != "❌" for v in checks.values()]):
        logger.info("✅ ¡SISTEMA LISTO PARA ENTRENAMIENTO!")
        logger.info("  Ahora puedes ejecutar:")
        logger.info("    python iniciar_entrenamiento_hibrido.py")
    else:
        logger.warning("⚠️ Hay advertencias, pero el sistema puede funcionar.")
    logger.info("="*60)


if __name__ == "__main__":
    main()
