"""
pipeline.py
===========
Full RAG orchestrator: query → classify → retrieve → convert → generate.

Call order:
  1. classify_intent(question)         — detect language + intent
  2. encode_query(question)            — SBERT vector
  3. retrieve(vector, question, ...)   — hybrid FAISS+BM25 retrieval
  4. retrieval_dicts_to_documents()    — dict → Document dataclass
  5. ask(question, documents, ...)     — LLM generation (lazy import)
  6. Build and return AskResponse

llm_module is imported lazily inside run_full_pipeline() so that
importing this module at server startup does NOT trigger ModelRegistry(),
which would load all 3 LLMs and block startup for several minutes.
"""

import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LLM_DIR = os.path.join(_ROOT, "LLM_cmp")
for _p in [_ROOT, _LLM_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from data_pipeline.nlp_query_processor import classify_intent, encode_query
from data_pipeline.retrieval import retrieve
from backend.models.schemas import AskRequest, AskResponse, SourceDoc
from backend.services.converter import retrieval_dicts_to_documents


def run_full_pipeline(req: AskRequest) -> AskResponse:
    """
    Execute the full RAG pipeline for one user question.

    LLM inference can take 10–30 seconds on CPU (flan-t5) or longer for larger models.
    No timeout is set — the HTTP client should handle its own timeout if needed.

    Args:
        req: AskRequest from the FastAPI route.

    Returns:
        AskResponse ready to be serialised as JSON.

    Raises:
        Exception: propagated to the router which wraps it in HTTP 500.
    """
    # ── 1. Intent + language classification ─────────────────────────────────
    intent_result = classify_intent(req.query)

    # ── 2. Encode query to SBERT vector ─────────────────────────────────────
    query_vector = encode_query(req.query)

    # ── 3. Hybrid retrieval (FAISS α=0.1 best from evaluation) ──────────────
    # For list-type queries, widen retrieval to capture more distinct cancer types
    effective_top_k = max(req.top_k, 20) if intent_result.get("intent") == "list_types" else req.top_k

    retrieval_result = retrieve(
        query_vector=query_vector,
        question=req.query,
        top_k=effective_top_k,
        alpha=req.alpha,
        categorie_filter=req.categorie_filter,
        cancer_type_filter=req.cancer_type_filter,
    )
    top_k_raw: list = retrieval_result["top_k_docs"]

    # ── 3b. Relevance threshold — block answers when no doc is relevant ──────
    _RELEVANCE_THRESHOLD = 0.10
    if not top_k_raw or top_k_raw[0].get("score_final", 0.0) < _RELEVANCE_THRESHOLD:
        _no_info = (
            "Je n'ai pas trouvé d'information suffisamment pertinente dans ma base "
            "de données pour répondre à cette question. Essayez de préciser votre "
            "question (ex : type de cancer, protocole, médicament spécifique)."
        )
        return AskResponse(
            response=_no_info,
            model=req.model_name,
            model_id=req.model_name,
            latency=0.0,
            safe=True,
            prompt_template=req.prompt_template,
            language=intent_result.get("language", "unknown"),
            intent=intent_result.get("intent", "unknown"),
            intent_confidence=intent_result.get("confidence", 0.0),
            sources=[],
            error=None,
        )

    # ── 3c. list_types intent — aggregate cancer types directly, skip LLM ───
    if intent_result.get("intent") == "list_types":
        types_seen: list[str] = []
        types_set: set[str] = set()
        _skip = {"", "général", "general", "inconnu", "unknown", "divers", "autres"}
        for d in top_k_raw:
            t = d.get("type_cancer", "").strip()
            if t and t.lower() not in _skip and t.lower() not in types_set:
                types_set.add(t.lower())
                types_seen.append(t)

        _sources = [
            SourceDoc(
                id=d.get("id", ""),
                titre=d.get("titre", ""),
                categorie=d.get("categorie", ""),
                type_cancer=d.get("type_cancer", ""),
                score_final=d.get("score_final", 0.0),
                score_faiss_norm=d.get("score_faiss_norm", 0.0),
                score_bm25_norm=d.get("score_bm25_norm", 0.0),
                reference=d.get("reference", ""),
            )
            for d in top_k_raw
        ]

        if types_seen:
            _list = "\n".join(f"• {t.capitalize()}" for t in sorted(types_seen))
            _response = (
                "D'après ma base de données en oncologie médicale, "
                "les types de cancer documentés sont :\n\n" + _list
            )
        else:
            _response = (
                "Ma base de données contient des articles sur différents cancers, "
                "mais je n'ai pas pu extraire une liste exhaustive depuis les documents récupérés. "
                "Essayez une question plus précise, ex : 'traitement du cancer du sein'."
            )

        return AskResponse(
            response=_response,
            model="list_aggregation",
            model_id="list_aggregation",
            latency=0.0,
            safe=True,
            prompt_template="list_aggregation",
            language=intent_result.get("language", "unknown"),
            intent="list_types",
            intent_confidence=intent_result.get("confidence", 0.0),
            sources=_sources,
            error=None,
        )

    # ── 4. Convert retrieval dicts → Document dataclass ─────────────────────
    documents = retrieval_dicts_to_documents(top_k_raw)

    # ── 5. LLM generation — lazy import so startup doesn't load all 3 models ─
    import llm_module as _llm  # noqa: PLC0415
    llm_result: dict = _llm.ask(
        question=req.query,
        top_k_docs=documents,
        model_name=req.model_name,
        prompt_template=req.prompt_template,
    )

    # ── 6. Build SourceDoc list from the raw retrieval dicts ─────────────────
    sources = [
        SourceDoc(
            id=d.get("id", ""),
            titre=d.get("titre", ""),
            categorie=d.get("categorie", ""),
            type_cancer=d.get("type_cancer", ""),
            score_final=d.get("score_final", 0.0),
            score_faiss_norm=d.get("score_faiss_norm", 0.0),
            score_bm25_norm=d.get("score_bm25_norm", 0.0),
            reference=d.get("reference", ""),
        )
        for d in top_k_raw
    ]

    return AskResponse(
        response=llm_result.get("response", ""),
        model=llm_result.get("model", req.model_name),
        model_id=llm_result.get("model_id", req.model_name),
        latency=llm_result.get("latency", 0.0),
        safe=llm_result.get("safe", True),
        prompt_template=llm_result.get("prompt_template", req.prompt_template),
        language=intent_result.get("language", "unknown"),
        intent=intent_result.get("intent", "unknown"),
        intent_confidence=intent_result.get("confidence", 0.0),
        sources=sources,
        error=llm_result.get("error"),
    )
