import React, { useState } from 'react'
import axios from 'axios'
import { useSettings } from '../contexts/SettingsContext'

const Reports: React.FC = () => {
  const { t, theme } = useSettings()
  const [generating, setGenerating] = useState(false)

  const bgClass = theme === 'dark' ? 'bg-slate-800' : 'bg-white'
  const textClass = theme === 'dark' ? 'text-slate-200' : 'text-slate-800'

  const handleGenerateReports = async () => {
    setGenerating(true)
    try {
      await axios.post('/api/reports/generate')
      alert(theme === 'dark' ? 'Reports generated successfully!' : 'Reportes generados exitosamente!')
    } catch (err) {
      console.error('Error generating reports:', err)
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = (type: string) => {
    window.open(`/api/reports/download/${type}`, '_blank')
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className={`text-3xl font-bold ${textClass}`}>{t('reports')}</h1>
        <button
          onClick={handleGenerateReports}
          disabled={generating}
          className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
        >
          {generating ? (theme === 'dark' ? 'Generating...' : 'Generando...') : (theme === 'dark' ? 'Generate Reports' : 'Generar Reportes')}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className={`${bgClass} p-6 rounded-xl shadow-md text-center`}>
          <div className="text-4xl mb-4">📄</div>
          <h3 className={`text-xl font-semibold ${textClass} mb-4`}>PDF</h3>
          <button
            onClick={() => handleDownload('pdf')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {theme === 'dark' ? 'Download PDF' : 'Descargar PDF'}
          </button>
        </div>
        <div className={`${bgClass} p-6 rounded-xl shadow-md text-center`}>
          <div className="text-4xl mb-4">📘</div>
          <h3 className={`text-xl font-semibold ${textClass} mb-4`}>Word</h3>
          <button
            onClick={() => handleDownload('docx')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {theme === 'dark' ? 'Download Word' : 'Descargar Word'}
          </button>
        </div>
        <div className={`${bgClass} p-6 rounded-xl shadow-md text-center`}>
          <div className="text-4xl mb-4">📊</div>
          <h3 className={`text-xl font-semibold ${textClass} mb-4`}>Excel</h3>
          <button
            onClick={() => handleDownload('xlsx')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {theme === 'dark' ? 'Download Excel' : 'Descargar Excel'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Reports
