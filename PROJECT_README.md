# SiPakMed-AI - Sistema de Análisis de Células Cervicales

Este proyecto es un sistema completo para la clasificación de células cervicales, con:
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Características**: EDA, Entrenamiento de Modelos, Validación Cruzada, Tunning de Hiperparámetros, Pruebas Estadísticas, Generación de Reportes y Clasificación de Imágenes.

## Archivos Eliminados (Duplicados o Innecesarios)
- `app_optimized.py`: Placeholder sin funcionalidad
- `dashboard.py`: Duplicaba funcionalidad de `app.py`
- `iniciar_entrenamiento_hibrido.py`: Solo llamaba a `train.py`
- `test_pdf.py`: Script de prueba
- `debug_images.py`: Script de prueba
- `run_in_codespaces.py`: Placeholder sin funcionalidad
- `test_report.pdf`: Archivo de prueba

## Estructura del Proyecto
```
SiPakMed-AI/
├── app.py                          # App original de Streamlit
├── app_config/                     # Configuración de la app
├── app_utils/                      # Utilidades de la app
├── assets/                         # Recursos
├── backend/                        # Backend con FastAPI
│   ├── main.py                     # Endpoints de la API
│   └── requirements.txt            # Dependencias del backend
├── data/                           # Datos y resultados
├── frontend/                       # Frontend con React
│   ├── src/
│   │   ├── components/             # Componentes React
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── models/                         # Modelos de ML
├── reports/                        # Reportes generados
└── ...
```

## Cómo Ejecutar el Proyecto

### 1. Backend (FastAPI)
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```
2. Ejecutar el servidor:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

### 2. Frontend (React + Vite)
1. Instalar dependencias:
   ```bash
   cd frontend
   npm install
   ```
2. Ejecutar el servidor de desarrollo:
   ```bash
   npm run dev
   ```

## Usuarios de Prueba
- Usuario: `admin`, Contraseña: `admin123`
- Usuario: `usuario`, Contraseña: `usuario123`
