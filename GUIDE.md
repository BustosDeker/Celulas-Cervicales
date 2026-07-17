# Guía de Uso de SiPakMed-AI

## Estructura del Proyecto

- **Backend (Flask)**: `backend.py` - API para análisis de imágenes y predicciones
- **Frontend (React + Vite)**: `frontend/` - Interfaz de usuario para análisis de imágenes
- **Streamlit (Entrenamiento)**: `app_training.py` - Aplicación para ver resultados de entrenamiento
- **Streamlit (Original)**: `app.py` - Aplicación original (para referencia)
- **Entrenamiento**: `train.py` - Script para entrenar modelos

## Instalación de Dependencias

### Backend (Python)
```bash
pip install -r requirements.txt
```

### Frontend (Node.js)
```bash
cd frontend
npm install
```

## Ejecución

### 1. Backend (Flask)
```bash
python backend.py
```
Se ejecutará en `http://localhost:5000`

### 2. Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
Se ejecutará en `http://localhost:3000`

### 3. Streamlit (Entrenamiento)
```bash
streamlit run app_training.py
```
Se ejecutará en `http://localhost:8501`

## Funcionamiento

1. **Analizar Imágenes**: Usa el frontend en `http://localhost:3000` para cargar imágenes, mejorarlas con CLAHE y obtener predicciones
2. **Ver Entrenamiento**: Usa Streamlit en `http://localhost:8501` para ver resultados de entrenamiento, matrices de confusión, etc.
3. **API**: El backend en `http://localhost:5000` expone endpoints para predicciones, mejora de imágenes y generación de PDFs

## Endpoints del Backend

- `GET /api/health` - Verifica que la API esté activa
- `GET /api/models` - Obtiene información de los modelos cargados
- `POST /api/enhance` - Mejora una imagen usando CLAHE (envía imagen como form-data con key 'image')
- `POST /api/predict` - Realiza predicciones (envía imagen como form-data, opcionalmente 'enhance' = 'true' para mejorar la imagen primero)
- `POST /api/generate-pdf` - Genera un reporte PDF (envía JSON con 'predictions', 'image_info', 'patient_info')
