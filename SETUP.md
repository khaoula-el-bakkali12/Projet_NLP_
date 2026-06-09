# Installation & Lancement

Assistant médical en oncologie — pipeline RAG (FAISS + BM25 + LLM locaux) avec API FastAPI et interface React.

---

## 1. Prérequis

| Outil | Version | Remarque |
|-------|---------|----------|
| Python | 3.10 – 3.12 | pour le pipeline, l'API et les LLM |
| Node.js | 18+ | pour l'interface React (Vite) |
| RAM | 8 Go min. (16 Go conseillé) | les LLM tournent en float32 sur CPU |
| Connexion internet | requise au 1er lancement | téléchargement des modèles HuggingFace (~5 Go, une seule fois) |
| GPU NVIDIA | optionnel | accélère la génération ; sinon tout tourne sur CPU |

> **Sans GPU (Intel / macOS)** : le projet fonctionne entièrement sur CPU. La génération est simplement plus lente (~20–60 s par réponse). Aucune configuration supplémentaire n'est nécessaire.

---

## 2. Backend (API + RAG + LLM)

Toutes les commandes se lancent **depuis la racine du projet**.

### 2.1 — Créer et activer un environnement virtuel

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2.2 — Installer les dépendances Python
```bash
pip install -r requirements.txt
pip install -r LLM_cmp/requirements_local.txt
pip install -r backend/requirements_backend.txt
```

> **GPU NVIDIA uniquement** : pour accélérer Qwen, dé-commentez `bitsandbytes` dans
> `LLM_cmp/requirements_local.txt` puis installez la version CUDA de PyTorch :
> `pip install torch --index-url https://download.pytorch.org/whl/cu121`

### 2.3 — Construire les index de recherche (FAISS + BM25)

Les index ne sont pas versionnés ; il faut les générer une fois :
```bash
python -m data_pipeline.indexer
```
Cela crée `data/indexes/faiss_index.bin`, `bm25_index.pkl` et `index_metadata.json`.

### 2.4 — Lancer l'API
```bash
uvicorn backend.main:app --reload --port 8000
```
- L'API écoute sur **http://localhost:8000**
- Au **premier lancement**, les 3 modèles se téléchargent depuis HuggingFace (~5 Go). Les lancements suivants utilisent le cache local.
- Vérifier que l'API répond : http://localhost:8000/api/health

---

## 3. Frontend (interface React)

Dans un **second terminal** :
```bash
cd frontend
npm install
npm run dev
```
- Interface accessible sur **http://localhost:5173**
- Le serveur Vite redirige automatiquement `/api` vers le backend (port 8000) — aucune configuration nécessaire.

---

## 4. Récapitulatif — démarrage rapide

```bash
# Terminal 1 — Backend
python -m venv .venv
source .venv/bin/activate            # Windows : .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r LLM_cmp/requirements_local.txt
pip install -r backend/requirements_backend.txt
python -m data_pipeline.indexer
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

Ouvrir **http://localhost:5173** puis créer un compte pour accéder à l'assistant.

---

## 5. Modèles utilisés

| Slot | Modèle | Type | Taille |
|------|--------|------|--------|
| model_a | `google/flan-t5-base` | Seq2Seq | 250M |
| model_b | `Qwen/Qwen2.5-1.5B-Instruct` | Causal (instruct) | 1.5B |
| model_c | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | Causal | 1.1B |

Le téléchargement est automatique au premier appel de chaque modèle.

---

## 6. Structure du projet

```
data_pipeline/   indexation + recherche hybride (FAISS + BM25) + NLP
LLM_cmp/         module LLM : génération, prompts, benchmarking
backend/         API FastAPI (RAG, auth, historique, upload, benchmark)
frontend/        interface React + Vite + Tailwind
data/raw/        dataset oncologique + index
tests/           tests unitaires (pytest)
```

## 7. Tests
```bash
pytest
```
