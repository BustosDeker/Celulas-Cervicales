import React from 'react'
import { useSettings } from '../contexts/SettingsContext'

const Dashboard: React.FC = () => {
  const { t, theme } = useSettings()
  const bgClass = theme === 'dark' ? 'bg-slate-800' : 'bg-white'
  const textClass = theme === 'dark' ? 'text-slate-200' : 'text-slate-800'
  const subTextClass = theme === 'dark' ? 'text-slate-400' : 'text-slate-600'

  const features = [
    'Análisis Exploratorio de Datos (EDA)',
    'Entrenamiento de Modelos',
    'Validación Cruzada',
    'Tunning de Hiperparámetros',
    'Pruebas Estadísticas Robustas',
    'Generación de Reportes',
    'Clasificación de Imágenes',
    'Dashboard Interactivo',
  ]

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className={`text-4xl font-bold ${textClass} mb-4`}>{t('welcomeTitle')}</h1>
        <p className={`text-xl ${subTextClass}`}>{t('welcomeSubtitle')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className={`${bgClass} p-6 rounded-xl shadow-md`}>
          <div className="text-3xl mb-2">🤖</div>
          <h3 className={`text-xl font-semibold ${textClass}`}>{t('models')}</h3>
          <p className={subTextClass}>{t('modelsSubtitle')}</p>
        </div>
        <div className={`${bgClass} p-6 rounded-xl shadow-md`}>
          <div className="text-3xl mb-2">🔬</div>
          <h3 className={`text-xl font-semibold ${textClass}`}>{t('classes')}</h3>
          <p className={subTextClass}>{t('classesSubtitle')}</p>
        </div>
        <div className={`${bgClass} p-6 rounded-xl shadow-md`}>
          <div className="text-3xl mb-2">📊</div>
          <h3 className={`text-xl font-semibold ${textClass}`}>{t('accuracy')}</h3>
          <p className={subTextClass}>{t('accuracySubtitle')}</p>
        </div>
        <div className={`${bgClass} p-6 rounded-xl shadow-md`}>
          <div className="text-3xl mb-2">📄</div>
          <h3 className={`text-xl font-semibold ${textClass}`}>{t('reportFormats')}</h3>
          <p className={subTextClass}>{t('reportFormatsSubtitle')}</p>
        </div>
      </div>

      <div className={`${bgClass} p-8 rounded-xl shadow-md`}>
        <h2 className={`text-2xl font-bold ${textClass} mb-4`}>{t('systemFeatures')}</h2>
        <ul className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${subTextClass}`}>
          {features.map((feature, index) => (
            <li key={index} className="flex items-center gap-3">
              <span className="text-green-500">✓</span> {feature}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default Dashboard
