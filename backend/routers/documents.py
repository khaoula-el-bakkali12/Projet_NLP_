import json
import os
import sys
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATASET_PATH = os.path.join(_ROOT, "data", "raw", "dataset_oncologie_FINAL_v6.json")

# Mutable module-level cache — updated in place by upload_doc.py after uploads/deletes
with open(_DATASET_PATH, encoding="utf-8") as _f:
    _DATASET: list[dict] = json.load(_f)

_BY_ID: dict[str, dict] = {doc["id"]: doc for doc in _DATASET}


@router.get("/documents")
def list_documents(
    type_cancer: Optional[str] = Query(None, description="Filter by cancer type"),
    categorie: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    docs = _DATASET

    if type_cancer:
        docs = [d for d in docs if d.get("type_cancer", "").lower() == type_cancer.lower()]
    if categorie:
        docs = [d for d in docs if d.get("categorie", "").lower() == categorie.lower()]

    total = len(docs)
    page = docs[offset: offset + limit]

    # Return a lightweight summary (avoid sending full content in list view)
    summary = [
        {
            "id": d["id"],
            "titre": d.get("titre", ""),
            "categorie": d.get("categorie", ""),
            "type_cancer": d.get("type_cancer", ""),
            "sous_type": d.get("sous_type", ""),
            "stade": d.get("stade", ""),
            "reference": d.get("reference", ""),
            "est_synthetique": d.get("est_synthetique", False),
            "date_creation": d.get("date_creation", ""),
        }
        for d in page
    ]

    return {"total": total, "offset": offset, "limit": limit, "documents": summary}


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = _BY_ID.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc


@router.get("/cancer-types")
def cancer_types():
    types = sorted(set(d.get("type_cancer", "") for d in _DATASET if d.get("type_cancer")))
    return types


@router.get("/categories")
def categories():
    cats = sorted(set(d.get("categorie", "") for d in _DATASET if d.get("categorie")))
    return cats


@router.get("/statistics")
def statistics():
    import sqlite3
    from collections import Counter

    total = len(_DATASET)

    cancer_counts   = Counter(d.get("type_cancer", "inconnu") for d in _DATASET)
    category_counts = Counter(d.get("categorie",   "inconnu") for d in _DATASET)

    real_count      = sum(1 for d in _DATASET if not d.get("est_synthetique", False))
    synthetic_count = sum(1 for d in _DATASET if d.get("est_synthetique", False))
    has_protocol    = sum(1 for d in _DATASET if d.get("protocole"))
    has_effects     = sum(1 for d in _DATASET if d.get("effets_secondaires"))
    has_scenario    = sum(1 for d in _DATASET if d.get("scenario_patient"))
    uploaded_count  = sum(1 for d in _DATASET if d.get("source_file"))

    all_keywords    = [kw for d in _DATASET for kw in (d.get("mots_cles") or [])]
    unique_keywords = len(set(all_keywords))
    avg_content_len = round(sum(len(d.get("contenu", "")) for d in _DATASET) / total) if total else 0

    # ── Usage stats from SQLite history ──────────────────────────────────────
    _DB_PATH = os.path.join(_ROOT, "data", "oncologia.db")
    usage = {"total_queries": 0, "models_used": {}}
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM history")
            usage["total_queries"] = cur.fetchone()[0]
            cur.execute("SELECT model, COUNT(*) AS cnt FROM history WHERE model IS NOT NULL GROUP BY model ORDER BY cnt DESC")
            usage["models_used"] = {r[0]: r[1] for r in cur.fetchall()}
    except Exception:
        pass

    return {
        "total_documents":   total,
        "total_cancer_types": len(cancer_counts),
        "unique_keywords":   unique_keywords,
        "docs_with_protocol": has_protocol,
        "uploaded_chunks":   uploaded_count,
        "cancer_distribution": [
            {"type": k, "count": v, "pct": round(v * 100 / total)}
            for k, v in cancer_counts.most_common()
        ],
        "category_distribution": [
            {"categorie": k, "count": v, "pct": round(v * 100 / total)}
            for k, v in category_counts.most_common()
        ],
        "composition": {
            "real":             real_count,
            "synthetic":        synthetic_count,
            "has_protocol":     has_protocol,
            "has_effects":      has_effects,
            "has_scenario":     has_scenario,
            "avg_content_length": avg_content_len,
        },
        "usage": usage,
    }
