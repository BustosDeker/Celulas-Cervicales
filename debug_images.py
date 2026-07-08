
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from app_utils.data_loader import load_training_images, RESULTS_DIR

print("Directorio de resultados:", RESULTS_DIR)
print("Directorio existe:", RESULTS_DIR.exists())

if RESULTS_DIR.exists():
    print("\nArchivos en el directorio de resultados:")
    for file in RESULTS_DIR.glob("*.png"):
        print("  -", file.name)

print("\nResultado de load_training_images():")
training_images = load_training_images()

print("  - model_comparison:", training_images.get('model_comparison'))
print("  - confusion_matrices:", training_images.get('confusion_matrices'))
print("  - training_histories:", training_images.get('training_histories'))
print("  - hybrid_comparison:", training_images.get('hybrid_comparison'))

print("\nDepuracion completada!")

