import React, { useState } from 'react'
import axios from 'axios'

const CrossValidation: React.FC = () => {
  const [nSplits, setNSplits] = useState(5)
  const [running, setRunning] = useState(false)

  const handleRunCV = async () => {
    setRunning(true)
    try {
      await axios.post(`/api/cross-validation/run?n_splits=${nSplits}`)
      alert('Validación Cruzada completada!')
    } catch (err) {
      console.error('Error running cross validation:', err)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Validación Cruzada</h1>
        <div className="flex gap-4 items-center">
          <label className="text-slate-700 font-medium">Folds:</label>
          <input
            type="number"
            value={nSplits}
            onChange={(e) => setNSplits(Number(e.target.value))}
            min="2"
            max="10"
            className="w-20 px-3 py-2 border border-slate-300 rounded-lg"
          />
          <button
            onClick={handleRunCV}
            disabled={running}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {running ? 'Ejecutando...' : 'Ejecutar CV'}
          </button>
        </div>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Información</h2>
        <p className="text-slate-600">
          La validación cruzada con {nSplits} folds evalúa el rendimiento de los modelos de manera más robusta,
          dividiendo el conjunto de datos en {nSplits} partes y entrenando/evaluando {nSplits} veces.
        </p>
      </div>
    </div>
  )
}

export default CrossValidation
