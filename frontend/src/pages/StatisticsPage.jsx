import { useState, useEffect } from 'react'
import {
  BarChart3, Database, Tag, FileText, Layers,
  MessageSquare, Cpu, FileUp
} from 'lucide-react'
import { getStatistics } from '../api/client'

// ── Color palettes ─────────────────────────────────────────────────────────
const CANCER_COLORS = [
  '#1966f2', '#0ea5e9', '#8b5cf6', '#10b981',
  '#f59e0b', '#ef4444', '#6366f1', '#14b8a6',
]
const CATEGORY_COLORS = [
  '#1966f2', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#0ea5e9',
]
const MODEL_COLORS = { model_a: '#1966f2', model_b: '#8b5cf6', model_c: '#10b981' }

const CANCER_LABEL = {
  sein: 'Sein', general: 'Général', poumon: 'Poumon', colorectal: 'Colorectal',
  ORL: 'ORL', col_uterin: 'Col utérin', cerebral: 'Cérébral', pancreas: 'Pancréas',
  ovaire: 'Ovaire', prostate: 'Prostate', melanome: 'Mélanome',
  sarcome_osseux: 'Sarcome osseux', thyroide: 'Thyroïde', estomac: 'Estomac',
  GIST: 'GIST', sein_col_uterin: 'Sein + Col utérin',
}
const CATEGORY_LABEL = {
  traitement: 'Traitement', diagnostic: 'Diagnostic', suivi: 'Suivi',
  epidemiologie: 'Épidémiologie', research: 'Recherche', depistage: 'Dépistage',
  resultat_depistage: 'Résultat dépistage', recommandation: 'Recommandation',
  infrastructure: 'Infrastructure',
}
const MODEL_LABEL = { model_a: 'Flan-T5', model_b: 'Qwen 2.5', model_c: 'TinyLlama' }

// ── SVG Donut chart ────────────────────────────────────────────────────────
function DonutChart({ data, size = 170, strokeWidth = 24, centerLabel, centerSub }) {
  const r   = (size - strokeWidth) / 2
  const cx  = size / 2
  const C   = 2 * Math.PI * r
  const total = data.reduce((s, d) => s + d.value, 0)

  let cumLen = 0
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <g transform={`rotate(-90 ${cx} ${cx})`}>
          {/* track */}
          <circle cx={cx} cy={cx} r={r} fill="none" stroke="#f1f5f9" strokeWidth={strokeWidth} />
          {data.map((seg, i) => {
            const len    = total ? (seg.value / total) * C : 0
            const offset = -cumLen
            cumLen += len
            return (
              <circle key={i}
                cx={cx} cy={cx} r={r} fill="none"
                stroke={seg.color}
                strokeWidth={strokeWidth}
                strokeDasharray={`${Math.max(0, len - 3)} ${C}`}
                strokeDashoffset={offset}
                strokeLinecap="butt"
              />
            )
          })}
        </g>
      </svg>
      {centerLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold text-slate-900 leading-none">{centerLabel}</span>
          {centerSub && <span className="text-[10px] text-slate-400 mt-1 font-medium">{centerSub}</span>}
        </div>
      )}
    </div>
  )
}

// ── SVG Ring (single segment progress) ────────────────────────────────────
function RingProgress({ pct, color, size = 110, strokeWidth = 12 }) {
  const r  = (size - strokeWidth) / 2
  const cx = size / 2
  const C  = 2 * Math.PI * r
  const drawn = (pct / 100) * C
  return (
    <svg width={size} height={size}>
      <g transform={`rotate(-90 ${cx} ${cx})`}>
        <circle cx={cx} cy={cx} r={r} fill="none" stroke="#f1f5f9" strokeWidth={strokeWidth} />
        <circle cx={cx} cy={cx} r={r} fill="none"
          stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={`${drawn} ${C}`}
          strokeLinecap="round"
        />
      </g>
    </svg>
  )
}

// ── KPI card ───────────────────────────────────────────────────────────────
function KpiCard({ icon: Icon, value, label, sub }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        <Icon className="w-4 h-4 text-slate-300" />
      </div>
      <div>
        <p className="text-3xl font-bold text-slate-900 tracking-tight leading-none">
          {typeof value === 'number' ? value.toLocaleString('fr-FR') : value}
        </p>
        <p className="text-xs text-slate-400 mt-1.5 leading-snug">{sub}</p>
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export default function StatisticsPage() {
  const [stats,   setStats]   = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStatistics().then(setStats).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-full text-slate-400">
      <BarChart3 className="w-6 h-6 animate-pulse mr-2" />
      <span className="text-sm font-medium">Chargement…</span>
    </div>
  )
  if (!stats) return (
    <div className="flex items-center justify-center h-full">
      <p className="text-sm text-slate-400">Impossible de charger les statistiques.</p>
    </div>
  )

  const {
    total_documents, total_cancer_types, unique_keywords, docs_with_protocol,
    uploaded_chunks, cancer_distribution, category_distribution, composition, usage,
  } = stats

  const topCancer = cancer_distribution[0]
  const topCategory = category_distribution[0]
  const totalQueries = usage?.total_queries ?? 0
  const modelsUsed   = usage?.models_used  ?? {}
  const totalModelQ  = Object.values(modelsUsed).reduce((s, v) => s + v, 0)

  // Donut data
  const cancerDonut = cancer_distribution.slice(0, 7).map((d, i) => ({
    label: CANCER_LABEL[d.type] ?? d.type,
    value: d.count,
    pct:   d.pct,
    color: CANCER_COLORS[i % CANCER_COLORS.length],
  }))
  const categoryDonut = category_distribution.slice(0, 6).map((d, i) => ({
    label: CATEGORY_LABEL[d.categorie] ?? d.categorie,
    value: d.count,
    pct:   d.pct,
    color: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
  }))

  // Richness cards
  const richness = [
    { label: 'Protocole de traitement', count: composition.has_protocol, color: '#1966f2',  ringColor: '#1966f2'  },
    { label: 'Effets secondaires',      count: composition.has_effects,  color: '#8b5cf6',  ringColor: '#8b5cf6'  },
    { label: 'Scénario patient',        count: composition.has_scenario, color: '#10b981',  ringColor: '#10b981'  },
  ]

  return (
    <div className="p-8 md:p-10 w-full h-full overflow-y-auto space-y-8">

      {/* ── Header ── */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <p className="text-xs font-bold text-medical-600 uppercase tracking-widest mb-1">AMFROM 2024</p>
          <h2 className="font-bold text-2xl text-slate-900 tracking-tight font-display">Tableau de bord</h2>
          <p className="text-slate-400 mt-1 text-sm">{total_documents} fiches médicales · {total_cancer_types} types de cancer couverts</p>
        </div>
      </div>

      {/* ── KPI row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <KpiCard icon={Database}      value={total_documents}   label="Fiches"      sub="base de connaissances" />
        <KpiCard icon={Layers}        value={total_cancer_types} label="Cancers"     sub="types de cancer couverts" />
        <KpiCard icon={FileText}      value={docs_with_protocol} label="Protocoles"  sub={`${Math.round(docs_with_protocol*100/total_documents)}% des fiches`} />
        <KpiCard icon={Tag}           value={unique_keywords}    label="Mots-clés"   sub="termes médicaux uniques" />
        <KpiCard icon={MessageSquare} value={totalQueries}       label="Questions"   sub="posées à l'assistant" />
      </div>

      {/* ── Charts row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Cancer donut */}
        <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
          <div className="mb-5">
            <h3 className="font-bold text-slate-900">Répartition par type de cancer</h3>
            <p className="text-xs text-slate-400 mt-0.5">{total_cancer_types} types · top {cancerDonut.length} représentés</p>
          </div>
          <div className="flex items-center gap-8">
            <DonutChart
              data={cancerDonut}
              size={170}
              strokeWidth={26}
              centerLabel={total_documents}
              centerSub="fiches"
            />
            <div className="flex-1 space-y-2.5 min-w-0">
              {cancerDonut.map((seg) => (
                <div key={seg.label} className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: seg.color }} />
                  <span className="text-xs text-slate-600 font-medium flex-1 truncate">{seg.label}</span>
                  <span className="text-xs font-bold text-slate-700">{seg.value}</span>
                  <span className="text-[10px] text-slate-400 w-8 text-right">{seg.pct}%</span>
                </div>
              ))}
              {cancer_distribution.length > 7 && (
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-sm bg-slate-200 flex-shrink-0" />
                  <span className="text-xs text-slate-400 flex-1">+{cancer_distribution.length - 7} autres</span>
                  <span className="text-xs font-bold text-slate-400">
                    {cancer_distribution.slice(7).reduce((s, d) => s + d.count, 0)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Category donut */}
        <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
          <div className="mb-5">
            <h3 className="font-bold text-slate-900">Répartition par catégorie</h3>
            <p className="text-xs text-slate-400 mt-0.5">{category_distribution.length} catégories médicales</p>
          </div>
          <div className="flex items-center gap-8">
            <DonutChart
              data={categoryDonut}
              size={170}
              strokeWidth={26}
              centerLabel={topCategory ? `${topCategory.pct}%` : ''}
              centerSub={topCategory ? (CATEGORY_LABEL[topCategory.categorie] ?? topCategory.categorie) : ''}
            />
            <div className="flex-1 space-y-2.5 min-w-0">
              {categoryDonut.map((seg) => (
                <div key={seg.label} className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: seg.color }} />
                  <span className="text-xs text-slate-600 font-medium flex-1 truncate">{seg.label}</span>
                  <span className="text-xs font-bold text-slate-700">{seg.value}</span>
                  <span className="text-[10px] text-slate-400 w-8 text-right">{seg.pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Richness + Usage row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Data richness */}
        <div className="lg:col-span-3 bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
          <div className="mb-6">
            <h3 className="font-bold text-slate-900">Richesse des fiches</h3>
            <p className="text-xs text-slate-400 mt-0.5">Pourcentage de fiches contenant chaque type d'information</p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {richness.map(({ label, count, color, ringColor }) => {
              const pct = Math.round(count * 100 / total_documents)
              return (
                <div key={label} className="flex flex-col items-center gap-3">
                  <div className="relative">
                    <RingProgress pct={pct} color={ringColor} size={110} strokeWidth={11} />
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-xl font-bold text-slate-900">{pct}%</span>
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-semibold text-slate-700 leading-tight">{label}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{count.toLocaleString('fr-FR')} fiches</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Usage */}
        <div className="lg:col-span-2 bg-white border border-slate-100 rounded-2xl p-6 shadow-sm flex flex-col gap-5">
          <div>
            <h3 className="font-bold text-slate-900">Utilisation</h3>
            <p className="text-xs text-slate-400 mt-0.5">Activité de l'assistant IA</p>
          </div>

          {/* Queries stat */}
          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
              <MessageSquare className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 leading-none">{totalQueries}</p>
              <p className="text-xs text-slate-500 mt-1">questions posées au total</p>
            </div>
          </div>

          {/* Model breakdown */}
          <div className="flex-1">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" /> Modèles les plus utilisés
            </p>
            {Object.keys(modelsUsed).length === 0 ? (
              <p className="text-xs text-slate-400">Aucune donnée disponible</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(modelsUsed).map(([model, count]) => {
                  const pct = Math.round(count * 100 / (totalModelQ || 1))
                  const color = MODEL_COLORS[model] ?? '#94a3b8'
                  return (
                    <div key={model}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-slate-700">
                          {MODEL_LABEL[model] ?? model}
                        </span>
                        <span className="text-xs text-slate-400">{count} ({pct}%)</span>
                      </div>
                      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${pct}%`, backgroundColor: color }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Uploaded chunks */}
          {(uploaded_chunks ?? 0) > 0 && (
            <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
              <FileUp className="w-4 h-4 text-slate-400 flex-shrink-0" />
              <p className="text-xs text-slate-600 font-medium">
                <span className="font-bold text-slate-800">{uploaded_chunks}</span> chunks importés manuellement
              </p>
            </div>
          )}
        </div>
      </div>


    </div>
  )
}
