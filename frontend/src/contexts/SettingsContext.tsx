import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type Language = 'es' | 'en'
type Theme = 'light' | 'dark'

interface SettingsContextType {
  language: Language
  setLanguage: (lang: Language) => void
  theme: Theme
  setTheme: (theme: Theme) => void
  t: (key: string) => string
}

const translations = {
  es: {
    dashboard: 'Dashboard',
    eda: 'EDA',
    training: 'Entrenamiento',
    crossValidation: 'Validación Cruzada',
    hyperparameterTuning: 'Tunning',
    statisticalTests: 'Pruebas Estadísticas',
    reports: 'Reportes',
    classification: 'Clasificación',
    welcomeTitle: 'Bienvenido a SiPakMed-AI',
    welcomeSubtitle: 'Sistema de Análisis de Células Cervicales',
    models: '5 Modelos',
    modelsSubtitle: '3 clásicos + 2 híbridos',
    classes: '5 Clases',
    classesSubtitle: 'Tipos de células cervicales',
    accuracy: '93.7% Accuracy',
    accuracySubtitle: 'Mejor modelo (ResNet50)',
    reportFormats: '3 Reportes',
    reportFormatsSubtitle: 'PDF, Word y Excel',
    systemFeatures: 'Características del Sistema',
    logout: 'Cerrar Sesión',
    loginTitle: 'SiPakMed-AI',
    loginSubtitle: 'Iniciar Sesión',
    username: 'Usuario',
    password: 'Contraseña',
    enter: 'Ingresar',
    loginHint: 'Usuarios de prueba: admin/admin123 o usuario/usuario123',
    edaTitle: 'Análisis Exploratorio de Datos (EDA)',
    edaSubtitle: 'Explora y visualiza los datos',
    runEDA: 'Ejecutar EDA',
    trainingTitle: 'Entrenamiento de Modelos',
    trainingSubtitle: 'Entrena modelos de clasificación',
    startTraining: 'Iniciar Entrenamiento',
    classificationTitle: 'Clasificación de Imágenes',
    classificationSubtitle: 'Carga una imagen para clasificar',
    uploadImage: 'Subir Imagen',
    predict: 'Predecir',
  },
  en: {
    dashboard: 'Dashboard',
    eda: 'EDA',
    training: 'Training',
    crossValidation: 'Cross Validation',
    hyperparameterTuning: 'Hyperparameter Tuning',
    statisticalTests: 'Statistical Tests',
    reports: 'Reports',
    classification: 'Classification',
    welcomeTitle: 'Welcome to SiPakMed-AI',
    welcomeSubtitle: 'Cervical Cell Analysis System',
    models: '5 Models',
    modelsSubtitle: '3 classic + 2 hybrid',
    classes: '5 Classes',
    classesSubtitle: 'Cervical cell types',
    accuracy: '93.7% Accuracy',
    accuracySubtitle: 'Best model (ResNet50)',
    reportFormats: '3 Reports',
    reportFormatsSubtitle: 'PDF, Word and Excel',
    systemFeatures: 'System Features',
    logout: 'Logout',
    loginTitle: 'SiPakMed-AI',
    loginSubtitle: 'Login',
    username: 'Username',
    password: 'Password',
    enter: 'Enter',
    loginHint: 'Test users: admin/admin123 or usuario/usuario123',
    edaTitle: 'Exploratory Data Analysis (EDA)',
    edaSubtitle: 'Explore and visualize the data',
    runEDA: 'Run EDA',
    trainingTitle: 'Model Training',
    trainingSubtitle: 'Train classification models',
    startTraining: 'Start Training',
    classificationTitle: 'Image Classification',
    classificationSubtitle: 'Upload an image to classify',
    uploadImage: 'Upload Image',
    predict: 'Predict',
  },
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

interface SettingsProviderProps {
  children: ReactNode
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const [language, setLanguage] = useState<Language>(() => {
    return (localStorage.getItem('language') as Language) || 'es'
  })
  const [theme, setTheme] = useState<Theme>(() => {
    return (localStorage.getItem('theme') as Theme) || 'light'
  })

  useEffect(() => {
    localStorage.setItem('language', language)
  }, [language])

  useEffect(() => {
    localStorage.setItem('theme', theme)
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  const t = (key: string): string => {
    return translations[language][key as keyof typeof translations.es] || key
  }

  return (
    <SettingsContext.Provider value={{ language, setLanguage, theme, setTheme, t }}>
      {children}
    </SettingsContext.Provider>
  )
}

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}
