import { useState, useEffect, useCallback } from 'react'
import {
  FolderOpen, Search, Upload, FileText, Tag, Filter, ChevronDown, X,
  Trash2, RefreshCw, HardDrive, FileUp, Layers, CheckCircle2
} from 'lucide-react'
import { getDocuments, getCancerTypes, getCategories, getUploadedDocuments, deleteUploadedDocument } from '../api/client'
import PDFUploadZone from '../components/PDFUploadZone'
import ConfirmModal from '../components/ConfirmModal'

export default function DocumentsPage() {
  const [tab,          setTab]          = useState('browse')
  const [docs,         setDocs]         = useState([])
  const [cancerTypes,  setCancerTypes]  = useState([])
  const [categories,   setCategories]   = useState([])
  const [loading,      setLoading]      = useState(true)
  const [query,        setQuery]        = useState('')
  const [filterCancer, setFilterCancer] = useState('')
  const [filterCat,    setFilterCat]    = useState('')
  const [selected,     setSelected]     = useState(null)

  const [uploadedDocs,    setUploadedDocs]    = useState([])
  const [uploadedLoading, setUploadedLoading] = useState(false)
  const [deletingFile,    setDeletingFile]    = useState(null)
  const [confirm,         setConfirm]         = useState({ open: false, filename: null })

  useEffect(() => {
    Promise.all([getCancerTypes(), getCategories()])
      .then(([ct, ca]) => { setCancerTypes(ct); setCategories(ca) })
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    getDocuments({ type_cancer: filterCancer || undefined, categorie: filterCat || undefined, limit: 200 })
      .then(data => setDocs(Array.isArray(data) ? data : data.documents ?? []))
      .catch(() => setDocs([]))
      .finally(() => setLoading(false))
  }, [filterCancer, filterCat])

  const fetchUploadedDocs = useCallback(async () => {
    setUploadedLoading(true)
    try {
      const data = await getUploadedDocuments()
      setUploadedDocs(Array.isArray(data) ? data : [])
    } catch {
      setUploadedDocs([])
    } finally {
      setUploadedLoading(false)
    }
  }, [])

  useEffect(() => {
    if (tab === 'upload') fetchUploadedDocs()
  }, [tab, fetchUploadedDocs])

  const handleUploadSuccess = useCallback(() => {
    fetchUploadedDocs()
    getDocuments({ limit: 200 })
      .then(data => setDocs(Array.isArray(data) ? data : data.documents ?? []))
      .catch(() => {})
  }, [fetchUploadedDocs])

  const handleDeleteUploaded = async (filename) => {
    setDeletingFile(filename)
    try {
      await deleteUploadedDocument(filename)
      setUploadedDocs(prev => prev.filter(f => f.filename !== filename))
      getDocuments({ limit: 200 })
        .then(data => setDocs(Array.isArray(data) ? data : data.documents ?? []))
        .catch(() => {})
    } catch (err) {
      alert(`Erreur lors de la suppression : ${err.message}`)
    } finally {
      setDeletingFile(null)
    }
  }

  const filtered = docs.filter(d =>
    !query ||
    d.titre?.toLowerCase().includes(query.toLowerCase()) ||
    d.type_cancer?.toLowerCase().includes(query.toLowerCase()) ||
    d.contenu?.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="p-6 md:p-10 w-full h-full overflow-y-auto space-y-8">

      {/* ── Page header ── */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <FolderOpen className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-semibold text-2xl text-slate-900 font-display tracking-tight">Documents</h2>
          <p className="text-slate-500 mt-0.5 text-sm">Base de connaissances AMFROM 2024 · {docs.length} fiches</p>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="flex bg-slate-100 p-1 rounded-lg w-fit">
        {[['browse', 'Parcourir', FileText], ['upload', 'Ajouter un document', Upload]].map(([id, label, Icon]) => (
          <button key={id} onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-semibold transition-colors
              ${tab === id ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════════
          UPLOAD TAB
      ══════════════════════════════════════════════════════════ */}
      {tab === 'upload' && (
        <div className="grid lg:grid-cols-[1fr_380px] gap-6 items-stretch">

          {/* ── Left column: import form ── */}
          <div className="space-y-4">
            {/* Card: upload zone */}
            <div className="glass-card overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
                <div className="w-7 h-7 rounded-md bg-medical-50 flex items-center justify-center">
                  <Upload className="w-3.5 h-3.5 text-medical-600" />
                </div>
                <h3 className="font-semibold text-slate-900 text-sm">Importer un document</h3>
              </div>
              <div className="p-6">
                <PDFUploadZone onSuccess={handleUploadSuccess} />
              </div>
            </div>

          </div>

          {/* ── Right column: uploaded documents ── */}
          <div className="glass-card overflow-hidden">
            {/* Card header */}
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-md bg-slate-100 flex items-center justify-center">
                  <Layers className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <h3 className="font-semibold text-slate-900 text-sm">Documents importés</h3>
                {uploadedDocs.length > 0 && (
                  <span className="ml-1 px-2 py-0.5 rounded-full bg-medical-50 text-medical-700 text-xs font-bold">
                    {uploadedDocs.length}
                  </span>
                )}
              </div>
              <button onClick={fetchUploadedDocs} title="Rafraîchir"
                className="p-1.5 text-slate-400 hover:text-medical-600 hover:bg-slate-100 rounded-lg transition-colors">
                <RefreshCw className={`w-3.5 h-3.5 ${uploadedLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {/* Card body */}
            <div className="divide-y divide-slate-50">
              {/* Loading */}
              {uploadedLoading && uploadedDocs.length === 0 && (
                <div className="py-16 text-center">
                  <RefreshCw className="w-5 h-5 mx-auto mb-2 animate-spin text-slate-300" />
                  <p className="text-xs text-slate-400">Chargement…</p>
                </div>
              )}

              {/* Empty state */}
              {!uploadedLoading && uploadedDocs.length === 0 && (
                <div className="py-16 text-center px-6">
                  <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center mx-auto mb-3">
                    <HardDrive className="w-5 h-5 text-slate-300" />
                  </div>
                  <p className="text-sm font-medium text-slate-500">Aucun document importé</p>
                  <p className="text-xs text-slate-400 mt-1">Les fichiers que vous importez apparaîtront ici.</p>
                </div>
              )}

              {/* Document rows */}
              {uploadedDocs.map(doc => {
                const isPdf = doc.filename.toLowerCase().endsWith('.pdf')
                const isDeleting = deletingFile === doc.filename
                return (
                  <div key={doc.filename}
                    className={`px-6 py-4 flex items-start gap-3 group transition-colors hover:bg-slate-50/70 ${isDeleting ? 'opacity-50' : ''}`}>
                    {/* Icon */}
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5
                      ${isPdf ? 'bg-blue-50' : 'bg-emerald-50'}`}>
                      <FileText className={`w-4 h-4 ${isPdf ? 'text-blue-500' : 'text-emerald-500'}`} />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-slate-800 truncate leading-tight" title={doc.filename}>
                        {doc.filename}
                      </p>
                      <div className="flex items-center flex-wrap gap-x-2 gap-y-1 mt-1.5">
                        <span className="text-[11px] text-slate-400">
                          {(doc.size / 1024).toFixed(0)} KB
                        </span>
                        <span className="text-slate-200">·</span>
                        <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-1.5 py-0.5 rounded-md
                          ${doc.chunks > 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>
                          {doc.chunks > 0
                            ? <><CheckCircle2 className="w-2.5 h-2.5" /> {doc.chunks} chunks</>
                            : 'Non indexé'}
                        </span>
                        <span className="text-slate-200">·</span>
                        <span className="text-[11px] text-slate-400">
                          {new Date(doc.uploaded_at).toLocaleDateString('fr-FR', {
                            day: '2-digit', month: 'short'
                          })}
                        </span>
                      </div>
                    </div>

                    {/* Delete */}
                    <button
                      onClick={() => setConfirm({ open: true, filename: doc.filename })}
                      disabled={isDeleting}
                      title="Supprimer ce document"
                      className="mt-0.5 p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50 flex-shrink-0">
                      {isDeleting
                        ? <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        : <Trash2 className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                )
              })}
            </div>

            {/* Card footer with total chunks */}
            {uploadedDocs.length > 0 && (
              <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-400">
                  {uploadedDocs.reduce((s, d) => s + d.chunks, 0)} chunks ajoutés à la base
                </span>
                <span className="text-xs text-slate-400">
                  {(uploadedDocs.reduce((s, d) => s + d.size, 0) / 1024).toFixed(0)} KB total
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      <ConfirmModal
        open={confirm.open}
        title="Supprimer le document"
        message={`Retirer "${confirm.filename}" de l'index FAISS + BM25 et supprimer le fichier ? Cette action est irréversible.`}
        confirmLabel="Supprimer"
        onConfirm={() => handleDeleteUploaded(confirm.filename)}
        onCancel={() => setConfirm({ open: false, filename: null })}
      />

      {/* ══════════════════════════════════════════════════════════
          BROWSE TAB
      ══════════════════════════════════════════════════════════ */}
      {tab === 'browse' && (
        <>
          <div className="flex flex-wrap gap-3">
            <div className="relative group flex-1 min-w-[200px] max-w-xs">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-medical-600 transition-colors" />
              <input type="text" value={query} onChange={e => setQuery(e.target.value)}
                placeholder="Rechercher…"
                className="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 placeholder-slate-400 outline-none transition-colors" />
            </div>
            <FilterSelect value={filterCancer} onChange={setFilterCancer} options={cancerTypes} placeholder="Type de cancer" icon={Filter} />
            <FilterSelect value={filterCat}    onChange={setFilterCat}    options={categories}  placeholder="Catégorie"      icon={Tag}    />
            {(filterCancer || filterCat) && (
              <button onClick={() => { setFilterCancer(''); setFilterCat('') }}
                className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-red-500 px-3 py-2 bg-white border border-slate-200 rounded-lg transition-colors">
                <X className="w-3 h-3" /> Réinitialiser
              </button>
            )}
          </div>

          {selected && (
            <div className="glass-card p-6 border-l-2 border-l-medical-500">
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex flex-wrap gap-1.5">
                  {selected.categorie   && <span className="badge">{selected.categorie}</span>}
                  {selected.type_cancer && <span className="badge">{selected.type_cancer}</span>}
                </div>
                <button onClick={() => setSelected(null)} className="text-slate-400 hover:text-slate-600 text-xs font-medium shrink-0">Fermer ×</button>
              </div>
              <h3 className="font-semibold text-lg text-slate-900 mb-3">{selected.titre || selected.id}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{selected.contenu}</p>
              {selected.mots_cles?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-4">
                  {selected.mots_cles.map(k => <span key={k} className="badge">{k}</span>)}
                </div>
              )}
            </div>
          )}

          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="glass-card p-5 h-40 animate-pulse">
                  <div className="h-3 bg-slate-200 rounded w-1/3 mb-3" />
                  <div className="h-4 bg-slate-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-slate-100 rounded w-full mb-1" />
                  <div className="h-3 bg-slate-100 rounded w-5/6" />
                </div>
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="glass-card p-16 text-center text-slate-500 text-sm">
              <FolderOpen className="w-8 h-8 mx-auto mb-3 text-slate-300" />
              Aucun document trouvé.
            </div>
          ) : (
            <>
              <p className="text-xs text-slate-400 font-medium">{filtered.length} document{filtered.length > 1 ? 's' : ''}</p>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filtered.map(doc => (
                  <button key={doc.id} onClick={() => setSelected(selected?.id === doc.id ? null : doc)}
                    className={`glass-card p-5 text-left transition-colors cursor-pointer hover:border-slate-300
                      ${selected?.id === doc.id ? 'border-medical-500 ring-1 ring-medical-500' : ''}`}>
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {doc.categorie   && <span className="badge text-[10px]">{doc.categorie}</span>}
                      {doc.type_cancer && <span className="badge text-[10px]">{doc.type_cancer}</span>}
                    </div>
                    <h3 className="font-semibold text-sm text-slate-900 mb-1.5 line-clamp-2">{doc.titre || doc.id}</h3>
                    <p className="text-xs text-slate-500 line-clamp-3 leading-relaxed">{doc.contenu}</p>
                    {doc.mots_cles?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {doc.mots_cles.slice(0, 3).map(k => (
                          <span key={k} className="text-[9px] font-medium text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">{k}</span>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

function FilterSelect({ value, onChange, options, placeholder, icon: Icon }) {
  return (
    <div className="relative">
      <Icon className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
      <select value={value} onChange={e => onChange(e.target.value)}
        className="appearance-none bg-white border border-slate-200 rounded-lg pl-8 pr-8 py-2.5 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-medical-500/20 focus:border-medical-500 cursor-pointer outline-none transition-colors">
        <option value="">{placeholder}</option>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
      <ChevronDown className="w-3.5 h-3.5 absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
    </div>
  )
}
