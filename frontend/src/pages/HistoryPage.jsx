import { useState, useEffect, useMemo } from 'react'
import { Clock, Eye, Trash2, Search, MessageSquare, Calendar, Cpu, RefreshCw, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getHistory, deleteHistoryItem, clearHistory } from '../api/client'
import ConfirmModal from '../components/ConfirmModal'

export default function HistoryPage() {
  const { user } = useAuth()
  const [history,      setHistory]      = useState([])
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState(null)
  const [query,        setQuery]        = useState('')
  const [selected,     setSelected]     = useState(null)
  const [confirmClear, setConfirmClear] = useState(false)

  const fetchHistory = async () => {
    if (!user?.username) { setLoading(false); return }
    setLoading(true)
    setError(null)
    try {
      const data = await getHistory(user.username)
      setHistory(data)
    } catch {
      setError('Impossible de charger l\'historique.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchHistory() }, [user?.username])

  const handleDelete = async (id) => {
    try {
      await deleteHistoryItem(user.username, id)
      setHistory(prev => prev.filter(h => h.id !== id))
      if (selected?.id === id) setSelected(null)
    } catch { alert('Erreur lors de la suppression.') }
  }

  const handleClearAll = async () => {
    try {
      await clearHistory(user.username)
      setHistory([])
      setSelected(null)
    } catch { alert('Erreur lors de la suppression.') }
  }

  const filtered = useMemo(() => {
    if (!query.trim()) return history
    const q = query.toLowerCase()
    return history.filter(h =>
      h.question?.toLowerCase().includes(q) || h.answer?.toLowerCase().includes(q)
    )
  }, [history, query])

  return (
    <div className="p-6 md:p-10 w-full space-y-8 h-full overflow-y-auto">
      <ConfirmModal
        open={confirmClear}
        title="Effacer l'historique"
        message="Supprimer définitivement toutes vos conversations ? Cette action est irréversible."
        confirmLabel="Tout supprimer"
        onConfirm={handleClearAll}
        onCancel={() => setConfirmClear(false)}
      />
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
            <Clock className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-2xl text-slate-900 font-display tracking-tight">Historique</h2>
            <p className="text-slate-500 mt-0.5 text-sm">
              {history.length} échange{history.length > 1 ? 's' : ''} sauvegardé{history.length > 1 ? 's' : ''}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative w-full md:w-72 group">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-medical-600 transition-colors" />
            <input
              type="text" value={query} onChange={e => setQuery(e.target.value)}
              placeholder="Rechercher…"
              className="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-8 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 transition-colors placeholder-slate-400"
            />
            {query && (
              <button onClick={() => setQuery('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <button onClick={fetchHistory} title="Rafraîchir"
            className="p-2.5 text-slate-500 hover:text-medical-600 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors">
            <RefreshCw className="w-4 h-4" />
          </button>

          {history.length > 0 && (
            <button onClick={() => setConfirmClear(true)}
              className="px-3 py-2.5 text-xs font-medium text-red-600 hover:bg-red-50 rounded-lg border border-red-100 transition-colors">
              Tout supprimer
            </button>
          )}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="glass-card p-16 text-center text-slate-500 text-sm">
          <RefreshCw className="w-6 h-6 mx-auto mb-3 text-slate-300 animate-spin" />
          Chargement…
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="glass-card p-8 text-center text-red-500 text-sm">{error}</div>
      )}

      {/* Detail panel */}
      {!loading && selected && (
        <div className="glass-card p-6 border-l-2 border-l-medical-500">
          <div className="flex items-start justify-between gap-4 mb-3">
            <p className="font-semibold text-slate-900">{selected.question}</p>
            <button onClick={() => setSelected(null)} className="text-slate-400 hover:text-slate-600 text-xs font-medium flex-shrink-0">Fermer ×</button>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{selected.answer}</p>
          {selected.sources?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {selected.sources.slice(0, 3).map((s, i) => (
                <span key={i} className="badge">{s.titre || s.id || `Source ${i+1}`}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filtered.length === 0 && (
        <div className="glass-card p-16 text-center text-slate-500 text-sm">
          <Clock className="w-8 h-8 mx-auto mb-3 text-slate-300" />
          {history.length === 0 ? 'Aucun historique — posez votre première question.' : 'Aucun résultat pour cette recherche.'}
        </div>
      )}

      {/* Table */}
      {!loading && !error && filtered.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 font-semibold text-slate-700 uppercase tracking-wider text-xs">
                    <div className="flex items-center gap-2"><MessageSquare className="w-3.5 h-3.5 text-slate-400" /> Question</div>
                  </th>
                  <th className="px-6 py-4 font-semibold text-slate-700 uppercase tracking-wider text-xs hidden md:table-cell">
                    <div className="flex items-center gap-2"><Calendar className="w-3.5 h-3.5 text-slate-400" /> Date</div>
                  </th>
                  <th className="px-6 py-4 font-semibold text-slate-700 uppercase tracking-wider text-xs hidden lg:table-cell">
                    <div className="flex items-center gap-2"><Cpu className="w-3.5 h-3.5 text-slate-400" /> Modèle</div>
                  </th>
                  <th className="px-6 py-4 text-right" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map(item => (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors group cursor-pointer" onClick={() => setSelected(item)}>
                    <td className="px-6 py-4 max-w-xs">
                      <p className="font-medium text-slate-900 line-clamp-1">{item.question}</p>
                      <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{item.answer}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-400 font-medium hidden md:table-cell">
                      {new Date(item.timestamp).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-6 py-4 hidden lg:table-cell">
                      <span className="badge"><Cpu className="w-3 h-3" /> {item.model || '—'}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={e => { e.stopPropagation(); setSelected(item) }}
                          className="p-2 text-slate-400 hover:text-medical-600 hover:bg-slate-100 rounded-lg transition-colors" title="Voir">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button onClick={e => { e.stopPropagation(); handleDelete(item.id) }}
                          className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Supprimer">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
