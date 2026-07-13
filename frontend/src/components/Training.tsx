import React, { useState, useEffect } from 'react'
import axios from 'axios'

const Training: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    fetchResults()
  }, [])

  const fetchResults = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/training/results')
      setResults(response.data.data)
    } catch (err) {
      console.error('Error fetching training results:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunTraining = async () => {
    setRunning(true)
    try {
      await axios.post('/api/training/run')
      await fetchResults()
    } catch (err) {
      console.error('Error running training:', err)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Entrenamiento de Modelos</h1>
        <button
          onClick={handleRunTraining}
          disabled={running}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          {running ? 'Entrenando...' : 'Ejecutar Entrenamiento'}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
        </div>
      ) : results ? (
        <div className="space-y-8">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Métricas de Entrenamiento</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {results.training_metrics?.comparison?.modelos?.map((model: string, idx: number) => (
                <div key={model} className="border p-4 rounded-lg">
                  <h4 className="font-medium text-slate-800">{model}</h4>
                  <p className="text-sm text-slate-600">
                    Accuracy: {results.training_metrics.comparison.accuracy[idx]}%
                  </p>
                  <p className="text-sm text-slate-600">
                    MCC: {results.training_metrics.comparison.mcc[idx]}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-xl shadow-md">
          <p className="text-slate-600">No hay resultados de entrenamiento disponibles. Ejecuta el entrenamiento para ver los resultados.</p>
        </div>
      )}
    </div>
  )
}

export default Training
