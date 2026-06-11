import { Bot } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div
        className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center"
        style={{
          background: 'linear-gradient(135deg, #060D1B 0%, #0F2444 100%)',
          boxShadow: '0 4px 14px rgba(6,13,27,0.28)',
        }}
      >
        <Bot style={{ width: 15, height: 15, color: '#93C5FD' }} />
      </div>

      <div
        className="msg-ai flex items-center gap-2 px-5 py-4"
      >
        {[0, 160, 320].map(delay => (
          <span
            key={delay}
            className="w-2 h-2 rounded-full animate-dot"
            style={{
              background: 'linear-gradient(135deg, #1A56DB, #06B6D4)',
              animationDelay: `${delay}ms`,
            }}
          />
        ))}
      </div>
    </div>
  )
}
