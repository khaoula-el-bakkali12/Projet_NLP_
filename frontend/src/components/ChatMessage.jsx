import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Bot, User, BookOpen, ChevronDown, ChevronUp, Cpu, ShieldAlert, Clock } from 'lucide-react'

const MODEL_NAMES = {
  model_a: 'flan-t5-base',
  model_b: 'Qwen2.5-1.5B',
  model_c: 'TinyLlama-1.1B',
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const [showSources, setShowSources] = useState(false)

  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>

      {/* Avatar */}
      <div
        className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center"
        style={isUser ? {
          background: 'linear-gradient(135deg, #1d4ed8 0%, #2563EB 100%)',
          boxShadow: '0 4px 14px rgba(29,78,216,0.38)',
        } : {
          background: 'linear-gradient(135deg, #060D1B 0%, #0F2444 100%)',
          boxShadow: '0 4px 14px rgba(6,13,27,0.28)',
        }}
      >
        {isUser
          ? <User style={{ width: 15, height: 15, color: 'white' }} />
          : <Bot  style={{ width: 15, height: 15, color: '#93C5FD' }} />
        }
      </div>

      {/* Bubble + metadata */}
      <div className={`flex flex-col gap-2 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={isUser ? 'msg-user' : 'msg-ai'}>
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div
              className="prose prose-slate prose-sm max-w-none
                          prose-p:leading-relaxed prose-p:my-1
                          prose-strong:text-[#0F172A] prose-strong:font-semibold
                          prose-code:text-[#2563eb] prose-code:bg-[#EFF6FF] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:text-[12px]
                          prose-headings:text-[#0F172A] prose-headings:font-bold
                          prose-li:my-0.5 prose-ol:my-1 prose-ul:my-1"
              dir={message.language === 'arabic' ? 'rtl' : 'ltr'}
            >
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Metadata bar */}
        {!isUser && message.model && message.model !== 'system' && (
          <div className="flex flex-wrap items-center gap-1.5 px-1">
            {message.model && (
              <span className="badge">
                <Cpu style={{ width: 10, height: 10 }} />
                {MODEL_NAMES[message.model] || message.model}
              </span>
            )}
            {message.latency != null && (
              <span className="badge">
                <Clock style={{ width: 10, height: 10 }} />
                {message.latency.toFixed(1)}s
              </span>
            )}
            {message.safe === false && (
              <span className="badge"
                    style={{ background: '#FEF2F2', color: '#DC2626', borderColor: '#FECACA' }}>
                <ShieldAlert style={{ width: 10, height: 10 }} />
                Avertissement
              </span>
            )}
            {message.sources?.length > 0 && (
              <button
                onClick={() => setShowSources(v => !v)}
                className="badge cursor-pointer"
                style={{ transition: 'all 0.15s ease' }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = '#EFF6FF'
                  e.currentTarget.style.color = '#1d4ed8'
                  e.currentTarget.style.borderColor = '#BFDBFE'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = '#F8FAFC'
                  e.currentTarget.style.color = '#64748B'
                  e.currentTarget.style.borderColor = '#E8EDF2'
                }}
              >
                {showSources
                  ? <ChevronUp   style={{ width: 10, height: 10 }} />
                  : <ChevronDown style={{ width: 10, height: 10 }} />}
                {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
              </button>
            )}
          </div>
        )}

        {/* Sources panel */}
        {!isUser && showSources && message.sources?.length > 0 && (
          <div
            className="w-full mt-1 rounded-2xl overflow-hidden animate-slide-up"
            style={{
              border: '1.5px solid #E8EDF2',
              background: 'white',
              boxShadow: '0 8px 28px rgba(0,0,0,0.07), 0 2px 6px rgba(0,0,0,0.04)',
            }}
          >
            <div
              className="px-4 py-3 flex items-center gap-2"
              style={{ borderBottom: '1px solid #F0F4F8', background: '#F8FAFC' }}
            >
              <BookOpen style={{ width: 13, height: 13, color: '#94A3B8' }} />
              <span className="text-xs font-bold text-[#475569]">Sources</span>
              <span className="text-xs text-[#94A3B8]">
                · {message.sources.length} document{message.sources.length > 1 ? 's' : ''}
              </span>
            </div>

            <div className="divide-y" style={{ borderColor: '#F0F4F8' }}>
              {message.sources.map((doc, i) => (
                <div
                  key={doc.id || i}
                  className="px-4 py-3 flex items-start gap-3 transition-colors"
                  onMouseEnter={e => e.currentTarget.style.background = '#F8FAFC'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <span
                    className="mt-0.5 flex-shrink-0 w-6 h-6 rounded-lg font-bold flex items-center justify-center text-[10px] tabular-nums"
                    style={{
                      background: '#EFF6FF',
                      color: '#2563EB',
                      border: '1px solid #BFDBFE',
                    }}
                  >
                    {i + 1}
                  </span>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-xs font-semibold text-[#0F172A] leading-snug">
                        {doc.titre || doc.id}
                      </p>
                      <Relevance score={doc.score_final} />
                    </div>
                    <p className="text-xs text-[#64748B] leading-relaxed line-clamp-2 mt-1">
                      {doc.contenu}
                    </p>
                    <div className="flex gap-1.5 mt-2 flex-wrap">
                      {doc.type_cancer && (
                        <span className="text-[10px] font-semibold text-[#475569] bg-[#F1F5F9] px-2 py-0.5 rounded-md">
                          {doc.type_cancer}
                        </span>
                      )}
                      {doc.categorie && (
                        <span className="text-[10px] font-semibold text-[#475569] bg-[#F1F5F9] px-2 py-0.5 rounded-md">
                          {doc.categorie}
                        </span>
                      )}
                      {doc.reference && (
                        <span className="text-[10px] font-bold text-[#2563EB] bg-[#EFF6FF] px-2 py-0.5 rounded-md"
                              style={{ border: '1px solid #BFDBFE' }}>
                          {doc.reference}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Relevance({ score }) {
  if (score == null) return null
  const pct   = Math.round(score * 100)
  const color = pct >= 70 ? '#2563EB' : pct >= 45 ? '#F59E0B' : '#94A3B8'
  return (
    <div className="flex items-center gap-1.5 flex-shrink-0 pt-0.5">
      <div className="w-12 h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, background: color, transition: 'width 0.4s ease' }}
        />
      </div>
      <span className="text-[10px] font-bold text-[#94A3B8] tabular-nums w-7 text-right">
        {pct}%
      </span>
    </div>
  )
}
