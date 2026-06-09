import { createContext, useCallback, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)
const STORAGE_KEY = 'oncologia_auth'

export function AuthProvider({ children }) {
  const [user,  setUser]  = useState(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) setUser(JSON.parse(stored))
    } catch {
      localStorage.removeItem(STORAGE_KEY)
    }
    setReady(true)
  }, [])

  const login = useCallback((username, token) => {
    const u = { username, token }
    setUser(u)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u))
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  const updateUser = useCallback((newUsername) => {
    setUser(prev => {
      const updated = { ...prev, username: newUsername }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
      return updated
    })
  }, [])

  return (
    <AuthContext.Provider value={{ user, ready, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
