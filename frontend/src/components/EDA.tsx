import React, { useState, useEffect } from 'react'
import axios from 'axios'

const EDA: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    fetchResults()
  }, [])

  const fetchResults = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/eda/results')
      setResults(response.data.data)
    } catch (err) {
      console.error('Error fetching EDA results:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunEDA = async () => {
    setRunning(true)
    try {
      await axios.post('/api/eda/run')
      await fetchResults()
    } catch (err) {
      console.error('Error running EDA:', err)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Análisis Exploratorio de Datos</h1>
        <button
          onClick={handleRunEDA}
          disabled={running}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {running ? 'Ejecutando...' : 'Ejecutar EDA'}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : results ? (
        <div className="space-y-8">
          {Object.entries(results.images).map(([name, path]) => (
            <div key={name} className="bg-white p-6 rounded-xl shadow-md">
              <h3 className="text-xl font-semibold text-slate-800 mb-4">
                {name.replace('_', ' ').toUpperCase()}
              </h3>
              <img
                src={`/api/eda/images/${name}.png`}
                alt={name}
                className="w-full max-w-4xl mx-auto rounded-lg shadow-sm"
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-xl shadow-md">
          <p className="text-slate-600">No hay resultados de EDA disponibles. Ejecuta el EDA para ver los resultados.</p>
        </div>
      )}
    </div>
  )
}

export default EDA
