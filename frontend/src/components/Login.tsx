import React, { useState } from 'react'
import axios from 'axios'
import { useSettings } from '../contexts/SettingsContext'

interface LoginProps {
  onLogin: (username: string) => void
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const { t, theme } = useSettings()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/login', { username, password })
      if (response.data.success) {
        onLogin(username)
      } else {
        setError(response.data.message)
      }
    } catch (err) {
      setError('Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`flex items-center justify-center min-h-screen ${theme === 'dark' ? 'bg-gradient-to-br from-slate-800 to-slate-900' : 'bg-gradient-to-br from-blue-500 to-purple-600'}`}>
      <div className={`p-8 rounded-2xl shadow-2xl w-full max-w-md ${theme === 'dark' ? 'bg-slate-800 text-white' : 'bg-white text-slate-800'}`}>
        <h1 className="text-3xl font-bold text-center mb-8">{t('loginTitle')}</h1>
        <h2 className="text-xl text-center mb-8">{t('loginSubtitle')}</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-700'}`}>{t('username')}</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                theme === 'dark' ? 'bg-slate-700 border-slate-600 text-white' : 'border-slate-300'
              }`}
              placeholder=""
            />
          </div>
          <div>
            <label className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-700'}`}>{t('password')}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                theme === 'dark' ? 'bg-slate-700 border-slate-600 text-white' : 'border-slate-300'
              }`}
              placeholder=""
            />
          </div>
          {error && (
            <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Cargando...' : t('enter')}
          </button>
        </form>
        <div className={`mt-6 text-center text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
          <p>{t('loginHint')}</p>
        </div>
      </div>
    </div>
  )
}

export default Login
