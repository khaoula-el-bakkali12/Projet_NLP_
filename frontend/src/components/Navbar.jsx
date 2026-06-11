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
    background: '#241a12',
    borderBottom: '1px solid #3a2d1f',
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
    color: '#e7ddcf',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#a1683a',
  },
  brandText: { fontWeight: 600, fontSize: 15, letterSpacing: '-0.01em' },
  brandSub: { fontSize: 12, color: '#8a7c6c', marginLeft: 4 },
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
            color: isActive ? '#d3ad85' : '#a89a88',
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
