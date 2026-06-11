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

// Modality pill colors
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
      <label className="block text-xs font-bold text-[#6b5d4f] uppercase tracking-widest mb-1.5">
        {label}
      </label>
      <div className="relative">
        <select
          value={value}
          onChange={e => onChange(e.target.value)}
          className="w-full appearance-none bg-white border border-[#e7ddcf] rounded-xl px-3 py-2.5 text-sm text-[#2b2520] font-medium focus:outline-none focus:border-[#9a7f9b] focus:ring-2 focus:ring-[#9a7f9b]/20 transition-all"
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
      <label className="block text-xs font-bold text-[#6b5d4f] uppercase tracking-widest mb-1.5">
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
              className="px-2.5 py-1 rounded-lg text-xs font-semibold transition-all border"
              style={{
                background: active ? '#f4ece0' : '#faf6ef',
                borderColor: active ? '#9a7f9b' : '#e7ddcf',
                color: active ? '#7a5230' : '#8a7c6c',
                boxShadow: active ? '0 0 0 2px rgba(192,132,252,0.20)' : 'none',
              }}
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
      <label className="block text-xs font-bold text-[#6b5d4f] uppercase tracking-widest mb-1.5">
        Comorbidités
      </label>
      <div
        className="min-h-[42px] flex flex-wrap gap-1.5 items-center bg-white border border-[#e7ddcf] rounded-xl px-3 py-2 focus-within:border-[#9a7f9b] focus-within:ring-2 focus-within:ring-[#9a7f9b]/20 transition-all"
      >
        {tags.map(t => (
          <span
            key={t}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold"
            style={{ background: '#f4ece0', color: '#6b5d4f', border: '1px solid #e7ddcf' }}
          >
            {t}
            <button type="button" onClick={() => remove(t)} className="text-slate-400 hover:text-red-400 transition-colors ml-0.5">×</button>
          </span>
        ))}
        <input
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={addTag}
          placeholder={tags.length === 0 ? 'Tapez et appuyez Entrée (ex: diabète, IRC)' : ''}
          className="flex-1 min-w-[120px] text-sm text-[#2b2520] bg-transparent focus:outline-none placeholder:text-slate-300"
        />
      </div>
      <p className="text-[10px] text-slate-400 mt-1">Entrée ou virgule pour ajouter</p>
    </div>
  )
}

function ModalityPill({ label }) {
  const c = MODALITY_COLORS[label] || { bg: '#f4ece0', border: '#e7ddcf', text: '#6b5d4f' }
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
            <div
              key={i}
              className="rounded-xl border overflow-hidden"
              style={{ borderColor: '#e7ddcf' }}
            >
              <div
                className="px-4 py-2.5 flex items-center gap-2 font-bold text-sm"
                style={{ background: 'linear-gradient(135deg, #f4ece0 0%, #f0e6d6 100%)', color: '#5a3219' }}
              >
                <span
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-black text-white"
                  style={{ background: '#7a5230' }}
                >
                  {i + 1}
                </span>
                {heading}
              </div>
              {body && (
                <div className="px-4 py-3 text-sm text-[#4a4036] leading-relaxed whitespace-pre-wrap bg-white">
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
    <pre className="text-sm text-[#4a4036] leading-relaxed whitespace-pre-wrap font-sans">
      {text}
    </pre>
  )
}

function SourcesAccordion({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources?.length) return null

  return (
    <div className="rounded-xl border overflow-hidden" style={{ borderColor: '#e7ddcf' }}>
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold text-[#6b5d4f] hover:bg-slate-50 transition-colors"
        style={{ background: '#faf6ef' }}
      >
        <span className="flex items-center gap-2">
          <BookOpen style={{ width: 14, height: 14, color: '#a89a88' }} />
          {sources.length} source{sources.length > 1 ? 's' : ''} consultée{sources.length > 1 ? 's' : ''}
        </span>
        <ChevronDown
          style={{
            width: 14, height: 14, color: '#a89a88',
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s',
          }}
        />
      </button>
      {open && (
        <div className="divide-y divide-[#f4ece0]">
          {sources.map((s, i) => (
            <div key={i} className="px-4 py-2.5 bg-white">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-[#2b2520] truncate">{s.titre || s.id}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {s.type_cancer && <span className="mr-2">{s.type_cancer}</span>}
                    {s.categorie && <span className="mr-2">{s.categorie}</span>}
                    {s.reference && <span className="italic">{s.reference}</span>}
                  </p>
                </div>
                <span
                  className="flex-shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full"
                  style={{ background: '#f4ece0', color: '#a89a88' }}
                >
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
    <div className="flex flex-col h-full overflow-hidden" style={{ background: '#f7f1e8' }}>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div
        className="flex items-center gap-4 px-6 py-3.5 flex-shrink-0 bg-white"
        style={{ borderBottom: '1px solid #ece3d6', boxShadow: '0 1px 6px rgba(0,0,0,0.05)' }}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{
            background: 'linear-gradient(135deg, #7a5230 0%, #9a7f9b 100%)',
            boxShadow: '0 4px 14px rgba(124,58,237,0.30)',
          }}
        >
          <FlaskConical style={{ width: 18, height: 18, color: 'white' }} />
        </div>
        <div>
          <h2 className="font-bold text-[15px] text-[#2b2520] tracking-tight" style={{ fontFamily: 'Playfair Display, system-ui, sans-serif' }}>
            Traitement Hybride
          </h2>
          <p className="text-xs text-[#a89a88] mt-0.5">
            Analyse multi-modale · Guide AMFROM 2024
          </p>
        </div>
      </div>

      {/* ── Content ─────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

          {/* ── Form card ─────────────────────────────────────────────── */}
          <div
            className="bg-white rounded-2xl p-5 space-y-4"
            style={{ border: '1px solid #ece3d6', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}
          >
            <div>
              <h3 className="font-bold text-sm text-[#2b2520]">Profil patient</h3>
              <p className="text-xs text-[#a89a88] mt-0.5">
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
                <label className="block text-xs font-bold text-[#6b5d4f] uppercase tracking-widest mb-1.5">
                  Modèle LLM
                </label>
                <div className="flex gap-2">
                  {MODELS.map(m => (
                    <button
                      key={m.value}
                      type="button"
                      onClick={() => setModelName(m.value)}
                      className="flex-1 px-3 py-2 rounded-xl border text-left transition-all"
                      style={{
                        borderColor: modelName === m.value ? '#9a7f9b' : '#e7ddcf',
                        background:  modelName === m.value ? '#f4ece0' : 'white',
                        boxShadow:   modelName === m.value ? '0 0 0 2px rgba(192,132,252,0.20)' : 'none',
                      }}
                    >
                      <p className="text-xs font-bold" style={{ color: modelName === m.value ? '#7a5230' : '#2b2520' }}>
                        {m.label}
                      </p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{m.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={!cancerType || loading}
                className="w-full py-3 rounded-xl font-bold text-sm text-white transition-all disabled:opacity-40"
                style={{
                  background: 'linear-gradient(135deg, #7a5230 0%, #9a7f9b 100%)',
                  boxShadow: '0 4px 16px rgba(124,58,237,0.35)',
                }}
                onMouseEnter={e => { if (!e.currentTarget.disabled) e.currentTarget.style.transform = 'translateY(-1px)' }}
                onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)' }}
              >
                {loading
                  ? <span className="flex items-center justify-center gap-2"><Loader2 style={{ width: 14, height: 14 }} className="animate-spin" /> Analyse en cours…</span>
                  : 'Analyser le traitement hybride'
                }
              </button>
            </form>
          </div>

          {/* ── Results panel ─────────────────────────────────────────── */}
          <div className="space-y-4">

            {/* Loading */}
            {loading && (
              <div
                className="bg-white rounded-2xl p-8 flex flex-col items-center justify-center gap-4 text-center"
                style={{ border: '1px solid #ece3d6', minHeight: 200 }}
              >
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, #f4ece0, #f0e6d6)' }}
                >
                  <FlaskConical style={{ width: 24, height: 24, color: '#7a5230' }} className="animate-pulse" />
                </div>
                <div>
                  <p className="font-bold text-sm text-[#2b2520]">Analyse multi-modale en cours</p>
                  <p className="text-xs text-slate-400 mt-1">Récupération des protocoles par modalité…</p>
                </div>
              </div>
            )}

            {/* Error */}
            {error && !loading && (
              <div
                className="bg-white rounded-2xl p-4 flex items-start gap-3"
                style={{ border: '1px solid #FECACA' }}
              >
                <AlertCircle style={{ width: 16, height: 16, color: '#EF4444', flexShrink: 0, marginTop: 1 }} />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Result */}
            {result && !loading && (
              <>
                {/* Modalities found */}
                {result.modalities_found?.length > 0 && (
                  <div
                    className="bg-white rounded-2xl p-4"
                    style={{ border: '1px solid #ece3d6', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle2 style={{ width: 14, height: 14, color: '#10B981' }} />
                      <span className="text-xs font-bold text-[#2b2520] uppercase tracking-wider">
                        Modalités identifiées
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {result.modalities_found.map(m => <ModalityPill key={m} label={m} />)}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-2.5 flex items-center gap-1">
                      Modèle : <strong className="text-slate-500">{result.model}</strong>
                      &nbsp;·&nbsp; Latence : <strong className="text-slate-500">{result.latency}s</strong>
                    </p>
                  </div>
                )}

                {/* Plan */}
                {result.plan && (
                  <div
                    className="bg-white rounded-2xl p-5"
                    style={{ border: '1px solid #ece3d6', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}
                  >
                    <h3 className="font-bold text-sm text-[#2b2520] mb-4 flex items-center gap-2">
                      <FlaskConical style={{ width: 14, height: 14, color: '#7a5230' }} />
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
              <div
                className="bg-white rounded-2xl p-8 flex flex-col items-center justify-center gap-3 text-center"
                style={{ border: '1px solid #ece3d6', minHeight: 200 }}
              >
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center"
                  style={{ background: '#f4ece0' }}
                >
                  <FlaskConical style={{ width: 20, height: 20, color: '#9a7f9b' }} />
                </div>
                <p className="text-sm font-semibold text-[#6b5d4f]">Renseignez le profil patient</p>
                <p className="text-xs text-slate-400 max-w-xs">
                  Le système va interroger la base pour chaque modalité thérapeutique et synthétiser un plan hybride.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
