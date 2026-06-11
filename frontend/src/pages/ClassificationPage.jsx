import { useState } from 'react'
import {
  Microscope, Send, Loader2, AlertTriangle, Sparkles,
  Target, Cpu, ScanSearch,
} from 'lucide-react'
import { postClassifyCancer } from '../api/client'

// ── Display metadata ──────────────────────────────────────────────────────────
const CANCER_META = {
  sein:       { label: 'Cancer du sein',        color: '#EC4899', emoji: '🎗️' },
  poumon:     { label: 'Cancer du poumon',      color: '#3B82F6', emoji: '🫁' },
  colorectal: { label: 'Cancer colorectal',     color: '#F59E0B', emoji: '🩺' },
  inconnu:    { label: 'Non déterminé',          color: '#94A3B8', emoji: '❔' },
}

const METHOD_LABEL = {
  keyword:  'Mots-clés (FR/AR/EN)',
  sbert:    'Similarité sémantique SBERT',
  fallback: 'Aucune correspondance',
}

const EXAMPLES = [
  'Quel est le protocole AC pour le cancer du sein HER2+ ?',
  'Patient de 55 ans, CBNPC stade IIIA, quelle prise en charge ?',
  'Protocole FOLFOX après résection colique stade III',
  'Tumeur mammaire chez une femme de 50 ans',
  'ما هو علاج سرطان الرئة ؟',
]

export default function ClassificationPage() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading]   = useState(false)
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState(null)

  async function handleSubmit(e) {
    e?.preventDefault()
    const q = question.trim()
    if (!q || loading) return
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await postClassifyCancer({ question: q })
      setResult(res)
    } catch (err) {
      setError(err.message || 'La classification a échoué.')
    } finally {
      setLoading(false)
    }
  }

  const meta = result ? (CANCER_META[result.cancer] ?? CANCER_META.inconnu) : null

  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <Microscope className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 tracking-tight font-display">
            Classification des cancers
          </h2>
          <p className="text-slate-400 mt-0.5 text-sm">
            Détection du type de cancer — classifieur hybride mots-clés + SBERT
          </p>
        </div>
      </div>

      {/* Query card */}
      <div className="glass-card overflow-hidden max-w-3xl">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-medical-50 flex items-center justify-center">
            <ScanSearch className="w-3.5 h-3.5 text-medical-600" />
          </div>
          <h3 className="font-semibold text-slate-900 text-sm">Question clinique</h3>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Ex : Quel est le traitement du cancer du sein HER2+ ?"
              disabled={loading}
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 font-medium focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 disabled:opacity-60 transition-colors"
            />
            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="btn-primary px-5 disabled:opacity-60"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              {loading ? 'Analyse…' : 'Classifier'}
            </button>
          </div>

          {/* Example chips */}
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                type="button"
                onClick={() => setQuestion(ex)}
                disabled={loading}
                className="text-xs px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 hover:border-medical-300 hover:text-medical-600 transition-colors disabled:opacity-50"
              >
                {ex.length > 48 ? ex.slice(0, 48) + '…' : ex}
              </button>
            ))}
          </div>

          {error && (
            <div className="flex items-start gap-2 text-sm text-red-600">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" /> {error}
            </div>
          )}
        </form>
      </div>

      {/* Result */}
      {result && !loading && meta && (
        <div className="max-w-3xl space-y-5 animate-fade-in">
          {/* Main verdict */}
          <div
            className="bg-white border rounded-2xl p-6 shadow-sm flex items-center gap-5"
            style={{ borderColor: meta.color + '40' }}
          >
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0"
              style={{ background: meta.color + '14' }}
            >
              {meta.emoji}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">
                Type de cancer détecté
              </p>
              <h3 className="text-2xl font-bold tracking-tight" style={{ color: meta.color }}>
                {meta.label}
              </h3>
              <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <Cpu className="w-3.5 h-3.5" /> {METHOD_LABEL[result.method] ?? result.method}
                </span>
              </div>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Confiance</p>
              <p className="text-3xl font-bold tabular-nums" style={{ color: meta.color }}>
                {Math.round(result.confidence * 100)}%
              </p>
            </div>
          </div>

          {/* SBERT per-class scores (only present when method === sbert) */}
          {result.scores && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-4 h-4 text-medical-600" />
                <span className="text-sm font-semibold text-slate-900">
                  Scores de similarité sémantique par classe
                </span>
              </div>
              <div className="space-y-3">
                {Object.entries(result.scores)
                  .sort((a, b) => b[1] - a[1])
                  .map(([cls, score]) => {
                    const m = CANCER_META[cls] ?? CANCER_META.inconnu
                    return (
                      <div key={cls}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-semibold text-slate-600">{m.label}</span>
                          <span className="text-xs font-bold text-slate-700 tabular-nums">
                            {Math.round(score * 100)}%
                          </span>
                        </div>
                        <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.max(0, score * 100)}%`, background: m.color }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </div>
            </div>
          )}

          <p className="text-[11px] text-slate-400 px-1 flex items-center gap-1.5">
            <Sparkles className="w-3 h-3" />
            Le classifieur priorise les mots-clés multilingues, puis bascule sur la
            similarité SBERT pour les paraphrases. Couvre sein · poumon · colorectal.
          </p>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="glass-card p-16 text-center max-w-3xl">
          <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center mx-auto mb-3">
            <Microscope className="w-5 h-5 text-slate-300" />
          </div>
          <p className="text-sm font-medium text-slate-500">
            Saisissez une question clinique pour détecter le type de cancer
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Classifieur hybride — mots-clés FR/AR/EN + repli sémantique SBERT
          </p>
        </div>
      )}
    </div>
  )
}
