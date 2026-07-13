import React from 'react'

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-slate-800 mb-4">Bienvenido a SiPakMed-AI</h1>
        <p className="text-xl text-slate-600">Sistema de Análisis de Células Cervicales</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="text-3xl mb-2">🤖</div>
          <h3 className="text-xl font-semibold text-slate-800">5 Modelos</h3>
          <p className="text-slate-600">3 clásicos + 2 híbridos</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="text-3xl mb-2">🔬</div>
          <h3 className="text-xl font-semibold text-slate-800">5 Clases</h3>
          <p className="text-slate-600">Tipos de células cervicales</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="text-3xl mb-2">📊</div>
          <h3 className="text-xl font-semibold text-slate-800">93.7% Accuracy</h3>
          <p className="text-slate-600">Mejor modelo (ResNet50)</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-md">
          <div className="text-3xl mb-2">📄</div>
          <h3 className="text-xl font-semibold text-slate-800">3 Reportes</h3>
          <p className="text-slate-600">PDF, Word y Excel</p>
        </div>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-md">
        <h2 className="text-2xl font-bold text-slate-800 mb-4">Características del Sistema</h2>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 text-slate-600">
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Análisis Exploratorio de Datos (EDA)
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Entrenamiento de Modelos
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Validación Cruzada
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Tunning de Hiperparámetros
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Pruebas Estadísticas Robustas
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Generación de Reportes
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Clasificación de Imágenes
          </li>
          <li className="flex items-center gap-3">
            <span className="text-green-500">✓</span> Dashboard Interactivo
          </li>
        </ul>
      </div>
    </div>
  )
}

export default Dashboard
