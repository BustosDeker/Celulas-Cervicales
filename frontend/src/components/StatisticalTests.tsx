import React, { useState } from 'react'
import axios from 'axios'

const StatisticalTests: React.FC = () => {
  const [running, setRunning] = useState(false)

  const handleRunTests = async () => {
    setRunning(true)
    try {
      await axios.post('/api/statistical-tests/run')
      alert('Pruebas Estadísticas completadas!')
    } catch (err) {
      console.error('Error running statistical tests:', err)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Pruebas Estadísticas</h1>
        <button
          onClick={handleRunTests}
          disabled={running}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          {running ? 'Ejecutando...' : 'Ejecutar Pruebas'}
        </button>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Pruebas Implementadas</h2>
        <ul className="list-disc list-inside space-y-2 text-slate-600">
          <li>Shapiro-Wilk: Prueba de normalidad</li>
          <li>Levene: Prueba de homogeneidad de varianzas</li>
          <li>ANOVA: Prueba de diferencias entre medias (paramétrica)</li>
          <li>Kruskal-Wallis: Prueba de diferencias entre medias (no paramétrica)</li>
          <li>Tukey HSD: Prueba post-hoc para comparaciones múltiples</li>
          <li>McNemar: Prueba para comparar dos modelos en las mismas muestras</li>
        </ul>
      </div>
    </div>
  )
}

export default StatisticalTests
