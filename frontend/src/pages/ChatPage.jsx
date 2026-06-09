import { useRef, useEffect, useState } from 'react'
import { Send, ChevronDown, Bot, Syringe, Activity, Stethoscope } from 'lucide-react'
import { useChat } from '../hooks/useChat'
import ChatMessage from '../components/ChatMessage'
import TypingIndicator from '../components/TypingIndicator'

const MODELS = [
  { value: 'model_a', label: 'flan-t5-base',       desc: 'Seq2Seq · rapide' },
  { value: 'model_b', label: 'Qwen2.5-1.5B',       desc: '1.5B · CPU' },
  { value: 'model_c', label: 'TinyLlama-1.1B',      desc: '1.1B · léger' },
]

const STRATEGIES = [
  { value: 'zero_shot',        label: 'Zero-shot' },
  { value: 'few_shot',         label: 'Few-shot' },
  { value: 'chain_of_thought', label: 'Chain of Thought' },
]

const SUGGESTED = [
  { icon: Syringe,     q: 'Quel est le protocole de traitement du cancer du sein ?' },
  { icon: Activity,    q: 'Quels sont les effets secondaires de la chimiothérapie ?' },
  { icon: Stethoscope, q: 'Comment se déroule le diagnostic d’un cancer ?' },
]

export default function ChatPage({ availableModels = [] }) {
  const { messages, loading, sendMessage, clearChat } = useChat()
  const [input,       setInput]       = useState('')
  const [model,       setModel]       = useState('model_a')
  const [strategy,    setStrategy]    = useState('zero_shot')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function modelEnabled(val) {
    return availableModels.length === 0 || availableModels.includes(val)
  }

  function handleSubmit(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    sendMessage(q, model, strategy)
  }

  function handleSuggest(q) {
    if (loading) return
    sendMessage(q, model, strategy)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 p-4 border-b border-slate-200 flex-shrink-0 bg-white">
        <div>
          <h2 className="font-semibold text-lg text-slate-900">Assistant RAG Oncologique</h2>
          <p className="text-xs text-slate-500">
            Basé sur les guidelines AMFROM 2024 · {Math.floor(messages.length / 2)} échanges
          </p>
        </div>

        {/* Always-visible model + strategy selectors */}
        <div className="flex items-end gap-3 flex-shrink-0">
          <div>
            <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Modèle</label>
            <div className="relative">
              <select value={model} onChange={e => setModel(e.target.value)}
                className="appearance-none bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-1.5 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 cursor-pointer">
                {MODELS.map(m => (
                  <option key={m.value} value={m.value} disabled={!modelEnabled(m.value)}>
                    {m.label}{!modelEnabled(m.value) ? ' (indisponible)' : ''}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Stratégie</label>
            <div className="relative">
              <select value={strategy} onChange={e => setStrategy(e.target.value)}
                className="appearance-none bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-1.5 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 cursor-pointer">
                {STRATEGIES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
          </div>
        </div>
      </div>

      {/* Messages / empty state */}
      {messages.length === 0 && !loading ? (
        /* ── Empty state: centered welcome + suggestion cards ── */
        <div className="flex-1 overflow-y-auto">
          <div className="min-h-full flex flex-col items-center justify-center max-w-2xl mx-auto px-6 py-10 text-center">
            <div className="w-14 h-14 rounded-2xl bg-medical-600 flex items-center justify-center mb-5 shadow-lg shadow-medical-600/20">
              <Bot className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 tracking-tight font-display">Comment puis-je vous aider ?</h3>
            <p className="text-sm text-slate-500 mt-2 max-w-md leading-relaxed">
              Posez une question sur les protocoles, diagnostics ou traitements oncologiques.
              Les réponses s’appuient uniquement sur les guidelines AMFROM 2024.
            </p>

            <div className="w-full mt-8 grid sm:grid-cols-3 gap-3">
              {SUGGESTED.map(({ icon: Icon, q }, i) => (
                <button key={i} onClick={() => handleSuggest(q)}
                  className="group flex flex-col items-start gap-3 p-4 rounded-xl bg-white border border-slate-200 text-left
                             hover:border-medical-300 hover:shadow-md transition-all duration-200">
                  <div className="w-9 h-9 rounded-lg bg-slate-100 group-hover:bg-medical-50 flex items-center justify-center transition-colors">
                    <Icon className="w-4 h-4 text-slate-500 group-hover:text-medical-600 transition-colors" />
                  </div>
                  <span className="text-[13px] font-medium text-slate-700 leading-snug">{q}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* ── Conversation ── */
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="px-6 py-4 border-t border-slate-200 flex-shrink-0 bg-white">
        <div className="flex gap-3">
          <input
            type="text" value={input} onChange={e => setInput(e.target.value)}
            placeholder="Posez votre question oncologique…" disabled={loading}
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900
                       placeholder-slate-400 font-medium focus:outline-none focus:ring-2 focus:ring-medical-500/20
                       focus:border-medical-500 disabled:opacity-60 transition-all"
          />
          <button type="submit" disabled={!input.trim() || loading} className="btn-primary px-4">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
