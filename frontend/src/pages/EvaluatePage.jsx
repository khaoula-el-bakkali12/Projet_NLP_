import { useState, useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer, Dot,
} from 'recharts'
import { getBenchmarkResults } from '../api/client'
import { TrendingUp, Target, Award } from 'lucide-react'

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
    <div style={{
      background: '#2b2118', border: '1px solid #3a2d1f',
      borderRadius: 10, padding: '16px 18px',
      borderLeft: `3px solid ${accent}`,
    }}>
      <Icon size={14} style={{ color: accent, marginBottom: 10 }} />
      <div style={{ fontSize: 24, fontWeight: 700, color: '#f4ece0', marginBottom: 2 }}>{value}</div>
      <div style={{ fontSize: 12, color: '#a89a88' }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: '#6b5d4f', marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

function CustomTooltip({ active, payload, label, bestAlpha }) {
  if (!active || !payload?.length) return null
  const isBest = label === bestAlpha
  return (
    <div style={{
      background: '#2b2118', border: `1px solid ${isBest ? '#a1683a' : '#3a2d1f'}`,
      borderRadius: 8, padding: '10px 14px', minWidth: 160,
    }}>
      <div style={{ fontSize: 11, color: isBest ? '#b8824e' : '#8a7c6c', marginBottom: 8, fontWeight: 600 }}>
        α = {label}{isBest ? ' ★ best' : ''}
      </div>
      {payload.map(p => (
        <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 4 }}>
          <span style={{ fontSize: 12, color: p.color }}>{LINE_LABELS[p.dataKey]}</span>
          <span style={{ fontSize: 12, color: '#e7ddcf', fontWeight: 600 }}>{(p.value * 100).toFixed(1)}%</span>
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
      <circle cx={cx} cy={cy} r={6} fill={stroke} stroke="#1f160f" strokeWidth={2} />
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
      .catch(e => setError(e.response?.data?.detail || 'Could not load evaluation results'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Centered>Loading evaluation results…</Centered>
  if (error)   return <Centered error>{error}</Centered>

  const sweep     = data.sweep_results ?? []
  const bestAlpha = data.best_alpha ?? 0.1
  const bestRow   = sweep.find(r => r.alpha === bestAlpha) ?? sweep[0] ?? {}
  const numQ      = data.num_test_questions ?? 17
  const topK      = data.top_k_evaluated ?? 5

  return (
    <main style={{ maxWidth: 960, margin: '0 auto', padding: '32px 24px 60px' }}>

      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f4ece0', margin: '0 0 4px' }}>Retrieval Evaluation</h1>
        <p style={{ color: '#8a7c6c', fontSize: 13, margin: 0 }}>
          Alpha sweep — FAISS vs BM25 weight (α) over {numQ} test questions, top-{topK} retrieval
        </p>
      </div>

      {/* Summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 28 }}>
        <StatCard icon={Award}     label="Best alpha"       value={`α = ${bestAlpha}`}            sub="optimal FAISS weight"   accent="#a1683a" />
        <StatCard icon={Target}    label="Hit Rate@5"       value={`${(bestRow.hit_rate * 100).toFixed(0)}%`} sub="at best alpha" accent="#10b981" />
        <StatCard icon={TrendingUp} label="MRR"             value={`${(bestRow.mrr * 100).toFixed(0)}%`}     sub="Mean Reciprocal Rank" accent="#f59e0b" />
      </div>

      {/* Chart */}
      <div style={{
        background: '#2b2118', border: '1px solid #3a2d1f',
        borderRadius: 10, padding: '20px 16px 12px',
      }}>
        <div style={{ fontSize: 12, color: '#6b5d4f', marginBottom: 16 }}>
          Metric scores across alpha values — higher is better
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={sweep} margin={{ top: 4, right: 20, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="#3a2d1f" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="alpha"
              tickFormatter={v => v.toFixed(1)}
              tick={{ fontSize: 11, fill: '#8a7c6c' }}
              tickLine={false}
              axisLine={{ stroke: '#3a2d1f' }}
              label={{ value: 'Alpha (FAISS weight)', position: 'insideBottomRight', offset: -4, fontSize: 11, fill: '#6b5d4f' }}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={v => `${(v * 100).toFixed(0)}%`}
              tick={{ fontSize: 11, fill: '#8a7c6c' }}
              tickLine={false}
              axisLine={false}
              width={44}
            />
            <Tooltip content={<CustomTooltip bestAlpha={bestAlpha} />} />
            <Legend
              formatter={key => (
                <span style={{ fontSize: 12, color: '#a89a88' }}>{LINE_LABELS[key]}</span>
              )}
            />
            <ReferenceLine
              x={bestAlpha}
              stroke="#a1683a"
              strokeDasharray="4 4"
              strokeOpacity={0.5}
              label={{ value: `α=${bestAlpha}`, position: 'top', fontSize: 10, fill: '#b8824e' }}
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
      <div style={{
        background: '#2b2118', border: '1px solid #3a2d1f',
        borderRadius: 10, overflow: 'hidden', marginTop: 12,
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #3a2d1f' }}>
              {['Alpha', 'Hit Rate@5', 'MRR', 'Precision@5'].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, color: '#6b5d4f', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sweep.map(row => {
              const isBest = row.alpha === bestAlpha
              return (
                <tr key={row.alpha} style={{ borderBottom: '1px solid #2b2118', background: isBest ? 'rgba(59,130,246,0.06)' : 'transparent' }}>
                  <td style={{ padding: '9px 16px', color: isBest ? '#b8824e' : '#e7ddcf', fontWeight: isBest ? 600 : 400 }}>
                    {row.alpha.toFixed(1)}{isBest ? ' ★' : ''}
                  </td>
                  <td style={{ padding: '9px 16px', color: '#d8ccbb' }}>{(row.hit_rate * 100).toFixed(1)}%</td>
                  <td style={{ padding: '9px 16px', color: '#d8ccbb' }}>{(row.mrr * 100).toFixed(1)}%</td>
                  <td style={{ padding: '9px 16px', color: '#d8ccbb' }}>{(row.precision_at_k * 100).toFixed(1)}%</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </main>
  )
}

function Centered({ children, error }) {
  return (
    <main style={{ maxWidth: 960, margin: '0 auto', padding: '80px 24px', textAlign: 'center' }}>
      <div style={{
        color: error ? '#fca5a5' : '#6b5d4f',
        background: error ? 'rgba(239,68,68,0.08)' : 'transparent',
        border: error ? '1px solid rgba(239,68,68,0.2)' : 'none',
        borderRadius: error ? 10 : 0, padding: error ? '14px 18px' : 0,
        display: 'inline-block',
      }}>
        {children}
      </div>
    </main>
  )
}
