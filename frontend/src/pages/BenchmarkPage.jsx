import { useState } from 'react'
import {
  GitCompare, Cpu, Clock, ChevronDown, ChevronUp, Loader2,
  AlertTriangle, Sparkles, Send, FileText, Trophy, Database
} from 'lucide-react'
import { compareModels } from '../api/client'

const MODEL_INFO = {
  model_a: { name: 'flan-t5-base',   desc: 'Seq2Seq · 250M' },
  model_b: { name: 'Qwen2.5-1.5B',   desc: 'Instruct · 1.5B' },
  model_c: { name: 'TinyLlama-1.1B', desc: 'Causal · 1.1B' },
}

const pct = v => (v == null ? null : v > 1 ? v : v * 100)

const STRATEGIES = [
  { value: 'zero_shot',        label: 'Zero-shot' },
  { value: 'few_shot',         label: 'Few-shot' },
  { value: 'chain_of_thought', label: 'Chain of Thought' },
]

export default function BenchmarkPage() {
  const [cQuestion,  setCQuestion]  = useState('')
  const [cReference, setCReference] = useState('')
  const [strategy,   setStrategy]   = useState('zero_shot')
  const [showRef,    setShowRef]    = useState(false)
  const [comparing,  setComparing]  = useState(false)
  const [cResult,    setCResult]    = useState(null)
  const [cError,     setCError]     = useState(null)

  async function handleCompare(e) {
    e?.preventDefault()
    const q = cQuestion.trim()
    if (!q || comparing) return
    setComparing(true); setCError(null); setCResult(null)
    try {
      const res = await compareModels({ question: q, reference: cReference.trim() || null, template: strategy })
      setCResult(res)
    } catch (err) {
      setCError(err.message || 'La comparaison a échoué.')
    } finally {
      setComparing(false)
    }
  }

  // Best model = highest BERTScore (if reference) else highest Faithfulness.
  let bestModel = null
  if (cResult?.models?.length) {
    const scoreOf = m => (cResult.has_reference && m.bertscore != null) ? m.bertscore : (m.faithfulness ?? -1)
    bestModel = cResult.models.reduce((b, m) => (scoreOf(m) > scoreOf(b) ? m : b), cResult.models[0])?.model
  }

  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <GitCompare className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 tracking-tight font-display">Benchmark LLM</h2>
          <p className="text-slate-400 mt-0.5 text-sm">Comparaison des 3 modèles sur une même question</p>
        </div>
      </div>

      {/* Query card */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-medical-50 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-medical-600" />
          </div>
          <h3 className="font-semibold text-slate-900 text-sm">Comparaison interactive</h3>
        </div>

        <form onSubmit={handleCompare} className="p-6 space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={cQuestion}
              onChange={e => setCQuestion(e.target.value)}
              placeholder="Ex : Quel est le traitement standard du cancer de l'ovaire avancé ?"
              disabled={comparing}
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 font-medium focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 disabled:opacity-60 transition-colors"
            />
            <button type="submit" disabled={!cQuestion.trim() || comparing} className="btn-primary px-5 disabled:opacity-60">
              {comparing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              {comparing ? 'En cours…' : 'Comparer'}
            </button>
          </div>

          {/* Controls row */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-3">
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-slate-500">Stratégie</label>
              <div className="relative">
                <select
                  value={strategy}
                  onChange={e => setStrategy(e.target.value)}
                  disabled={comparing}
                  className="appearance-none bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-1.5 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 cursor-pointer disabled:opacity-60"
                >
                  {STRATEGIES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
                <ChevronDown className="w-3.5 h-3.5 absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
              <span className="text-[11px] text-slate-400 hidden sm:inline">appliquée à Qwen uniquement</span>
            </div>

            <button
              type="button"
              onClick={() => setShowRef(v => !v)}
              className="text-xs font-semibold text-slate-500 hover:text-medical-600 flex items-center gap-1 transition-colors"
            >
              {showRef ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              Réponse de référence
              <span className="text-slate-400 font-normal">— active BLEU / ROUGE / BERT</span>
            </button>
          </div>

          {showRef && (
            <textarea
              value={cReference}
              onChange={e => setCReference(e.target.value)}
              placeholder="Saisissez la réponse correcte attendue pour calculer les métriques basées sur une référence."
              disabled={comparing}
              rows={3}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 disabled:opacity-60 resize-y transition-colors"
            />
          )}
        </form>

        {comparing && (
          <div className="px-6 pb-6 flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            Les 3 modèles génèrent leur réponse sur CPU — cela peut prendre quelques minutes…
          </div>
        )}

        {cError && (
          <div className="px-6 pb-6 flex items-start gap-2 text-sm text-red-600">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" /> {cError}
          </div>
        )}
      </div>

      {/* Results */}
      {cResult && !comparing && (
        <div className="space-y-5 animate-fade-in">
          {/* Context relevance — retrieval quality, shared by all 3 models */}
          {cResult.context_relevance != null && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-2.5">
                <div className="w-8 h-8 rounded-lg bg-medical-50 flex items-center justify-center flex-shrink-0">
                  <Database className="w-4 h-4 text-medical-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-900">Pertinence du contexte</p>
                  <p className="text-[11px] text-slate-400">Qualité du retrieval — commune aux 3 modèles</p>
                </div>
                <span className="text-lg font-bold text-slate-800 tabular-nums flex-shrink-0">
                  {Math.round(pct(cResult.context_relevance))}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full bg-medical-500 rounded-full transition-all duration-500"
                  style={{ width: `${pct(cResult.context_relevance)}%` }} />
              </div>
            </div>
          )}

          <div className="grid lg:grid-cols-3 gap-5">
            {cResult.models.map(m => {
              const info = MODEL_INFO[m.model] ?? { name: m.model, desc: '' }
              const isBest = m.model === bestModel && !m.error
              return (
                <div key={m.model}
                  className={`relative bg-white rounded-2xl p-5 flex flex-col transition-all
                    ${isBest ? 'border border-medical-300 ring-1 ring-medical-200 shadow-md'
                             : 'border border-slate-200 shadow-sm'}`}>
                  {isBest && (
                    <span className="absolute -top-2.5 left-5 inline-flex items-center gap-1 bg-medical-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
                      <Trophy className="w-2.5 h-2.5" /> Meilleur score
                    </span>
                  )}

                  {/* Card header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2.5">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
                        ${isBest ? 'bg-medical-50' : 'bg-slate-100'}`}>
                        <Cpu className={`w-4 h-4 ${isBest ? 'text-medical-600' : 'text-slate-500'}`} />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900 leading-tight">{info.name}</p>
                        <p className="text-[10px] text-slate-400">{info.desc}</p>
                      </div>
                    </div>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1 flex-shrink-0 mt-1">
                      <Clock className="w-3 h-3" /> {m.latency}s
                    </span>
                  </div>

                  {/* Answer */}
                  <p className="text-sm text-slate-600 leading-relaxed flex-1 whitespace-pre-wrap mb-4">
                    {m.error ? <span className="text-red-500 italic">{m.error}</span> : m.response}
                  </p>

                  {/* Metrics */}
                  {(m.faithfulness != null || m.relevance != null) && (
                    <div className="space-y-2.5 pt-4 border-t border-slate-100">
                      <MetricBar label="Fidélité"   val={pct(m.faithfulness)} accent />
                      <MetricBar label="Pertinence" val={pct(m.relevance)}    accent />
                      {cResult.has_reference && m.bleu != null && (
                        <>
                          <MetricBar label="BLEU"      val={pct(m.bleu)} />
                          <MetricBar label="ROUGE-L"   val={pct(m.rouge_l)} />
                          <MetricBar label="BERTScore" val={pct(m.bertscore)} />
                        </>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Metric legend */}
          <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-[11px] text-slate-400 px-1">
            <span><b className="text-slate-600 font-semibold">Fidélité</b> · réponse ancrée dans le contexte récupéré</span>
            <span><b className="text-slate-600 font-semibold">Pertinence</b> · réponse en lien avec la question</span>
            {cResult.has_reference && (
              <span><b className="text-slate-600 font-semibold">BLEU / ROUGE / BERT</b> · similarité avec la référence</span>
            )}
          </div>

          {/* Sources */}
          {cResult.sources?.length > 0 && (
            <div className="glass-card overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-100 flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-xs font-semibold text-slate-600">{cResult.sources.length} sources récupérées</span>
              </div>
              <div className="p-4 flex flex-wrap gap-2">
                {cResult.sources.map((s, i) => (
                  <span key={i} className="inline-flex items-center gap-1.5 text-[11px] bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-slate-600">
                    <span className="w-4 h-4 rounded bg-slate-200 text-slate-500 text-[9px] font-bold flex items-center justify-center">{i + 1}</span>
                    {s.titre || s.id}
                    <span className="text-slate-400 font-semibold">{(s.score_final * 100).toFixed(0)}%</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!cResult && !comparing && !cError && (
        <div className="glass-card p-16 text-center">
          <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center mx-auto mb-3">
            <GitCompare className="w-5 h-5 text-slate-300" />
          </div>
          <p className="text-sm font-medium text-slate-500">Posez une question pour comparer les 3 modèles</p>
          <p className="text-xs text-slate-400 mt-1">Fidélité et Pertinence sont calculées automatiquement ; ajoutez une réponse de référence pour BLEU / ROUGE / BERT.</p>
        </div>
      )}
    </div>
  )
}

function MetricBar({ label, val, accent = false }) {
  const v = val == null ? null : Math.round(val)
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        <span className="text-xs font-bold text-slate-700 tabular-nums">{v == null ? '—' : `${v}%`}</span>
      </div>
      <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${accent ? 'bg-medical-500' : 'bg-slate-300'}`}
          style={{ width: `${v ?? 0}%` }}
        />
      </div>
    </div>
  )
}
