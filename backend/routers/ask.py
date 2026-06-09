"""
POST /api/ask — Full RAG pipeline endpoint.

LLM inference (especially phi-2) can take 10–30 seconds on a GTX 1050.
The endpoint does not set an explicit timeout; callers should handle their own.
"""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import AskRequest, AskResponse
from backend.services.pipeline import run_full_pipeline

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        return run_full_pipeline(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
