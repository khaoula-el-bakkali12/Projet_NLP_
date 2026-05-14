"""
indexer.py — Module data-pipeline
==================================
Preprocessing & Indexation du dataset oncologique.

Livrables générés :
  - data/indexes/faiss_index.bin      : index vectoriel FAISS
  - data/indexes/bm25_index.pkl       : index lexical BM25
  - data/indexes/index_metadata.json  : mapping vecteur → entrée
  - data/raw/dataset_oncologie_FINAL_v6.json : corrigé

Usage :
    python -m data_pipeline.indexer
"""

import json
import os
import re
import pickle
import unicodedata
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from unidecode import unidecode

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("indexer")

BASE_DIR   = Path(__file__).resolve().parent.parent   # racine du projet
DATA_RAW   = BASE_DIR / "data" / "raw"
DATA_IDX   = BASE_DIR / "data" / "indexes"
JSON_PATH  = DATA_RAW / "dataset_oncologie_FINAL_v6.json"

FAISS_PATH    = DATA_IDX / "faiss_index.bin"
BM25_PATH     = DATA_IDX / "bm25_index.pkl"
META_PATH     = DATA_IDX / "index_metadata.json"

# Modèle Sentence-BERT multilingue (français/arabe supportés)
SBERT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Stop-words français (liste compacte des plus fréquents)
FRENCH_STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "d", "l",
    "et", "en", "est", "que", "qui", "dans", "ce", "il", "elle",
    "au", "aux", "son", "sa", "ses", "se", "sur", "par", "pour",
    "pas", "ne", "plus", "ou", "avec", "sont", "ont", "leur", "leurs",
    "a", "été", "cette", "ces", "nous", "vous", "ils", "elles",
    "tout", "tous", "toute", "toutes", "être", "avoir", "fait",
    "peut", "mais", "si", "je", "tu", "mon", "ma", "mes",
    "te", "me", "lui", "y", "dont", "on", "aussi", "même",
    "quand", "entre", "après", "avant", "comme", "très",
    "chez", "encore", "bien", "sans", "sous", "donc", "ni",
}

# Stop-words arabes (les plus courants)
ARABIC_STOPWORDS = {
    "في", "من", "إلى", "على", "و", "هو", "هي", "أن", "ما", "لا",
    "هذا", "هذه", "التي", "الذي", "كان", "عن", "أو", "بين",
    "ذلك", "بعد", "قبل", "كل", "لم", "عند", "قد", "حتى",
    "ان", "مع", "هل", "لن", "ثم", "منذ",
}

ALL_STOPWORDS = FRENCH_STOPWORDS | ARABIC_STOPWORDS

# Schéma attendu pour la validation
REQUIRED_FIELDS = {
    "id":                str,
    "categorie":         str,
    "type_cancer":       str,
    "titre":             str,
    "contenu":           str,
    "mots_cles":         list,
    "reference":         str,
    "est_synthetique":   bool,
    "date_creation":     str,
}


# ============================================================================
# 1. CHARGEMENT & VALIDATION
# ============================================================================

def load_json(path: Path) -> List[Dict[str, Any]]:
    """Charge le fichier JSON du dataset."""
    logger.info("Chargement du dataset depuis %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info("  → %d entrées chargées", len(data))
    return data


def validate_schema(data: List[Dict], required: Dict[str, type]) -> List[str]:
    """Vérifie le schéma, les types et retourne les erreurs trouvées."""
    errors = []
    for i, entry in enumerate(data):
        eid = entry.get("id", f"index-{i}")
        for field, ftype in required.items():
            if field not in entry:
                errors.append(f"{eid}: champ manquant '{field}'")
            elif not isinstance(entry[field], ftype):
                actual = type(entry[field]).__name__
                errors.append(
                    f"{eid}: type incorrect pour '{field}' "
                    f"(attendu {ftype.__name__}, obtenu {actual})"
                )
    return errors


def fix_duplicates(data: List[Dict]) -> List[Dict]:
    """
    Corrige les IDs dupliqués.
    Les entrées 154-177 (épidémiologie, dépistage, recherche) réutilisent
    des IDs existants. On leur attribue de nouveaux IDs uniques.
    Le dataset contient des IDs de formats variés :
      ONC-XXX, ONC-SYN-XXX, ONC-AR-XXX, SMC-SYN-XXX, EXT-SYN-XXX
    """
    from collections import Counter
    id_counts = Counter(d["id"] for d in data)
    dupes = {k for k, v in id_counts.items() if v > 1}

    if not dupes:
        logger.info("  Aucun doublon d'ID détecté.")
        return data

    logger.info("  %d IDs dupliqués détectés, correction en cours…", len(dupes))

    # Trouver le prochain numéro disponible (parcourt tous les formats)
    max_num = 0
    for d in data:
        # Extraire le dernier segment numérique de l'ID
        parts = d["id"].split("-")
        for part in reversed(parts):
            if part.isdigit():
                max_num = max(max_num, int(part))
                break
    next_id = max_num + 1

    seen = set()
    for entry in data:
        eid = entry["id"]
        if eid in seen:
            new_id = f"ONC-{next_id:03d}"
            logger.info("    %s (doublon) → %s (%s)", eid, new_id, entry["titre"][:50])
            entry["id"] = new_id
            next_id += 1
        seen.add(eid)

    return data


def fix_onc029(data: List[Dict]) -> List[Dict]:
    """
    Corrige l'entrée ONC-029 (doublon à l'index 167) :
    - type_cancer était 'sein' au lieu de 'ORL' (titre = cancers lèvres/cavité buccale)
    """
    for entry in data:
        if entry["id"] in ("ONC-029",) or "ONC-0" in entry["id"]:
            # Chercher l'entrée ORL mal classée
            titre_lower = entry.get("titre", "").lower()
            if ("lèvres" in titre_lower or "levres" in titre_lower
                or "cavit" in titre_lower and "buccal" in titre_lower):
                if entry["type_cancer"] != "ORL":
                    logger.info(
                        "  Correction %s: type_cancer '%s' → 'ORL' (titre: %s)",
                        entry["id"], entry["type_cancer"], entry["titre"][:60]
                    )
                    entry["type_cancer"] = "ORL"
    return data


# ============================================================================
# 2. NETTOYAGE & NORMALISATION DU TEXTE
# ============================================================================

def remove_accents(text: str) -> str:
    """Supprime les accents (diacritiques) d'une chaîne."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def clean_text(text: str) -> str:
    """
    Pipeline de nettoyage :
      1. Minuscules
      2. Suppression accents
      3. Suppression caractères spéciaux (garder alphanumérique + espaces)
      4. Normalisation espaces multiples
    """
    text = text.lower()
    text = remove_accents(text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_stopwords(text: str, stopwords: set = ALL_STOPWORDS) -> str:
    """Retire les stop-words français et arabes."""
    tokens = text.split()
    filtered = [t for t in tokens if remove_accents(t.lower()) not in stopwords and len(t) > 1]
    return " ".join(filtered)


def tokenize(text: str) -> List[str]:
    """Tokenise un texte nettoyé en liste de mots."""
    cleaned = clean_text(text)
    cleaned = remove_stopwords(cleaned)
    return cleaned.split()


# ============================================================================
# 3. CONSTRUCTION DU CORPUS POUR BM25
# ============================================================================

def build_corpus_text(entry: Dict) -> str:
    """
    Concatène titre + contenu + mots_clés pour construire le texte BM25.
    """
    titre   = entry.get("titre", "")
    contenu = entry.get("contenu", "")
    mots    = " ".join(entry.get("mots_cles", []))

    # Ajouter aussi le scénario patient et les effets secondaires
    scenario = entry.get("scenario_patient", "") or ""
    effets   = " ".join(entry.get("effets_secondaires", []))
    metastase = entry.get("metastase", "") or ""

    raw = f"{titre} {contenu} {mots} {scenario} {effets} {metastase}"
    return raw


def build_bm25_corpus(data: List[Dict]) -> Tuple[List[List[str]], List[str]]:
    """
    Retourne :
      - tokenized_corpus : liste de listes de tokens (pour BM25)
      - raw_corpus       : liste de textes bruts (pour embedding)
    """
    tokenized = []
    raw = []
    for entry in data:
        text = build_corpus_text(entry)
        raw.append(text)
        tokenized.append(tokenize(text))
    return tokenized, raw


# ============================================================================
# 4. GÉNÉRATION DES EMBEDDINGS (Sentence-BERT)
# ============================================================================

def generate_embeddings(texts: List[str], model_name: str = SBERT_MODEL) -> np.ndarray:
    """
    Génère les embeddings pour une liste de textes avec Sentence-BERT.
    Utilise un modèle multilingue pour supporter français et arabe.
    """
    from sentence_transformers import SentenceTransformer

    logger.info("Chargement du modèle Sentence-BERT : %s", model_name)
    model = SentenceTransformer(model_name)

    logger.info("Génération des embeddings pour %d textes…", len(texts))
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,  # normalisation L2 pour cosine similarity
    )
    logger.info("  → Embeddings shape: %s", embeddings.shape)
    return embeddings.astype("float32")


# ============================================================================
# 5. INDEXATION FAISS (Recherche Vectorielle)
# ============================================================================

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Construit un index FAISS pour la recherche par similarité cosinus.
    Utilise IndexFlatIP (Inner Product) car les vecteurs sont normalisés L2.
    """
    dim = embeddings.shape[1]
    logger.info("Construction de l'index FAISS (dim=%d, n=%d)", dim, len(embeddings))
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    logger.info("  → Index FAISS construit : %d vecteurs", index.ntotal)
    return index


def save_faiss_index(index: faiss.IndexFlatIP, path: Path):
    """Sauvegarde l'index FAISS sur disque."""
    faiss.write_index(index, str(path))
    logger.info("  Index FAISS sauvegardé : %s", path)


def load_faiss_index(path: Path) -> faiss.IndexFlatIP:
    """Charge un index FAISS depuis le disque."""
    return faiss.read_index(str(path))


# ============================================================================
# 6. INDEXATION BM25 (Recherche Lexicale)
# ============================================================================

def build_bm25_index(tokenized_corpus: List[List[str]]) -> BM25Okapi:
    """Construit l'index BM25 à partir du corpus tokenisé."""
    logger.info("Construction de l'index BM25 (%d documents)", len(tokenized_corpus))
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25


def save_bm25_index(bm25: BM25Okapi, path: Path):
    """Sauvegarde l'index BM25 avec pickle."""
    with open(path, "wb") as f:
        pickle.dump(bm25, f)
    logger.info("  Index BM25 sauvegardé : %s", path)


def load_bm25_index(path: Path) -> BM25Okapi:
    """Charge un index BM25 depuis le disque."""
    with open(path, "rb") as f:
        return pickle.load(f)


# ============================================================================
# 7. EXPORT METADATA
# ============================================================================

def build_index_metadata(data: List[Dict]) -> List[Dict]:
    """
    Construit le fichier de métadonnées qui mappe chaque vecteur (par position)
    à son entrée dans le dataset.
    """
    metadata = []
    for i, entry in enumerate(data):
        metadata.append({
            "vector_index":   i,
            "id":             entry["id"],
            "type_cancer":    entry["type_cancer"],
            "categorie":      entry["categorie"],
            "sous_type":      entry.get("sous_type", ""),
            "stade":          entry.get("stade", ""),
            "titre":          entry["titre"],
            "reference":      entry.get("reference", ""),
            "est_synthetique": entry.get("est_synthetique", False),
        })
    return metadata


def save_metadata(metadata: List[Dict], path: Path):
    """Sauvegarde le fichier de métadonnées JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info("  Métadonnées sauvegardées : %s (%d entrées)", path, len(metadata))


# ============================================================================
# 8. FONCTIONS DE RECHERCHE (utilisées par les tests et le module retrieval)
# ============================================================================

def search_faiss(query: str, index: faiss.IndexFlatIP, metadata: List[Dict],
                 model=None, top_k: int = 5) -> List[Dict]:
    """Recherche vectorielle via FAISS."""
    from sentence_transformers import SentenceTransformer

    if model is None:
        model = SentenceTransformer(SBERT_MODEL)

    q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
    scores, indices = index.search(q_emb, top_k)

    results = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
        result = dict(metadata[idx])
        result["score"] = float(score)
        result["rank"]  = rank + 1
        results.append(result)
    return results


def search_bm25(query: str, bm25: BM25Okapi, metadata: List[Dict],
                top_k: int = 5) -> List[Dict]:
    """Recherche lexicale via BM25."""
    query_tokens = tokenize(query)
    scores = bm25.get_scores(query_tokens)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for rank, idx in enumerate(top_indices):
        result = dict(metadata[idx])
        result["score"] = float(scores[idx])
        result["rank"]  = rank + 1
        results.append(result)
    return results


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def run_pipeline():
    """Exécute le pipeline complet de preprocessing et indexation."""
    logger.info("=" * 60)
    logger.info("PIPELINE DE PREPROCESSING & INDEXATION — ONCOLOGIE")
    logger.info("=" * 60)

    # --- 1. Chargement ---
    data = load_json(JSON_PATH)

    # --- 2. Validation du schéma ---
    logger.info("Validation du schéma…")
    errors = validate_schema(data, REQUIRED_FIELDS)
    if errors:
        logger.warning("  %d erreurs de schéma trouvées :", len(errors))
        for e in errors[:10]:
            logger.warning("    • %s", e)
    else:
        logger.info("  ✓ Schéma valide pour toutes les entrées.")

    # --- 3. Correction des doublons ---
    logger.info("Correction des doublons d'ID…")
    data = fix_duplicates(data)

    # --- 4. Correction ONC-029 ---
    logger.info("Correction de ONC-029…")
    data = fix_onc029(data)

    # --- 5. Sauvegarder le dataset corrigé ---
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Dataset corrigé sauvegardé : %s", JSON_PATH)

    # --- 6. Construction du corpus ---
    logger.info("Construction du corpus texte…")
    tokenized_corpus, raw_corpus = build_bm25_corpus(data)
    logger.info("  → Corpus : %d documents, taille moy. %d tokens/doc",
                len(tokenized_corpus),
                int(np.mean([len(t) for t in tokenized_corpus])))

    # --- 7. Génération des embeddings ---
    embeddings = generate_embeddings(raw_corpus)

    # --- 8. Indexation FAISS ---
    faiss_index = build_faiss_index(embeddings)
    save_faiss_index(faiss_index, FAISS_PATH)

    # --- 9. Indexation BM25 ---
    bm25_index = build_bm25_index(tokenized_corpus)
    save_bm25_index(bm25_index, BM25_PATH)

    # --- 10. Export métadonnées ---
    logger.info("Export des métadonnées…")
    metadata = build_index_metadata(data)
    save_metadata(metadata, META_PATH)

    # --- 11. Vérification rapide ---
    logger.info("=" * 60)
    logger.info("VÉRIFICATION RAPIDE")
    logger.info("=" * 60)

    # Test FAISS : chercher chaque entrée, vérifier top-1
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(SBERT_MODEL)

    success_faiss = 0
    success_bm25 = 0
    total = len(data)

    for i, entry in enumerate(data):
        # FAISS test
        q_emb = model.encode([raw_corpus[i]], normalize_embeddings=True).astype("float32")
        _, faiss_ids = faiss_index.search(q_emb, 1)
        if faiss_ids[0][0] == i:
            success_faiss += 1

        # BM25 test
        scores = bm25_index.get_scores(tokenized_corpus[i])
        if np.argmax(scores) == i:
            success_bm25 += 1

    logger.info("  FAISS top-1 self-retrieval : %d/%d (%.1f%%)",
                success_faiss, total, 100 * success_faiss / total)
    logger.info("  BM25  top-1 self-retrieval : %d/%d (%.1f%%)",
                success_bm25, total, 100 * success_bm25 / total)

    logger.info("=" * 60)
    logger.info("PIPELINE TERMINÉ AVEC SUCCÈS")
    logger.info("=" * 60)
    logger.info("Fichiers générés :")
    logger.info("  • %s", FAISS_PATH)
    logger.info("  • %s", BM25_PATH)
    logger.info("  • %s", META_PATH)

    return data, faiss_index, bm25_index, metadata, model


if __name__ == "__main__":
    run_pipeline()
