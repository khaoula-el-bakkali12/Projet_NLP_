"""
nlp_query_processor.py — Module NLP pour la compréhension des questions
========================================================================

Réalise le preprocessing et classification des questions en arabe/français/anglais.

Livrables :
  - Pipeline NLP multilingue (tokenisation, normalisation, stop-words)
  - Classification d'intention (question générale vs clinique spécifique)
  - Encodage des questions avec Sentence-BERT
  - Fonction encode_query() : question → vecteur

Modèles utilisés :
  - Sentence-BERT "paraphrase-multilingual-MiniLM-L12-v2"
    ✓ Supporte FR, AR, EN, +100 langues
    ✓ 384 dimensions (léger, rapide)
    ✓ Fine-tuned sur paraphrase (idéal pour questions variées)
    ✓ Normalisation L2 automatique (cosine similarity)

Usage :
    from data_pipeline.nlp_query_processor import encode_query, classify_intent
    
    question = "Quel est le traitement du cancer du sein HER2+ ?"
    vector = encode_query(question)  # → np.ndarray (384,)
    intent = classify_intent(question)  # → "clinical"

    question_ar = "ما هو العلاج الأول لسرطان الثدي؟"
    vector_ar = encode_query(question_ar)  # ✓ fonctionne aussi
"""

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Configuration & Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nlp_query_processor")

BASE_DIR = Path(__file__).resolve().parent.parent

# Modèle Sentence-BERT multilingue
SBERT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Stop-words français
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
    "est", "c", "ca", "cet", "celui", "semblent", "semble",
    "quel", "quelle", "quels", "quelles", "comment", "pourquoi",
}

# Stop-words arabes
ARABIC_STOPWORDS = {
    "في", "من", "إلى", "على", "و", "هو", "هي", "أن", "ما", "لا",
    "هذا", "هذه", "التي", "الذي", "كان", "عن", "أو", "بين",
    "ذلك", "بعد", "قبل", "كل", "لم", "عند", "قد", "حتى",
    "ان", "مع", "هل", "لن", "ثم", "منذ", "لم", "أم", "إن",
    "كيف", "أين", "متى", "ماذا", "لماذا", "من",
}

# Stop-words anglais (courants)
ENGLISH_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be",
    "have", "has", "had", "do", "does", "did", "will", "would", "should",
    "can", "could", "may", "might", "must", "shall", "what", "which",
    "who", "whom", "where", "when", "why", "how", "as", "if", "that",
    "this", "these", "those", "i", "you", "he", "she", "it", "we", "they",
    "my", "your", "his", "her", "its", "our", "their", "me", "him", "us",
}

ALL_STOPWORDS = FRENCH_STOPWORDS | ARABIC_STOPWORDS | ENGLISH_STOPWORDS

# ============================================================================
# 1. PIPELINE NLP MULTILINGUE
# ============================================================================

def remove_accents(text: str) -> str:
    """
    Supprime les accents/diacritiques (accent aigus, graves, etc.)
    Exemple: "épidémiologie" → "epidemiologie"
    """
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def detect_language(text: str) -> str:
    """
    Détecte la langue principale du texte.
    
    Retourne: "arabic", "french", "english" ou "mixed"
    """
    # Compter caractères arabes et latin
    arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    latin_count = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    
    if arabic_count > latin_count:
        return "arabic"
    elif latin_count > arabic_count:
        # Distinguer français et anglais par certains mots clés
        text_lower = text.lower()
        fr_markers = ["qu'", "ç", "œ", "œuvre", "généralt", "spécifique", "traitement"]
        fr_score = sum(1 for marker in fr_markers if marker in text_lower)
        return "french" if fr_score > 0 else "english"
    else:
        return "mixed"


def clean_text(text: str, remove_punctuation: bool = True) -> str:
    """
    Pipeline de nettoyage du texte :
      1. Minuscules (sauf pour l'arabe qui n'a pas de casse)
      2. Suppression des accents français
      3. Suppression des caractères spéciaux (garder alphanumérique + espaces)
      4. Normalisation des espaces multiples
    
    Args:
        text: Texte à nettoyer
        remove_punctuation: Si True, supprime la ponctuation
    """
    text = text.lower()
    text = remove_accents(text)
    
    if remove_punctuation:
        # Garder alphanumérique + espaces + caractères arabes
        text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    
    # Normaliser espaces multiples
    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def remove_stopwords(text: str, stopwords: set = ALL_STOPWORDS) -> str:
    """
    Retire les stop-words en tous langages.
    
    Stratégie : compare après normalisation (minuscules + accents) pour
    capturer les variantes.
    """
    tokens = text.split()
    filtered = []
    
    for token in tokens:
        # Normaliser pour comparaison
        normalized = remove_accents(token.lower())
        
        # Garder si pas dans stop-words ET longueur > 1
        if normalized not in stopwords and len(token) > 1:
            filtered.append(token)
    
    return " ".join(filtered)


def tokenize(text: str) -> List[str]:
    """
    Tokenise un texte nettoyé en liste de mots.
    """
    cleaned = clean_text(text)
    cleaned = remove_stopwords(cleaned)
    return cleaned.split()


def preprocess_query(query: str, remove_sw: bool = True) -> str:
    """
    Pipeline complet de preprocessing d'une question :
      1. Détection de langue (informatif)
      2. Nettoyage du texte
      3. Suppression stop-words (optionnel)
    
    Returns:
        Texte prétraité
    """
    lang = detect_language(query)
    logger.debug(f"  Langue détectée: {lang}")
    
    cleaned = clean_text(query)
    
    if remove_sw:
        cleaned = remove_stopwords(cleaned)
    
    return cleaned


# ============================================================================
# 2. CLASSIFICATION D'INTENTION
# ============================================================================

# Patterns pour la classification
GENERAL_QUESTION_PATTERNS = {
    # Questions définition
    r"qu'est.*ce.*que",
    r"c'est.*quoi",
    r"define|definition",
    r"qu'est|what is",
    r"qu'est-ce",
    r"ماهو|ماهى|تعريف",
    
    # Questions générales
    r"donner.*info|general info",
    r"explain",
    r"tell.*about",
    r"شرح|معلومات عامة",
}

CLINICAL_QUESTION_PATTERNS = {
    # Traitement
    r"traitement|treatment|علاج",
    r"thérapie|therapy|cure|thérapeutique",
    r"chimiothérapie|chemo|chemotherapy|كيماوي",
    r"radiothérapie|radiation|rayons",
    r"immunothérapie|immuno|immunotherapy",
    r"hormonothérapie|hormone|hormonal",
    
    # Diagnostic/Staging
    r"diagnostic|diagnosis|diagnosis|تشخيص",
    r"stade|stage|grading|classement",
    r"scanner|irm|ct|mri|pet",
    r"biopsy|biopsie|فحص",
    
    # Protocole
    r"protocole|protocol|protocolle",
    r"dosage|dose|جرعة",
    r"schéma|regimen|نظام",
    r"taux.*survie|survival",
    
    # Symptômes/Effets
    r"symptôm|symptom|علامة",
    r"effet.*secondaire|side effect|الآثار الجانبية",
    r"toxicité|toxicity|complications",
    r"prognosis|pronostic|توقعات",
    
    # Patient specifics
    r"her2|hormone.*receptor|récepteur",
    r"grade|grading|histology|histologie",
    r"mutation|brca|p53|tp53",
    r"score|index|grade.*malignité",
}

def classify_intent(query: str) -> Dict[str, Any]:
    """
    Classifie l'intention d'une question.
    
    Retourne dict avec:
      - intent: "clinical" ou "general"
      - confidence: float [0, 1]
      - matched_patterns: list de patterns qui ont matché
    
    Logique :
      1. Chercher les patterns de question clinique
      2. Si aucun → question générale
      3. Calculer confiance = nombre de patterns matchés
    """
    query_lower = clean_text(query)
    
    clinical_matches = []
    general_matches = []
    
    # Tester les patterns cliniques
    for pattern in CLINICAL_QUESTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            clinical_matches.append(pattern)
    
    # Tester les patterns généraux
    for pattern in GENERAL_QUESTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            general_matches.append(pattern)
    
    # Déterminer l'intention
    if clinical_matches and len(clinical_matches) >= len(general_matches):
        intent = "clinical"
        confidence = min(len(clinical_matches) / 3.0, 1.0)  # normaliser
        matches = clinical_matches
    else:
        intent = "general"
        confidence = min(len(general_matches) / 2.0, 1.0) if general_matches else 0.5
        matches = general_matches
    
    return {
        "intent": intent,
        "confidence": confidence,
        "matched_patterns": matches,
        "language": detect_language(query),
    }


# ============================================================================
# 3. ENCODAGE AVEC SENTENCE-BERT
# ============================================================================

_SBERT_MODEL = None  # Cache global du modèle

def get_sbert_model(model_name: str = SBERT_MODEL):
    """
    Charge le modèle Sentence-BERT une seule fois (cache).
    
    Raison du cache : les modèles LLM sont lourds (~150 MB).
    Les charger une fois améliore les perfs.
    """
    global _SBERT_MODEL
    if _SBERT_MODEL is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Chargement du modèle Sentence-BERT: {model_name}")
        _SBERT_MODEL = SentenceTransformer(model_name)
    return _SBERT_MODEL


def encode_query(query: str, preprocess: bool = True, model_name: str = SBERT_MODEL) -> np.ndarray:
    """
    Encode une question en vecteur dense avec Sentence-BERT.
    
    **Pipeline:**
      1. Prétraitement optionnel (tokenisation, suppression stop-words)
      2. Chargement du modèle (cache)
      3. Encodage avec normalisation L2
    
    **Args:**
        query: Question en français, arabe ou anglais
        preprocess: Si True, applique le preprocessing NLP
        model_name: Nom du modèle HuggingFace
    
    **Returns:**
        np.ndarray de shape (384,) et dtype float32
        Les vecteurs sont normalisés L2 (prêts pour cosine similarity)
    
    **Exemple:**
        >>> query = "Quel est le traitement du cancer du sein HER2+ ?"
        >>> vector = encode_query(query)
        >>> vector.shape
        (384,)
        >>> np.linalg.norm(vector)  # vérifier normalisation
        1.0
    """
    if preprocess:
        query_processed = preprocess_query(query)
        logger.debug(f"Query brut: {query[:50]}...")
        logger.debug(f"Query prétraité: {query_processed[:50]}...")
    else:
        query_processed = query
    
    # Charger le modèle
    model = get_sbert_model(model_name)
    
    # Encoder
    embedding = model.encode(
        query_processed,
        normalize_embeddings=True,  # L2 normalization
        convert_to_numpy=True,
    ).astype("float32")
    
    return embedding


def encode_queries_batch(queries: List[str], preprocess: bool = True, 
                        batch_size: int = 32) -> np.ndarray:
    """
    Encode plusieurs questions en batch (plus efficace).
    
    **Args:**
        queries: Liste de questions
        preprocess: Si True, applique preprocessing à chaque question
        batch_size: Taille du batch (par défaut 32)
    
    **Returns:**
        np.ndarray de shape (n_queries, 384) et dtype float32
    """
    if preprocess:
        queries_processed = [preprocess_query(q) for q in queries]
    else:
        queries_processed = queries
    
    model = get_sbert_model()
    
    logger.info(f"Encodage en batch de {len(queries)} questions...")
    embeddings = model.encode(
        queries_processed,
        show_progress_bar=True,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")
    
    return embeddings


# ============================================================================
# 4. ÉVALUATION QUALITÉ DES EMBEDDINGS
# ============================================================================

def compute_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs.
    (Rapide car les vecteurs sont déjà normalisés L2)
    """
    return float(np.dot(vec1, vec2))


def evaluate_embedding_quality(test_queries: List[Tuple[str, str]], 
                               similarity_threshold: float = 0.5) -> Dict[str, Any]:
    """
    Évalue la qualité des embeddings sur des paires de questions.
    
    **Principe:**
      Les questions sémantiquement proches doivent avoir haute similarité.
      Les questions différentes doivent avoir basse similarité.
    
    **Args:**
        test_queries: Liste de tuples (question1, question2, should_be_similar)
        similarity_threshold: Seuil pour considérer comme similaire
    
    **Returns:**
        Dict avec métrique d'évaluation
    """
    logger.info("Évaluation de la qualité des embeddings...")
    
    similarities = []
    predictions = []
    actuals = []
    
    for q1, q2, should_match in test_queries:
        v1 = encode_query(q1)
        v2 = encode_query(q2)
        sim = compute_similarity(v1, v2)
        
        pred = sim >= similarity_threshold
        actual = should_match
        
        similarities.append(sim)
        predictions.append(pred)
        actuals.append(actual)
    
    # Calcul des métriques
    similarities = np.array(similarities)
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    
    accuracy = np.mean(predictions == actuals)
    true_positives = np.sum((predictions == True) & (actuals == True))
    false_positives = np.sum((predictions == True) & (actuals == False))
    false_negatives = np.sum((predictions == False) & (actuals == True))
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "mean_similarity": float(similarities.mean()),
        "std_similarity": float(similarities.std()),
        "min_similarity": float(similarities.min()),
        "max_similarity": float(similarities.max()),
    }


# ============================================================================
# TESTS MANUELS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("NLP QUERY PROCESSOR — Tests")
    print("="*70)
    
    # Test 1: Prétraitement multilingue
    print("\n1️⃣ PREPROCESSING MULTILINGUE")
    print("-" * 70)
    
    test_queries = [
        "Quel est le traitement du cancer du sein HER2+ ?",
        "ما هو العلاج الأول لسرطان الثدي ؟",
        "What are the side effects of trastuzumab therapy?",
    ]
    
    for q in test_queries:
        preprocessed = preprocess_query(q)
        lang = detect_language(q)
        print(f"  [{lang.upper():6s}] {q}")
        print(f"  → {preprocessed}\n")
    
    # Test 2: Classification d'intention
    print("\n2️⃣ CLASSIFICATION D'INTENTION")
    print("-" * 70)
    
    test_intents = [
        "Quel est le traitement standard du cancer du sein HER2+ ?",
        "Qu'est-ce que le cancer ?",
        "ما هو العلاج الأول لسرطان الثدي؟",
        "Définition du cancer du pancréas",
    ]
    
    for q in test_intents:
        result = classify_intent(q)
        print(f"  Question: {q}")
        print(f"    Intent: {result['intent']:8s} | Confidence: {result['confidence']:.2f} | Lang: {result['language']}")
        print()
    
    # Test 3: Encodage et similarité
    print("\n3️⃣ ENCODAGE & SIMILARITÉ")
    print("-" * 70)
    
    pairs = [
        ("Traitement du cancer du sein", "Protocole thérapeutique pour le cancer mammaire", True),
        ("Effets secondaires du trastuzumab", "Quel est le traitement du cancer ?", False),
    ]
    
    for q1, q2, should_be_similar in pairs:
        v1 = encode_query(q1)
        v2 = encode_query(q2)
        sim = compute_similarity(v1, v2)
        match = "✓" if (sim > 0.5) == should_be_similar else "✗"
        print(f"  {match} Similarity: {sim:.3f} | Expected similar: {should_be_similar}")
        print(f"    Q1: {q1}")
        print(f"    Q2: {q2}\n")
    
    print("="*70)
    print("Tests complétés !")
    print("="*70)
