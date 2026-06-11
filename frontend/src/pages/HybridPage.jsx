import { useState } from 'react'
import { FlaskConical, ChevronDown, Loader2, AlertCircle, CheckCircle2, BookOpen } from 'lucide-react'
import { postHybridTreatment } from '../api/client'

// ── Static data ──────────────────────────────────────────────────────────────

const CANCER_TYPES = [
  'sein', 'poumon', 'colorectal', 'prostate', 'col utérin', 'ovaire',
  'endomètre', 'lymphome', 'leucémie', 'thyroïde', 'mélanome',
  'estomac', 'foie', 'pancréas', 'rein', 'vessie', 'larynx', 'nasopharynx',
]

const STAGES = [
  'Stade I', 'Stade II', 'Stade III', 'Stade IV',
  'Localisé', 'Localement avancé', 'Métastatique',
]

const MARKERS = [
  'HER2+', 'HER2-', 'ER+', 'ER-', 'PR+', 'PR-',
  'Triple négatif', 'BRCA1', 'BRCA2',
  'PD-L1+', 'ALK+', 'EGFR muté', 'RAS muté', 'Ki-67 élevé',
]

const MODELS = [
  { value: 'model_b', label: 'Qwen2.5-1.5B', desc: 'Recommandé · meilleur raisonnement' },
  { value: 'model_c', label: 'TinyLlama-1.1B', desc: 'Léger · rapide' },
]

// Modality pill colors — kept semantic (each modality has its own meaning)
const MODALITY_COLORS = {
  'chimiothérapie':  { bg: '#FEF3C7', border: '#FDE68A', text: '#92400E' },
  'radiothérapie':   { bg: '#f0e0cc', border: '#e3cdb4', text: '#6f3e20' },
  'hormonothérapie': { bg: '#FCE7F3', border: '#FBCFE8', text: '#9D174D' },
  'immunothérapie':  { bg: '#D1FAE5', border: '#A7F3D0', text: '#065F46' },
  'chirurgie':       { bg: '#f0e6d6', border: '#e3cdb4', text: '#5a3219' },
}

// ── Sub-components ────────────────────────────────────────────────────────────

function SelectField({ label, value, onChange, options, placeholder }) {
  return (
    <div>
      <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">
        {label}
      </label>
      <div className="relative">
        <select
          value={value}
          onChange={e => onChange(e.target.value)}
          className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-900 font-medium focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 transition-colors"
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map(o => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400" style={{ width: 14, height: 14 }} />
      </div>
    </div>
  )
}

function MarkerCheckboxes({ selected, onChange }) {
  const toggle = (m) =>
    onChange(selected.includes(m) ? selected.filter(x => x !== m) : [...selected, m])

  return (
    <div>
      <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">
        Marqueurs moléculaires
      </label>
      <div className="flex flex-wrap gap-1.5">
        {MARKERS.map(m => {
          const active = selected.includes(m)
          return (
            <button
              key={m}
              type="button"
              onClick={() => toggle(m)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors ${
                active
                  ? 'bg-medical-50 border-medical-400 text-medical-700 ring-2 ring-medical-500/20'
                  : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-medical-300 hover:text-medical-600'
              }`}
            >
              {m}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function ComorbiditiesInput({ tags, onChange }) {
  const [draft, setDraft] = useState('')

  function addTag(e) {
    if ((e.key === 'Enter' || e.key === ',') && draft.trim()) {
      e.preventDefault()
      const val = draft.trim().replace(/,$/, '')
      if (val && !tags.includes(val)) onChange([...tags, val])
      setDraft('')
    }
  }

  function remove(t) { onChange(tags.filter(x => x !== t)) }

  return (
    <div>
      <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">
        Comorbidités
      </label>
      <div className="min-h-[42px] flex flex-wrap gap-1.5 items-center bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:border-medical-500 focus-within:ring-2 focus-within:ring-medical-500/20 transition-colors">
        {tags.map(t => (
          <span
            key={t}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-medical-50 text-medical-700 border border-medical-200"
          >
            {t}
            <button type="button" onClick={() => remove(t)} className="text-slate-400 hover:text-red-500 transition-colors ml-0.5">×</button>
          </span>
        ))}
        <input
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={addTag}
          placeholder={tags.length === 0 ? 'Tapez et appuyez Entrée (ex: diabète, IRC)' : ''}
          className="flex-1 min-w-[120px] text-sm text-slate-900 bg-transparent focus:outline-none placeholder:text-slate-300"
        />
      </div>
      <p className="text-[10px] text-slate-400 mt-1">Entrée ou virgule pour ajouter</p>
    </div>
  )
}

function ModalityPill({ label }) {
  const c = MODALITY_COLORS[label] || { bg: '#f1f5f9', border: '#e2e8f0', text: '#64748b' }
  return (
    <span
      className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border"
      style={{ background: c.bg, borderColor: c.border, color: c.text }}
    >
      {label}
    </span>
  )
}

function PlanRenderer({ text }) {
  if (!text) return null

  // Try to split by "Phase N" headings for structured rendering
  const phaseRegex = /(?=Phase\s+\d+)/i
  const parts = text.split(phaseRegex).filter(Boolean)

  if (parts.length > 1) {
    return (
      <div className="space-y-4">
        {parts.map((part, i) => {
          const lines = part.trim().split('\n').filter(Boolean)
          const heading = lines[0]
          const body = lines.slice(1).join('\n')
          return (
            <div key={i} className="rounded-xl border border-slate-200 overflow-hidden">
              <div className="px-4 py-2.5 flex items-center gap-2 font-bold text-sm bg-medical-50 text-medical-800">
                <span className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-black text-white bg-medical-600">
                  {i + 1}
                </span>
                {heading}
              </div>
              {body && (
                <div className="px-4 py-3 text-sm text-slate-600 leading-relaxed whitespace-pre-wrap bg-white">
                  {body}
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  // Fallback: plain pre-formatted text
  return (
    <pre className="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap font-sans">
      {text}
    </pre>
  )
}

function SourcesAccordion({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources?.length) return null

  return (
    <div className="rounded-xl border border-slate-200 overflow-hidden">
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold text-slate-600 bg-slate-50 hover:bg-slate-100 transition-colors"
      >
        <span className="flex items-center gap-2">
          <BookOpen className="w-3.5 h-3.5 text-slate-400" />
          {sources.length} source{sources.length > 1 ? 's' : ''} consultée{sources.length > 1 ? 's' : ''}
        </span>
        <ChevronDown
          className="w-3.5 h-3.5 text-slate-400"
          style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
        />
      </button>
      {open && (
        <div className="divide-y divide-slate-100">
          {sources.map((s, i) => (
            <div key={i} className="px-4 py-2.5 bg-white">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-900 truncate">{s.titre || s.id}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {s.type_cancer && <span className="mr-2">{s.type_cancer}</span>}
                    {s.categorie && <span className="mr-2">{s.categorie}</span>}
                    {s.reference && <span className="italic">{s.reference}</span>}
                  </p>
                </div>
                <span className="flex-shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
                  {(s.score_final * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function HybridPage() {
  const [cancerType,    setCancerType]    = useState('')
  const [stage,         setStage]         = useState('')
  const [markers,       setMarkers]       = useState([])
  const [comorbidities, setComorbidities] = useState([])
  const [modelName,     setModelName]     = useState('model_b')
  const [loading,       setLoading]       = useState(false)
  const [result,        setResult]        = useState(null)
  const [error,         setError]         = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!cancerType) return
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const data = await postHybridTreatment({
        cancer_type:    cancerType,
        stage:          stage,
        markers:        markers,
        comorbidities:  comorbidities,
        model_name:     modelName,
      })
      setResult(data)
    } catch (err) {
      setError(err.message || "Erreur lors de l'analyse hybride.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto space-y-8">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <FlaskConical className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 tracking-tight font-display">
            Traitement hybride
          </h2>
          <p className="text-slate-400 mt-0.5 text-sm">
            Analyse multi-modale · Guide AMFROM 2024
          </p>
        </div>
      </div>

      {/* ── Content ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

        {/* ── Form card ─────────────────────────────────────────────── */}
        <div className="glass-card p-5 space-y-4">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Profil patient</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Renseignez le profil clinique pour générer un plan thérapeutique multi-modal.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <SelectField
              label="Type de cancer *"
              value={cancerType}
              onChange={setCancerType}
              options={CANCER_TYPES}
              placeholder="Sélectionner…"
            />

            <SelectField
              label="Stade"
              value={stage}
              onChange={setStage}
              options={STAGES}
              placeholder="Non précisé"
            />

            <MarkerCheckboxes selected={markers} onChange={setMarkers} />

            <ComorbiditiesInput tags={comorbidities} onChange={setComorbidities} />

            {/* Model selector */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">
                Modèle LLM
              </label>
              <div className="flex gap-2">
                {MODELS.map(m => {
                  const active = modelName === m.value
                  return (
                    <button
                      key={m.value}
                      type="button"
                      onClick={() => setModelName(m.value)}
                      className={`flex-1 px-3 py-2 rounded-xl border text-left transition-colors ${
                        active
                          ? 'border-medical-400 bg-medical-50 ring-2 ring-medical-500/20'
                          : 'border-slate-200 bg-white hover:border-medical-300'
                      }`}
                    >
                      <p className={`text-xs font-bold ${active ? 'text-medical-700' : 'text-slate-900'}`}>
                        {m.label}
                      </p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{m.desc}</p>
                    </button>
                  )
                })}
              </div>
            </div>

            <button
              type="submit"
              disabled={!cancerType || loading}
              className="btn-primary w-full justify-center disabled:opacity-50"
            >
              {loading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Analyse en cours…</>
                : 'Analyser le traitement hybride'
              }
            </button>
          </form>
        </div>

        {/* ── Results panel ─────────────────────────────────────────── */}
        <div className="space-y-4">

          {/* Loading */}
          {loading && (
            <div className="glass-card p-8 flex flex-col items-center justify-center gap-4 text-center" style={{ minHeight: 200 }}>
              <div className="w-14 h-14 rounded-2xl bg-medical-50 flex items-center justify-center">
                <FlaskConical className="w-6 h-6 text-medical-600 animate-pulse" />
              </div>
              <div>
                <p className="font-bold text-sm text-slate-900">Analyse multi-modale en cours</p>
                <p className="text-xs text-slate-400 mt-1">Récupération des protocoles par modalité…</p>
              </div>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="bg-white border border-red-100 rounded-2xl p-4 flex items-start gap-3 shadow-sm">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Result */}
          {result && !loading && (
            <>
              {/* Modalities found */}
              {result.modalities_found?.length > 0 && (
                <div className="glass-card p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Modalités identifiées
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.modalities_found.map(m => <ModalityPill key={m} label={m} />)}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-2.5">
                    Modèle : <strong className="text-slate-500">{result.model}</strong>
                    &nbsp;·&nbsp; Latence : <strong className="text-slate-500">{result.latency}s</strong>
                  </p>
                </div>
              )}

              {/* Plan */}
              {result.plan && (
                <div className="glass-card p-5">
                  <h3 className="font-bold text-sm text-slate-900 mb-4 flex items-center gap-2">
                    <FlaskConical className="w-3.5 h-3.5 text-medical-600" />
                    Plan thérapeutique hybride
                  </h3>
                  <PlanRenderer text={result.plan} />
                </div>
              )}

              {/* Sources */}
              <SourcesAccordion sources={result.sources} />
            </>
          )}

          {/* Empty state */}
          {!loading && !result && !error && (
            <div className="glass-card p-8 flex flex-col items-center justify-center gap-3 text-center" style={{ minHeight: 200 }}>
              <div className="w-12 h-12 rounded-2xl bg-slate-50 flex items-center justify-center">
                <FlaskConical className="w-5 h-5 text-slate-300" />
              </div>
              <p className="text-sm font-semibold text-slate-500">Renseignez le profil patient</p>
              <p className="text-xs text-slate-400 max-w-xs">
                Le système va interroger la base pour chaque modalité thérapeutique et synthétiser un plan hybride.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
