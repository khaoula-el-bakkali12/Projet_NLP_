import { useState } from 'react'
import {
  MessageSquare, Clock, FolderOpen, BarChart3,
  GitCompare, Activity, User, LogOut, Stethoscope, FlaskConical,
  Microscope, LineChart,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { id: 'chat',           icon: MessageSquare, label: 'Assistant',            rgb: '138,79,42'  },
  { id: 'classification', icon: Microscope,    label: 'Classification',       rgb: '138,79,42'  },
  { id: 'history',        icon: Clock,         label: 'Historique',           rgb: '138,79,42'  },
  { id: 'documents',      icon: FolderOpen,    label: 'Documents',            rgb: '138,79,42'  },
  { id: 'statistics',     icon: BarChart3,     label: 'Statistiques',         rgb: '138,79,42'  },
  { id: 'benchmark',      icon: GitCompare,    label: 'Benchmark LLM',        rgb: '138,79,42'  },
  { id: 'evaluate',       icon: LineChart,     label: 'Évaluation Retrieval', rgb: '138,79,42'  },
  { id: 'hybrid',         icon: FlaskConical,  label: 'Traitement Hybride',   rgb: '138,79,42'  },
  { id: 'journey',        icon: Activity,      label: 'Parcours Patient',     rgb: '138,79,42'  },
  { id: 'profile',        icon: User,          label: 'Profil',               rgb: '138,79,42'  },
]

const CLAY = '#8a4f2a'

export default function Sidebar({ activePage, onNavigate, health }) {
  const { user, logout } = useAuth()
  const [hovered, setHovered] = useState(null)

  return (
    <aside
      className="w-60 flex-shrink-0 flex flex-col h-screen select-none relative overflow-hidden"
      style={{
        background: 'linear-gradient(180deg, #fffdf9 0%, #f9f4ec 55%, #f4ece0 100%)',
        borderRight: '1px solid #e7ddcf',
        boxShadow: '4px 0 32px rgba(63,45,28,0.06)',
      }}
    >
      {/* ── Logo ────────────────────────────────────────────── */}
      <div className="px-5 py-5 flex items-center gap-3 relative z-10"
           style={{ borderBottom: '1px solid #e7ddcf' }}>
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
             style={{
               background: 'linear-gradient(135deg, #8a4f2a 0%, #b8824e 100%)',
               boxShadow: '0 4px 18px rgba(138,79,42,0.34), 0 1px 0 rgba(255,255,255,0.22) inset',
             }}>
          <Stethoscope className="text-white" strokeWidth={2.2} style={{ width: 17, height: 17 }} />
        </div>
        <div className="leading-none">
          <span className="font-bold text-[16px] tracking-tight block"
                style={{ fontFamily: '"Playfair Display", Georgia, serif', color: '#2b2520' }}>
            OncologIA
          </span>
          <span className="text-[10px] font-medium mt-1 block"
                style={{ color: '#a89a88', letterSpacing: '0.04em' }}>
            Plateforme RAG médicale
          </span>
        </div>
      </div>

      {/* ── Nav label ───────────────────────────────────────── */}
      <div className="px-4 pt-5 pb-2 relative z-10">
        <span className="text-[9px] font-bold tracking-[0.14em] uppercase"
              style={{ color: '#b8a890' }}>
          Navigation
        </span>
      </div>

      {/* ── Nav items ───────────────────────────────────────── */}
      <nav className="flex-1 px-3 pb-2 space-y-0.5 overflow-y-auto relative z-10">
        {NAV.map(({ id, icon: Icon, label, rgb }) => {
          const isActive  = activePage === id
          const isHovered = hovered === id && !isActive
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              onMouseEnter={() => setHovered(id)}
              onMouseLeave={() => setHovered(null)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold transition-all relative"
              style={{
                color: isActive
                  ? CLAY
                  : isHovered
                  ? '#4a4036'
                  : '#8a7c6c',
                background: isActive
                  ? `rgba(${rgb},0.10)`
                  : isHovered
                  ? 'rgba(63,45,28,0.04)'
                  : 'transparent',
                transform: isHovered && !isActive ? 'translateX(3px)' : 'translateX(0)',
                boxShadow: isActive
                  ? `inset 0 1px 0 rgba(255,255,255,0.5)`
                  : 'none',
                border: isActive
                  ? `1px solid rgba(${rgb},0.20)`
                  : '1px solid transparent',
              }}
            >
              {/* Active pill */}
              {isActive && (
                <span
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full"
                  style={{ background: CLAY, boxShadow: `0 0 10px rgba(${rgb},0.5)` }}
                />
              )}

              {/* Icon container */}
              <div
                className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{
                  background: isActive
                    ? `rgba(${rgb},0.16)`
                    : isHovered
                    ? 'rgba(63,45,28,0.05)'
                    : 'rgba(63,45,28,0.03)',
                  transition: 'all 0.2s ease',
                }}
              >
                <Icon
                  style={{
                    width: 14, height: 14,
                    color: isActive ? CLAY : isHovered ? '#6b5d4f' : '#a89a88',
                    transition: 'color 0.2s ease',
                  }}
                />
              </div>
              {label}
            </button>
          )
        })}
      </nav>

      {/* ── Health status ────────────────────────────────────── */}
      {health && (
        <div className="mx-3 mb-2.5 px-3 py-2 rounded-xl relative z-10"
             style={{
               background: 'rgba(63,45,28,0.03)',
               border: '1px solid #e7ddcf',
             }}>
          <div className="flex items-center gap-2">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{
                background: health.status === 'ok' ? '#7d9b6f' : '#c0705a',
                boxShadow:  health.status === 'ok'
                  ? '0 0 8px rgba(125,155,111,0.7)'
                  : '0 0 8px rgba(192,112,90,0.7)',
              }}
            />
            <span className="text-[11px] font-medium" style={{ color: '#8a7c6c' }}>
              {health.dataset_size ?? 0} docs
              &nbsp;·&nbsp;
              {health.status === 'ok' ? 'En ligne' : 'Hors ligne'}
            </span>
          </div>
        </div>
      )}

      {/* ── User footer ──────────────────────────────────────── */}
      {user && (
        <div className="p-3 relative z-10"
             style={{ borderTop: '1px solid #e7ddcf' }}>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('profile')}
              className="flex items-center gap-2.5 flex-1 p-2 rounded-xl transition-all overflow-hidden"
              style={{ color: '#6b5d4f' }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'rgba(63,45,28,0.05)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent'
              }}
            >
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                style={{
                  background: 'linear-gradient(135deg, #8a4f2a 0%, #b8824e 100%)',
                  boxShadow: '0 2px 10px rgba(138,79,42,0.34)',
                }}
              >
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <span className="text-[13px] font-semibold truncate block"
                      style={{ color: '#2b2520' }}>
                  {user.username}
                </span>
                <span className="text-[10px] block"
                      style={{ color: '#a89a88' }}>
                  Médecin
                </span>
              </div>
            </button>

            <button
              onClick={logout}
              className="p-2 rounded-xl transition-all flex-shrink-0"
              style={{ color: '#a89a88' }}
              onMouseEnter={e => {
                e.currentTarget.style.color      = '#c0705a'
                e.currentTarget.style.background = 'rgba(192,112,90,0.10)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.color      = '#a89a88'
                e.currentTarget.style.background = 'transparent'
              }}
              title="Déconnexion"
            >
              <LogOut style={{ width: 14, height: 14 }} />
            </button>
          </div>
        </div>
      )}
    </aside>
  )
}
