import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Database, Cpu, Layers } from 'lucide-react'

const stats = [
  { icon: Database, value: '178', label: 'Clinical documents', sub: '16 cancer types' },
  { icon: Layers,   value: 'FAISS + BM25', label: 'Hybrid retrieval', sub: 'α = 0.1 · 100% Hit@5' },
  { icon: Cpu,      value: '3 LLMs', label: 'Local inference', sub: 'flan-t5 · phi-2 · TinyLlama' },
]

const examples = [
  'Quel est le protocole AC pour le cancer du sein ?',
  'Traitement de première ligne pour le lymphome de Hodgkin',
  'Effets secondaires de la chimiothérapie FOLFOX',
  'Prise en charge du cancer du col utérin stade III',
]

export default function HomePage() {
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  function submit(text) {
    const question = (text ?? q).trim()
    if (!question) return
    navigate(`/chat?q=${encodeURIComponent(question)}`)
  }

  return (
    <main style={{ maxWidth: 780, margin: '0 auto', padding: '80px 24px 60px' }}>

      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)',
          borderRadius: 20, padding: '4px 14px', marginBottom: 28,
          fontSize: 12, color: '#b8824e', fontWeight: 500,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#a1683a', display: 'inline-block' }} />
          Oncologie · Maroc · RAG local
        </div>

        <h1 style={{ fontSize: 40, fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.02em', marginBottom: 16, color: '#f4ece0' }}>
          Assistant médical
          <br />
          <span style={{ color: '#a1683a' }}>oncologie</span>
        </h1>

        <p style={{ color: '#8a7c6c', fontSize: 16, lineHeight: 1.6, maxWidth: 480, margin: '0 auto' }}>
          Posez vos questions cliniques. Le système retrouve les documents pertinents
          et génère une réponse via un LLM local.
        </p>
      </div>

      {/* Search bar */}
      <div style={{ position: 'relative', marginBottom: 16 }}>
        <Search size={16} style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: '#6b5d4f' }} />
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
          placeholder="Ex: Traitement HER2+ cancer du sein stade II..."
          style={{
            width: '100%',
            boxSizing: 'border-box',
            background: '#2b2118',
            border: '1px solid #3a2d1f',
            borderRadius: 10,
            padding: '14px 52px 14px 44px',
            fontSize: 15,
            color: '#e7ddcf',
            outline: 'none',
          }}
        />
        <button
          onClick={() => submit()}
          style={{
            position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)',
            background: '#a1683a', color: '#fff', border: 'none',
            borderRadius: 7, padding: '6px 16px', fontSize: 13, fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Ask
        </button>
      </div>

      {/* Example questions */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginBottom: 64 }}>
        {examples.map(ex => (
          <button
            key={ex}
            onClick={() => submit(ex)}
            style={{
              background: '#2b2118', border: '1px solid #3a2d1f',
              borderRadius: 20, padding: '5px 14px',
              fontSize: 12, color: '#a89a88', cursor: 'pointer',
              transition: 'border-color 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.borderColor = '#a1683a'}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#3a2d1f'}
          >
            {ex}
          </button>
        ))}
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {stats.map(({ icon: Icon, value, label, sub }) => (
          <div key={label} style={{
            background: '#2b2118', border: '1px solid #3a2d1f',
            borderRadius: 10, padding: '20px 16px',
          }}>
            <Icon size={16} style={{ color: '#a1683a', marginBottom: 12 }} />
            <div style={{ fontSize: 20, fontWeight: 700, color: '#f4ece0', marginBottom: 2 }}>{value}</div>
            <div style={{ fontSize: 12, color: '#a89a88', fontWeight: 500 }}>{label}</div>
            <div style={{ fontSize: 11, color: '#6b5d4f', marginTop: 2 }}>{sub}</div>
          </div>
        ))}
      </div>
    </main>
  )
}
