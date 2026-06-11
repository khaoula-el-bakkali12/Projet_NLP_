"""
POST /api/hybrid-treatment
==========================
Propose a multi-modal hybrid oncology treatment plan.

Logic:
  1. For each treatment modality (chimio, radio, hormono, immuno, chirurgie),
     build a targeted query and retrieve top-3 relevant docs from the knowledge base.
  2. Assemble a multi-section context with one section per modality.
  3. Feed a structured hybrid prompt to the LLM (model_b / model_c only —
     FLAN-T5 seq2seq is too weak for multi-section synthesis and is auto-switched
     to model_b).
  4. Return the plan, the modalities found, and the source documents.
"""

import os
import sys
import time
import traceback

from fastapi import APIRouter, HTTPException
from backend.models.schemas import HybridRequest, HybridResponse, SourceDoc

router = APIRouter()

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in [ROOT, os.path.join(ROOT, "LLM_cmp")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Modality definitions ────────────────────────────────────────────────────
# Each entry: (modality_label, primary_keyword_for_query)
_MODALITIES = [
    ("chimiothérapie",  "chimiothérapie protocole cytotoxique"),
    ("radiothérapie",   "radiothérapie irradiation rayons"),
    ("hormonothérapie", "hormonothérapie hormonale endocrine"),
    ("immunothérapie",  "immunothérapie checkpoint pembrolizumab"),
    ("chirurgie",       "chirurgie résection exérèse"),
]


def _build_hybrid_prompt(patient_info: str, context_sections: list[str]) -> str:
    full_context = "\n\n".join(context_sections)
    return (
        "Tu es un assistant oncologique spécialisé. "
        "Propose un plan de traitement hybride structuré en phases numérotées "
        "(Phase 1, Phase 2…) pour le profil patient suivant :\n"
        f"{patient_info}\n\n"
        "Utilise UNIQUEMENT les protocoles ci-dessous issus du guide AMFROM 2024. "
        "Pour chaque phase : indique la modalité thérapeutique, le protocole précis "
        "avec doses si disponibles, et cite la source [SOURCE] entre parenthèses. "
        "Si une modalité n'est pas couverte par le contexte, indique-le clairement. "
        "Ne pose aucun diagnostic. Ce plan est un support décisionnel pour oncologue.\n\n"
        f"{full_context}\n\n"
        "Plan de traitement hybride (phases numérotées, avec citations) :"
    )


@router.post("/hybrid-treatment", response_model=HybridResponse)
def hybrid_treatment(req: HybridRequest):
    try:
        from data_pipeline.nlp_query_processor import encode_query
        from data_pipeline.retrieval import retrieve
        import llm_module as _llm

        t0 = time.perf_counter()

        # ── Step 1: per-modality retrieval ────────────────────────────────────
        per_modality: dict[str, list] = {}
        seen_ids: set[str] = set()

        for label, keywords in _MODALITIES:
            query = (
                f"cancer {req.cancer_type} "
                f"{req.stage} "
                f"{keywords} traitement"
            ).strip()

            vec = encode_query(query)
            result = retrieve(
                query_vector=vec,
                question=query,
                top_k=4,
                alpha=0.3,
                categorie_filter=None,
                cancer_type_filter=req.cancer_type.lower() if req.cancer_type else None,
            )

            docs = [
                d for d in result["top_k_docs"]
                if d.get("id") not in seen_ids
                and d.get("score_final", 0.0) > 0.05
            ]
            for d in docs:
                seen_ids.add(d["id"])

            if docs:
                per_modality[label] = docs[:3]

        # ── Step 2: build multi-section context ───────────────────────────────
        context_sections: list[str] = []
        for label, docs in per_modality.items():
            lines = [f"[{label.upper()}]"]
            for d in docs:
                lines.append(d.get("contenu", "")[:600])
                if d.get("protocole"):
                    lines.append(f"Protocole : {d['protocole']}")
                ref = d.get("reference") or d.get("id", "")
                if ref:
                    lines.append(f"[SOURCE] {ref}")
            context_sections.append("\n".join(lines))

        if not context_sections:
            return HybridResponse(
                plan=(
                    f"Aucun protocole trouvé dans la base pour le cancer '{req.cancer_type}' "
                    f"stade '{req.stage}'. "
                    "Vérifiez que ce type de cancer est couvert dans votre base de données."
                ),
                modalities_found=[],
                sources=[],
                model=req.model_name,
                latency=round(time.perf_counter() - t0, 3),
                error=None,
            )

        # ── Step 3: patient info string ───────────────────────────────────────
        parts = [f"Cancer : {req.cancer_type}"]
        if req.stage:
            parts.append(f"Stade : {req.stage}")
        if req.markers:
            parts.append(f"Marqueurs : {', '.join(req.markers)}")
        if req.comorbidities:
            parts.append(f"Comorbidités : {', '.join(req.comorbidities)}")
        patient_info = " | ".join(parts)

        # ── Step 4: LLM generation ────────────────────────────────────────────
        prompt = _build_hybrid_prompt(patient_info, context_sections)
        result_llm = _llm.generate_with_prompt(prompt, model_name=req.model_name)

        # ── Step 5: build SourceDoc list ──────────────────────────────────────
        all_raw = [d for docs in per_modality.values() for d in docs]
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
            for d in all_raw
        ]

        return HybridResponse(
            plan=result_llm.get("response", ""),
            modalities_found=list(per_modality.keys()),
            sources=sources,
            model=result_llm.get("model", req.model_name),
            latency=round(time.perf_counter() - t0, 3),
            error=result_llm.get("error"),
        )

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
