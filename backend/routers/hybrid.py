"""
POST /api/hybrid-treatment
==========================
Propose un plan de traitement hybride (multi-modal) à partir du guide AMFROM 2024.

Contrairement à une simple recherche filtrée, ce module *synthétise* une
proposition thérapeutique séquencée :

  1. Récupération ciblée des protocoles par modalité (chimio, radio, hormono,
     immuno, chirurgie) dans la base de connaissances construite.
  2. Séquencement oncologique déterministe selon le contexte clinique :
       - maladie localisée  → néoadjuvant → chirurgie → radiothérapie/adjuvant → surveillance
       - maladie métastatique → traitement systémique 1re ligne → radiothérapie
         symptomatique → chirurgie sélective → soins de support → réévaluation
  3. Adaptation aux marqueurs moléculaires (HER2+, EGFR, ALK, BRCA, RAS, PD-L1…)
     et aux comorbidités (insuffisance rénale, cardiopathie, diabète, fragilité…).
  4. Génération d'une reformulation pédagogique par le LLM (module de génération),
     en gardant le plan structuré déterministe comme garde-fou (citations exactes,
     pages du guide), sans aucun diagnostic direct.

La réponse contient à la fois `plan` (texte structuré en phases, rendu par l'UI),
`recommended_sequence` (séquence machine-lisible), `caveats` (adaptations) et
`summary` (narration LLM).
"""

import os
import sys
import time
import traceback

from fastapi import APIRouter, HTTPException
from backend.models.schemas import HybridRequest, HybridResponse, HybridPhase, SourceDoc

router = APIRouter()

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in [ROOT, os.path.join(ROOT, "LLM_cmp")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Modality definitions : (label, requête de récupération) ──────────────────
_MODALITIES = [
    ("chimiothérapie",  "chimiothérapie protocole cytotoxique cycles"),
    ("immunothérapie",  "immunothérapie checkpoint pembrolizumab PD-L1"),
    ("thérapie ciblée", "thérapie ciblée inhibiteur mutation driver"),
    ("hormonothérapie", "hormonothérapie hormonale endocrine"),
    ("radiothérapie",   "radiothérapie irradiation rayons curiethérapie"),
    ("chirurgie",       "chirurgie résection exérèse chirurgicale"),
]

# Mots-clés indiquant un stade avancé / métastatique
_METASTATIC_TOKENS = (
    "metasta", "métasta", "iv", "avancé", "avance", "mcrpc",
    "extensif", "m1", "incurable", "récidiv", "recidiv", "résistant",
)


def _is_metastatic(stage: str) -> bool:
    s = (stage or "").lower()
    return any(tok in s for tok in _METASTATIC_TOKENS)


def _doc_citation(d: dict) -> str:
    """Citation courte avec page du guide si disponible."""
    ref = (d.get("reference") or "").strip()
    return ref or d.get("id", "source inconnue")


def _doc_reco(d: dict, max_len: int = 320) -> str:
    """Construit une recommandation lisible à partir d'un document."""
    proto = d.get("protocole")
    if proto:
        if isinstance(proto, dict):
            proto = proto.get("nom") or proto.get("sequence") or str(proto)
        text = f"{d.get('titre', '')} — Protocole : {proto}"
    else:
        text = d.get("titre") or d.get("contenu", "")[:max_len]
    text = text.strip()
    return text[:max_len].rstrip() + ("…" if len(text) > max_len else "")


# ── Adaptation aux marqueurs moléculaires ────────────────────────────────────
def _marker_caveats(markers: list[str]) -> list[str]:
    out = []
    blob = " ".join(markers).lower()
    if "her2+" in blob or "her2 +" in blob:
        out.append("HER2+ : ajouter un double blocage anti-HER2 (Trastuzumab + Pertuzumab) ; surveiller la FEVG.")
    if "triple négatif" in blob or "triple negatif" in blob:
        out.append("Triple négatif : envisager l'immunothérapie néoadjuvante et le rattrapage (Capécitabine/Olaparib si BRCA).")
    if "egfr" in blob:
        out.append("EGFR muté : privilégier une thérapie ciblée orale (Osimertinib) plutôt que la chimiothérapie en 1re ligne.")
    if "alk" in blob:
        out.append("ALK+ : inhibiteur d'ALK (Alectinib) en 1re ligne.")
    if "pd-l1" in blob:
        out.append("PD-L1 élevé : l'immunothérapie (Pembrolizumab) prend une place prépondérante.")
    if "ras" in blob:
        out.append("Statut RAS : un anti-EGFR n'est indiqué que si RAS est sauvage.")
    if "brca" in blob:
        out.append("Mutation BRCA : envisager un inhibiteur de PARP en maintenance.")
    return out


# ── Adaptation aux comorbidités ──────────────────────────────────────────────
def _comorbidity_caveats(comorbidities: list[str]) -> list[str]:
    out = []
    for c in comorbidities:
        cl = c.lower()
        if "rén" in cl or "ren" in cl or "irc" in cl or "dfg" in cl or "rein" in cl:
            out.append(f"{c} : adapter les sels de platine (Carboplatine selon Calvert/DFG, prudence avec le Cisplatine) et hydrater.")
        elif "card" in cl or "fevg" in cl or "cœur" in cl or "coeur" in cl or "insuffisance cardiaque" in cl:
            out.append(f"{c} : prudence avec les anthracyclines et le Trastuzumab ; surveillance de la FEVG.")
        elif "diab" in cl:
            out.append(f"{c} : surveiller la glycémie sous corticoïdes ; attention à la neuropathie surajoutée.")
        elif "hta" in cl or "tension" in cl or "hypertension" in cl:
            out.append(f"{c} : surveiller la tension sous anti-angiogéniques (Bevacizumab) et adapter.")
        elif "âge" in cl or "age" in cl or "fragil" in cl or "gériatr" in cl or "geriatr" in cl:
            out.append(f"{c} : évaluation onco-gériatrique (G8), schémas allégés et soins de support renforcés.")
        elif "hépat" in cl or "hepat" in cl or "foie" in cl:
            out.append(f"{c} : adapter les médicaments à métabolisme hépatique ; surveiller le bilan hépatique.")
        else:
            out.append(f"{c} : à intégrer dans la décision de RCP (adaptation de doses / surveillance dédiée).")
    return out


def _build_sequence(per_modality: dict, metastatic: bool) -> list[HybridPhase]:
    """
    Séquence les modalités disponibles en un plan multimodal cohérent.
    On ne crée une phase que si la modalité a été retrouvée dans la base.
    """
    def best(label):
        docs = per_modality.get(label) or []
        return docs[0] if docs else None

    systemic_order = ["thérapie ciblée", "immunothérapie", "chimiothérapie", "hormonothérapie"]
    phases: list[HybridPhase] = []
    n = 0

    if not metastatic:
        # ── Maladie localisée : intention curative ──
        # Phase systémique néoadjuvante
        neo = next((m for m in ["chimiothérapie", "immunothérapie", "thérapie ciblée"] if best(m)), None)
        if neo:
            d = best(neo); n += 1
            phases.append(HybridPhase(
                phase=n, label="Traitement néoadjuvant", modality=neo,
                recommendation=f"Réduire la tumeur avant la chirurgie. {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
        # Chirurgie
        if best("chirurgie"):
            d = best("chirurgie"); n += 1
            phases.append(HybridPhase(
                phase=n, label="Chirurgie d'exérèse", modality="chirurgie",
                recommendation=f"Résection carcinologique (objectif R0). {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
        # Radiothérapie adjuvante
        if best("radiothérapie"):
            d = best("radiothérapie"); n += 1
            phases.append(HybridPhase(
                phase=n, label="Radiothérapie adjuvante", modality="radiothérapie",
                recommendation=f"Consolidation locorégionale après chirurgie. {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
        # Traitement adjuvant systémique restant / hormonothérapie
        adj = next((m for m in ["hormonothérapie", "thérapie ciblée", "chimiothérapie"]
                    if best(m) and m != neo), None)
        if adj:
            d = best(adj); n += 1
            phases.append(HybridPhase(
                phase=n, label="Traitement adjuvant / maintenance", modality=adj,
                recommendation=f"Réduire le risque de récidive (micrométastases). {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
    else:
        # ── Maladie métastatique : intention de contrôle ──
        # Traitement systémique de 1re ligne (meilleure modalité systémique trouvée)
        first = next((m for m in systemic_order if best(m)), None)
        if first:
            d = best(first); n += 1
            phases.append(HybridPhase(
                phase=n, label="Traitement systémique de 1re ligne", modality=first,
                recommendation=f"Contrôle de la maladie disséminée. {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
        # Modalité systémique d'association/2e ligne
        second = next((m for m in systemic_order if best(m) and m != first), None)
        if second:
            d = best(second); n += 1
            phases.append(HybridPhase(
                phase=n, label="Association / ligne ultérieure", modality=second,
                recommendation=f"Intensification ou relais thérapeutique. {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
        # Radiothérapie symptomatique / oligométastatique
        if best("radiothérapie"):
            d = best("radiothérapie"); n += 1
            phases.append(HybridPhase(
                phase=n, label="Radiothérapie symptomatique", modality="radiothérapie",
                recommendation=f"Contrôle local (douleur, oligométastases, compression). {_doc_reco(d)}",
                sources=[_doc_citation(d)]))
        # Chirurgie sélective
        if best("chirurgie"):
            d = best("chirurgie"); n += 1
            phases.append(HybridPhase(
                phase=n, label="Chirurgie sélective", modality="chirurgie",
                recommendation=f"Métastasectomie ou chirurgie de propreté chez les patients sélectionnés. {_doc_reco(d)}",
                sources=[_doc_citation(d)]))

    # Phase finale commune : surveillance / soins de support
    n += 1
    surv_label = "Soins de support et réévaluation" if metastatic else "Surveillance post-traitement"
    surv_reco = (
        "Soins de support précoces, évaluation de la réponse (RECIST) et réévaluation en RCP."
        if metastatic else
        "Suivi clinique, biologique et radiologique régulier pour détecter une récidive (critères RECIST)."
    )
    phases.append(HybridPhase(
        phase=n, label=surv_label, modality="suivi",
        recommendation=surv_reco, sources=["Guide AMFROM 2024 – Surveillance / Soins de support, p.265"]))

    return phases


def _render_plan(patient_info: str, phases: list[HybridPhase], caveats: list[str]) -> str:
    """Rend la séquence en texte structuré (compatible avec l'UI : 'Phase N')."""
    lines = [f"Profil patient : {patient_info}", ""]
    for p in phases:
        lines.append(f"Phase {p.phase} — {p.label} ({p.modality})")
        lines.append(p.recommendation)
        if p.sources:
            lines.append("Source : " + " ; ".join(p.sources))
        lines.append("")
    if caveats:
        lines.append("Adaptations spécifiques :")
        for c in caveats:
            lines.append(f"• {c}")
    lines.append("")
    lines.append("⚠️ Support décisionnel pour oncologue — ne remplace pas la décision de RCP. Aucun diagnostic direct.")
    return "\n".join(lines).strip()


def _build_llm_prompt(patient_info: str, plan_text: str) -> str:
    return (
        "Tu es un assistant oncologique. Reformule le plan de traitement hybride "
        "ci-dessous de façon claire et pédagogique pour un oncologue, en gardant "
        "les phases numérotées, les protocoles et les citations (pages du guide). "
        "N'ajoute aucune information absente du plan, ne pose aucun diagnostic.\n\n"
        f"Profil : {patient_info}\n\n"
        f"Plan structuré (issu du guide AMFROM 2024) :\n{plan_text}\n\n"
        "Reformulation pédagogique :"
    )


@router.post("/hybrid-treatment", response_model=HybridResponse)
def hybrid_treatment(req: HybridRequest):
    try:
        from data_pipeline.nlp_query_processor import encode_query
        from data_pipeline.retrieval import retrieve

        t0 = time.perf_counter()
        metastatic = _is_metastatic(req.stage)

        # ── Step 1 : récupération ciblée par modalité ─────────────────────────
        per_modality: dict[str, list] = {}
        seen_ids: set[str] = set()
        marker_str = " ".join(req.markers)

        for label, keywords in _MODALITIES:
            query = f"cancer {req.cancer_type} {req.stage} {marker_str} {keywords} traitement".strip()
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
                if d.get("id") not in seen_ids and d.get("score_final", 0.0) > 0.05
            ]
            for d in docs:
                seen_ids.add(d["id"])
            if docs:
                per_modality[label] = docs[:2]

        if not per_modality:
            return HybridResponse(
                plan=(
                    f"Aucun protocole trouvé dans la base pour le cancer '{req.cancer_type}' "
                    f"stade '{req.stage}'. Vérifiez que ce type de cancer est couvert "
                    "dans votre base de données."
                ),
                modalities_found=[], sources=[], model=req.model_name,
                latency=round(time.perf_counter() - t0, 3),
                intent="metastatique" if metastatic else "localise",
            )

        # ── Step 2 : profil patient ──────────────────────────────────────────
        parts = [f"Cancer : {req.cancer_type}"]
        if req.stage:         parts.append(f"Stade : {req.stage}")
        if req.markers:       parts.append(f"Marqueurs : {', '.join(req.markers)}")
        if req.comorbidities: parts.append(f"Comorbidités : {', '.join(req.comorbidities)}")
        patient_info = " | ".join(parts)

        # ── Step 3 : séquencement déterministe + adaptations ─────────────────
        phases = _build_sequence(per_modality, metastatic)
        caveats = _marker_caveats(req.markers) + _comorbidity_caveats(req.comorbidities)
        plan_text = _render_plan(patient_info, phases, caveats)

        # ── Step 4 : reformulation LLM (best-effort, ne casse pas le plan) ────
        summary = ""
        model_used = req.model_name
        llm_error = None
        try:
            import llm_module as _llm
            llm_out = _llm.generate_with_prompt(
                _build_llm_prompt(patient_info, plan_text), model_name=req.model_name
            )
            summary = (llm_out.get("response") or "").strip()
            model_used = llm_out.get("model", req.model_name)
            llm_error = llm_out.get("error")
        except Exception as le:
            llm_error = f"LLM indisponible : {le}"

        # ── Step 5 : sources ─────────────────────────────────────────────────
        all_raw = [d for docs in per_modality.values() for d in docs]
        sources = [
            SourceDoc(
                id=d.get("id", ""), titre=d.get("titre", ""),
                categorie=d.get("categorie", ""), type_cancer=d.get("type_cancer", ""),
                score_final=d.get("score_final", 0.0),
                score_faiss_norm=d.get("score_faiss_norm", 0.0),
                score_bm25_norm=d.get("score_bm25_norm", 0.0),
                reference=d.get("reference", ""),
            )
            for d in all_raw
        ]

        return HybridResponse(
            plan=plan_text,
            modalities_found=list(per_modality.keys()),
            sources=sources,
            model=model_used,
            latency=round(time.perf_counter() - t0, 3),
            error=llm_error,
            recommended_sequence=phases,
            caveats=caveats,
            intent="metastatique" if metastatic else "localise",
            summary=summary,
        )

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
