import { useState, useRef } from 'react'
import { UploadCloud, FileText, CheckCircle, AlertCircle, X } from 'lucide-react'
import { uploadDocument } from '../api/client'

export default function PDFUploadZone({ onSuccess }) {
  const [dragging,  setDragging]  = useState(false)
  const [file,      setFile]      = useState(null)
  const [progress,  setProgress]  = useState(0)
  const [status,    setStatus]    = useState(null) // null | 'uploading' | 'success' | 'error'
  const [result,    setResult]    = useState(null)
  const inputRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) selectFile(f)
  }

  function selectFile(f) {
    const allowed = ['application/pdf', 'text/plain']
    if (!allowed.includes(f.type) && !f.name.endsWith('.txt') && !f.name.endsWith('.pdf')) {
      setStatus('error')
      setResult('Seuls les fichiers PDF et TXT sont acceptés.')
      return
    }
    if (f.size > 20 * 1024 * 1024) {
      setStatus('error')
      setResult('Fichier trop volumineux (max 20 MB).')
      return
    }
    setFile(f)
    setStatus(null)
    setResult(null)
    setProgress(0)
  }

  async function handleUpload() {
    if (!file) return
    setStatus('uploading')
    setProgress(0)
    try {
      const data = await uploadDocument(file, pct => setProgress(pct))
      setStatus('success')
      setResult(data.message || `Document indexé avec succès (${data.chunks_added ?? '?'} chunks ajoutés).`)
      if (onSuccess) onSuccess(data)
    } catch (err) {
      setStatus('error')
      setResult(err.message)
    }
  }

  function reset() {
    setFile(null); setStatus(null); setResult(null); setProgress(0)
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center gap-3 cursor-pointer transition-colors
          ${dragging ? 'border-medical-500 bg-medical-50' : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'}`}
      >
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center transition-colors
          ${dragging ? 'bg-medical-100 text-medical-600' : 'bg-slate-100 text-slate-400'}`}>
          <UploadCloud className="w-7 h-7" />
        </div>
        <div className="text-center">
          <p className="font-semibold text-slate-700">
            {dragging ? 'Déposez le fichier ici' : 'Glissez-déposez ou cliquez pour sélectionner'}
          </p>
          <p className="text-sm text-slate-400 mt-1">PDF ou TXT · max 20 MB</p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          className="hidden"
          onChange={e => e.target.files[0] && selectFile(e.target.files[0])}
        />
      </div>

      {/* Selected file */}
      {file && status !== 'success' && (
        <div className="glass-card p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-slate-800 truncate">{file.name}</p>
            <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          <button onClick={reset} className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Progress bar */}
      {status === 'uploading' && (
        <div>
          <div className="flex justify-between text-xs font-medium text-slate-600 mb-1.5">
            <span>Indexation en cours...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="h-full bg-medical-600 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Result feedback */}
      {status === 'success' && (
        <div className="glass-card p-4 border-l-2 border-l-emerald-500 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-emerald-700">Indexation réussie</p>
            <p className="text-sm text-slate-600 mt-0.5">{result}</p>
            <button onClick={reset} className="text-xs text-blue-600 hover:underline mt-2 font-medium">
              Ajouter un autre document
            </button>
          </div>
        </div>
      )}
      {status === 'error' && (
        <div className="glass-card p-4 border-l-2 border-l-red-500 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-600">Erreur d'indexation</p>
            <p className="text-sm text-slate-600 mt-0.5">{result}</p>
          </div>
        </div>
      )}

      {/* Upload button */}
      {file && status === null && (
        <button onClick={handleUpload} className="btn-primary w-full">
          <UploadCloud className="w-4 h-4" />
          Indexer dans la base de connaissances
        </button>
      )}
    </div>
  )
}
