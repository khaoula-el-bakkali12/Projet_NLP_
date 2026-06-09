import { MessageSquare, Clock, FolderOpen, BarChart3, GitCompare, Activity, User, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { id: 'chat',       icon: MessageSquare, label: 'Assistant' },
  { id: 'history',    icon: Clock,         label: 'Historique' },
  { id: 'documents',  icon: FolderOpen,    label: 'Documents' },
  { id: 'statistics', icon: BarChart3,     label: 'Statistiques' },
  { id: 'benchmark',  icon: GitCompare,    label: 'Benchmark LLM' },
  { id: 'journey',    icon: Activity,      label: 'Parcours Patient' },
  { id: 'profile',    icon: User,          label: 'Profil' },
]

export default function Sidebar({ activePage, onNavigate, health }) {
  const { user, logout } = useAuth()

  return (
    <aside className="w-56 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col h-screen">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-200 flex items-center gap-2.5">
        <div className="w-9 h-9 rounded-lg bg-medical-600 flex items-center justify-center flex-shrink-0">
          <Activity className="w-5 h-5 text-white" strokeWidth={2.5} />
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-base text-slate-900 tracking-tight leading-none font-display">
            OncologIA
          </span>
          <span className="text-[10px] font-medium text-slate-400 tracking-wide mt-1">Plateforme RAG</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {NAV.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors font-medium
              ${activePage === id
                ? 'bg-blue-50 text-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'}`}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </button>
        ))}
      </nav>

      {/* User footer */}
      {user && (
        <div className="p-3 border-t border-slate-200 bg-slate-50">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onNavigate('profile')}
              className="flex items-center gap-2.5 overflow-hidden hover:bg-slate-200/50 p-1.5 rounded-xl transition-colors cursor-pointer flex-1 text-left mr-1 group"
            >
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold flex-shrink-0 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <p className="text-sm text-slate-700 truncate font-semibold group-hover:text-slate-900 transition-colors">
                {user.username}
              </p>
            </button>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors flex-shrink-0"
              title="Déconnexion"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </aside>
  )
}
