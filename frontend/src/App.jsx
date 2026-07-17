import { useState } from 'react'
import axios from 'axios'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import './App.css'
import { translations } from './translations'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const CLASS_NAMES = ['dyskeratotic', 'koilocytotic', 'metaplastic', 'parabasal', 'superficial-intermedia']
const CLASS_FRIENDLY_ES = {
  'dyskeratotic': 'Disqueratótica',
  'koilocytotic': 'Koilocítica',
  'metaplastic': 'Metaplásica',
  'parabasal': 'Parabasal',
  'superficial-intermedia': 'Superficial-Intermedia'
}
const CLASS_FRIENDLY_EN = {
  'dyskeratotic': 'Dyskeratotic',
  'koilocytotic': 'Koilocytotic',
  'metaplastic': 'Metaplastic',
  'parabasal': 'Parabasal',
  'superficial-intermedia': 'Superficial-Intermediate'
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [enhancedPreview, setEnhancedPreview] = useState(null)
  const [predictions, setPredictions] = useState(null)
  const [consensus, setConsensus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [enhance, setEnhance] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [lang, setLang] = useState('es')
  const [patientInfo, setPatientInfo] = useState({ name: '', id: '' })
  const [generatingPdf, setGeneratingPdf] = useState(false)
  const [generatingWord, setGeneratingWord] = useState(false)
  const [generatingExcel, setGeneratingExcel] = useState(false)
  const t = translations[lang]

  const CLASS_FRIENDLY = lang === 'es' ? CLASS_FRIENDLY_ES : CLASS_FRIENDLY_EN

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        setPreview(event.target.result)
      }
      reader.readAsDataURL(file)
      setEnhancedPreview(null)
      setPredictions(null)
      setConsensus(null)
      setError(null)
    }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setPreview(null)
    setEnhancedPreview(null)
    setPredictions(null)
    setConsensus(null)
    setError(null)
    setEnhance(false)
    setPatientInfo({ name: '', id: '' })
    // Reset file input
    const fileInput = document.getElementById('file-input')
    if (fileInput) {
      fileInput.value = ''
    }
  }

  const handleEnhance = async () => {
    if (!selectedFile) return
    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('image', selectedFile)
      const response = await axios.post('http://localhost:5000/api/enhance', formData)
      setEnhancedPreview(`data:image/png;base64,${response.data.enhanced_image}`)
    } catch (err) {
      setError((lang === 'es' ? 'Error al mejorar la imagen: ' : 'Error enhancing image: ') + (err.response?.data?.error || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    if (!selectedFile) return
    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('image', selectedFile)
      formData.append('enhance', enhance.toString())
      const response = await axios.post('http://localhost:5000/api/predict', formData)
      setPredictions(response.data.predictions)
      setConsensus(response.data.consensus)
    } catch (err) {
      setError((lang === 'es' ? 'Error al analizar la imagen: ' : 'Error analyzing image: ') + (err.response?.data?.error || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePdf = async () => {
    if (!predictions || !selectedFile) return
    setGeneratingPdf(true)
    setError(null)
    try {
      // Prepare image info
      const imageInfo = {
        filename: selectedFile.name,
        size: 'N/A',
        format: selectedFile.type,
        mode: 'RGB'
      }

      // Call backend to generate PDF
      const response = await axios.post('http://localhost:5000/api/generate-pdf', {
        predictions,
        image_info: imageInfo,
        patient_info: patientInfo
      })

      // Download the PDF
      const pdfData = response.data.pdf
      const pdfBlob = new Blob([Uint8Array.from(atob(pdfData), c => c.charCodeAt(0))], { type: 'application/pdf' })
      const pdfUrl = URL.createObjectURL(pdfBlob)
      const a = document.createElement('a')
      a.href = pdfUrl
      a.download = response.data.filename || 'reporte_sipakmed.pdf'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(pdfUrl)
    } catch (err) {
      setError((lang === 'es' ? 'Error al generar el reporte PDF: ' : 'Error generating PDF report: ') + (err.response?.data?.error || err.message))
    } finally {
      setGeneratingPdf(false)
    }
  }

  const handleGenerateWord = async () => {
    if (!predictions || !selectedFile) return
    setGeneratingWord(true)
    setError(null)
    try {
      const imageInfo = {
        filename: selectedFile.name,
        size: 'N/A',
        format: selectedFile.type,
        mode: 'RGB'
      }

      const response = await axios.post('http://localhost:5000/api/generate-word', {
        predictions,
        image_info: imageInfo,
        patient_info: patientInfo
      })

      const wordData = response.data.word
      const wordBlob = new Blob([Uint8Array.from(atob(wordData), c => c.charCodeAt(0))], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
      const wordUrl = URL.createObjectURL(wordBlob)
      const a = document.createElement('a')
      a.href = wordUrl
      a.download = response.data.filename || 'reporte_sipakmed.docx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(wordUrl)
    } catch (err) {
      setError((lang === 'es' ? 'Error al generar el reporte Word: ' : 'Error generating Word report: ') + (err.response?.data?.error || err.message))
    } finally {
      setGeneratingWord(false)
    }
  }

  const handleGenerateExcel = async () => {
    if (!predictions || !selectedFile) return
    setGeneratingExcel(true)
    setError(null)
    try {
      const imageInfo = {
        filename: selectedFile.name,
        size: 'N/A',
        format: selectedFile.type,
        mode: 'RGB'
      }

      const response = await axios.post('http://localhost:5000/api/generate-excel', {
        predictions,
        image_info: imageInfo,
        patient_info: patientInfo
      })

      const excelData = response.data.excel
      const excelBlob = new Blob([Uint8Array.from(atob(excelData), c => c.charCodeAt(0))], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const excelUrl = URL.createObjectURL(excelBlob)
      const a = document.createElement('a')
      a.href = excelUrl
      a.download = response.data.filename || 'reporte_sipakmed.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(excelUrl)
    } catch (err) {
      setError((lang === 'es' ? 'Error al generar el reporte Excel: ' : 'Error generating Excel report: ') + (err.response?.data?.error || err.message))
    } finally {
      setGeneratingExcel(false)
    }
  }

  const getColorForModel = (index) => {
    const colors = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    return colors[index % colors.length]
  }

  // Opciones comunes para todas las gráficas (modo oscuro/claro)
  const getChartOptions = () => {
    return {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: {
            color: isDarkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.1)'
          },
          ticks: {
            color: isDarkMode ? '#94a3b8' : '#64748b',
            font: { size: 11 }
          }
        },
        x: {
          grid: { display: false },
          ticks: {
            color: isDarkMode ? '#94a3b8' : '#64748b',
            font: { size: 11 }
          }
        }
      }
    }
  }

  return (
    <div className={`app-container ${!isDarkMode ? 'light-mode' : ''}`}>
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L4 7V10C4 14.42 6.85 18.24 11 19.5V22H13V19.5C17.15 18.24 20 14.42 20 10V7L12 2Z" fill="url(#gradient1)"/>
              <path d="M12 15C14.21 15 16 13.21 16 11C16 8.79 14.21 7 12 7C9.79 7 8 8.79 8 11C8 13.21 9.79 15 12 15Z" fill="white"/>
              <defs>
                <linearGradient id="gradient1" x1="4" y1="2" x2="20" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#8b5cf6"/>
                  <stop offset="1" stopColor="#6366f1"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="sidebar-title">
            <h2>SiPakMed AI</h2>
            <p>{lang === 'es' ? 'Análisis de células cervicales' : 'Cervical cell analysis'}</p>
          </div>
        </div>

        {/* Botones de control */}
        <div className="sidebar-controls">
          <button 
            className="control-btn" 
            onClick={() => setIsDarkMode(!isDarkMode)} 
            title={isDarkMode ? 'Modo Claro' : 'Dark Mode'}
          >
            {isDarkMode ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3V4M12 20V21M4 12H5M19 12H20M17.66 6.34L18.36 7.05M5.64 16.95L6.34 17.66M6.34 6.34L5.64 7.05M18.36 16.95L17.66 17.66M12 8C14.21 8 16 9.79 16 12C16 14.21 14.21 16 12 16C9.79 16 8 14.21 8 12C8 9.79 9.79 8 12 8Z" stroke="white" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79Z" stroke="#1e293b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </button>
          <button 
            className="control-btn" 
            onClick={() => setLang(lang === 'es' ? 'en' : 'es')} 
            title={lang === 'es' ? 'English' : 'Español'}
          >
            <span className="lang-text">{lang === 'es' ? 'EN' : 'ES'}</span>
          </button>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="nav-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 13H11V3H3V13Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M13 21H21V11H13V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M13 3H21V7H13V3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 21H11V15H3V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </span>
            {t.dashboard}
          </button>
          <button 
            className={`nav-item ${activeTab === 'analizar' ? 'active' : ''}`}
            onClick={() => setActiveTab('analizar')}
          >
            <span className="nav-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </span>
            {t.analyze}
          </button>
        </nav>
        
        <div className="sidebar-footer">
          <div className="system-info">
            <div className="info-item">
              <span className="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 16V8C21 6.89543 20.1046 6 19 6H5C3.89543 6 3 6.89543 3 8V16C3 17.1046 3.89543 18 5 18H19C20.1046 18 21 17.1046 21 16Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M7 6V4C7 2.89543 7.89543 2 9 2H15C16.1046 2 17 2.89543 17 4V6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <span className="info-text">{t.modelsLoaded}</span>
            </div>
            <div className="info-item">
              <span className="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 11H7M13 11H11M17 11H15M4 7H20M4 12H20M4 17H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <span className="info-text">{t.classes}</span>
            </div>
            <div className="info-item">
              <span className="info-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 20V10M12 20V4M6 20V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <span className="info-text">{t.precision}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="content-header">
          <div className="header-left">
            {activeTab === 'dashboard' ? (
              <>
                <h1>{t.dashboard}</h1>
                <p>{t.welcome}</p>
              </>
            ) : (
              <>
                <h1>{t.analyze}</h1>
                <p>{t.welcome}</p>
              </>
            )}
          </div>
        </header>

        <div className="content-body">
          {activeTab === 'dashboard' ? (
            <div className="dashboard">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon blue">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M21 16V8C21 6.89543 20.1046 6 19 6H5C3.89543 6 3 6.89543 3 8V16C3 17.1046 3.89543 18 5 18H19C20.1046 18 21 17.1046 21 16Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M7 6V4C7 2.89543 7.89543 2 9 2H15C16.1046 2 17 2.89543 17 4V6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <h3>5</h3>
                    <p>{t.modelsLoadedText}</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon purple">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 17C16.4183 17 20 13.4183 20 9C20 4.58172 16.4183 1 12 1C7.58172 1 4 4.58172 4 9C4 13.4183 7.58172 17 12 17Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 21L7 16" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <h3>5</h3>
                    <p>{t.classesText}</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon green">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M22 4L12 14.01L9 11.01" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <h3>92%</h3>
                    <p>{t.avgPrecision}</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon orange">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <h3>24/7</h3>
                    <p>{t.activeSystem}</p>
                  </div>
                </div>
              </div>

              <div className="charts-grid">
                <div className="chart-card compact-chart">
                  <h3>{t.comparison}</h3>
                  <Bar
                    data={{
                      labels: ['MobileNetV2', 'ResNet50', 'EfficientNetB0', 'HybridEnsemble', 'HybridMultiScale'],
                      datasets: [{
                        label: lang === 'es' ? 'Precisión (%)' : 'Precision (%)',
                        data: [84.1, 93.7, 85.9, 93.2, 90.7],
                        backgroundColor: ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
                        borderRadius: 8
                      }]
                    }}
                    options={getChartOptions()}
                  />
                </div>
                <div className="chart-card">
                  <h3>{t.classDistribution}</h3>
                  <Bar
                    data={{
                      labels: Object.values(CLASS_FRIENDLY),
                      datasets: [{
                        label: lang === 'es' ? 'Distribución' : 'Distribution',
                        data: [20, 25, 15, 18, 22],
                        backgroundColor: ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
                        borderRadius: 8
                      }]
                    }}
                    options={getChartOptions()}
                  />
                </div>
              </div>

              <div className="models-section">
                <h2 className="section-title">{t.modelsSection}</h2>
                <div className="models-grid">
                  <div className="model-card">
                    <div className="model-header">
                      <div className="model-icon blue">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 3H15L18 8V16L15 21H9L6 16V8L9 3Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M9 8H15" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <div>
                        <h4>MobileNetV2</h4>
                        <span className="accuracy-badge model-badge">84.1%</span>
                      </div>
                    </div>
                    <p className="model-desc">{t.mobilenetDesc}</p>
                    <div className="model-type">{lang === 'es' ? 'Clásico' : 'Classic'}</div>
                  </div>

                  <div className="model-card">
                    <div className="model-header">
                      <div className="model-icon purple">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M2 17L12 22L22 17" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M2 12L12 17L22 12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <div>
                        <h4>ResNet50</h4>
                        <span className="accuracy-badge model-badge">93.7%</span>
                      </div>
                    </div>
                    <p className="model-desc">{t.resnetDesc}</p>
                    <div className="model-type">{lang === 'es' ? 'Clásico' : 'Classic'}</div>
                  </div>

                  <div className="model-card">
                    <div className="model-header">
                      <div className="model-icon green">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 4H20V8H4V4Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M4 10H20V14H4V10Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M4 16H20V20H4V16Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <div>
                        <h4>EfficientNetB0</h4>
                        <span className="accuracy-badge model-badge">85.9%</span>
                      </div>
                    </div>
                    <p className="model-desc">{t.efficientnetDesc}</p>
                    <div className="model-type">{lang === 'es' ? 'Clásico' : 'Classic'}</div>
                  </div>

                  <div className="model-card">
                    <div className="model-header">
                      <div className="model-icon orange">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 2L2 7V12C2 17.52 5.84 22.27 11 23.8C16.16 22.27 20 17.52 20 12V7L12 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <div>
                        <h4>HybridEnsemble</h4>
                        <span className="accuracy-badge model-badge">93.2%</span>
                      </div>
                    </div>
                    <p className="model-desc">{t.hybridEnsembleDesc}</p>
                    <div className="model-type hybrid">{lang === 'es' ? 'Híbrido' : 'Hybrid'}</div>
                  </div>

                  <div className="model-card">
                    <div className="model-header">
                      <div className="model-icon red">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M12 8V12L14 14" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <div>
                        <h4>HybridMultiScale</h4>
                        <span className="accuracy-badge model-badge">90.7%</span>
                      </div>
                    </div>
                    <p className="model-desc">{t.hybridMultiscaleDesc}</p>
                    <div className="model-type hybrid">{lang === 'es' ? 'Híbrido' : 'Hybrid'}</div>
                  </div>
                </div>
              </div>

              <div className="features-section">
                <h2 className="section-title">{t.features}</h2>
                <div className="features-grid">
                  <div className="feature-card">
                    <div className="feature-icon blue">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 3H15L18 8V16L15 21H9L6 16V8L9 3Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <h4>{t.feature1}</h4>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon purple">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 4H20V20H4V4Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M4 4L12 12L20 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <h4>{t.feature2}</h4>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon green">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <h4>{t.feature3}</h4>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon orange">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M14 2V8H20" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <h4>{t.feature4}</h4>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon red">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7V12C2 17.52 5.84 22.27 11 23.8C16.16 22.27 20 17.52 20 12V7L12 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M9 12L11 14L15 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <h4>{t.feature5}</h4>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon cyan">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <h4>{t.feature6}</h4>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="image-analysis">
              {/* Upload Section */}
              <div className="section-card">
                <h3>{t.upload}</h3>
                <div className="upload-area">
                  <input
                    type="file"
                    id="file-input"
                    accept="image/*"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="file-input" className="upload-label">
                    {!preview ? (
                      <div className="upload-placeholder">
                        <div className="upload-icon">
                          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M21 12V17C21 18.0609 20.5786 19.0783 19.8284 19.8284C19.0783 20.5786 18.0609 21 17 21H7C5.93913 21 4.92172 20.5786 4.17157 19.8284C3.42143 19.0783 3 18.0609 3 17V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <path d="M16 6L12 2L8 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            <path d="M12 2V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        </div>
                        <p>{t.selectImage}</p>
                        <span className="upload-hint">{t.imageHint}</span>
                      </div>
                    ) : (
                      <div className="preview-container">
                        <img src={preview} alt="Preview" className="preview-img" />
                        <button
                          type="button"
                          className="clear-btn"
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                            handleClear()
                          }}
                          title={lang === 'es' ? 'Limpiar imagen' : 'Clear image'}
                        >
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 6L6 18M6 6L18 18" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        </button>
                      </div>
                    )}
                  </label>
                </div>

                {preview && (
                  <div className="actions">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={enhance}
                        onChange={(e) => setEnhance(e.target.checked)}
                      />
                      <span className="checkbox-text">{t.enhanceImage}</span>
                    </label>
                    <div className="button-group">
                      {!enhancedPreview && (
                        <button
                          className="btn btn-secondary"
                          onClick={handleEnhance}
                          disabled={loading}
                        >
                          {loading ? t.enhancing : t.enhanceBtn}
                        </button>
                      )}
                      <button
                        className="btn btn-primary"
                        onClick={handlePredict}
                        disabled={loading}
                      >
                        {loading ? t.analyzing : t.analyzeBtn}
                      </button>
                    </div>
                  </div>
                )}

                {enhancedPreview && (
                  <div className="enhanced-preview">
                    <h4>{t.enhancedTitle}</h4>
                    <img src={enhancedPreview} alt="Enhanced" className="preview-img" />
                  </div>
                )}

                {error && (
                  <div className="error-message">
                    ❌ {error}
                  </div>
                )}
              </div>

              {/* Results Section */}
              {predictions && (
                <div className="results-section">
                  <div className="section-card">
                    <h3>{t.resultsTitle}</h3>

                    {/* Consensus */}
                    {consensus && (
                      <div className="consensus-card">
                        <div className="consensus-header">
                          <span className="consensus-icon">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              <path d="M22 4L12 14.01L9 11.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </span>
                          <h4>{t.consensusTitle}</h4>
                        </div>
                        <div className="consensus-content">
                          <p className="consensus-class">{
                            lang === 'es' ? consensus.class_friendly : 
                            CLASS_FRIENDLY[consensus.class_friendly?.toLowerCase() || ''] || consensus.class_friendly
                          }</p>
                          <p className="consensus-votes">
                            {consensus.votes}/{consensus.total_models} {t.votes}{Math.round(consensus.agreement_level)}{t.percent}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Predictions Cards */}
                    <div className="predictions-grid">
                      {Object.entries(predictions).map(([modelName, pred], index) => (
                        <div key={modelName} className="prediction-card" style={{ borderLeftColor: getColorForModel(index) }}>
                          <div className="card-header">
                            <h4>{modelName}</h4>
                            <span className="accuracy-badge">{pred.confidence.toFixed(1)}%</span>
                          </div>
                          <div className="card-body">
                            <p className="predicted-class">
                              <strong>{t.class}:</strong> {
                                lang === 'es' ? pred.predicted_class : 
                                CLASS_FRIENDLY[pred.predicted_class?.toLowerCase() || ''] || pred.predicted_class
                              }
                            </p>
                            <div className="probabilities">
                              {pred.probabilities.map((prob, i) => (
                                <div key={i} className="prob-bar">
                                  <span className="prob-label">{CLASS_FRIENDLY[CLASS_NAMES[i]]}</span>
                                  <div className="prob-fill-container">
                                    <div
                                      className="prob-fill"
                                      style={{
                                        width: `${(prob * 100).toFixed(1)}%`,
                                        backgroundColor: getColorForModel(index)
                                      }}
                                    ></div>
                                  </div>
                                  <span className="prob-value">{(prob * 100).toFixed(1)}%</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Charts */}
                    <div className="charts-section">
                      <h4 className="subsection-title">{t.probabilitiesTitle}</h4>
                      <div className="charts-grid">
                        {Object.entries(predictions).map(([modelName, pred], index) => {
                          const data = {
                            labels: Object.values(CLASS_FRIENDLY),
                            datasets: [
                              {
                                label: modelName,
                                data: pred.probabilities.map(p => (p * 100).toFixed(1)),
                                backgroundColor: getColorForModel(index),
                              },
                            ],
                          };
                          return (
                            <div key={modelName} className="chart-card">
                              <h5>{modelName}</h5>
                              <Bar data={data} options={getChartOptions()} />
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Patient Info and Report Generation */}
                    <div className="pdf-section">
                      <h4 className="subsection-title">{lang === 'es' ? '📄 Generar Reportes' : '📄 Generate Reports'}</h4>
                      
                      <div className="patient-info-form">
                        <div className="form-group">
                          <label>{lang === 'es' ? 'Nombre del Paciente (opcional)' : 'Patient Name (optional)'}</label>
                          <input
                            type="text"
                            value={patientInfo.name}
                            onChange={(e) => setPatientInfo({ ...patientInfo, name: e.target.value })}
                            placeholder={lang === 'es' ? 'Ingrese el nombre del paciente' : 'Enter patient name'}
                          />
                        </div>
                        <div className="form-group">
                          <label>{lang === 'es' ? 'ID del Paciente (opcional)' : 'Patient ID (optional)'}</label>
                          <input
                            type="text"
                            value={patientInfo.id}
                            onChange={(e) => setPatientInfo({ ...patientInfo, id: e.target.value })}
                            placeholder={lang === 'es' ? 'Ingrese el ID del paciente' : 'Enter patient ID'}
                          />
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '16px' }}>
                        <button
                          className="btn btn-primary"
                          onClick={handleGeneratePdf}
                          disabled={generatingPdf}
                        >
                          {generatingPdf 
                            ? (lang === 'es' ? 'Generando PDF...' : 'Generating PDF...') 
                            : (lang === 'es' ? '📥 Descargar PDF' : '📥 Download PDF')
                          }
                        </button>

                        <button
                          className="btn btn-primary"
                          onClick={handleGenerateWord}
                          disabled={generatingWord}
                          style={{ backgroundColor: '#2563eb' }}
                        >
                          {generatingWord 
                            ? (lang === 'es' ? 'Generando Word...' : 'Generating Word...') 
                            : (lang === 'es' ? '📥 Descargar Word' : '📥 Download Word')
                          }
                        </button>

                        <button
                          className="btn btn-primary"
                          onClick={handleGenerateExcel}
                          disabled={generatingExcel}
                          style={{ backgroundColor: '#059669' }}
                        >
                          {generatingExcel 
                            ? (lang === 'es' ? 'Generando Excel...' : 'Generating Excel...') 
                            : (lang === 'es' ? '📥 Descargar Excel' : '📥 Download Excel')
                          }
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
