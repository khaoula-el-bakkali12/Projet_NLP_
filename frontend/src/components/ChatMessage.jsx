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
      <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center shadow-sm
                       ${isUser ? 'bg-blue-100 border border-blue-200' : 'bg-indigo-100 border border-indigo-200'}`}>
        {isUser
          ? <User className="w-4 h-4 text-blue-600" />
          : <Bot  className="w-4 h-4 text-indigo-600" />}
      </div>

      {/* Bubble + metadata */}
      <div className={`flex flex-col gap-1.5 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={isUser ? 'msg-user' : 'msg-ai'}>
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-slate prose-sm max-w-none
                            prose-p:leading-relaxed prose-p:my-1
                            prose-strong:text-slate-900
                            prose-code:text-indigo-600 prose-code:bg-indigo-50 prose-code:px-1 prose-code:rounded
                            prose-headings:text-slate-900 prose-li:my-0.5"
                 dir={message.language === 'arabic' ? 'rtl' : 'ltr'}>
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Metadata bar */}
        {!isUser && message.model && message.model !== 'system' && (
          <div className="flex flex-wrap items-center gap-2 px-1 mt-1">
            {message.model && (
              <span className="badge">
                <Cpu className="w-3 h-3" /> {MODEL_NAMES[message.model] || message.model}
              </span>
            )}
            {message.latency != null && (
              <span className="badge">
                <Clock className="w-3 h-3" /> {message.latency.toFixed(1)}s
              </span>
            )}
            {message.safe === false && (
              <span className="badge bg-red-50 text-red-600 border-red-200"><ShieldAlert className="w-3 h-3" /> Avertissement</span>
            )}
            {message.sources?.length > 0 && (
              <button
                onClick={() => setShowSources(v => !v)}
                className="badge hover:bg-slate-200 hover:text-slate-800 cursor-pointer transition-colors"
              >
                {showSources ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
              </button>
            )}
          </div>
        )}

        {/* Sources panel */}
        {!isUser && showSources && message.sources?.length > 0 && (
          <div className="w-full mt-2 rounded-xl border border-slate-200 bg-white overflow-hidden animate-slide-up">
            {/* Panel header */}
            <div className="px-4 py-2.5 border-b border-slate-100 bg-slate-50/60 flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-xs font-semibold text-slate-600">Sources</span>
              <span className="text-xs text-slate-400">
                · {message.sources.length} document{message.sources.length > 1 ? 's' : ''} de la base
              </span>
            </div>

            {/* Citation rows */}
            <div className="divide-y divide-slate-100">
              {message.sources.map((doc, i) => (
                <div key={doc.id || i} className="px-4 py-3 flex items-start gap-3 hover:bg-slate-50/60 transition-colors">
                  {/* Rank */}
                  <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-md bg-slate-100 text-slate-500 text-[10px] font-bold flex items-center justify-center tabular-nums">
                    {i + 1}
                  </span>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-xs font-semibold text-slate-800 leading-snug">{doc.titre || doc.id}</p>
                      <Relevance score={doc.score_final} />
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed line-clamp-2 mt-1">{doc.contenu}</p>
                    {(doc.type_cancer || doc.categorie) && (
                      <div className="flex gap-1.5 mt-2 flex-wrap">
                        {doc.type_cancer && <span className="text-[10px] font-medium text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{doc.type_cancer}</span>}
                        {doc.categorie  && <span className="text-[10px] font-medium text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{doc.categorie}</span>}
                      </div>
                    )}
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

// Subtle, monochrome relevance indicator — a thin bar + muted percentage,
// instead of the previous traffic-light (green/amber/red) score pill.
function Relevance({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  return (
    <div className="flex items-center gap-1.5 flex-shrink-0 pt-0.5">
      <div className="w-10 h-1 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-full bg-medical-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] font-semibold text-slate-400 tabular-nums w-7 text-right">{pct}%</span>
    </div>
  )
}
