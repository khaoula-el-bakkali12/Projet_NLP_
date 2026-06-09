import { useEffect, useState } from 'react'
import { CheckCircle, AlertCircle, X } from 'lucide-react'

const ICONS = {
  success: <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />,
  error:   <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />,
}

export default function Snackbar({ message, type = 'success', onClose }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!message) return
    setVisible(true)
    const t = setTimeout(() => {
      setVisible(false)
      setTimeout(onClose, 300)
    }, 3500)
    return () => clearTimeout(t)
  }, [message])

  if (!message) return null

  return (
    <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-4 py-3
                     bg-gray-900 border border-gray-700 rounded-xl shadow-xl
                     text-sm text-gray-200 max-w-sm transition-all duration-300
                     ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'}`}>
      {ICONS[type]}
      <span className="flex-1">{message}</span>
      <button
        onClick={() => { setVisible(false); setTimeout(onClose, 300) }}
        className="text-gray-500 hover:text-gray-300 transition-colors"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}
