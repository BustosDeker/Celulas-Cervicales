import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useSettings } from '../contexts/SettingsContext'

const EDA: React.FC = () => {
  const { theme } = useSettings()
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [running, setRunning] = useState(false)
  const bgClass = theme === 'dark' ? 'bg-slate-800' : 'bg-white'
  const textClass = theme === 'dark' ? 'text-slate-200' : 'text-slate-800'
  const subTextClass = theme === 'dark' ? 'text-slate-400' : 'text-slate-600'

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

  const renderStats = (stats: any, title: string) => (
    <div className={`${bgClass} p-6 rounded-xl shadow-md`}>
      <h3 className={`text-xl font-semibold ${textClass} mb-4`}>{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <tbody>
            {Object.entries(stats).map(([key, value]) => (
              <tr key={key} className="border-b">
                <td className={`py-2 px-3 font-medium ${textClass}`}>
                  {key.replace('_', ' ').toUpperCase()}
                </td>
                <td className={`py-2 px-3 text-right ${subTextClass}`}>
                  {typeof value === 'number' 
                    ? (Number.isInteger(value) ? value : value.toFixed(4))
                    : String(value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className={`text-3xl font-bold ${textClass}`}>Análisis Exploratorio de Datos</h1>
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
          {/* Estadísticas generales */}
          {results.statistics && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {results.statistics.total_images && (
                <div className={`${bgClass} p-6 rounded-xl shadow-md`}>
                  <h3 className={`text-xl font-semibold ${textClass} mb-4`}>Resumen General</h3>
                  <p className={`text-2xl font-bold text-blue-600`}>
                    {results.statistics.total_images} Imágenes
                  </p>
                </div>
              )}
              {results.statistics.classes_distribution && renderStats(
                results.statistics.classes_distribution,
                'Distribución de Clases'
              )}
            </div>
          )}

          {/* Estadísticas de ancho, alto, tamaño de archivo, canales */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {results.statistics?.width_stats && renderStats(results.statistics.width_stats, 'Estadísticas de Ancho (px)')}
            {results.statistics?.height_stats && renderStats(results.statistics.height_stats, 'Estadísticas de Alto (px)')}
            {results.statistics?.file_size_stats && renderStats(results.statistics.file_size_stats, 'Estadísticas de Tamaño de Archivo (KB)')}
            {results.statistics?.channels_distribution && renderStats(results.statistics.channels_distribution, 'Distribución de Canales')}
          </div>

          {/* Visualizaciones (imágenes) */}
          {Object.entries(results.images).map(([name]) => (
            <div key={name} className={`${bgClass} p-6 rounded-xl shadow-md`}>
              <h3 className={`text-xl font-semibold ${textClass} mb-4`}>
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
        <div className={`text-center py-12 ${bgClass} rounded-xl shadow-md`}>
          <p className={subTextClass}>No hay resultados de EDA disponibles. Ejecuta el EDA para ver los resultados.</p>
        </div>
      )}
    </div>
  )
}

export default EDA
