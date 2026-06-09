"""
converter.py
============
Converts raw dicts returned by data_pipeline.retrieval.retrieve()
into Document dataclass instances expected by LLM_cmp.llm_module.ask().

Critical field rename:
  retrieval dict key  "reference"  →  Document field  "source_reference"

protocole can be None, a plain string, or a dict (from the dataset).
We normalise it to a plain string in all cases.

IMPORTANT: we do NOT import llm_module at the top level.
llm_module.py runs ModelRegistry() at import time, which loads all 3 LLMs.
We define a local mirror of Document here to avoid that startup cost.
llm_module is imported lazily only when ask() is actually called (in pipeline.py).
"""

from dataclasses import dataclass, field


@dataclass
class Document:
    """Mirror of llm_module.Document — kept in sync manually."""
    id: str
    contenu: str
    categorie: str = ""
    type_cancer: str = ""
    mots_cles: list = field(default_factory=list)
    protocole: str = ""
    source_reference: str = ""


def _protocole_to_str(value) -> str:
    """Normalise protocole to a clean human-readable string.

    The dataset protocole dict has shape:
      { nom, sequence: [{phase, medicaments: [{nom, dose, voie, jour}], frequence, cycles}],
        duree_totale, remarques }

    We flatten this to a compact paragraph so small LLMs don't loop on
    raw Python dict notation like 'phase': 'phase': 'phase': ...
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return str(value)

    parts = []

    # NB: do NOT prefix with "Protocole : " here — build_context() in
    # llm_module already prepends that label. Prefixing here too produced
    # the doubled "Protocole : Protocole : …" seen in model output.
    if value.get("nom"):
        parts.append(f"{value['nom']}.")

    for step in value.get("sequence") or []:
        phase = step.get("phase", "")
        freq  = step.get("frequence", "")
        cyc   = step.get("cycles", "")
        meds  = step.get("medicaments") or []
        med_strs = []
        for m in meds:
            m_name = m.get("nom", "")
            m_dose = m.get("dose", "")
            m_voie = m.get("voie", "")
            m_jour = m.get("jour", "")
            med_strs.append(
                " ".join(filter(None, [m_name, m_dose, m_voie, m_jour]))
            )
        line = phase
        if med_strs:
            line += " : " + ", ".join(med_strs)
        if freq:
            line += f" (fréquence : {freq})"
        if cyc:
            line += f", {cyc} cycles"
        parts.append(line + ".")

    if value.get("duree_totale"):
        parts.append(f"Durée totale : {value['duree_totale']}.")
    if value.get("remarques"):
        parts.append(f"Remarques : {value['remarques']}.")

    return " ".join(parts) if parts else str(value)


def retrieval_dicts_to_documents(top_k_docs: list) -> list:
    """
    Convert enriched dicts from retrieve() to Document dataclass instances.

    Field mapping:
        id            → id
        contenu       → contenu
        categorie     → categorie
        type_cancer   → type_cancer
        mots_cles     → mots_cles     (already a list[str])
        protocole     → protocole     (normalised to str)
        reference     → source_reference  ← critical rename
    """
    return [
        Document(
            id=d.get("id", ""),
            contenu=d.get("contenu", ""),
            categorie=d.get("categorie", ""),
            type_cancer=d.get("type_cancer", ""),
            mots_cles=d.get("mots_cles") or [],
            protocole=_protocole_to_str(d.get("protocole")),
            source_reference=d.get("reference", ""),
        )
        for d in top_k_docs
    ]
