import { useState } from 'react'
import { User, Lock, Save, ShieldCheck, LogOut, KeyRound, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuth()
  const [username,        setUsername]        = useState(user?.username || '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword,     setNewPassword]     = useState('')
  const [saving,          setSaving]          = useState(false)
  const [message,         setMessage]         = useState({ text: '', type: '' })

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setMessage({ text: '', type: '' })

    const changingUsername = username.trim() !== user.username
    const changingPassword = Boolean(newPassword)

    if (!changingUsername && !changingPassword) {
      setMessage({ text: 'Aucune modification détectée.', type: 'error' })
      setSaving(false)
      return
    }
    if (!currentPassword) {
      setMessage({ text: 'Le mot de passe actuel est requis pour toute modification.', type: 'error' })
      setSaving(false)
      return
    }

    try {
      const res = await api.put('/auth/profile', {
        username:         user.username,
        current_password: currentPassword,
        new_username:     changingUsername ? username.trim() : undefined,
        new_password:     changingPassword ? newPassword     : undefined,
      })
      if (res.data.username !== user.username) updateUser(res.data.username)
      setMessage({ text: res.data.message || 'Profil mis à jour avec succès.', type: 'success' })
      setCurrentPassword('')
      setNewPassword('')
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Erreur lors de la mise à jour.'
      setMessage({ text: detail, type: 'error' })
    } finally {
      setSaving(false)
    }
  }

  const inputClass = "w-full bg-white border border-slate-200 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 transition-colors outline-none placeholder-slate-400"

  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto space-y-8">

      {/* ── Header ── */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 font-display tracking-tight">Mon Profil</h2>
          <p className="text-slate-400 mt-0.5 text-sm">Gérez vos informations et votre sécurité.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 items-start">

        {/* ── Left: identity card ── */}
        <div className="glass-card overflow-hidden">
          {/* Banner */}
          <div className="h-24 bg-gradient-to-br from-medical-600 to-medical-700" />

          <div className="-mt-10 px-6 pb-6">
            {/* Avatar */}
            <div className="w-20 h-20 rounded-2xl bg-white border-4 border-white shadow-md shadow-slate-200 flex items-center justify-center mb-4">
              <span className="text-3xl font-bold text-medical-600 select-none">
                {username.charAt(0).toUpperCase()}
              </span>
            </div>

            <h3 className="font-bold text-lg text-slate-900 leading-tight">{username}</h3>
            <p className="text-sm text-slate-400 mt-0.5">Utilisateur OncologIA</p>

            <div className="mt-5 pt-5 border-t border-slate-100">
              <div className="flex items-center gap-2.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span className="text-sm font-medium text-slate-600">Compte vérifié et sécurisé</span>
              </div>
            </div>

            <button
              onClick={logout}
              className="mt-5 w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-red-600 hover:bg-red-50 border border-red-200 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Déconnexion
            </button>
          </div>
        </div>

        {/* ── Right: edit form ── */}
        <div className="glass-card overflow-hidden">
          <form onSubmit={handleSave}>

            {/* ── Alert banner ── */}
            {message.text && (
              <div className={`mx-6 mt-6 p-4 rounded-xl flex items-center gap-3 text-sm font-medium
                ${message.type === 'success'
                  ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
                  : 'bg-red-50 border border-red-200 text-red-600'}`}>
                {message.type === 'success'
                  ? <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  : <AlertCircle  className="w-4 h-4 flex-shrink-0" />}
                {message.text}
              </div>
            )}

            {/* ── Section: General ── */}
            <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-slate-100 flex items-center justify-center">
                <User className="w-3.5 h-3.5 text-slate-500" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm">Informations générales</h3>
            </div>

            <div className="p-6 border-b border-slate-100">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Nom d'utilisateur
              </label>
              <div className="relative group max-w-sm">
                <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-medical-600 transition-colors" />
                <input
                  type="text" value={username} onChange={e => setUsername(e.target.value)}
                  required minLength={3} className={inputClass}
                  placeholder="Votre identifiant"
                />
              </div>
              <p className="mt-2 text-xs text-slate-400">Minimum 3 caractères. Modifiera votre identifiant de connexion.</p>
            </div>

            {/* ── Section: Security ── */}
            <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-slate-100 flex items-center justify-center">
                <KeyRound className="w-3.5 h-3.5 text-slate-500" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm">Sécurité</h3>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Mot de passe actuel
                    <span className="ml-1 text-red-400 text-xs font-normal">requis</span>
                  </label>
                  <div className="relative group">
                    <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-medical-600 transition-colors" />
                    <input
                      type="password" value={currentPassword}
                      onChange={e => setCurrentPassword(e.target.value)}
                      placeholder="••••••••" className={inputClass}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Nouveau mot de passe
                    <span className="ml-1 text-slate-400 text-xs font-normal">optionnel</span>
                  </label>
                  <div className="relative group">
                    <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-medical-600 transition-colors" />
                    <input
                      type="password" value={newPassword}
                      onChange={e => setNewPassword(e.target.value)}
                      placeholder="••••••••" minLength={6} className={inputClass}
                    />
                  </div>
                  <p className="mt-2 text-xs text-slate-400">Minimum 6 caractères.</p>
                </div>
              </div>
            </div>

            {/* ── Footer / save ── */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
              <p className="text-xs text-slate-400">
                Le mot de passe actuel est toujours requis pour confirmer toute modification.
              </p>
              <button type="submit" disabled={saving || !username.trim()} className="btn-primary flex-shrink-0">
                {saving
                  ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  : <Save className="w-4 h-4" />}
                {saving ? 'Enregistrement…' : 'Enregistrer'}
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  )
}
