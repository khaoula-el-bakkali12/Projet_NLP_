"""
retrieval.py — Module de recherche hybride (FAISS + BM25)
==========================================================

Combine la recherche vectorielle (FAISS) et lexicale (BM25) en un score
fusionné :

    score_final = α × score_FAISS_norm + (1 − α) × score_BM25_norm

Fonctionnalités :
  - Normalisation min-max des scores avant fusion
  - Filtrage par catégorie et type de cancer
  - Expérimentation avec différentes valeurs de α
  - API principale : retrieve(query_vector, question) → {top_k_docs, enriched_prompt}

Usage :
    from data_pipeline.retrieval import retrieve, load_retrieval_resources

    resources = load_retrieval_resources()
    vector = encode_query("Traitement du cancer du sein HER2+")
    result = retrieve(vector, "Traitement du cancer du sein HER2+")
    print(result["enriched_prompt"])
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Configuration & Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("retrieval")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_IDX = BASE_DIR / "data" / "indexes"

FAISS_PATH = DATA_IDX / "faiss_index.bin"
BM25_PATH = DATA_IDX / "bm25_index.pkl"
META_PATH = DATA_IDX / "index_metadata.json"
JSON_PATH = DATA_RAW / "dataset_oncologie_FINAL_v6.json"

# Modèle Sentence-BERT (même que indexer.py)
SBERT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Nombre de candidats à récupérer de chaque moteur avant fusion
CANDIDATE_POOL_SIZE = 30

# Valeur α par défaut (pondération FAISS vs BM25)
DEFAULT_ALPHA = 0.7


# ============================================================================
# 1. CHARGEMENT DES RESSOURCES (avec cache)
# ============================================================================

_CACHED_RESOURCES: Optional[Dict[str, Any]] = None


def load_retrieval_resources(force_reload: bool = False) -> Dict[str, Any]:
    """
    Charge toutes les ressources nécessaires à la recherche hybride.

    Retourne un dict avec :
      - faiss_index : index FAISS chargé
      - bm25_index  : index BM25 chargé
      - metadata    : liste de métadonnées par vecteur
      - dataset     : dataset complet (pour récupérer le contenu)
      - sbert_model : modèle Sentence-BERT chargé

    Les ressources sont mises en cache (singleton) pour éviter
    de recharger à chaque appel.
    """
    global _CACHED_RESOURCES

    if _CACHED_RESOURCES is not None and not force_reload:
        return _CACHED_RESOURCES

    import faiss
    from rank_bm25 import BM25Okapi
    from sentence_transformers import SentenceTransformer

    logger.info("Chargement des ressources de recherche...")

    # Vérifier que les fichiers existent
    for path, name in [(FAISS_PATH, "FAISS index"), (BM25_PATH, "BM25 index"),
                       (META_PATH, "Metadata"), (JSON_PATH, "Dataset")]:
        if not path.exists():
            raise FileNotFoundError(
                f"{name} introuvable : {path}\n"
                "Exécutez d'abord : python -m data_pipeline.indexer"
            )

    # Charger le FAISS index
    logger.info("  Chargement de l'index FAISS...")
    faiss_index = faiss.read_index(str(FAISS_PATH))
    logger.info("    → %d vecteurs", faiss_index.ntotal)

    # Charger le BM25 index
    logger.info("  Chargement de l'index BM25...")
    with open(BM25_PATH, "rb") as f:
        bm25_index = pickle.load(f)

    # Charger les métadonnées
    logger.info("  Chargement des métadonnées...")
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    logger.info("    → %d entrées de métadonnées", len(metadata))

    # Charger le dataset complet (pour le contenu des documents)
    logger.info("  Chargement du dataset...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    logger.info("    → %d documents", len(dataset))

    # Charger le modèle SBERT
    logger.info("  Chargement du modèle Sentence-BERT...")
    sbert_model = SentenceTransformer(SBERT_MODEL)

    _CACHED_RESOURCES = {
        "faiss_index": faiss_index,
        "bm25_index": bm25_index,
        "metadata": metadata,
        "dataset": dataset,
        "sbert_model": sbert_model,
    }

    logger.info("✓ Toutes les ressources chargées avec succès.")
    return _CACHED_RESOURCES


# ============================================================================
# 2. RECHERCHE FAISS (Vectorielle)
# ============================================================================

def _search_faiss(
    query_vector: np.ndarray,
    faiss_index,
    top_n: int = CANDIDATE_POOL_SIZE,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Recherche vectorielle via FAISS.

    Args:
        query_vector: Vecteur de la question (384,)
        faiss_index: Index FAISS chargé
        top_n: Nombre de candidats à retourner

    Returns:
        (indices, scores) — tableaux numpy de taille top_n
    """
    # Assurer le bon format
    q_vec = query_vector.reshape(1, -1).astype("float32")

    # Limiter top_n au nombre de vecteurs dans l'index
    top_n = min(top_n, faiss_index.ntotal)

    scores, indices = faiss_index.search(q_vec, top_n)

    return indices[0], scores[0]


# ============================================================================
# 3. RECHERCHE BM25 (Lexicale)
# ============================================================================

def _search_bm25(
    question: str,
    bm25_index,
    top_n: int = CANDIDATE_POOL_SIZE,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Recherche lexicale via BM25.

    Args:
        question: Question en texte brut
        bm25_index: Index BM25 chargé
        top_n: Nombre de candidats à retourner

    Returns:
        (indices, scores) — tableaux numpy de taille top_n
    """
    from data_pipeline.indexer import tokenize

    query_tokens = tokenize(question)
    all_scores = bm25_index.get_scores(query_tokens)

    # Trier par score décroissant
    top_indices = np.argsort(all_scores)[::-1][:top_n]
    top_scores = all_scores[top_indices]

    return top_indices, top_scores


# ============================================================================
# 4. NORMALISATION DES SCORES
# ============================================================================

def _normalize_scores(scores: np.ndarray) -> np.ndarray:
    """
    Normalise les scores avec min-max scaling vers [0, 1].

    Gère les cas limites :
      - Tous les scores identiques → retourne des 1.0
      - Un seul score → retourne 1.0
      - Scores vides → retourne tableau vide
    """
    if len(scores) == 0:
        return np.array([], dtype="float64")

    min_s = np.min(scores)
    max_s = np.max(scores)

    if max_s == min_s:
        # Tous les scores sont identiques
        return np.ones_like(scores, dtype="float64")

    return (scores - min_s) / (max_s - min_s)


# ============================================================================
# 5. FUSION DES SCORES
# ============================================================================

def _fuse_scores(
    faiss_indices: np.ndarray,
    faiss_scores: np.ndarray,
    bm25_indices: np.ndarray,
    bm25_scores: np.ndarray,
    alpha: float = DEFAULT_ALPHA,
) -> List[Tuple[int, float, float, float]]:
    """
    Fusionne les scores FAISS et BM25 avec la formule :

        score_final = α × score_FAISS_norm + (1 − α) × score_BM25_norm

    Stratégie :
      1. Normaliser chaque ensemble de scores indépendamment (min-max)
      2. Union des candidats des deux moteurs
      3. Calculer le score fusionné pour chaque candidat
      4. Trier par score décroissant

    Args:
        faiss_indices, faiss_scores: Résultats FAISS
        bm25_indices, bm25_scores: Résultats BM25
        alpha: Poids de FAISS (0 = pur BM25, 1 = pur FAISS)

    Returns:
        Liste de tuples (doc_index, score_final, score_faiss_norm, score_bm25_norm)
        triée par score_final décroissant
    """
    # 1. Normaliser les scores
    faiss_norm = _normalize_scores(faiss_scores)
    bm25_norm = _normalize_scores(bm25_scores)

    # 2. Construire des dictionnaires index → score normalisé
    faiss_dict = {}
    for idx, score in zip(faiss_indices, faiss_norm):
        faiss_dict[int(idx)] = float(score)

    bm25_dict = {}
    for idx, score in zip(bm25_indices, bm25_norm):
        bm25_dict[int(idx)] = float(score)

    # 3. Union des candidats
    all_candidates = set(faiss_dict.keys()) | set(bm25_dict.keys())

    # 4. Calculer le score fusionné
    fused_results = []
    for doc_idx in all_candidates:
        s_faiss = faiss_dict.get(doc_idx, 0.0)
        s_bm25 = bm25_dict.get(doc_idx, 0.0)
        score_final = alpha * s_faiss + (1 - alpha) * s_bm25
        fused_results.append((doc_idx, score_final, s_faiss, s_bm25))

    # 5. Trier par score final décroissant
    fused_results.sort(key=lambda x: x[1], reverse=True)

    return fused_results


# ============================================================================
# 6. FILTRAGE PAR MÉTADONNÉES
# ============================================================================

def _apply_filters(
    fused_results: List[Tuple[int, float, float, float]],
    metadata: List[Dict],
    categorie_filter: Optional[str] = None,
    cancer_type_filter: Optional[str] = None,
) -> List[Tuple[int, float, float, float]]:
    """
    Filtre les résultats fusionnés par catégorie et/ou type de cancer.

    Le filtrage se fait AVANT le top-k pour ne pas écarter des documents
    pertinents. Si aucun filtre n'est spécifié, retourne les résultats
    tels quels.

    Args:
        fused_results: Résultats fusionnés (doc_idx, score_final, s_faiss, s_bm25)
        metadata: Liste des métadonnées par index
        categorie_filter: Filtre sur le champ 'categorie' (ex: "traitement")
        cancer_type_filter: Filtre sur le champ 'type_cancer' (ex: "sein")

    Returns:
        Résultats filtrés (même format que l'entrée)
    """
    if categorie_filter is None and cancer_type_filter is None:
        return fused_results

    filtered = []
    for doc_idx, score_final, s_faiss, s_bm25 in fused_results:
        if doc_idx < 0 or doc_idx >= len(metadata):
            continue

        meta = metadata[doc_idx]

        # Filtrage par catégorie
        if categorie_filter is not None:
            if meta.get("categorie", "").lower() != categorie_filter.lower():
                continue

        # Filtrage par type de cancer
        if cancer_type_filter is not None:
            if meta.get("type_cancer", "").lower() != cancer_type_filter.lower():
                continue

        filtered.append((doc_idx, score_final, s_faiss, s_bm25))

    logger.info(
        "  Filtrage : %d → %d résultats (categorie=%s, type_cancer=%s)",
        len(fused_results), len(filtered),
        categorie_filter, cancer_type_filter,
    )

    return filtered


# ============================================================================
# 7. ENRICHISSEMENT DES DOCUMENTS
# ============================================================================

def _enrich_documents(
    fused_results: List[Tuple[int, float, float, float]],
    metadata: List[Dict],
    dataset: List[Dict],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Enrichit les top-k résultats avec le contenu complet du document.

    Chaque document retourné contient :
      - Toutes les métadonnées (id, categorie, type_cancer, titre, etc.)
      - Le contenu complet du document
      - Les scores (final, FAISS normalisé, BM25 normalisé)
      - Le rang

    Args:
        fused_results: Résultats fusionnés et filtrés
        metadata: Métadonnées par index
        dataset: Dataset complet
        top_k: Nombre de documents à retourner

    Returns:
        Liste de dicts enrichis
    """
    enriched = []
    for rank, (doc_idx, score_final, s_faiss, s_bm25) in enumerate(fused_results[:top_k]):
        if doc_idx < 0 or doc_idx >= len(dataset):
            continue

        doc = dataset[doc_idx]
        meta = metadata[doc_idx] if doc_idx < len(metadata) else {}

        enriched_doc = {
            # Métadonnées
            "rank": rank + 1,
            "doc_index": doc_idx,
            "id": meta.get("id", doc.get("id", "")),
            "categorie": meta.get("categorie", doc.get("categorie", "")),
            "type_cancer": meta.get("type_cancer", doc.get("type_cancer", "")),
            "sous_type": meta.get("sous_type", doc.get("sous_type", "")),
            "stade": meta.get("stade", doc.get("stade", "")),
            "titre": meta.get("titre", doc.get("titre", "")),
            "reference": meta.get("reference", doc.get("reference", "")),
            # Contenu complet
            "contenu": doc.get("contenu", ""),
            "mots_cles": doc.get("mots_cles", []),
            "scenario_patient": doc.get("scenario_patient", ""),
            "protocole": doc.get("protocole"),
            "effets_secondaires": doc.get("effets_secondaires", []),
            "metastase": doc.get("metastase", ""),
            # Scores
            "score_final": round(score_final, 4),
            "score_faiss_norm": round(s_faiss, 4),
            "score_bm25_norm": round(s_bm25, 4),
        }
        enriched.append(enriched_doc)

    return enriched


# ============================================================================
# 8. FONCTION PRINCIPALE : retrieve()
# ============================================================================

def retrieve(
    query_vector: np.ndarray,
    question: str,
    *,
    top_k: int = 5,
    alpha: float = DEFAULT_ALPHA,
    categorie_filter: Optional[str] = None,
    cancer_type_filter: Optional[str] = None,
    prompt_strategy: str = "zero_shot",
    candidate_pool_size: int = CANDIDATE_POOL_SIZE,
) -> Dict[str, Any]:
    """
    Recherche hybride FAISS + BM25 avec construction de prompt.

    Pipeline :
      1. Recherche FAISS (top-N candidats sémantiques)
      2. Recherche BM25 (top-N candidats lexicaux)
      3. Normalisation min-max des scores
      4. Fusion : score_final = α × FAISS_norm + (1−α) × BM25_norm
      5. Filtrage par métadonnées (optionnel)
      6. Enrichissement des top-k documents
      7. Construction du prompt avec la stratégie choisie

    Args:
        query_vector: Vecteur encodé de la question (384,), via encode_query()
        question: Question en texte brut (pour BM25 et le prompt)
        top_k: Nombre de documents à retourner (défaut : 5)
        alpha: Poids FAISS dans la fusion (défaut : 0.7)
                α=0 → pur BM25, α=1 → pur FAISS
        categorie_filter: Filtrer par catégorie (ex: "traitement", "diagnostic")
        cancer_type_filter: Filtrer par type de cancer (ex: "sein", "poumon")
        prompt_strategy: Stratégie de prompt ("zero_shot", "few_shot", "chain_of_thought")
        candidate_pool_size: Nombre de candidats par moteur avant fusion

    Returns:
        {
            "top_k_docs": List[Dict],       # Documents enrichis triés par score
            "enriched_prompt": str,          # Prompt prêt pour le LLM
            "scores": List[float],           # Scores finaux fusionnés
            "alpha": float,                  # Valeur α utilisée
            "strategy": str,                 # Stratégie de prompt utilisée
            "num_candidates_faiss": int,     # Candidats FAISS avant fusion
            "num_candidates_bm25": int,      # Candidats BM25 avant fusion
            "num_after_filter": int,         # Résultats après filtrage
            "filters_applied": Dict,         # Filtres appliqués
        }
    """
    from data_pipeline.prompt_builder import build_prompt

    logger.info("=" * 60)
    logger.info("RECHERCHE HYBRIDE — α=%.2f, top_k=%d, stratégie=%s",
                alpha, top_k, prompt_strategy)
    logger.info("  Question : %s", question[:80])

    # Charger les ressources
    resources = load_retrieval_resources()
    faiss_index = resources["faiss_index"]
    bm25_index = resources["bm25_index"]
    metadata = resources["metadata"]
    dataset = resources["dataset"]

    # --- 1. Recherche FAISS ---
    logger.info("  [1/5] Recherche FAISS (top-%d)...", candidate_pool_size)
    faiss_indices, faiss_scores = _search_faiss(
        query_vector, faiss_index, top_n=candidate_pool_size
    )

    # --- 2. Recherche BM25 ---
    logger.info("  [2/5] Recherche BM25 (top-%d)...", candidate_pool_size)
    bm25_indices, bm25_scores = _search_bm25(
        question, bm25_index, top_n=candidate_pool_size
    )

    # --- 3. Fusion des scores ---
    logger.info("  [3/5] Fusion des scores (α=%.2f)...", alpha)
    fused_results = _fuse_scores(
        faiss_indices, faiss_scores,
        bm25_indices, bm25_scores,
        alpha=alpha,
    )
    logger.info("    → %d candidats après fusion", len(fused_results))

    # --- 4. Filtrage par métadonnées ---
    logger.info("  [4/5] Application des filtres...")
    num_before_filter = len(fused_results)
    filtered_results = _apply_filters(
        fused_results, metadata,
        categorie_filter=categorie_filter,
        cancer_type_filter=cancer_type_filter,
    )

    # --- 5. Enrichissement + Prompt ---
    logger.info("  [5/5] Enrichissement des top-%d documents...", top_k)
    top_k_docs = _enrich_documents(
        filtered_results, metadata, dataset, top_k=top_k
    )

    # Construire le prompt
    enriched_prompt = build_prompt(
        question=question,
        documents=top_k_docs,
        strategy=prompt_strategy,
    )

    # Résultat final
    result = {
        "top_k_docs": top_k_docs,
        "enriched_prompt": enriched_prompt,
        "scores": [doc["score_final"] for doc in top_k_docs],
        "alpha": alpha,
        "strategy": prompt_strategy,
        "num_candidates_faiss": len(faiss_indices),
        "num_candidates_bm25": len(bm25_indices),
        "num_after_filter": len(filtered_results),
        "filters_applied": {
            "categorie": categorie_filter,
            "cancer_type": cancer_type_filter,
        },
    }

    logger.info("✓ Recherche terminée : %d documents retournés", len(top_k_docs))
    logger.info("=" * 60)

    return result


# ============================================================================
# 9. EXPÉRIMENTATION : Sweep de α
# ============================================================================

def evaluate_alpha_range(
    test_questions: List[Dict[str, Any]],
    alpha_values: Optional[List[float]] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Évalue la qualité de la recherche pour différentes valeurs de α.

    Pour chaque question de test, on calcule :
      - Hit Rate (le document attendu est-il dans le top-k ?)
      - MRR (Mean Reciprocal Rank)
      - Precision@k

    Args:
        test_questions: Liste de dicts avec :
            - "question": texte de la question
            - "expected_id": ID du document attendu (ex: "ONC-001")
            - "expected_ids": Liste d'IDs pertinents (alternatif)
        alpha_values: Valeurs de α à tester (défaut: 0.0, 0.1, ..., 1.0)
        top_k: Nombre de documents à considérer

    Returns:
        Liste de dicts avec les résultats par valeur de α :
            - alpha, hit_rate, mrr, precision_at_k, details
    """
    from data_pipeline.nlp_query_processor import encode_query

    if alpha_values is None:
        alpha_values = [round(a * 0.1, 1) for a in range(11)]

    logger.info("=" * 60)
    logger.info("ÉVALUATION α — %d questions × %d valeurs de α",
                len(test_questions), len(alpha_values))
    logger.info("=" * 60)

    # Charger les ressources une fois
    resources = load_retrieval_resources()
    faiss_index = resources["faiss_index"]
    bm25_index = resources["bm25_index"]
    metadata = resources["metadata"]
    dataset = resources["dataset"]

    results_by_alpha = []

    for alpha in alpha_values:
        hits = 0
        reciprocal_ranks = []
        precisions = []

        for q_info in test_questions:
            question = q_info["question"]
            expected_ids = q_info.get("expected_ids", [])
            if not expected_ids and "expected_id" in q_info:
                expected_ids = [q_info["expected_id"]]

            # Encoder la question
            q_vec = encode_query(question)

            # Recherche hybride (sans prompt pour optimiser)
            faiss_idx, faiss_sc = _search_faiss(q_vec, faiss_index)
            bm25_idx, bm25_sc = _search_bm25(question, bm25_index)

            fused = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=alpha)
            top_docs = _enrich_documents(fused, metadata, dataset, top_k=top_k)

            # Calculer les métriques
            retrieved_ids = [doc["id"] for doc in top_docs]

            # Hit Rate : au moins un ID attendu dans le top-k
            hit = any(eid in retrieved_ids for eid in expected_ids)
            hits += int(hit)

            # MRR : rang du premier ID attendu trouvé
            rr = 0.0
            for rank, rid in enumerate(retrieved_ids, 1):
                if rid in expected_ids:
                    rr = 1.0 / rank
                    break
            reciprocal_ranks.append(rr)

            # Precision@k : proportion d'IDs attendus dans le top-k
            relevant_in_topk = sum(1 for rid in retrieved_ids if rid in expected_ids)
            precisions.append(relevant_in_topk / top_k)

        n = len(test_questions)
        result = {
            "alpha": alpha,
            "hit_rate": hits / n if n > 0 else 0.0,
            "mrr": np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0,
            "precision_at_k": np.mean(precisions) if precisions else 0.0,
        }
        results_by_alpha.append(result)

        logger.info(
            "  α=%.1f | Hit Rate=%.2f | MRR=%.3f | P@%d=%.3f",
            alpha, result["hit_rate"], result["mrr"], top_k, result["precision_at_k"]
        )

    # Trouver le meilleur α
    best = max(results_by_alpha, key=lambda r: r["mrr"])
    logger.info("\n  ★ Meilleur α = %.1f (MRR=%.3f, Hit Rate=%.2f)",
                best["alpha"], best["mrr"], best["hit_rate"])

    return results_by_alpha


# ============================================================================
# POINT D'ENTRÉE (pour test rapide)
# ============================================================================

if __name__ == "__main__":
    from data_pipeline.nlp_query_processor import encode_query

    print("\n" + "=" * 70)
    print("RETRIEVAL MODULE — Test rapide")
    print("=" * 70)

    question = "Quel est le traitement du cancer du sein HER2+ ?"
    print(f"\nQuestion : {question}")

    # Encoder
    vector = encode_query(question)

    # Recherche hybride
    result = retrieve(
        vector, question,
        top_k=5,
        alpha=0.7,
        prompt_strategy="zero_shot",
    )

    print(f"\n--- Top {len(result['top_k_docs'])} documents ---")
    for doc in result["top_k_docs"]:
        print(f"  [{doc['rank']}] {doc['id']} | {doc['titre'][:60]}")
        print(f"      Score: {doc['score_final']:.4f} "
              f"(FAISS: {doc['score_faiss_norm']:.4f}, BM25: {doc['score_bm25_norm']:.4f})")

    print(f"\n--- Prompt ({result['strategy']}) ---")
    print(result["enriched_prompt"][:500] + "...")

    # Test avec filtre
    print("\n--- Test avec filtre cancer_type='sein' ---")
    result_filtered = retrieve(
        vector, question,
        top_k=3,
        alpha=0.7,
        cancer_type_filter="sein",
        prompt_strategy="few_shot",
    )
    for doc in result_filtered["top_k_docs"]:
        print(f"  [{doc['rank']}] {doc['id']} | {doc['type_cancer']} | {doc['titre'][:50]}")

    print("\n" + "=" * 70)
    print("Test terminé !")
    print("=" * 70)
