import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120_000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  res => res,
  err => {
    const raw =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Erreur réseau inconnue'
    const message = typeof raw === 'string' ? raw : JSON.stringify(raw)
    return Promise.reject(new Error(message))
  }
)

export const getHealth      = ()     => api.get('/health').then(r => r.data)
// 10-minute timeout for /ask — phi-2 and TinyLlama download on first use
export const postAsk        = (body) => api.post('/ask', body, { timeout: 600_000 }).then(r => r.data)
export const postRetrieve   = (body) => api.post('/retrieve', body).then(r => r.data)
export const postClassify   = (body) => api.post('/classify', body).then(r => r.data)
export const postClassifyCancer = (body) => api.post('/classify-cancer', body).then(r => r.data)
export const getDocuments   = (p)    => api.get('/documents', { params: p }).then(r => r.data)
export const getDocument    = (id)   => api.get(`/documents/${id}`).then(r => r.data)
export const getCancerTypes = ()     => api.get('/cancer-types').then(r => r.data)
export const getStatistics  = ()     => api.get('/statistics').then(r => r.data)
export const getCategories  = ()     => api.get('/categories').then(r => r.data)
export const getBenchmark   = ()     => api.get('/benchmark/results').then(r => r.data)
// Alias used by EvaluatePage — retrieval alpha-sweep evaluation results.
export const getBenchmarkResults = () => api.get('/benchmark/results').then(r => r.data)
export const getLlmBenchmark = ()    => api.get('/benchmark/llm').then(r => r.data)
// LLM benchmark runs 3 models × N questions on CPU — allow up to 30 min.
export const runLlmBenchmark = (limit = 2, template = 'zero_shot') =>
  api.post('/benchmark/run', null, { params: { limit, template }, timeout: 1_800_000 }).then(r => r.data)
// One question × 3 models — allow up to 5 min (first call also loads models).
export const compareModels = (body) =>
  api.post('/benchmark/compare', body, { timeout: 300_000 }).then(r => r.data)
// One question × 3 prompt strategies (Qwen only) — allow up to 5 min.
export const comparePrompts = (body) =>
  api.post('/benchmark/compare-prompts', body, { timeout: 300_000 }).then(r => r.data)

export const uploadDocument = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload-document', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: e => {
      if (e.total && onProgress) onProgress(Math.round(e.loaded * 100 / e.total))
    },
  }).then(r => r.data)
}

export const authLogin    = (body) => api.post('/auth/login',    body).then(r => r.data)
export const authRegister = (body) => api.post('/auth/register', body).then(r => r.data)

// ── Hybrid treatment (5 modality retrievals + LLM synthesis) ───────────────
// Allow up to 10 min — loads Qwen on first call then runs 5 retrievals.
export const postHybridTreatment = (body) =>
  api.post('/hybrid-treatment', body, { timeout: 600_000 }).then(r => r.data)

// ── Uploaded documents ─────────────────────────────────────────────────────
export const getUploadedDocuments    = ()         => api.get('/uploaded-documents').then(r => r.data)
export const deleteUploadedDocument  = (filename) => api.delete(`/uploaded-documents/${encodeURIComponent(filename)}`).then(r => r.data)

// ── History (server-side, persists across logout/restart) ──────────────────
export const getHistory        = (username)         => api.get('/history', { params: { username } }).then(r => r.data)
export const saveHistoryItem   = (username, item)   => api.post('/history', { username, item }).then(r => r.data)
export const deleteHistoryItem = (username, itemId) => api.delete(`/history/${itemId}`, { params: { username } }).then(r => r.data)
export const clearHistory      = (username)         => api.delete('/history', { params: { username } }).then(r => r.data)

export default api
