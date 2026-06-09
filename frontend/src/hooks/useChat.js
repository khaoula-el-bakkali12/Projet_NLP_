import { useState, useCallback } from 'react'
import { postAsk, saveHistoryItem } from '../api/client'
import { useAuth } from '../context/AuthContext'

export function useChat() {
  const { user }   = useAuth()
  const [messages, setMessages] = useState([])
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState(null)

  const sendMessage = useCallback(async (question, model = 'model_a', strategy = 'zero_shot') => {
    setError(null)

    const userMsg = { id: `u-${Date.now()}`, role: 'user', content: question }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const data = await postAsk({ question, model_name: model, prompt_template: strategy, alpha: 0.3 })

      const aiMsg = {
        id:       `a-${Date.now()}`,
        role:     'assistant',
        content:  data.response || 'Aucune réponse générée.',
        sources:  data.sources  || [],
        model:    data.model    || model,
        latency:  data.latency,
        safe:     data.safe,
        intent:   data.intent,
        language: data.language,
      }
      setMessages(prev => [...prev, aiMsg])

      // Persist to server-side SQLite (survives logout + backend restart)
      if (user?.username && data.response) {
        saveHistoryItem(user.username, {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          question,
          answer: data.response,
          model: data.model || model,
          sources: data.sources || [],
        }).catch(e => console.error('History save failed:', e))
      }
    } catch (err) {
      setError(err.message)
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`, role: 'assistant',
        content: `Erreur : ${err.message}`,
        sources: [], model: 'error',
      }])
    } finally {
      setLoading(false)
    }
  }, [user])

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, loading, error, sendMessage, clearChat }
}
