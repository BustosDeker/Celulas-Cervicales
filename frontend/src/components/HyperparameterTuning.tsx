import React, { useState } from 'react'
import axios from 'axios'

const HyperparameterTuning: React.FC = () => {
  const [running, setRunning] = useState(false)

  const handleRunTuning = async () => {
    setRunning(true)
    try {
      await axios.post('/api/hyperparameter-tuning/run')
      alert('Tunning de Hiperparámetros completado!')
    } catch (err) {
      console.error('Error running hyperparameter tuning:', err)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Tunning de Hiperparámetros</h1>
        <button
          onClick={handleRunTuning}
          disabled={running}
          className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50"
        >
          {running ? 'Ejecutando...' : 'Ejecutar Tunning'}
        </button>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Información</h2>
        <p className="text-slate-600">
          El tunning de hiperparámetros utiliza Optuna para encontrar la mejor combinación de parámetros
          para cada modelo, optimizando el accuracy en el conjunto de validación.
        </p>
      </div>
    </div>
  )
}

export default HyperparameterTuning
