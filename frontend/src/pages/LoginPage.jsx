import { useState, useEffect } from 'react'
import {
  BrainCircuit, ShieldCheck, Activity, ArrowRight, ChevronRight,
  Database, Search, Cpu, Server, Github, Mail, Phone, MapPin, ChevronDown,
} from 'lucide-react'
import { authLogin, authRegister } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function LoginPage({ onSuccess }) {
  const { login }   = useAuth()
  const [tab,       setTab]       = useState('login')
  const [username,  setUsername]  = useState('')
  const [password,  setPassword]  = useState('')
  const [error,     setError]     = useState('')
  const [loading,   setLoading]   = useState(false)
  const [scrolled,  setScrolled]  = useState(false)

  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', h)
    return () => window.removeEventListener('scroll', h)
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const fn   = tab === 'login' ? authLogin : authRegister
      const data = await fn({ username, password })
      login(data.username, data.token)
      onSuccess(tab === 'login' ? `Bienvenue, ${data.username}.` : `Compte créé. Bienvenue, ${data.username} !`)
    } catch (err) {
      setError(err.message || 'Une erreur est survenue.')
    } finally {
      setLoading(false)
    }
  }

  const scrollToLogin = () =>
    document.getElementById('login-section')?.scrollIntoView({ behavior: 'smooth' })

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-blue-100 overflow-x-hidden">

      {/* ── Navbar ─────────────────────────────────────────────── */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-200 border-b
                       ${scrolled ? 'bg-white border-slate-200 py-3' : 'bg-transparent border-transparent py-4'}`}>
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-8 h-8 rounded-lg bg-medical-600 flex items-center justify-center">
              <BrainCircuit className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-slate-900 tracking-tight font-display">OncologIA</span>
          </div>

          <div className="hidden lg:flex items-center gap-8">
            {['#pipeline','#missions','#faq'].map((href, i) => (
              <a key={i} href={href} className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
                {['Architecture','Vision','FAQ'][i]}
              </a>
            ))}
          </div>

          <button onClick={scrollToLogin} className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg font-semibold text-sm flex items-center gap-2 transition-colors">
            Portail <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────── */}
      <section className="pt-32 pb-20 px-6 border-b border-slate-200">
        <div className="max-w-6xl mx-auto w-full flex flex-col lg:flex-row gap-12 lg:gap-16 items-center">
          {/* Left copy */}
          <div className="flex-1 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-600 text-xs font-semibold mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-medical-600" />
              AMFROM 2024 · 178 fiches oncologiques indexées
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-[3.5rem] font-display font-bold text-slate-900 leading-[1.1] tracking-tight mb-5">
              Décision clinique<br />
              <span className="text-medical-600">augmentée par RAG</span>
            </h1>

            <p className="text-lg text-slate-600 mb-8 leading-relaxed max-w-xl mx-auto lg:mx-0">
              Interrogez les guidelines oncologiques marocaines via un pipeline RAG hybride
              FAISS + BM25. Une plateforme locale et souveraine conçue pour les équipes RCP.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3">
              <button onClick={scrollToLogin}
                className="w-full sm:w-auto bg-medical-600 hover:bg-medical-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors">
                <Activity className="w-4 h-4" /> Accéder à l'assistant
              </button>
              <a href="#pipeline"
                className="w-full sm:w-auto px-6 py-3 rounded-lg font-semibold text-slate-700 bg-white border border-slate-200 hover:border-slate-300 transition-colors flex items-center justify-center gap-2">
                Voir l'architecture <ChevronRight className="w-4 h-4 text-slate-400" />
              </a>
            </div>
          </div>

          {/* Login widget */}
          <div id="login-section" className="w-full max-w-[400px] shrink-0">
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8">
              <div className="text-center mb-6">
                <div className="w-12 h-12 rounded-xl bg-medical-50 flex items-center justify-center mx-auto mb-4">
                  <ShieldCheck className="w-6 h-6 text-medical-600" />
                </div>
                <h2 className="text-lg font-semibold text-slate-900 font-display">Portail sécurisé</h2>
                <p className="text-slate-500 mt-1 text-sm">Authentification hôpital / université</p>
              </div>

              {/* Tabs */}
              <div className="flex bg-slate-100 p-1 rounded-lg mb-6">
                {[['login','Connexion'],['register','Inscription']].map(([t, label]) => (
                  <button key={t} onClick={() => { setTab(t); setError('') }}
                    className={`flex-1 py-2 rounded-md text-sm font-semibold transition-colors
                      ${tab === t ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>
                    {label}
                  </button>
                ))}
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Identifiant</label>
                  <input type="text" value={username} onChange={e => setUsername(e.target.value)}
                    required minLength={3} placeholder="ex: dr.benali"
                    className="w-full bg-white border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 transition-colors outline-none" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 block mb-1.5">Mot de passe</label>
                  <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                    required minLength={6} placeholder="••••••••"
                    className="w-full bg-white border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 transition-colors outline-none" />
                </div>

                {error && (
                  <div className="p-3 bg-red-50 border border-red-100 rounded-lg flex items-center gap-2.5">
                    <Activity className="w-4 h-4 text-red-500 shrink-0" />
                    <p className="text-sm font-medium text-red-600 leading-tight">{error}</p>
                  </div>
                )}

                <button type="submit" disabled={loading}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white py-2.5 rounded-lg font-semibold transition-colors disabled:opacity-60 flex items-center justify-center gap-2">
                  {loading
                    ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    : tab === 'login' ? 'Connexion' : 'Créer mon compte'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* ── Trust bar (static) ─────────────────────────────────── */}
      <div className="bg-slate-900 py-4">
        <div className="max-w-6xl mx-auto px-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-3">
          {[
            [ShieldCheck,'Directives AMFROM 2024'],
            [Database,'178 fiches oncologiques'],
            [Cpu,'3 LLMs locaux comparés'],
            [Server,'Pipeline RAG hybride'],
            [Search,'Retrieval sémantique + lexical'],
          ].map(([Icon, label], i) => (
            <span key={i} className="text-slate-300 font-medium text-[13px] flex items-center gap-2">
              <Icon className="w-4 h-4 text-slate-500" /> {label}
            </span>
          ))}
        </div>
      </div>

      {/* ── Pipeline Architecture ──────────────────────────────── */}
      <section id="pipeline" className="py-24 bg-slate-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-medical-600 font-semibold tracking-wide uppercase text-xs mb-3">Architecture transparente</p>
            <h3 className="text-3xl font-bold text-slate-900 font-display mb-4">Le pipeline RAG expliqué</h3>
            <p className="text-slate-500 max-w-2xl mx-auto">
              Comment le système génère des réponses cliniques basées exclusivement sur les guidelines indexées.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { i:1, title:'Base de connaissances', desc:'178 fiches AMFROM 2024 segmentées en chunks sémantiques avec métadonnées structurées.', Icon:Database },
              { i:2, title:'Vectorisation FAISS',   desc:'Embeddings multilingues SBERT (paraphrase-multilingual-MiniLM) sur 384 dimensions.',    Icon:Cpu },
              { i:3, title:'Retrieval hybride',     desc:'Combinaison FAISS (sémantique) + BM25 (lexical) avec pondération α optimisée à 0.1.',   Icon:Search },
              { i:4, title:'Génération contrôlée',  desc:'3 LLMs locaux (flan-t5, Qwen2.5, TinyLlama) avec zero-shot, few-shot et chain-of-thought.', Icon:ShieldCheck },
            ].map(({ i, title, desc, Icon }) => (
              <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-medical-50 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-medical-600" />
                  </div>
                  <span className="text-xs font-bold text-slate-300">0{i}</span>
                </div>
                <h4 className="text-base font-semibold text-slate-900 mb-2 font-display">{title}</h4>
                <p className="text-sm text-slate-600 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Metrics banner ─────────────────────────────────────── */}
      <section className="py-16 bg-slate-900">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-10 lg:divide-x divide-slate-800">
            {[
              ['100%', 'Souverain & local'],
              ['99.4%', 'Précision FAISS Top-1'],
              ['Zéro', 'Hallucination'],
              ['3', 'LLMs comparés'],
            ].map(([val, label], i) => (
              <div key={i} className="px-4 lg:px-8 text-center lg:text-left">
                <p className="text-4xl font-bold font-display text-white tracking-tight mb-2">{val}</p>
                <p className="text-slate-400 text-xs font-semibold uppercase tracking-wide">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Vision cards ──────────────────────────────────────── */}
      <section id="missions" className="py-24 bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid lg:grid-cols-3 gap-6">
            {[
              { icon: ShieldCheck,  title:'Conformité totale',      body:"Chaque réponse est ancrée dans les standards AMFROM, garantissant une conformité thérapeutique vérifiable et des sources citées." },
              { icon: BrainCircuit, title:'Secret médical garanti', body:"Inférence 100% locale. Aucune donnée ne quitte le serveur hospitalier. Compatible avec les exigences RGPD et HDS." },
              { icon: Activity,     title:'Efficacité clinique',    body:"De minutes de recherche manuelle à quelques secondes d'interrogation en langage naturel — en français, arabe ou anglais." },
            ].map(({ icon: Icon, title, body }, i) => (
              <div key={i} className="rounded-xl p-8 border border-slate-200 bg-white">
                <div className="w-11 h-11 rounded-lg bg-medical-50 flex items-center justify-center mb-5">
                  <Icon className="w-5 h-5 text-medical-600" />
                </div>
                <h4 className="text-lg font-semibold mb-2 font-display text-slate-900">{title}</h4>
                <p className="leading-relaxed text-sm text-slate-600">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ───────────────────────────────────────────────── */}
      <section id="faq" className="py-24 bg-slate-50 border-b border-slate-200">
        <div className="max-w-3xl mx-auto px-6">
          <h3 className="text-3xl font-bold text-center text-slate-900 font-display mb-12">Questions fréquentes</h3>
          <div className="space-y-3">
            {[
              ['Qu\'est-ce que le RAG ?', 'Retrieval-Augmented Generation : l\'IA lit exclusivement la base indexée (AMFROM) avant de répondre. Impossible d\'inventer des informations non présentes dans les guidelines.'],
              ['Les données patients sont-elles partagées ?', 'Non. L\'inférence est locale. Aucun appel externe n\'est effectué. Les modèles (flan-t5, Qwen2.5, TinyLlama) tournent sur le serveur de l\'institution.'],
              ['Quels langages sont supportés ?', 'Français, arabe (avec affichage RTL automatique) et anglais. La classification de la langue est automatique.'],
              ['Comment fonctionne le retrieval hybride ?', 'FAISS pour la similarité sémantique (vecteurs SBERT) + BM25 pour la pertinence lexicale. Les scores sont fusionnés avec un paramètre α=0.1 optimisé.'],
            ].map(([q, a], i) => (
              <div key={i} className="p-5 bg-white border border-slate-200 rounded-xl">
                <h4 className="font-semibold text-slate-900 text-[15px] flex items-center justify-between">
                  {q}
                  <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
                </h4>
                <p className="text-slate-600 text-sm mt-2.5 leading-relaxed">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────── */}
      <footer className="bg-slate-900 text-slate-300 py-16">
        <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-4 gap-10">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-lg bg-medical-600 flex items-center justify-center">
                <BrainCircuit className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-lg text-white font-display">OncologIA</span>
            </div>
            <p className="text-slate-400 leading-relaxed max-w-sm text-sm">
              Plateforme universitaire RAG déployée pour optimiser l'accès aux recommandations
              de pratiques cliniques en cancérologie marocaine.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-5 text-sm">Contact</h4>
            <ul className="space-y-3 text-sm">
              {[[Mail,'contact@oncologia.ma'],[Phone,'+212 5 00 00 00 00'],[MapPin,'CHU Ibn Rochd, Casa']].map(([Icon,text],i)=>(
                <li key={i} className="flex items-center gap-2.5 text-slate-400">
                  <Icon className="w-4 h-4 text-slate-500" /> {text}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-5 text-sm">Projet</h4>
            <ul className="space-y-3 text-sm text-slate-400">
              <li><a href="#pipeline" className="hover:text-white transition-colors">Architecture pipeline</a></li>
              <li><a href="#missions" className="hover:text-white transition-colors">Vision clinique</a></li>
              <li><span className="opacity-50">Documentation API</span></li>
            </ul>
          </div>
        </div>
        <div className="max-w-6xl mx-auto px-6 mt-12 pt-8 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-slate-500">© 2026 Projet NLP Universitaire — Tous droits réservés.</p>
          <a href="#" className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center hover:bg-slate-700 transition-colors text-white">
            <Github className="w-4 h-4" />
          </a>
        </div>
      </footer>
    </div>
  )
}
