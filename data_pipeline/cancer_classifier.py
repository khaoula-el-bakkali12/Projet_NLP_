"""
cancer_classifier.py — Classification du type de cancer à partir d'une question
================================================================================

Détecte le type de cancer évoqué dans une question utilisateur parmi :
  - "sein"        (cancer du sein / breast)
  - "poumon"      (cancer broncho-pulmonaire / lung)
  - "colorectal"  (cancer du côlon-rectum / colorectal)
  - "inconnu"     (aucun des trois ou ambigu)

Hybride : combinaison de **matching de mots-clés multilingues** (FR/AR/EN) et
**similarité sémantique SBERT** (fallback). Le résultat est renvoyé sous
forme de dictionnaire JSON-compatible pour s'intégrer proprement au pipeline.

Pourquoi hybride ?
  - Les mots-clés couvrent les formulations canoniques (médicaments
    spécifiques : Trastuzumab, Oxaliplatine ; stades : HER2+ ; examens :
    coloscopie, fibroscopie bronchique).
  - Le SBERT attrape les paraphrases ("tumeur mammaire", "néo du rectum")
    que les mots-clés seuls manquent.

API publique :
  classify_cancer_type(question: str) -> dict

Sortie :
  {
    "cancer":     "sein" | "poumon" | "colorectal" | "inconnu",
    "confidence": float,        # 0..1
    "method":     "keyword" | "sbert" | "fallback",
    "scores":     {             # présent uniquement quand method == "sbert"
        "sein": 0.62, "poumon": 0.31, "colorectal": 0.18
    }
  }

Usage :
    from data_pipeline.cancer_classifier import classify_cancer_type
    classify_cancer_type("Quel protocole AC pour le cancer du sein ?")
    # -> {"cancer": "sein", "confidence": 1.0, "method": "keyword", ...}
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("cancer_classifier")

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

#: Libellés canoniques renvoyés par la fonction.
CANCER_LABELS = ("sein", "poumon", "colorectal")

#: Seuil de similarité SBERT pour accepter une classe.
SBERT_CONFIDENCE_THRESHOLD = 0.45

#: Phrases de référence (canoniques) encodées une fois pour le scoring SBERT.
#: Une par classe, dans les 3 langues supportées par le projet (FR/AR/EN).
SBERT_REFERENCE_SENTENCES: Dict[str, List[str]] = {
    "sein": [
        # FR
        "cancer du sein, tumeur mammaire, sein HER2 positif, traitement du cancer du sein",
        # AR
        "سرطان الثدي، ورم في الثدي، علاج سرطان الثدي الإيجابي HER2",
        # EN
        "breast cancer, mammary tumor, HER2 positive breast cancer treatment",
    ],
    "poumon": [
        # FR
        "cancer du poumon, tumeur broncho-pulmonaire, CBNPC, cancer pulmonaire non à petites cellules",
        # AR
        "سرطان الرئة، ورم رئوي، سرطان الرئة غير صغير الخلايا",
        # EN
        "lung cancer, non-small cell lung cancer, pulmonary tumor, NSCLC",
    ],
    "colorectal": [
        # FR
        "cancer colorectal, cancer du côlon, cancer du rectum, protocole FOLFOX, FOLFIRI",
        # AR
        "سرطان القولون والمستقيم، ورم القولون، علاج سرطان القولون",
        # EN
        "colorectal cancer, colon cancer, rectal cancer, FOLFOX regimen",
    ],
}


# ---------------------------------------------------------------------------
# 1. MATCHING PAR MOTS-CLÉS (rapide, prioritaire)
# ---------------------------------------------------------------------------

# Patterns FR/AR/EN pour chaque classe. On utilise des mots-entiers (\b) ou
# des fragments discriminants (noms de médicaments / examens spécifiques)
# pour minimiser les faux positifs.
_KEYWORD_PATTERNS: Dict[str, List[str]] = {
    "sein": [
        # FR — anatomie / sous-types
        r"\bsein\b", r"\bmammaire[s]?\b", r"\bmammograph", r"\bmastectom",
        r"\bcanalaire\b", r"\bcanalaire infiltrant\b",
        # FR — biomarqueurs
        r"\bHER2\b", r"\btrastuzumab\b", r"\bpertuzumab\b", r"\btucatinib\b",
        r"\bherceptin\b", r"\bRH\s*\+/?-?\b",
        # AR
        r"الثدي", r"الصدر(?!ة\bحجر)",  # catch breast context
        r"تراستوزوماب", r"هيرتو",
        # EN
        r"\bbreast\b", r"\bmammary\b", r"\bmastectomy\b",
        r"\bHER2\b", r"\btrastuzumab\b", r"\bpertuzumab\b",
    ],
    "poumon": [
        # FR — anatomie / sous-types
        r"\bpoumon[s]?\b", r"\bpulmonaire[s]?\b", r"\bbronchique[s]?\b",
        r"\bbroncho[- ]?pulmonaire\b", r"\bCBNPC\b", r"\bCPC\b",
        r"non à petites cellules", r"épidermo[ïi]de",
        # FR — examens / traitements
        r"\bfibroscopie\s+bronchique\b", r"\bpleur[ée]sie\b",
        r"\bplatine[ -]?(?:cis|cisplatine|carboplatine)\b",  # weak but valid for lung
        r"\bétoposide\b", r"\bchimiothérapie\s+concomitante\b",
        # AR
        r"الرئة", r"رئوي", r"القصبات", r"الصدر",
        # EN
        r"\blung\b", r"\bpulmonary\b", r"\bbronchial\b", r"\bNSCLC\b",
        r"\bSCLC\b", r"\bsmall[- ]?cell\s+lung\b",
        r"\bnon[- ]?small[- ]?cell\b", r"\bbronchoscop",
    ],
    "colorectal": [
        # FR — anatomie
        r"\bcolorectal\b", r"\bcolique[s]?\b", r"\bc[oô]lon\b", r"\brectum\b",
        r"\brectal(e|aux)?\b", r"\banus\b", r"\bcoloscopie\b",
        r"\bFOLFOX\b", r"\bFOLFIRI\b", r"\bFOLFOXIRI\b",
        # FR — médicaments
        r"\boxaliplatine\b", r"\birinot[ée]can\b", r"\bleucovorine\b",
        r"\bc[ée]tuximab\b",  # used in colorectal (but also head & neck — risk noted)
        # AR
        r"القولون", r"المستقيم", r"الشرج", r"قولون",
        # EN
        r"\bcolorectal\b", r"\brectal\b", r"\bcolon\b", r"\bcolonosco",
        r"\bFOLFOX\b", r"\bFOLFIRI\b", r"\boxaliplatin\b", r"\birinotecan\b",
    ],
}


def _keyword_classify(question: str) -> Optional[Tuple[str, int]]:
    """
    Match the question against keyword patterns.

    Returns:
        (cancer_label, hit_count) for the best-matching class, or None if
        no keyword hits.
    """
    q = question or ""
    scores: Dict[str, int] = {}
    for label, patterns in _KEYWORD_PATTERNS.items():
        count = 0
        for pat in patterns:
            # On drape insensitive + unicode. `re.UNICODE` est implicite en Py3.
            if re.search(pat, q, flags=re.IGNORECASE | re.UNICODE):
                count += 1
        if count:
            scores[label] = count

    if not scores:
        return None

    # Si égalité, on tranche avec une priorité déclarative (ordre CANCER_LABELS).
    top_score = max(scores.values())
    for label in CANCER_LABELS:
        if scores.get(label, 0) == top_score:
            return label, top_score
    return None  # unreachable


# ---------------------------------------------------------------------------
# 2. CLASSIFICATION SBERT (fallback pour les paraphrases)
# ---------------------------------------------------------------------------

_SBERT_VECTORS: Optional[Dict[str, List[Any]]] = None


def _get_sbert_centroids():
    """
    Calcule (et cache) les centroïdes SBERT des phrases de référence pour
    chaque classe. Encodage en mode "lazy" — on ne charge SBERT que si la
    classification par mots-clés échoue.
    """
    global _SBERT_VECTORS
    if _SBERT_VECTORS is not None:
        return _SBERT_VECTORS

    try:
        from data_pipeline.nlp_query_processor import get_sbert_model
    except Exception as e:
        logger.warning("cancer_classifier: SBERT non disponible — %s", e)
        return None

    try:
        model = get_sbert_model()
    except Exception as e:
        logger.warning("cancer_classifier: échec chargement SBERT — %s", e)
        return None

    centroids: Dict[str, List[Any]] = {}
    for label, sentences in SBERT_REFERENCE_SENTENCES.items():
        try:
            embs = model.encode(
                sentences,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            # Centroïde = moyenne des vecteurs (puis re-normalisation L2).
            centroid = embs.mean(axis=0)
            centroid = centroid / (centroid @ centroid) ** 0.5  # L2 norm
            centroids[label] = centroid
        except Exception as e:
            logger.warning("cancer_classifier: encodage centroïde %s échoué — %s", label, e)
            return None

    _SBERT_VECTORS = centroids
    return centroids


def _sbert_classify(question: str) -> Optional[Dict[str, Any]]:
    """
    Encode la question, calcule la similarité cosinus avec chaque centroïde,
    retourne la classe la plus proche si elle dépasse le seuil.
    """
    centroids = _get_sbert_centroids()
    if centroids is None:
        return None

    try:
        from data_pipeline.nlp_query_processor import get_sbert_model
        model = get_sbert_model()
        q_vec = model.encode(
            [question],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
    except Exception as e:
        logger.warning("cancer_classifier: encodage question échoué — %s", e)
        return None

    scores: Dict[str, float] = {}
    for label, centroid in centroids.items():
        # Cosinus = produit scalaire quand les vecteurs sont normalisés L2.
        scores[label] = float(q_vec @ centroid)

    if not scores:
        return None

    best_label = max(scores, key=scores.get)  # type: ignore[arg-type]
    best_score = scores[best_label]
    if best_score < SBERT_CONFIDENCE_THRESHOLD:
        return None
    return {
        "cancer": best_label,
        "confidence": round(best_score, 4),
        "method": "sbert",
        "scores": {k: round(v, 4) for k, v in scores.items()},
    }


# ---------------------------------------------------------------------------
# 3. API PRINCIPALE
# ---------------------------------------------------------------------------

def classify_cancer_type(question: str) -> Dict[str, Any]:
    """
    Classifie le type de cancer évoqué dans `question`.

    Stratégie :
      1. Matching de mots-clés multilingues (rapide, prioritaire).
      2. Si rien trouvé, similarité SBERT vs centroïdes de référence.
      3. Sinon, renvoie `inconnu`.

    Args:
        question: Question utilisateur (FR, AR, ou EN).

    Returns:
        Dict JSON-compatible :
          {
            "cancer":     "sein" | "poumon" | "colorectal" | "inconnu",
            "confidence": float,    # 0..1
            "method":     "keyword" | "sbert" | "fallback",
            "scores":     {...}     # optionnel, présent pour SBERT
          }
    """
    question = (question or "").strip()
    if not question:
        return {"cancer": "inconnu", "confidence": 0.0, "method": "fallback"}

    # 1. Keyword matching
    kw = _keyword_classify(question)
    if kw is not None:
        label, hits = kw
        # Confidence augmente avec le nombre de hits, plafonnée à 0.99 (jamais 1.0
        # pour signaler que c'est heuristique).
        confidence = min(0.5 + 0.15 * hits, 0.99)
        return {
            "cancer": label,
            "confidence": round(confidence, 4),
            "method": "keyword",
        }

    # 2. SBERT fallback
    sbert_result = _sbert_classify(question)
    if sbert_result is not None:
        return sbert_result

    # 3. Rien n'a matché
    return {"cancer": "inconnu", "confidence": 0.0, "method": "fallback"}


# ---------------------------------------------------------------------------
# Test rapide
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_questions = [
        # Keyword
        "Quel est le protocole AC pour le cancer du sein ?",
        "Patiente HER2+, quel traitement néoadjuvant ?",
        # SBERT (paraphrase)
        "Tumeur mammaire chez une femme de 50 ans, quelle prise en charge ?",
        # Keyword
        "Patient de 55 ans, cancer du poumon non à petites cellules stade IIIA",
        # SBERT
        "Tumeur broncho-pulmonaire avec métastases hépatiques",
        # Keyword
        "Quel est le protocole FOLFOX pour le cancer colorectal ?",
        "Coloscopie de contrôle après résection rectale",
        # AR
        "ما هو علاج سرطان الثدي الإيجابي HER2؟",
        "علاج سرطان القولون المنتشر",
        # Inconnu (général)
        "Quelle est la différence entre chimiothérapie adjuvante et néoadjuvante ?",
        "Qu'est-ce que les critères RECIST ?",
    ]
    for q in test_questions:
        r = classify_cancer_type(q)
        print(f"  → {r['cancer']:<10s} | conf={r['confidence']:.2f} | method={r['method']:<8s} | {q[:60]}")
