import { NavLink } from 'react-router-dom'
import { Activity, MessageSquare, BookOpen, BarChart2, FlaskConical } from 'lucide-react'

const links = [
  { to: '/',          label: 'Home',       icon: Activity },
  { to: '/chat',      label: 'Assistant',  icon: MessageSquare },
  { to: '/documents', label: 'Documents',  icon: BookOpen },
  { to: '/evaluate',  label: 'Retrieval',  icon: BarChart2 },
  { to: '/benchmark', label: 'Benchmark',  icon: FlaskConical },
]

const S = {
  nav: {
    position: 'sticky',
    top: 0,
    zIndex: 50,
    background: '#12151f',
    borderBottom: '1px solid #1e2235',
    display: 'flex',
    alignItems: 'center',
    padding: '0 24px',
    height: 56,
    gap: 8,
  },
  brand: {
    marginRight: 'auto',
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    textDecoration: 'none',
    color: '#e2e8f0',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#3b82f6',
  },
  brandText: { fontWeight: 600, fontSize: 15, letterSpacing: '-0.01em' },
  brandSub: { fontSize: 12, color: '#64748b', marginLeft: 4 },
}

export default function Navbar() {
  return (
    <nav style={S.nav}>
      <NavLink to="/" style={S.brand}>
        <span style={S.dot} />
        <span style={S.brandText}>OncoPilot</span>
        <span style={S.brandSub}>Maroc</span>
      </NavLink>

      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '6px 12px',
            borderRadius: 6,
            textDecoration: 'none',
            fontSize: 13,
            fontWeight: 500,
            color: isActive ? '#93c5fd' : '#94a3b8',
            background: isActive ? 'rgba(59,130,246,0.08)' : 'transparent',
            transition: 'color 0.15s, background 0.15s',
          })}
        >
          <Icon size={14} />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
