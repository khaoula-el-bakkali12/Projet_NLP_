import { useState } from 'react'
import {
  MessageSquare, Clock, FolderOpen, BarChart3,
  GitCompare, Activity, User, LogOut, Stethoscope, FlaskConical,
  Microscope, LineChart,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { id: 'chat',           icon: MessageSquare, label: 'Assistant',          color: '#60A5FA', rgb: '96,165,250'  },
  { id: 'classification', icon: Microscope,    label: 'Classification',     color: '#2DD4BF', rgb: '45,212,191'  },
  { id: 'history',        icon: Clock,         label: 'Historique',         color: '#34D399', rgb: '52,211,153'  },
  { id: 'documents',      icon: FolderOpen,    label: 'Documents',          color: '#FBBF24', rgb: '251,191,36'  },
  { id: 'statistics',     icon: BarChart3,     label: 'Statistiques',       color: '#A78BFA', rgb: '167,139,250' },
  { id: 'benchmark',      icon: GitCompare,    label: 'Benchmark LLM',      color: '#F472B6', rgb: '244,114,182' },
  { id: 'evaluate',       icon: LineChart,     label: 'Évaluation Retrieval', color: '#38BDF8', rgb: '56,189,248'  },
  { id: 'hybrid',         icon: FlaskConical,  label: 'Traitement Hybride', color: '#C084FC', rgb: '192,132,252' },
  { id: 'journey',        icon: Activity,      label: 'Parcours Patient',   color: '#06B6D4', rgb: '6,182,212'   },
  { id: 'profile',        icon: User,          label: 'Profil',             color: '#94A3B8', rgb: '148,163,184' },
]

export default function Sidebar({ activePage, onNavigate, health }) {
  const { user, logout } = useAuth()
  const [hovered, setHovered] = useState(null)

  return (
    <aside
      className="w-60 flex-shrink-0 flex flex-col h-screen select-none relative overflow-hidden"
      style={{
        background: 'linear-gradient(180deg, #060D1B 0%, #08111F 45%, #0B1A30 100%)',
        borderRight: '1px solid rgba(255,255,255,0.055)',
        boxShadow: '4px 0 32px rgba(0,0,0,0.30)',
      }}
    >
      {/* ── Decorative orbs ─────────────────────────────────── */}
      <div className="orb"
           style={{
             width: 200, height: 200,
             background: 'radial-gradient(circle, rgba(26,86,219,0.16) 0%, transparent 70%)',
             top: -60, right: -60,
           }} />
      <div className="orb"
           style={{
             width: 160, height: 160,
             background: 'radial-gradient(circle, rgba(6,182,212,0.10) 0%, transparent 70%)',
             bottom: 80, left: -50,
           }} />

      {/* ── Grid overlay ────────────────────────────────────── */}
      <div className="absolute inset-0 bg-grid pointer-events-none opacity-100" />

      {/* ── Logo ────────────────────────────────────────────── */}
      <div className="px-5 py-5 flex items-center gap-3 relative z-10"
           style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
             style={{
               background: 'linear-gradient(135deg, #1A56DB 0%, #06B6D4 100%)',
               boxShadow: '0 4px 18px rgba(26,86,219,0.48), 0 1px 0 rgba(255,255,255,0.22) inset',
             }}>
          <Stethoscope className="text-white" strokeWidth={2.2} style={{ width: 17, height: 17 }} />
        </div>
        <div className="leading-none">
          <span className="font-bold text-[15px] text-white tracking-tight block"
                style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}>
            OncologIA
          </span>
          <span className="text-[10px] font-medium mt-0.5 block"
                style={{ color: 'rgba(255,255,255,0.28)', letterSpacing: '0.04em' }}>
            Plateforme RAG médicale
          </span>
        </div>
      </div>

      {/* ── Nav label ───────────────────────────────────────── */}
      <div className="px-4 pt-5 pb-2 relative z-10">
        <span className="text-[9px] font-bold tracking-[0.14em] uppercase"
              style={{ color: 'rgba(255,255,255,0.18)' }}>
          Navigation
        </span>
      </div>

      {/* ── Nav items ───────────────────────────────────────── */}
      <nav className="flex-1 px-3 pb-2 space-y-0.5 overflow-y-auto relative z-10">
        {NAV.map(({ id, icon: Icon, label, color, rgb }) => {
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
                  ? '#FFFFFF'
                  : isHovered
                  ? 'rgba(255,255,255,0.82)'
                  : 'rgba(255,255,255,0.42)',
                background: isActive
                  ? `rgba(${rgb},0.14)`
                  : isHovered
                  ? 'rgba(255,255,255,0.055)'
                  : 'transparent',
                transform: isHovered && !isActive ? 'translateX(3px)' : 'translateX(0)',
                boxShadow: isActive
                  ? `0 2px 16px rgba(${rgb},0.16), inset 0 1px 0 rgba(255,255,255,0.07)`
                  : 'none',
                border: isActive
                  ? `1px solid rgba(${rgb},0.18)`
                  : '1px solid transparent',
              }}
            >
              {/* Active pill */}
              {isActive && (
                <span
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full"
                  style={{ background: color, boxShadow: `0 0 10px ${color}` }}
                />
              )}

              {/* Icon container */}
              <div
                className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{
                  background: isActive
                    ? `rgba(${rgb},0.20)`
                    : isHovered
                    ? 'rgba(255,255,255,0.07)'
                    : 'rgba(255,255,255,0.04)',
                  boxShadow: isActive ? `0 2px 8px rgba(${rgb},0.20)` : 'none',
                  transition: 'all 0.2s ease',
                }}
              >
                <Icon
                  style={{
                    width: 14, height: 14,
                    color: isActive ? color : isHovered ? 'rgba(255,255,255,0.62)' : 'rgba(255,255,255,0.32)',
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
               background: 'rgba(255,255,255,0.04)',
               border: '1px solid rgba(255,255,255,0.07)',
             }}>
          <div className="flex items-center gap-2">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{
                background: health.status === 'ok' ? '#34D399' : '#F87171',
                boxShadow:  health.status === 'ok'
                  ? '0 0 8px rgba(52,211,153,0.7)'
                  : '0 0 8px rgba(248,113,113,0.7)',
              }}
            />
            <span className="text-[11px] font-medium" style={{ color: 'rgba(255,255,255,0.32)' }}>
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
             style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('profile')}
              className="flex items-center gap-2.5 flex-1 p-2 rounded-xl transition-all overflow-hidden"
              style={{ color: 'rgba(255,255,255,0.55)' }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.075)'
                e.currentTarget.style.color      = 'rgba(255,255,255,0.92)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color      = 'rgba(255,255,255,0.55)'
              }}
            >
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                style={{
                  background: 'linear-gradient(135deg, #1A56DB 0%, #06B6D4 100%)',
                  boxShadow: '0 2px 10px rgba(26,86,219,0.4)',
                }}
              >
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <span className="text-[13px] font-semibold truncate block"
                      style={{ color: 'rgba(255,255,255,0.82)' }}>
                  {user.username}
                </span>
                <span className="text-[10px] block"
                      style={{ color: 'rgba(255,255,255,0.28)' }}>
                  Médecin
                </span>
              </div>
            </button>

            <button
              onClick={logout}
              className="p-2 rounded-xl transition-all flex-shrink-0"
              style={{ color: 'rgba(255,255,255,0.28)' }}
              onMouseEnter={e => {
                e.currentTarget.style.color      = '#F87171'
                e.currentTarget.style.background = 'rgba(248,113,113,0.12)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.color      = 'rgba(255,255,255,0.28)'
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
