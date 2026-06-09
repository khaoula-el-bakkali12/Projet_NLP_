import { useEffect } from 'react'
import { AlertTriangle, X } from 'lucide-react'

export default function ConfirmModal({
  open,
  title       = 'Confirmer',
  message     = 'Êtes-vous sûr ?',
  confirmLabel = 'Confirmer',
  cancelLabel  = 'Annuler',
  variant      = 'danger',   // 'danger' | 'default'
  onConfirm,
  onCancel,
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (e) => { if (e.key === 'Escape') onCancel?.() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onCancel])

  if (!open) return null

  const isDanger = variant === 'danger'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
        onClick={onCancel}
      />

      {/* Card */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 z-10 animate-in fade-in zoom-in-95 duration-150">
        {/* Close button */}
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Icon + content */}
        <div className="flex gap-4 pr-6">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5
            ${isDanger ? 'bg-red-50' : 'bg-slate-100'}`}>
            <AlertTriangle className={`w-5 h-5 ${isDanger ? 'text-red-500' : 'text-slate-500'}`} />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-base leading-tight">{title}</h3>
            <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">{message}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 mt-6">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            onClick={() => { onConfirm?.(); onCancel?.() }}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors
              ${isDanger
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-medical-600 hover:bg-medical-700 text-white'}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
