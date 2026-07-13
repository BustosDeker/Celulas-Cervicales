
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import json
from pathlib import Path
import hashlib
from datetime import datetime

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app_config.settings import DATA_DIR, MODEL_CONFIG
from models.eda import run_eda
from models.cross_validation import run_all_cross_validation
from models.hyperparameter_tuning import tune_all_models
from models.statistical_tests import run_all_statistical_tests
from models.report_generator import generate_all_reports
from models.data_loader import get_data_loaders, get_class_weights
import train

app = FastAPI(title="SiPakMed-AI API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User authentication (simple for demo)
USERS = {
    "admin": hashlib.sha256(b"admin123").hexdigest(),
    "usuario": hashlib.sha256(b"usuario123").hexdigest(),
}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None

# --- Authentication endpoints ---
@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    if request.username not in USERS:
        return LoginResponse(success=False, message="Usuario no encontrado")
    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
    if hashed_password != USERS[request.username]:
        return LoginResponse(success=False, message="Contraseña incorrecta")
    return LoginResponse(
        success=True,
        message="Inicio de sesión exitoso",
        username=request.username
    )

# --- EDA endpoints ---
@app.post("/api/eda/run")
async def run_eda_endpoint():
    try:
        result = run_eda(
            dataset_path=DATA_DIR / "dataset",
            output_dir=DATA_DIR / "eda_results"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eda/results")
async def get_eda_results():
    try:
        eda_stats_path = DATA_DIR / "eda_results" / "eda_statistics.json"
        eda_csv_path = DATA_DIR / "eda_results" / "dataset_info.csv"
        
        results = {}
        if eda_stats_path.exists():
            with open(eda_stats_path, "r") as f:
                results["statistics"] = json.load(f)
        
        # Get the image paths
        results["images"] = {
            "class_distribution": str(DATA_DIR / "eda_results" / "class_distribution.png"),
            "image_dimensions": str(DATA_DIR / "eda_results" / "image_dimensions.png"),
            "sample_images": str(DATA_DIR / "eda_results" / "sample_images.png"),
            "color_distribution": str(DATA_DIR / "eda_results" / "color_distribution.png")
        }
        
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eda/images/{image_name}")
async def get_eda_image(image_name: str):
    image_path = DATA_DIR / "eda_results" / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(str(image_path))

# --- Training endpoints ---
@app.post("/api/training/run")
async def run_training():
    try:
        all_metrics = train.main()
        return {"success": True, "data": all_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/results")
async def get_training_results():
    try:
        from app_utils.data_loader import load_training_metrics, load_hybrid_training_results, load_hybrid_comparison_results
        results = {
            "training_metrics": load_training_metrics(),
            "hybrid_training": load_hybrid_training_results(),
            "hybrid_comparison": load_hybrid_comparison_results()
        }
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Cross-validation endpoints ---
@app.post("/api/cross-validation/run")
async def run_cv_endpoint(n_splits: int = 5):
    try:
        result = run_all_cross_validation(
            dataset_path=DATA_DIR / "dataset",
            n_splits=n_splits,
            num_epochs=20
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Hyperparameter tuning endpoints ---
@app.post("/api/hyperparameter-tuning/run")
async def run_hp_tuning():
    try:
        result = tune_all_models(
            dataset_path=DATA_DIR / "dataset",
            n_trials=30
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Statistical tests endpoints ---
@app.post("/api/statistical-tests/run")
async def run_stats_tests():
    try:
        results, df = run_all_statistical_tests()
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Report generation endpoints ---
@app.post("/api/reports/generate")
async def generate_reports():
    try:
        generate_all_reports()
        return {"success": True, "message": "Reportes generados exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/download/{report_type}")
async def download_report(report_type: str):
    reports_dir = Path("reports")
    if report_type == "pdf":
        report_path = reports_dir / "report.pdf"
    elif report_type == "docx":
        report_path = reports_dir / "report.docx"
    elif report_type == "xlsx":
        report_path = reports_dir / "report.xlsx"
    else:
        raise HTTPException(status_code=400, detail="Tipo de reporte inválido")
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return FileResponse(str(report_path), filename=report_path.name)

# --- Image classification endpoints ---
@app.post("/api/classify")
async def classify_image(file: UploadFile = File(...)):
    try:
        from PIL import Image
        import io
        from app_utils.ml_predictions import enhance_cervical_cell_image, predict_cervical_cells
        from app_utils.data_loader import load_models

        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Load models
        models = load_models()

        # Predict
        predictions = predict_cervical_cells("uploaded_image", models, image)
        
        return {"success": True, "data": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
