import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import EDA from './components/EDA'
import Training from './components/Training'
import CrossValidation from './components/CrossValidation'
import HyperparameterTuning from './components/HyperparameterTuning'
import StatisticalTests from './components/StatisticalTests'
import Reports from './components/Reports'
import Classification from './components/Classification'
import { useSettings } from './contexts/SettingsContext'

function App() {
  const [isAuthenticated, setAuthenticated] = useState(false)
  const [user, setUser] = useState<string | null>(null)

  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setAuthenticated(true)
      setUser(storedUser)
    }
  }, [])

  const handleLogin = (username: string) => {
    setAuthenticated(true)
    setUser(username)
    localStorage.setItem('user', username)
  }

  const handleLogout = () => {
    setAuthenticated(false)
    setUser(null)
    localStorage.removeItem('user')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Router>
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <Login onLogin={handleLogin} /> : <Navigate to="/" />} />
          <Route path="/*" element={
            isAuthenticated ? (
              <div className="flex">
                <Sidebar user={user} onLogout={handleLogout} />
                <div className="flex-1 ml-64 p-6">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/eda" element={<EDA />} />
                    <Route path="/training" element={<Training />} />
                    <Route path="/cross-validation" element={<CrossValidation />} />
                    <Route path="/hyperparameter-tuning" element={<HyperparameterTuning />} />
                    <Route path="/statistical-tests" element={<StatisticalTests />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/classification" element={<Classification />} />
                  </Routes>
                </div>
              </div>
            ) : (
              <Navigate to="/login" />
            )
          } />
        </Routes>
      </Router>
    </div>
  )
}

function Sidebar({ user, onLogout }: { user: string | null; onLogout: () => void }) {
  const location = useLocation()
  const { language, setLanguage, theme, setTheme, t } = useSettings()
  const navItems = [
    { path: '/', label: 'dashboard', icon: '🏠' },
    { path: '/eda', label: 'eda', icon: '📊' },
    { path: '/training', label: 'training', icon: '🤖' },
    { path: '/cross-validation', label: 'crossValidation', icon: '🔄' },
    { path: '/hyperparameter-tuning', label: 'hyperparameterTuning', icon: '⚙️' },
    { path: '/statistical-tests', label: 'statisticalTests', icon: '📈' },
    { path: '/reports', label: 'reports', icon: '📄' },
    { path: '/classification', label: 'classification', icon: '🔬' },
  ]

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-slate-800 dark:bg-slate-900 text-white p-4 flex flex-col">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-center">SiPakMed-AI</h1>
        <p className="text-center text-slate-400 mt-2">Usuario: {user}</p>
      </div>

      <nav className="space-y-2 flex-1">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`block px-4 py-3 rounded-lg transition-colors ${
              location.pathname === item.path
                ? 'bg-blue-600 text-white'
                : 'hover:bg-slate-700 text-slate-300'
            }`}
          >
            {item.icon} {t(item.label)}
          </Link>
        ))}
      </nav>

      <div className="mt-auto space-y-3">
        <div className="flex gap-2 justify-center">
          <button
            onClick={() => setLanguage(language === 'es' ? 'en' : 'es')}
            className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm"
          >
            {language === 'es' ? '🇺🇸 EN' : '🇪🇸 ES'}
          </button>
          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>

        <button
          onClick={onLogout}
          className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
        >
          {t('logout')}
        </button>
      </div>
    </div>
  )
}

export default App
