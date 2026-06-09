import json
import os
import sys
import time
from datetime import datetime
from typing import Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


def _cosine(a, b) -> float:
    """Cosine similarity between two embedding vectors, clamped to [0, 1]."""
    a = np.asarray(a, dtype="float32").ravel()
    b = np.asarray(b, dtype="float32").ravel()
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return max(0.0, min(1.0, float(np.dot(a, b) / (na * nb))))

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LLM_DIR = os.path.join(_ROOT, "LLM_cmp")
for _p in [_ROOT, _LLM_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

_EVAL_PATH = os.path.join(_ROOT, "evaluation_results.json")          # retrieval eval (alpha sweep)
_GOLD_PATH = os.path.join(_LLM_DIR, "benchmark_gold_standard.json")  # LLM gold standard
_LLM_RESULTS_PATH = os.path.join(_ROOT, "llm_benchmark_results.json")  # LLM benchmark output
_FULL_PATH = os.path.join(_ROOT, "llm_benchmark_full.json")          # full per-model detail


@router.get("/benchmark/results")
def benchmark_results():
    """Retrieval evaluation (alpha sweep, hit-rate, MRR)."""
    if not os.path.exists(_EVAL_PATH):
        raise HTTPException(
            status_code=404,
            detail="evaluation_results.json not found. Run evaluate_retrieval.py first.",
        )
    with open(_EVAL_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("/benchmark/gold-standard")
def gold_standard():
    if not os.path.exists(_GOLD_PATH):
        raise HTTPException(status_code=404, detail="benchmark_gold_standard.json not found.")
    with open(_GOLD_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("/benchmark/llm")
def llm_benchmark_results():
    """Saved LLM generation benchmark (BLEU/ROUGE-L/BERTScore/latency per model)."""
    if not os.path.exists(_LLM_RESULTS_PATH):
        raise HTTPException(
            status_code=404,
            detail="Aucun benchmark LLM enregistré. Lancez-le depuis la page Benchmark.",
        )
    with open(_LLM_RESULTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _make_retrieval_fn():
    """Build a retrieval_fn(question) -> list[Document] using the real RAG pipeline."""
    from data_pipeline.nlp_query_processor import encode_query
    from data_pipeline.retrieval import retrieve
    from backend.services.converter import retrieval_dicts_to_documents

    def retrieval_fn(question: str):
        vec = encode_query(question)
        result = retrieve(query_vector=vec, question=question, top_k=5, alpha=0.3)
        return retrieval_dicts_to_documents(result["top_k_docs"])

    return retrieval_fn


@router.post("/benchmark/run")
def run_llm_benchmark(
    limit: int = Query(2, ge=1, le=20, description="Number of gold-standard questions to evaluate"),
    template: str = Query("zero_shot", description="Prompt strategy"),
):
    """
    Run the LLM benchmark over the first `limit` gold-standard questions, across
    all 3 models, computing BLEU / ROUGE-L / BERTScore / latency vs the reference
    answers. Persists results and returns them in the shape the frontend expects.

    This is slow on CPU (3 models × N questions). The HTTP client must use a long
    timeout.
    """
    if not os.path.exists(_GOLD_PATH):
        raise HTTPException(status_code=404, detail="benchmark_gold_standard.json not found.")

    with open(_GOLD_PATH, encoding="utf-8") as f:
        full_set = json.load(f)
    test_set = full_set[:limit]

    # Lazy import — triggers model loading, so keep it out of module import time.
    import llm_module as _llm

    started = time.time()
    retrieval_fn = _make_retrieval_fn()

    entries = _llm.run_benchmark(
        test_set=test_set,
        retrieval_fn=retrieval_fn,
        prompt_template=template,
        output_path=_FULL_PATH,
    )
    summary = _llm.summarize_benchmark(entries)
    duration = round(time.time() - started, 1)

    # Transform summary → frontend "results" shape.
    results = [
        {
            "model": name,
            "avg_bleu": s.get("bleu", 0.0),
            "avg_rouge_l": s.get("rouge_l", 0.0),
            "avg_bert_score": s.get("bertscore", 0.0),
            "avg_latency": s.get("latency_seconds", 0.0),
        }
        for name, s in summary.items()
    ]

    # Per-question detail with each model's answer.
    gold_detail = []
    for e in entries:
        gold_detail.append({
            "question": e.question,
            "reference_answer": e.gold_standard,
            "model_answers": {r.model_name: r.response for r in e.results},
            "metrics": e.metrics,
        })

    payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "num_questions": len(test_set),
        "template": template,
        "duration_seconds": duration,
        "results": results,
        "gold_standard": gold_detail,
    }

    with open(_LLM_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload


class CompareRequest(BaseModel):
    question: str
    reference: Optional[str] = None   # optional gold answer → enables metrics
    template: str = "zero_shot"


@router.post("/benchmark/compare")
def compare_models(req: CompareRequest):
    """
    Run a single user question through the real RAG pipeline and generate an
    answer with all 3 models for side-by-side comparison. If a reference answer
    is supplied, also compute BLEU / ROUGE-L / BERTScore per model.
    """
    question = (req.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question vide.")

    from data_pipeline.nlp_query_processor import encode_query
    from data_pipeline.retrieval import retrieve
    from backend.services.converter import retrieval_dicts_to_documents
    import llm_module as _llm

    # Retrieve once — same context for all 3 models, and reuse for sources.
    vec = encode_query(question)
    retrieval = retrieve(query_vector=vec, question=question, top_k=5, alpha=0.3)
    top_k_raw = retrieval["top_k_docs"]
    documents = retrieval_dicts_to_documents(top_k_raw)

    results = _llm.generate_all_models(question, documents, prompt_template=req.template)

    # ── Reference-free RAG metrics (SBERT cosine) ────────────────────────────
    # Faithfulness = answer grounded in retrieved context (vs hallucination).
    # Relevance    = answer addresses the question.
    # These need no gold reference, so every comparison gets meaningful scores.
    context_text = " ".join(d.get("contenu", "") for d in top_k_raw)[:3000]
    ctx_vec = encode_query(context_text) if context_text.strip() else None

    # Context Relevance = did retrieval find docs relevant to the question?
    # Query-level (shared by all 3 models). Separates retrieval quality from
    # generation quality — completes the reference-free RAG triad.
    context_relevance = round(_cosine(vec, ctx_vec), 4) if ctx_vec is not None else None

    reference = (req.reference or "").strip() or None
    models_out = []
    for res in results:
        item = {
            "model": res.model_name,
            "response": res.response,
            "latency": round(res.latency_seconds, 2),
            "safe": res.safe,
            "error": res.error,
        }
        ans = (res.response or "").strip()
        if ans:
            try:
                ans_vec = encode_query(ans)
                item["relevance"] = round(_cosine(ans_vec, vec), 4)
                if ctx_vec is not None:
                    item["faithfulness"] = round(_cosine(ans_vec, ctx_vec), 4)
            except Exception:
                import traceback
                traceback.print_exc()
        if reference:
            try:
                m = _llm.evaluate_result(res, reference)
                item["bleu"] = m.get("bleu", 0.0)
                item["rouge_l"] = m.get("rouge_l", 0.0)
                item["bertscore"] = m.get("bertscore", 0.0)
            except Exception as exc:
                # Don't let a metric failure discard the generated answers.
                import traceback
                traceback.print_exc()
                item["metric_error"] = str(exc)
        models_out.append(item)

    # Stable order: model_a, model_b, model_c
    order = {"model_a": 0, "model_b": 1, "model_c": 2}
    models_out.sort(key=lambda x: order.get(x["model"], 99))

    sources = [
        {
            "id": d.get("id", ""),
            "titre": d.get("titre", ""),
            "categorie": d.get("categorie", ""),
            "type_cancer": d.get("type_cancer", ""),
            "reference": d.get("reference", ""),
            "score_final": d.get("score_final", 0.0),
        }
        for d in top_k_raw
    ]

    return {
        "question": question,
        "has_reference": reference is not None,
        "template": req.template,
        "context_relevance": context_relevance,
        "models": models_out,
        "sources": sources,
    }
