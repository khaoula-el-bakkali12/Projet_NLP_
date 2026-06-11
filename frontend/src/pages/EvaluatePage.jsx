import { useState, useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { getBenchmarkResults } from '../api/client'
import { TrendingUp, Target, Award, BarChart3, AlertTriangle, Loader2 } from 'lucide-react'

const LINE_COLORS = {
  hit_rate:      '#a1683a',
  mrr:           '#10b981',
  precision_at_k: '#f59e0b',
}

const LINE_LABELS = {
  hit_rate:      'Hit Rate@5',
  mrr:           'MRR',
  precision_at_k: 'Precision@5',
}

function StatCard({ icon: Icon, label, value, sub, accent }) {
  return (
    <div
      className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-3"
      style={{ borderLeft: `3px solid ${accent}` }}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        <Icon className="w-4 h-4" style={{ color: accent }} />
      </div>
      <div>
        <p className="text-3xl font-bold text-slate-900 tracking-tight leading-none">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-1.5 leading-snug">{sub}</p>}
      </div>
    </div>
  )
}

function CustomTooltip({ active, payload, label, bestAlpha }) {
  if (!active || !payload?.length) return null
  const isBest = label === bestAlpha
  return (
    <div
      className="bg-white rounded-lg shadow-lg px-3.5 py-2.5"
      style={{ border: `1px solid ${isBest ? '#a1683a' : '#e2e8f0'}`, minWidth: 160 }}
    >
      <div
        className="text-xs font-semibold mb-2"
        style={{ color: isBest ? '#a1683a' : '#64748b' }}
      >
        α = {label}{isBest ? ' ★ optimal' : ''}
      </div>
      {payload.map(p => (
        <div key={p.dataKey} className="flex justify-between gap-4 mb-1 last:mb-0">
          <span className="text-xs" style={{ color: p.color }}>{LINE_LABELS[p.dataKey]}</span>
          <span className="text-xs font-semibold text-slate-700 tabular-nums">{(p.value * 100).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  )
}

function BestDot(props) {
  const { cx, cy, payload, bestAlpha, stroke } = props
  if (payload.alpha !== bestAlpha) return null
  return (
    <g>
      <circle cx={cx} cy={cy} r={6} fill={stroke} stroke="#fff" strokeWidth={2} />
      <circle cx={cx} cy={cy} r={10} fill="none" stroke={stroke} strokeWidth={1} opacity={0.4} />
    </g>
  )
}

export default function EvaluatePage() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    getBenchmarkResults()
      .then(setData)
      .catch(e => setError(e.response?.data?.detail || 'Impossible de charger les résultats d\'évaluation'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Centered><Loader2 className="w-5 h-5 animate-spin" /> Chargement des résultats d'évaluation…</Centered>
  if (error)   return <Centered error><AlertTriangle className="w-5 h-5" /> {error}</Centered>

  const sweep     = data.sweep_results ?? []
  const bestAlpha = data.best_alpha ?? 0.1
  const bestRow   = sweep.find(r => r.alpha === bestAlpha) ?? sweep[0] ?? {}
  const numQ      = data.num_test_questions ?? 17
  const topK      = data.top_k_evaluated ?? 5

  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto space-y-8">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <BarChart3 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 tracking-tight font-display">
            Évaluation du retrieval
          </h2>
          <p className="text-slate-400 mt-0.5 text-sm">
            Balayage alpha — pondération FAISS vs BM25 (α) sur {numQ} questions de test, retrieval top-{topK}
          </p>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard icon={Award}      label="Alpha optimal" value={`α = ${bestAlpha}`}                       sub="pondération FAISS optimale" accent="#a1683a" />
        <StatCard icon={Target}     label="Hit Rate@5"    value={`${(bestRow.hit_rate * 100).toFixed(0)}%`} sub="à l'alpha optimal"          accent="#10b981" />
        <StatCard icon={TrendingUp} label="MRR"           value={`${(bestRow.mrr * 100).toFixed(0)}%`}      sub="Mean Reciprocal Rank"       accent="#f59e0b" />
      </div>

      {/* Chart */}
      <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
        <div className="mb-5">
          <h3 className="font-bold text-slate-900">Scores des métriques selon alpha</h3>
          <p className="text-xs text-slate-400 mt-0.5">Plus le score est élevé, mieux c'est</p>
        </div>
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={sweep} margin={{ top: 4, right: 20, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="alpha"
              tickFormatter={v => v.toFixed(1)}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              label={{ value: 'Alpha (pondération FAISS)', position: 'insideBottomRight', offset: -4, fontSize: 11, fill: '#94a3b8' }}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={v => `${(v * 100).toFixed(0)}%`}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickLine={false}
              axisLine={false}
              width={44}
            />
            <Tooltip content={<CustomTooltip bestAlpha={bestAlpha} />} />
            <Legend
              formatter={key => (
                <span style={{ fontSize: 12, color: '#64748b' }}>{LINE_LABELS[key]}</span>
              )}
            />
            <ReferenceLine
              x={bestAlpha}
              stroke="#a1683a"
              strokeDasharray="4 4"
              strokeOpacity={0.5}
              label={{ value: `α=${bestAlpha}`, position: 'top', fontSize: 10, fill: '#a1683a' }}
            />
            {Object.entries(LINE_COLORS).map(([key, color]) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={color}
                strokeWidth={2}
                dot={<BestDot bestAlpha={bestAlpha} stroke={color} />}
                activeDot={{ r: 4, strokeWidth: 0 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Raw data table */}
      <div className="bg-white border border-slate-100 rounded-2xl shadow-sm overflow-hidden">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-100">
              {['Alpha', 'Hit Rate@5', 'MRR', 'Precision@5'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sweep.map(row => {
              const isBest = row.alpha === bestAlpha
              return (
                <tr key={row.alpha} className={`border-b border-slate-50 last:border-0 ${isBest ? 'bg-medical-50/50' : ''}`}>
                  <td className={`px-4 py-2.5 tabular-nums ${isBest ? 'text-medical-700 font-semibold' : 'text-slate-700'}`}>
                    {row.alpha.toFixed(1)}{isBest ? ' ★' : ''}
                  </td>
                  <td className="px-4 py-2.5 text-slate-600 tabular-nums">{(row.hit_rate * 100).toFixed(1)}%</td>
                  <td className="px-4 py-2.5 text-slate-600 tabular-nums">{(row.mrr * 100).toFixed(1)}%</td>
                  <td className="px-4 py-2.5 text-slate-600 tabular-nums">{(row.precision_at_k * 100).toFixed(1)}%</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Centered({ children, error }) {
  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto flex items-center justify-center">
      <div className={`flex items-center gap-2 text-sm font-medium rounded-xl px-5 py-3.5
        ${error ? 'text-red-600 bg-red-50 border border-red-100' : 'text-slate-500'}`}>
        {children}
      </div>
    </div>
  )
}
