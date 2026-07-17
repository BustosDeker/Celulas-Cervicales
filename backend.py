from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import logging
import base64
import numpy as np
from app_config.settings import MODEL_CONFIG
from app_utils.data_loader import load_models, get_class_names_friendly, get_clinical_info
from app_utils.ml_predictions import enhance_cervical_cell_image, predict_cervical_cells, calculate_consensus
from app_utils.pdf_generator import generate_pdf_report
from app_utils.report_generator import generate_word_report, generate_excel_report

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models once at startup
models = load_models()
logger.info("Models loaded successfully!")

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/api/models', methods=['GET'])
def get_models_info():
    model_info = []
    for name, config in MODEL_CONFIG["models"].items():
        model_info.append({
            "name": name,
            "type": config["type"],
            "accuracy": config["accuracy"],
            "loaded": (models.get(name) is not None)
        })
    return jsonify(model_info)

@app.route('/api/enhance', methods=['POST'])
def enhance_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        img = Image.open(file.stream)
        
        # Enhance the image
        enhanced_img = enhance_cervical_cell_image(img)
        
        # Convert to base64 for response
        buffered = io.BytesIO()
        enhanced_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            "enhanced_image": img_str,
            "format": "PNG"
        })
        
    except Exception as e:
        logger.error(f"Error enhancing image: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        img = Image.open(file.stream)
        
        # Optionally enhance
        enhance = request.form.get('enhance', 'false').lower() == 'true'
        if enhance:
            img = enhance_cervical_cell_image(img)
        
        # Make predictions
        predictions = predict_cervical_cells(img, models)
        
        # Calculate consensus
        consensus = calculate_consensus(predictions)
        
        # Get class info
        class_names_friendly = get_class_names_friendly()
        clinical_info = get_clinical_info()
        
        # Prepare response
        response = {
            "predictions": predictions,
            "consensus": consensus,
            "class_info": class_names_friendly,
            "clinical_info": clinical_info
        }
        
        # Convert numpy types to native Python types
        response = convert_numpy_types(response)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        
        # Extract data from request
        predictions = data.get('predictions', {})
        image_info = data.get('image_info', {})
        patient_info = data.get('patient_info', {})
        
        # Generate PDF report
        pdf_content = generate_pdf_report(
            predictions=predictions,
            image_info=image_info,
            patient_info=patient_info
        )
        
        if pdf_content:
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_content).decode()
            
            return jsonify({
                "pdf": pdf_base64,
                "filename": "reporte_sipakmed.pdf"
            })
        else:
            return jsonify({"error": "Failed to generate PDF"}), 500
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-word', methods=['POST'])
def generate_word():
    try:
        data = request.json
        
        # Extract data from request
        predictions = data.get('predictions', {})
        image_info = data.get('image_info', {})
        patient_info = data.get('patient_info', {})
        
        # Generate Word report
        word_buffer = generate_word_report(
            predictions=predictions,
            image_info=image_info,
            patient_info=patient_info
        )
        
        if word_buffer:
            # Convert to base64
            word_base64 = base64.b64encode(word_buffer.getvalue()).decode()
            
            return jsonify({
                "word": word_base64,
                "filename": "reporte_sipakmed.docx"
            })
        else:
            return jsonify({"error": "Failed to generate Word report"}), 500
        
    except Exception as e:
        logger.error(f"Error generating Word: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-excel', methods=['POST'])
def generate_excel():
    try:
        data = request.json
        
        # Extract data from request
        predictions = data.get('predictions', {})
        image_info = data.get('image_info', {})
        patient_info = data.get('patient_info', {})
        
        # Generate Excel report
        excel_buffer = generate_excel_report(
            predictions=predictions,
            image_info=image_info,
            patient_info=patient_info
        )
        
        if excel_buffer:
            # Convert to base64
            excel_base64 = base64.b64encode(excel_buffer.getvalue()).decode()
            
            return jsonify({
                "excel": excel_base64,
                "filename": "reporte_sipakmed.xlsx"
            })
        else:
            return jsonify({"error": "Failed to generate Excel report"}), 500
        
    except Exception as e:
        logger.error(f"Error generating Excel: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
