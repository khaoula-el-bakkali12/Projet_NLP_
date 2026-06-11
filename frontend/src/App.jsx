import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import Sidebar from './layouts/Sidebar'
import Snackbar from './components/Snackbar'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'
import HistoryPage from './pages/HistoryPage'
import DocumentsPage from './pages/DocumentsPage'
import StatisticsPage from './pages/StatisticsPage'
import BenchmarkPage from './pages/BenchmarkPage'
import EvaluatePage from './pages/EvaluatePage'
import ClassificationPage from './pages/ClassificationPage'
import HybridPage from './pages/HybridPage'
import JourneyPage from './pages/JourneyPage'
import ProfilePage from './pages/ProfilePage'
import { getHealth } from './api/client'

const PAGES = {
  chat:           ChatPage,
  classification: ClassificationPage,
  history:        HistoryPage,
  documents:      DocumentsPage,
  statistics:     StatisticsPage,
  benchmark:      BenchmarkPage,
  evaluate:       EvaluatePage,
  hybrid:         HybridPage,
  journey:        JourneyPage,
  profile:        ProfilePage,
}

function MainApp() {
  const { user, ready } = useAuth()
  const [activePage, setActivePage] = useState('chat')
  const [health, setHealth]         = useState(null)
  const [snack,  setSnack]          = useState({ message: '', type: 'success' })

  useEffect(() => {
    const fetch = () =>
      getHealth()
        .then(setHealth)
        .catch(() => setHealth({ status: 'error', dataset_size: 0, available_models: [] }))
    fetch()
    const id = setInterval(fetch, 30_000)
    return () => clearInterval(id)
  }, [])

  if (!ready) return null

  if (!user) {
    return (
      <>
        <LoginPage onSuccess={msg => setSnack({ message: msg, type: 'success' })} />
        <Snackbar {...snack} onClose={() => setSnack({ message: '', type: 'success' })} />
      </>
    )
  }

  const PageComponent = PAGES[activePage] ?? ChatPage
  const availableModels = (health?.available_models ?? []).map(s => s.split(' ')[0])

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: '#F8FAFC' }}>
      <Sidebar activePage={activePage} onNavigate={setActivePage} health={health} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageComponent onNavigate={setActivePage} availableModels={availableModels} />
      </main>
      <Snackbar {...snack} onClose={() => setSnack({ message: '', type: 'success' })} />
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  )
}
