import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Tag, MessageSquare } from 'lucide-react'
import { getDocument } from '../api/client'

function Field({ label, value }) {
  if (!value && value !== 0) return null
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontSize: 10, color: '#6b5d4f', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: 14, color: '#d8ccbb', lineHeight: 1.6 }}>{value}</div>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div style={{
      background: '#2b2118', border: '1px solid #3a2d1f',
      borderRadius: 10, padding: '18px 20px', marginBottom: 12,
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#6b5d4f', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
        {title}
      </div>
      {children}
    </div>
  )
}

function ProtocoleDisplay({ protocole }) {
  if (!protocole) return null

  if (typeof protocole === 'string') {
    return <div style={{ fontSize: 14, color: '#d8ccbb', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{protocole}</div>
  }

  // Structured dict: { nom, sequence, duree_totale, remarques }
  const { nom, sequence, duree_totale, remarques, ...rest } = protocole

  // Flatten all medicaments from all phases into table rows
  const rows = []
  if (Array.isArray(sequence)) {
    for (const phase of sequence) {
      const meds = Array.isArray(phase.medicaments) ? phase.medicaments : []
      if (meds.length === 0) {
        rows.push({ phase: phase.phase || '', medicament: '—', dose: '—', voie: '—', frequence: phase.frequence || '—', cycles: phase.cycles || '—' })
      } else {
        meds.forEach((med, i) => {
          rows.push({
            phase: i === 0 ? (phase.phase || '') : '',
            medicament: med.nom || med.name || '—',
            dose: med.dose || '—',
            voie: med.voie || '—',
            frequence: i === 0 ? (phase.frequence || '—') : '',
            cycles: i === 0 ? (phase.cycles || '—') : '',
          })
        })
      }
    }
  }

  return (
    <div>
      {nom && (
        <div style={{ fontSize: 13, fontWeight: 600, color: '#d3ad85', marginBottom: 12 }}>{nom}</div>
      )}

      {rows.length > 0 && (
        <div style={{ overflowX: 'auto', marginBottom: 12 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr>
                {['Phase', 'Médicament', 'Dose', 'Voie', 'Fréquence', 'Cycles'].map(h => (
                  <th key={h} style={{
                    textAlign: 'left', padding: '7px 10px',
                    fontSize: 10, color: '#6b5d4f', fontWeight: 600,
                    textTransform: 'uppercase', letterSpacing: '0.06em',
                    borderBottom: '1px solid #3a2d1f',
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)' }}>
                  {[r.phase, r.medicament, r.dose, r.voie, r.frequence, r.cycles].map((cell, ci) => (
                    <td key={ci} style={{
                      padding: '7px 10px', color: '#d8ccbb',
                      borderBottom: '1px solid rgba(30,34,53,0.6)',
                      verticalAlign: 'top',
                    }}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(duree_totale || remarques) && (
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 6 }}>
          {duree_totale && (
            <div>
              <div style={{ fontSize: 10, color: '#6b5d4f', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>Durée totale</div>
              <div style={{ fontSize: 13, color: '#a89a88' }}>{duree_totale}</div>
            </div>
          )}
          {remarques && (
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 10, color: '#6b5d4f', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>Remarques</div>
              <div style={{ fontSize: 13, color: '#a89a88', lineHeight: 1.5 }}>{remarques}</div>
            </div>
          )}
        </div>
      )}

      {/* Fallback for any extra dict keys not handled above */}
      {Object.keys(rest).length > 0 && (
        <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
          {Object.entries(rest).map(([k, v]) => (
            <div key={k}>
              <span style={{ fontSize: 10, color: '#a1683a', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{k}: </span>
              <span style={{ fontSize: 12, color: '#a89a88' }}>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TagList({ items }) {
  if (!items?.length) return null
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      {items.map(item => (
        <span key={item} style={{
          background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.15)',
          borderRadius: 20, padding: '3px 10px', fontSize: 12, color: '#b8824e',
        }}>
          {item}
        </span>
      ))}
    </div>
  )
}

export default function DocumentDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDocument(id)
      .then(setDoc)
      .catch(e => setError(e.response?.data?.detail || 'Document not found'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <main style={{ maxWidth: 780, margin: '0 auto', padding: '60px 24px', color: '#6b5d4f', textAlign: 'center' }}>
      Loading document…
    </main>
  )

  if (error) return (
    <main style={{ maxWidth: 780, margin: '0 auto', padding: '60px 24px' }}>
      <div style={{
        background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
        borderRadius: 10, padding: 20, color: '#fca5a5',
      }}>
        {error}
      </div>
    </main>
  )

  return (
    <main style={{ maxWidth: 780, margin: '0 auto', padding: '28px 24px 60px' }}>

      {/* Back + Ask button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'none', border: 'none', color: '#8a7c6c',
            cursor: 'pointer', fontSize: 13,
          }}
        >
          <ArrowLeft size={14} /> Back
        </button>
        <Link
          to={`/chat?q=${encodeURIComponent(`${doc.titre || ''} ${doc.type_cancer || ''}`.trim())}`}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)',
            borderRadius: 7, padding: '6px 14px',
            fontSize: 12, color: '#b8824e', textDecoration: 'none', fontWeight: 500,
          }}
        >
          <MessageSquare size={12} /> Ask about this
        </Link>
      </div>

      {/* Title block */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          <Pill value={doc.categorie} blue />
          <Pill value={doc.type_cancer} />
          {doc.sous_type && <Pill value={doc.sous_type} />}
          {doc.stade && <Pill value={`Stade ${doc.stade}`} />}
        </div>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f4ece0', lineHeight: 1.3, margin: '0 0 6px' }}>
          {doc.titre || doc.id}
        </h1>
        <div style={{ fontSize: 12, color: '#4a4036', fontFamily: 'monospace' }}>{doc.id}</div>
      </div>

      {/* Main content */}
      <Section title="Contenu clinique">
        <p style={{ fontSize: 14, color: '#d8ccbb', lineHeight: 1.75, margin: 0, whiteSpace: 'pre-wrap' }}>
          {doc.contenu}
        </p>
      </Section>

      {/* Protocole */}
      {doc.protocole && (
        <Section title="Protocole">
          <ProtocoleDisplay protocole={doc.protocole} />
        </Section>
      )}

      {/* Keywords */}
      {doc.mots_cles?.length > 0 && (
        <Section title="Mots-clés">
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            <Tag size={13} style={{ color: '#6b5d4f', marginTop: 3, flexShrink: 0 }} />
            <TagList items={doc.mots_cles} />
          </div>
        </Section>
      )}

      {/* Scenario & Side effects */}
      {(doc.scenario_patient || doc.effets_secondaires?.length > 0) && (
        <Section title="Scénario & effets secondaires">
          {doc.scenario_patient && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: '#6b5d4f', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>
                Scénario patient
              </div>
              <p style={{ fontSize: 14, color: '#d8ccbb', lineHeight: 1.6, margin: 0 }}>{doc.scenario_patient}</p>
            </div>
          )}
          {doc.effets_secondaires?.length > 0 && (
            <div>
              <div style={{ fontSize: 10, color: '#6b5d4f', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
                Effets secondaires
              </div>
              <TagList items={doc.effets_secondaires} />
            </div>
          )}
        </Section>
      )}

      {/* Meta */}
      <Section title="Métadonnées">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 24px' }}>
          <Field label="Référence" value={doc.reference} />
          <Field label="Date de création" value={doc.date_creation} />
          <Field label="Métastase" value={doc.metastase} />
          <Field label="Synthétique" value={doc.est_synthetique ? 'Oui' : 'Non'} />
        </div>
      </Section>
    </main>
  )
}

function Pill({ value, blue }) {
  if (!value) return null
  return (
    <span style={{
      fontSize: 10, fontWeight: 600, padding: '2px 10px', borderRadius: 20,
      textTransform: 'uppercase', letterSpacing: '0.06em',
      background: blue ? 'rgba(59,130,246,0.1)' : 'rgba(100,116,139,0.1)',
      color: blue ? '#b8824e' : '#a89a88',
      border: `1px solid ${blue ? 'rgba(59,130,246,0.2)' : 'rgba(100,116,139,0.15)'}`,
    }}>
      {value}
    </span>
  )
}
