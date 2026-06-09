import { Bot } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-indigo-100 border border-indigo-200">
        <Bot className="w-4 h-4 text-indigo-600" />
      </div>
      <div className="msg-ai flex items-center gap-1.5 py-4">
        <span className="w-2 h-2 bg-medical-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-medical-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-medical-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  )
}
