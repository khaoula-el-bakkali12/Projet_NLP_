import sys
import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Resolve project root so all sibling modules are importable ──────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLM_DIR = os.path.join(ROOT, "LLM_cmp")
for p in [ROOT, LLM_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from data_pipeline.retrieval import load_retrieval_resources
from data_pipeline.nlp_query_processor import get_sbert_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm caches on startup so the first request isn't slow."""
    print("[startup] Pre-warming retrieval resources and SBERT model...")
    load_retrieval_resources()
    get_sbert_model()
    print("[startup] All resources loaded -- API ready.")
    yield


app = FastAPI(
    title="Oncology RAG API",
    description="Medical oncology assistant — RAG pipeline (FAISS + BM25 + local LLM)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
from backend.routers import ask, retrieve, documents, classify, benchmark
from backend.routers.auth       import router as auth_router
from backend.routers.upload_doc import router as upload_router
from backend.routers.history    import router as history_router
from backend.routers.hybrid     import router as hybrid_router

app.include_router(ask.router,       prefix="/api")
app.include_router(retrieve.router,  prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(classify.router,  prefix="/api")
app.include_router(benchmark.router, prefix="/api")
app.include_router(auth_router,      prefix="/api")
app.include_router(upload_router,    prefix="/api")
app.include_router(history_router,   prefix="/api")
app.include_router(hybrid_router,    prefix="/api")


# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    dataset_path = os.path.join(ROOT, "data", "raw", "dataset_oncologie_FINAL_v6.json")
    try:
        with open(dataset_path, encoding="utf-8") as f:
            dataset = json.load(f)
        dataset_size = len(dataset)
    except Exception:
        dataset_size = -1

    return {
        "status": "ok",
        "dataset_size": dataset_size,
        "available_models": ["model_a (flan-t5-base)", "model_b (Qwen2.5-1.5B-Instruct)", "model_c (TinyLlama-1.1B)"],
    }
