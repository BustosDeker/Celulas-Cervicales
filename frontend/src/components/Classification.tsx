import React, { useState, useRef } from 'react'
import axios from 'axios'

const Classification: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [predictions, setPredictions] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleClassify = async () => {
    if (!selectedFile) return
    setLoading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)
    try {
      const response = await axios.post('/api/classify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setPredictions(response.data.data)
    } catch (err) {
      console.error('Error classifying image:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-slate-800">Clasificación de Imágenes</h1>

      <div className="bg-white p-8 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">Subir Imagen</h2>
        <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
          {imagePreview ? (
            <div className="space-y-4">
              <img src={imagePreview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
              <p className="text-slate-600">{selectedFile?.name}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-4xl">📁</div>
              <p className="text-slate-600">Selecciona una imagen de célula cervical</p>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="flex gap-4 justify-center mt-6">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
            >
              Seleccionar Imagen
            </button>
            {selectedFile && (
              <button
                onClick={handleClassify}
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Analizando...' : 'Analizar Imagen'}
              </button>
            )}
          </div>
        </div>
      </div>

      {predictions && (
        <div className="bg-white p-8 rounded-xl shadow-md">
          <h2 className="text-xl font-semibold text-slate-800 mb-6">Resultados de la Clasificación</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(predictions).map(([model, data]: [string, any]) => (
              <div key={model} className="border p-6 rounded-xl">
                <h3 className="text-lg font-medium text-slate-800 mb-3">{model}</h3>
                <p className="text-2xl font-bold text-blue-600 mb-2">
                  {data.class_friendly || data.predicted_class}
                </p>
                <p className="text-slate-600">
                  Confianza: {data.confidence}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Classification
