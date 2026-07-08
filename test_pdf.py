
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app_utils.pdf_generator import generate_pdf_report
from PIL import Image
import io

# Create test data
test_image = Image.new('RGB', (100, 100), color='red')

test_predictions = {
    "MobileNetV2": {
        "class_friendly": "Koilocitosis",
        "predicted_class": "Koilocitosis",
        "confidence": 85.5,
        "probabilities": [0.05, 0.10, 0.05, 0.75, 0.05]
    },
    "ResNet50": {
        "class_friendly": "Koilocitosis",
        "predicted_class": "Koilocitosis",
        "confidence": 92.3,
        "probabilities": [0.03, 0.05, 0.02, 0.88, 0.02]
    },
    "EfficientNetB0": {
        "class_friendly": "Células Intermedias",
        "predicted_class": "Células Intermedias",
        "confidence": 78.0,
        "probabilities": [0.10, 0.70, 0.10, 0.05, 0.05]
    }
}

test_image_info = {"filename": "test.png", "size": "100x100", "format": "PNG"}
test_patient_info = {"name": "Test User", "id": "12345"}

print("Testing PDF generation...")
pdf_content = generate_pdf_report(
    test_predictions, 
    test_image_info, 
    test_patient_info
)

if pdf_content:
    print(f"SUCCESS! Generated PDF: {len(pdf_content)} bytes")
    
    # Save the test PDF
    with open("test_report.pdf", "wb") as f:
        f.write(pdf_content)
    print("Test PDF saved as test_report.pdf")
else:
    print("ERROR: Failed to generate PDF")
