import { useRef, useEffect, useState } from 'react'
import { Send, ChevronDown, Bot, Syringe, Activity, Stethoscope, ListOrdered, Sparkles, Trash2 } from 'lucide-react'
import { useChat } from '../hooks/useChat'
import ChatMessage from '../components/ChatMessage'
import TypingIndicator from '../components/TypingIndicator'

const MODELS = [
  { value: 'model_a', label: 'flan-t5-base',   desc: 'Seq2Seq · rapide' },
  { value: 'model_b', label: 'Qwen2.5-1.5B',   desc: '1.5B · CPU'      },
  { value: 'model_c', label: 'TinyLlama-1.1B',  desc: '1.1B · léger'   },
]

const STRATEGIES = [
  { value: 'zero_shot',        label: 'Zero-shot'        },
  { value: 'few_shot',         label: 'Few-shot'         },
  { value: 'chain_of_thought', label: 'Chain of Thought' },
]

const SUGGESTED = [
  {
    icon: Syringe,
    q: 'Quel est le protocole de traitement du cancer du sein ?',
    color: '#F472B6', bg: '#FDF2F8', border: '#FBCFE8',
  },
  {
    icon: Activity,
    q: 'Quels sont les effets secondaires de la chimiothérapie ?',
    color: '#34D399', bg: '#F0FDF4', border: '#A7F3D0',
  },
  {
    icon: Stethoscope,
    q: "Comment se déroule le diagnostic d'un cancer ?",
    color: '#60A5FA', bg: '#EFF6FF', border: '#BFDBFE',
  },
  {
    icon: ListOrdered,
    q: 'Explique le protocole AC-T pour le cancer du sein étape par étape.',
    color: '#FBBF24', bg: '#FFFBEB', border: '#FDE68A',
  },
]

const STEP_BY_STEP_PREFIX =
  'Explique de manière structurée, en numérotant chaque étape clairement (Étape 1, Étape 2…) : '

export default function ChatPage({ availableModels = [] }) {
  const { messages, loading, sendMessage, clearChat } = useChat()
  const [input,      setInput]      = useState('')
  const [model,      setModel]      = useState('model_a')
  const [strategy,   setStrategy]   = useState('zero_shot')
  const [stepByStep, setStepByStep] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function modelEnabled(val) {
    return availableModels.length === 0 || availableModels.includes(val)
  }

  function formatQuestion(q) {
    return stepByStep ? `${STEP_BY_STEP_PREFIX}${q}` : q
  }

  function handleSubmit(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    sendMessage(formatQuestion(q), model, strategy)
  }

  function handleSuggest(q) {
    if (loading) return
    sendMessage(formatQuestion(q), model, strategy)
  }

  return (
    <div className="flex flex-col h-full" style={{ background: '#F4F7FB' }}>

      {/* ── Header ───────────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between gap-4 px-6 py-3.5 flex-shrink-0 bg-white"
        style={{ borderBottom: '1px solid #E8EDF2', boxShadow: '0 1px 6px rgba(0,0,0,0.05)' }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{
              background: 'linear-gradient(135deg, #080F1E 0%, #1A3A6B 100%)',
              boxShadow: '0 4px 14px rgba(8,15,30,0.22)',
            }}
          >
            <Bot style={{ width: 18, height: 18, color: '#93C5FD' }} />
          </div>
          <div>
            <h2
              className="font-bold text-[15px] text-[#0F172A] tracking-tight"
              style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}
            >
              Assistant RAG Oncologique
            </h2>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              Guidelines AMFROM 2024 · {Math.floor(messages.length / 2)} échanges
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-end gap-2 flex-shrink-0">
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="p-2 rounded-xl transition-all"
              style={{ color: '#CBD5E1' }}
              title="Effacer la conversation"
              onMouseEnter={e => {
                e.currentTarget.style.color = '#F87171'
                e.currentTarget.style.background = 'rgba(248,113,113,0.08)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.color = '#CBD5E1'
                e.currentTarget.style.background = 'transparent'
              }}
            >
              <Trash2 style={{ width: 15, height: 15 }} />
            </button>
          )}

          {[
            { label: 'Modèle', value: model, setter: setModel, opts: MODELS },
            { label: 'Stratégie', value: strategy, setter: setStrategy,
              opts: STRATEGIES.map(s => ({ value: s.value, label: s.label })) },
          ].map(({ label, value, setter, opts }) => (
            <div key={label}>
              <label className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-widest block mb-1">
                {label}
              </label>
              <div className="relative">
                <select
                  value={value}
                  onChange={e => setter(e.target.value)}
                  className="appearance-none bg-white rounded-xl pl-3 pr-8 py-1.5 text-[13px] font-semibold text-[#0F172A] cursor-pointer focus:outline-none"
                  style={{
                    border: '1.5px solid #E8EDF2',
                    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                  }}
                >
                  {opts.map(o => (
                    <option key={o.value} value={o.value}
                            disabled={label === 'Modèle' && !modelEnabled(o.value)}>
                      {o.label}
                      {label === 'Modèle' && !modelEnabled(o.value) ? ' (indisponible)' : ''}
                    </option>
                  ))}
                </select>
                <ChevronDown
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400"
                  style={{ width: 12, height: 12 }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Messages / Empty state ────────────────────────────────── */}
      {messages.length === 0 && !loading ? (
        <div className="flex-1 overflow-y-auto">
          <div className="min-h-full flex flex-col items-center justify-center max-w-2xl mx-auto px-6 py-10 text-center">

            {/* 3D floating bot icon */}
            <div className="relative mb-8">
              <div
                className="w-20 h-20 rounded-3xl flex items-center justify-center relative z-10 animate-float"
                style={{
                  background: 'linear-gradient(135deg, #080F1E 0%, #1A3A6B 50%, #1e40af 100%)',
                  boxShadow: '0 24px 56px rgba(8,15,30,0.22), 0 10px 20px rgba(8,15,30,0.14), 0 2px 0 rgba(255,255,255,0.08) inset',
                }}
              >
                <Bot style={{ width: 38, height: 38, color: '#93C5FD' }} />
              </div>
              {/* Glow halo */}
              <div
                className="absolute rounded-3xl opacity-25 pointer-events-none"
                style={{
                  inset: '-20px',
                  background: 'radial-gradient(circle, rgba(26,86,219,0.55) 0%, transparent 65%)',
                }}
              />
            </div>

            <h3
              className="text-2xl font-black text-[#0F172A] tracking-tight mb-2"
              style={{ fontFamily: 'Outfit, system-ui, sans-serif' }}
            >
              Comment puis-je vous aider ?
            </h3>
            <p className="text-sm text-[#64748B] max-w-md leading-relaxed">
              Posez une question sur les protocoles, diagnostics ou traitements oncologiques.
              Les réponses s'appuient uniquement sur les guidelines{' '}
              <span className="font-semibold text-[#475569]">AMFROM 2024</span>.
            </p>

            {/* Suggestion cards — 2 × 2 grid */}
            <div className="w-full mt-8 grid sm:grid-cols-2 gap-3">
              {SUGGESTED.map(({ icon: Icon, q, color, bg, border }, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggest(q)}
                  className="group flex items-start gap-3.5 p-4 rounded-2xl bg-white text-left animate-fade-in"
                  style={{
                    border: `1.5px solid ${border}`,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                    animationDelay: `${i * 0.07}s`,
                    transition: 'transform 0.25s cubic-bezier(0.23,1,0.32,1), box-shadow 0.25s ease, border-color 0.2s ease',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateY(-5px)'
                    e.currentTarget.style.boxShadow = '0 16px 40px rgba(0,0,0,0.10), 0 4px 8px rgba(0,0,0,0.05)'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)'
                  }}
                >
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: bg, border: `1.5px solid ${border}` }}
                  >
                    <Icon style={{ width: 17, height: 17, color }} />
                  </div>
                  <span className="text-[13px] font-medium text-[#0F172A] leading-snug">{q}</span>
                </button>
              ))}
            </div>

            {/* Tip */}
            <div
              className="mt-5 flex items-center gap-2 px-4 py-2.5 rounded-xl"
              style={{
                background: 'rgba(37,99,235,0.05)',
                border: '1px solid rgba(37,99,235,0.12)',
              }}
            >
              <Sparkles style={{ width: 12, height: 12, color: '#2563EB' }} />
              <span className="text-xs text-[#475569] font-medium">
                Activez <strong>Étape par étape</strong> pour des réponses structurées numérotées
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
      )}

      {/* ── Input bar ─────────────────────────────────────────────── */}
      <div
        className="px-6 py-4 flex-shrink-0 bg-white space-y-2.5"
        style={{ borderTop: '1px solid #E8EDF2', boxShadow: '0 -2px 8px rgba(0,0,0,0.04)' }}
      >
        <form onSubmit={handleSubmit} className="flex gap-2.5">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={
              stepByStep
                ? 'Posez votre question — réponse structurée étape par étape…'
                : 'Posez votre question oncologique…'
            }
            disabled={loading}
            className="flex-1 rounded-2xl px-4 py-3 text-sm text-[#0F172A] font-medium focus:outline-none disabled:opacity-60"
            style={{
              background: '#F4F7FB',
              border: `1.5px solid ${stepByStep ? '#2563EB' : '#E8EDF2'}`,
              boxShadow: stepByStep
                ? '0 0 0 4px rgba(37,99,235,0.09)'
                : '0 1px 3px rgba(0,0,0,0.05)',
              transition: 'border-color 0.2s, box-shadow 0.2s, background 0.2s',
            }}
            onFocus={e => {
              e.target.style.background   = 'white'
              e.target.style.borderColor  = '#2563EB'
              e.target.style.boxShadow    = '0 0 0 4px rgba(37,99,235,0.09)'
            }}
            onBlur={e => {
              e.target.style.background   = '#F4F7FB'
              e.target.style.borderColor  = stepByStep ? '#2563EB' : '#E8EDF2'
              e.target.style.boxShadow    = stepByStep
                ? '0 0 0 4px rgba(37,99,235,0.09)'
                : '0 1px 3px rgba(0,0,0,0.05)'
            }}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="flex-shrink-0 w-12 h-12 rounded-2xl flex items-center justify-center disabled:opacity-40"
            style={{
              background: 'linear-gradient(135deg, #1A56DB 0%, #2563EB 100%)',
              boxShadow: '0 4px 16px rgba(26,86,219,0.38)',
              color: 'white',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            }}
            onMouseEnter={e => {
              if (!e.currentTarget.disabled) {
                e.currentTarget.style.transform = 'scale(1.06) translateY(-1px)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(26,86,219,0.52)'
              }
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = 'scale(1) translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(26,86,219,0.38)'
            }}
          >
            <Send style={{ width: 16, height: 16 }} />
          </button>
        </form>

        {/* Toolbar */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setStepByStep(v => !v)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
            style={{
              background: stepByStep
                ? 'linear-gradient(135deg, #1A56DB, #2563EB)'
                : '#F1F5F9',
              color:      stepByStep ? 'white' : '#64748B',
              boxShadow:  stepByStep ? '0 2px 10px rgba(26,86,219,0.30)' : 'none',
            }}
          >
            <ListOrdered style={{ width: 13, height: 13 }} />
            Étape par étape
            {stepByStep && <span className="opacity-70 ml-0.5">· actif</span>}
          </button>

          {stepByStep && (
            <span className="text-[11px] text-[#2563EB] font-semibold animate-fade-in">
              Réponse structurée en étapes numérotées
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
