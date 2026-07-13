import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import EDA from './components/EDA'
import Training from './components/Training'
import CrossValidation from './components/CrossValidation'
import HyperparameterTuning from './components/HyperparameterTuning'
import StatisticalTests from './components/StatisticalTests'
import Reports from './components/Reports'
import Classification from './components/Classification'

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
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/eda', label: 'EDA', icon: '📊' },
    { path: '/training', label: 'Entrenamiento', icon: '🤖' },
    { path: '/cross-validation', label: 'Validación Cruzada', icon: '🔄' },
    { path: '/hyperparameter-tuning', label: 'Tunning', icon: '⚙️' },
    { path: '/statistical-tests', label: 'Pruebas Estadísticas', icon: '📈' },
    { path: '/reports', label: 'Reportes', icon: '📄' },
    { path: '/classification', label: 'Clasificación', icon: '🔬' },
  ]

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-slate-800 text-white p-4">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-center">SiPakMed-AI</h1>
        <p className="text-center text-slate-400 mt-2">Usuario: {user}</p>
      </div>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="block px-4 py-3 rounded-lg hover:bg-slate-700 hover:text-white transition-colors"
          >
            {item.icon} {item.label}
          </Link>
        ))}
      </nav>
      <button
        onClick={onLogout}
        className="mt-8 w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
      >
        Cerrar Sesión
      </button>
    </div>
  )
}

export default App
