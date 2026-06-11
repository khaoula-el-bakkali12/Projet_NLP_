import { useState } from 'react'
import { Database, Cpu, ShieldCheck, ArrowRight, Stethoscope, Heart, Brain, Activity } from 'lucide-react'
import { authLogin, authRegister } from '../api/client'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { icon: Database,    text: '291 protocoles AMFROM 2024 indexés', color: '#60A5FA', rgb: '96,165,250'  },
  { icon: Cpu,         text: '3 LLMs locaux comparables',          color: '#34D399', rgb: '52,211,153'  },
  { icon: ShieldCheck, text: 'Déploiement 100% local, souverain',  color: '#FBBF24', rgb: '251,191,36'  },
  { icon: Stethoscope, text: '28+ types de cancer couverts',       color: '#F472B6', rgb: '244,114,182' },
]

const STATS = [
  { n: '291', l: 'Protocoles', color: '#60A5FA' },
  { n: '28+', l: 'Cancers',    color: '#34D399' },
  { n: '3',   l: 'Modèles IA', color: '#FBBF24' },
]

export default function LoginPage({ onSuccess }) {
  const { login }    = useAuth()
  const [tab,      setTab]      = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const fn   = tab === 'login' ? authLogin : authRegister
      const data = await fn({ username, password })
      login(data.username, data.token)
      onSuccess(
        tab === 'login'
          ? `Bienvenue, ${data.username}.`
          : `Compte créé. Bienvenue, ${data.username} !`
      )
    } catch (err) {
      setError(err.message || 'Une erreur est survenue.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen flex font-sans overflow-hidden">

      {/* ── Left panel — branding ─────────────────────────────────── */}
      <div
        className="hidden lg:flex w-[44%] flex-col justify-between p-12 flex-shrink-0 relative overflow-hidden"
        style={{ background: 'linear-gradient(160deg, #050A14 0%, #09152A 45%, #0D1E3C 100%)' }}
      >
        {/* Decorative orbs */}
        <div className="orb"
             style={{
               width: 380, height: 380,
               background: 'radial-gradient(circle, rgba(26,86,219,0.18) 0%, transparent 65%)',
               top: -100, right: -80,
             }} />
        <div className="orb"
             style={{
               width: 260, height: 260,
               background: 'radial-gradient(circle, rgba(6,182,212,0.13) 0%, transparent 65%)',
               bottom: -60, left: 40,
             }} />
        <div className="orb"
             style={{
               width: 200, height: 200,
               background: 'radial-gradient(circle, rgba(167,139,250,0.09) 0%, transparent 65%)',
               top: '45%', left: '30%',
             }} />

        {/* Grid */}
        <div className="absolute inset-0 bg-grid pointer-events-none" />

        {/* Logo */}
        <div className="flex items-center gap-3 relative z-10">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center"
               style={{
                 background: 'linear-gradient(135deg, #1A56DB 0%, #06B6D4 100%)',
                 boxShadow: '0 6px 24px rgba(26,86,219,0.52), 0 1px 0 rgba(255,255,255,0.22) inset',
               }}>
            <Stethoscope className="text-white" strokeWidth={2.2} style={{ width: 20, height: 20 }} />
          </div>
          <div className="leading-none">
            <div className="font-bold text-white text-[17px] tracking-tight"
                 style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}>
              OncologIA
            </div>
            <div className="text-[11px] font-medium mt-0.5"
                 style={{ color: 'rgba(255,255,255,0.30)' }}>
              Plateforme RAG médicale
            </div>
          </div>
        </div>

        {/* Headline */}
        <div className="relative z-10">
          <div className="mb-6 inline-flex items-center gap-2.5 px-3.5 py-2 rounded-xl"
               style={{
                 background: 'rgba(26,86,219,0.14)',
                 border: '1px solid rgba(26,86,219,0.25)',
               }}>
            <Heart style={{ width: 14, height: 14, color: '#60A5FA' }} strokeWidth={2} />
            <span className="text-[12px] font-semibold"
                  style={{ color: 'rgba(255,255,255,0.55)' }}>
              Intelligence oncologique
            </span>
          </div>

          <h1 className="text-[2.6rem] font-black text-white leading-[1.12] mb-5 tracking-tight"
              style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}>
            Intelligence<br />artificielle au<br />
            service de{' '}
            <span style={{
              background: 'linear-gradient(135deg, #60A5FA 0%, #06B6D4 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              l'oncologie
            </span>
          </h1>

          <p className="text-[13px] leading-relaxed max-w-xs"
             style={{ color: 'rgba(255,255,255,0.42)' }}>
            Système RAG hybride (FAISS + BM25) basé sur les guidelines
            officiels AMFROM, SMCO et RORMA 2024.
          </p>

          {/* Feature list */}
          <div className="mt-7 space-y-2.5">
            {FEATURES.map(({ icon: Icon, text, color, rgb }) => (
              <div key={text} className="flex items-center gap-3">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{
                    background: `rgba(${rgb},0.12)`,
                    border: `1px solid rgba(${rgb},0.22)`,
                  }}
                >
                  <Icon style={{ width: 13, height: 13, color }} />
                </div>
                <span className="text-[13px] font-medium"
                      style={{ color: 'rgba(255,255,255,0.58)' }}>
                  {text}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div
          className="relative z-10 grid grid-cols-3 gap-4 pt-7"
          style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}
        >
          {STATS.map(({ n, l, color }) => (
            <div key={l}>
              <div className="text-2xl font-black mb-0.5"
                   style={{
                     fontFamily: 'Outfit, system-ui, sans-serif',
                     color,
                     textShadow: `0 0 20px ${color}55`,
                   }}>
                {n}
              </div>
              <div className="text-[11px] font-medium"
                   style={{ color: 'rgba(255,255,255,0.32)' }}>
                {l}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Right panel — form ────────────────────────────────────── */}
      <div
        className="flex-1 flex items-center justify-center p-8 overflow-y-auto relative"
        style={{ background: 'linear-gradient(145deg, #EEF2F8 0%, #F4F8FF 100%)' }}
      >
        {/* Background blobs */}
        <div className="orb"
             style={{
               width: 320, height: 320,
               background: 'radial-gradient(circle, rgba(37,99,235,0.07) 0%, transparent 70%)',
               top: '5%', right: '5%',
             }} />
        <div className="orb"
             style={{
               width: 240, height: 240,
               background: 'radial-gradient(circle, rgba(6,182,212,0.06) 0%, transparent 70%)',
               bottom: '5%', left: '5%',
             }} />

        <div className="w-full max-w-sm relative z-10">

          {/* Mobile logo */}
          <div className="lg:hidden mb-8 text-center">
            <div className="w-14 h-14 rounded-2xl mx-auto mb-3 flex items-center justify-center"
                 style={{
                   background: 'linear-gradient(135deg, #0A1628 0%, #0F2444 100%)',
                   boxShadow: '0 8px 28px rgba(10,22,40,0.22)',
                 }}>
              <Stethoscope className="text-white" strokeWidth={2.2} style={{ width: 24, height: 24 }} />
            </div>
            <div className="font-bold text-lg text-[#0F172A]"
                 style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}>
              OncologIA
            </div>
            <div className="text-sm text-[#94A3B8] mt-1">Plateforme RAG médicale</div>
          </div>

          {/* Card */}
          <div
            className="bg-white rounded-3xl p-8"
            style={{
              boxShadow: '0 24px 64px rgba(0,0,0,0.09), 0 8px 24px rgba(0,0,0,0.05), 0 1px 0 rgba(255,255,255,0.9) inset',
              border: '1px solid rgba(226,232,240,0.7)',
            }}
          >
            <div className="mb-6">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                   style={{
                     background: 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)',
                     border: '1px solid #BFDBFE',
                   }}>
                <Activity style={{ width: 18, height: 18, color: '#2563EB' }} strokeWidth={2.2} />
              </div>
              <h2 className="text-[22px] font-bold text-[#0F172A] mb-1 tracking-tight"
                  style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}>
                {tab === 'login' ? 'Connexion' : 'Créer un compte'}
              </h2>
              <p className="text-sm text-[#94A3B8]">
                {tab === 'login'
                  ? 'Accédez à votre espace médical'
                  : 'Rejoignez la plateforme OncologIA'}
              </p>
            </div>

            {/* Tab switcher */}
            <div className="flex gap-1 mb-6 p-1 rounded-xl"
                 style={{ background: '#F1F5F9', border: '1px solid #E8EDF2' }}>
              {[['login', 'Connexion'], ['register', 'Inscription']].map(([id, label]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => { setTab(id); setError('') }}
                  className="flex-1 py-2 rounded-lg text-sm font-semibold transition-all"
                  style={{
                    background:  tab === id ? 'white' : 'transparent',
                    color:       tab === id ? '#0F172A' : '#94A3B8',
                    boxShadow:   tab === id ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">

              <div>
                <label className="block text-[11px] font-bold text-[#475569] mb-1.5 uppercase tracking-widest">
                  Identifiant
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder="Votre nom d'utilisateur"
                  required
                  autoFocus
                  className="input-medical"
                  onFocus={e => {
                    e.target.style.borderColor = '#2563EB'
                    e.target.style.boxShadow   = '0 0 0 4px rgba(37,99,235,0.10)'
                    e.target.style.background  = 'white'
                  }}
                  onBlur={e => {
                    e.target.style.borderColor = '#E2E8F0'
                    e.target.style.boxShadow   = 'none'
                    e.target.style.background  = '#F8FAFC'
                  }}
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[#475569] mb-1.5 uppercase tracking-widest">
                  Mot de passe
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="input-medical"
                  onFocus={e => {
                    e.target.style.borderColor = '#2563EB'
                    e.target.style.boxShadow   = '0 0 0 4px rgba(37,99,235,0.10)'
                    e.target.style.background  = 'white'
                  }}
                  onBlur={e => {
                    e.target.style.borderColor = '#E2E8F0'
                    e.target.style.boxShadow   = 'none'
                    e.target.style.background  = '#F8FAFC'
                  }}
                />
              </div>

              {error && (
                <div className="flex items-center gap-2 px-3.5 py-3 rounded-xl text-xs font-semibold"
                     style={{
                       background: '#FEF2F2',
                       border: '1px solid #FECACA',
                       color: '#DC2626',
                     }}>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !username || !password}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm text-white
                           disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: 'linear-gradient(135deg, #1A56DB 0%, #2563EB 100%)',
                  boxShadow: '0 4px 20px rgba(26,86,219,0.38), 0 1px 0 rgba(255,255,255,0.22) inset',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                }}
                onMouseEnter={e => {
                  if (!e.currentTarget.disabled) {
                    e.currentTarget.style.transform = 'translateY(-2px)'
                    e.currentTarget.style.boxShadow = '0 10px 32px rgba(26,86,219,0.48), 0 1px 0 rgba(255,255,255,0.22) inset'
                  }
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(26,86,219,0.38), 0 1px 0 rgba(255,255,255,0.22) inset'
                }}
              >
                {loading ? (
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                ) : (
                  <>
                    {tab === 'login' ? 'Se connecter' : 'Créer mon compte'}
                    <ArrowRight style={{ width: 16, height: 16 }} />
                  </>
                )}
              </button>

            </form>
          </div>

          <p className="text-center text-[11px] mt-5 leading-relaxed"
             style={{ color: '#C4CDDB' }}>
            Plateforme à usage médical et académique exclusif
            <br />AMFROM 2024 · SMCO · RORMA
          </p>
        </div>
      </div>

    </div>
  )
}
