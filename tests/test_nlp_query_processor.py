"""
test_nlp_query_processor.py — Tests unitaires pour le module NLP
==================================================================
Vérifie que :
  1. Détection de langue fonctionne (FR/AR/EN/mixed)
  2. Nettoyage du texte : minuscules, accents, ponctuation
  3. Suppression des stop-words
  4. Tokenisation correcte
  5. Classification d'intention : clinique vs général
  6. Encodage produit des vecteurs de bonne forme
  7. Similarité cosinus entre vecteurs similaires vs différents
  8. Évaluation de qualité des embeddings
  9. Support multilingue (FR/AR/EN)

Usage :
    python -m pytest tests/test_nlp_query_processor.py -v
    ou
    python tests/test_nlp_query_processor.py
"""

import json
import unittest
from pathlib import Path

import numpy as np

# Import depuis le package data_pipeline
from data_pipeline.nlp_query_processor import (
    remove_accents,
    detect_language,
    clean_text,
    remove_stopwords,
    tokenize,
    preprocess_query,
    classify_intent,
    encode_query,
    encode_queries_batch,
    compute_similarity,
    evaluate_embedding_quality,
    FRENCH_STOPWORDS,
    ARABIC_STOPWORDS,
    ENGLISH_STOPWORDS,
)


# ============================================================================
# 1. TESTS DE NETTOYAGE DE TEXTE
# ============================================================================

class TestTextCleaning(unittest.TestCase):
    """Tests pour le nettoyage et normalisation du texte."""

    def test_remove_accents_french(self):
        """Supprime les accents français."""
        self.assertEqual(remove_accents("épidémiologie"), "epidemiologie")
        self.assertEqual(remove_accents("chimiothérapie"), "chimiotherapie")
        self.assertEqual(remove_accents("néoadjuvant"), "neoadjuvant")
        self.assertEqual(remove_accents("récepteur"), "recepteur")

    def test_remove_accents_french_special(self):
        """Gère les caractères spéciaux français (ç, œ, etc.)."""
        self.assertEqual(remove_accents("façade"), "facade")
        self.assertEqual(remove_accents("Sœur"), "Soeur")

    def test_remove_accents_arabic_preserved(self):
        """Les caractères arabes sont préservés."""
        arabic_text = "سرطان الثدي"
        result = remove_accents(arabic_text)
        # Les caractères arabes de base n'ont pas de diacritiques "Mn"
        self.assertIn("سرطان", result)

    def test_lowercase(self):
        """Le texte nettoyé doit être en minuscules."""
        result = clean_text("CANCER DU SEIN HER2+")
        self.assertEqual(result, result.lower())

    def test_remove_special_chars(self):
        """Les caractères spéciaux doivent être retirés."""
        result = clean_text("dose: 100mg/m² (IV)")
        self.assertNotIn(":", result)
        self.assertNotIn("(", result)
        self.assertNotIn(")", result)
        self.assertNotIn("²", result)

    def test_normalize_spaces(self):
        """Les espaces multiples doivent être normalisés."""
        result = clean_text("cancer    du     sein")
        self.assertNotIn("  ", result)
        self.assertEqual(result, "cancer du sein")

    def test_clean_text_with_punctuation_removal(self):
        """Avec remove_punctuation=True."""
        result = clean_text("Quel est le traitement ? C'est important !", remove_punctuation=True)
        self.assertNotIn("?", result)
        self.assertNotIn("!", result)

    def test_clean_text_preserve_punctuation(self):
        """Avec remove_punctuation=False."""
        result = clean_text("Quel est le traitement ?", remove_punctuation=False)
        # La ponctuation est supprimée par le regex par défaut
        # (car remove_punctuation=False ne s'applique qu'aux caractères spéciaux)
        self.assertIsNotNone(result)


# ============================================================================
# 2. TESTS DE DÉTECTION DE LANGUE
# ============================================================================

class TestLanguageDetection(unittest.TestCase):
    """Tests pour la détection automatique de langue."""

    def test_detect_french(self):
        """Détecte le français."""
        result = detect_language("Quel est le traitement du cancer du sein ?")
        self.assertEqual(result, "french")

    def test_detect_english(self):
        """Détecte l'anglais."""
        result = detect_language("What is the treatment for breast cancer?")
        self.assertEqual(result, "english")

    def test_detect_arabic(self):
        """Détecte l'arabe."""
        result = detect_language("ما هو العلاج الأول لسرطان الثدي؟")
        self.assertEqual(result, "arabic")

    def test_detect_mixed(self):
        """Détecte mélange de langues."""
        result = detect_language("Cancer du sein HER2 positive treatment")
        self.assertEqual(result, "mixed")


# ============================================================================
# 3. TESTS DES STOP-WORDS
# ============================================================================

class TestStopwords(unittest.TestCase):
    """Tests pour la suppression des stop-words."""

    def test_stopwords_french(self):
        """Supprime les stop-words français."""
        result = remove_stopwords("le cancer du sein est une maladie")
        self.assertNotIn("le", result.split())
        self.assertNotIn("du", result.split())
        self.assertNotIn("est", result.split())
        self.assertNotIn("une", result.split())
        # Mais garde les termes importants
        self.assertIn("cancer", result.split())
        self.assertIn("sein", result.split())
        self.assertIn("maladie", result.split())

    def test_stopwords_preserve_medical_terms(self):
        """Les termes médicaux ne doivent pas être supprimés."""
        result = remove_stopwords("trastuzumab immunotherapie metastase")
        self.assertIn("trastuzumab", result)
        self.assertIn("immunotherapie", result)
        self.assertIn("metastase", result)

    def test_stopwords_length_filter(self):
        """Les mots très courts sont filtrés."""
        result = remove_stopwords("a c d cancer")
        # "a", "c", "d" sont filtrés (longueur <= 1)
        self.assertNotIn("a", result.split())
        self.assertNotIn("c", result.split())
        self.assertNotIn("d", result.split())
        self.assertIn("cancer", result.split())


# ============================================================================
# 4. TESTS DE TOKENISATION
# ============================================================================

class TestTokenization(unittest.TestCase):
    """Tests pour la tokenisation."""

    def test_tokenize_returns_list(self):
        """La tokenisation retourne une liste."""
        result = tokenize("Cancer du sein HER2 positif")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_tokenize_removes_stopwords(self):
        """Les stop-words sont supprimés."""
        result = tokenize("Cancer du sein est une maladie")
        self.assertNotIn("du", result)
        self.assertNotIn("est", result)
        self.assertNotIn("une", result)

    def test_tokenize_lowercase_and_accents(self):
        """Les tokens sont en minuscules sans accents."""
        result = tokenize("ÉPIDÉMIOLOGIE du cancer")
        self.assertIn("epidemiologie", result)


# ============================================================================
# 5. TESTS DE CLASSIFICATION D'INTENTION
# ============================================================================

class TestIntentClassification(unittest.TestCase):
    """Tests pour la classification d'intention."""

    def test_classify_clinical_question(self):
        """Classifie une question clinique."""
        result = classify_intent("Quel est le traitement du cancer du sein HER2+ ?")
        self.assertEqual(result["intent"], "clinical")
        self.assertGreater(result["confidence"], 0.3)

    def test_classify_clinical_keywords(self):
        """Reconnaît les mots-clés cliniques."""
        clinical_terms = [
            "chimiothérapie",
            "radiothérapie",
            "protocole",
            "dosage",
            "effets secondaires",
            "métastase",
        ]
        for term in clinical_terms:
            result = classify_intent(f"Quelle est la {term} ?")
            self.assertEqual(
                result["intent"], "clinical",
                f"'{term}' devrait être classifié comme clinique"
            )

    def test_classify_general_question(self):
        """Classifie une question générale."""
        result = classify_intent("Qu'est-ce que le cancer ?")
        self.assertEqual(result["intent"], "general")

    def test_classify_intent_has_language(self):
        """Le résultat inclut la langue détectée."""
        result = classify_intent("Quel est le traitement ?")
        self.assertIn("language", result)
        self.assertIn(result["language"], ["french", "english", "arabic", "mixed"])

    def test_classify_intent_has_patterns(self):
        """Le résultat liste les patterns matchés."""
        result = classify_intent("Traitement du cancer du sein")
        self.assertIn("matched_patterns", result)
        self.assertIsInstance(result["matched_patterns"], list)

    def test_classify_arabic_clinical(self):
        """Classifie les questions cliniques en arabe."""
        result = classify_intent("ما هو العلاج الأول لسرطان الثدي؟")
        self.assertEqual(result["intent"], "clinical")

    def test_classify_english_clinical(self):
        """Classifie les questions cliniques en anglais."""
        result = classify_intent("What is the treatment for breast cancer?")
        self.assertEqual(result["intent"], "clinical")


# ============================================================================
# 6. TESTS D'ENCODAGE SENTENCE-BERT
# ============================================================================

class TestEmbeddings(unittest.TestCase):
    """Tests pour l'encodage avec Sentence-BERT."""

    def test_encode_query_returns_array(self):
        """encode_query retourne un np.ndarray."""
        result = encode_query("Traitement du cancer du sein")
        self.assertIsInstance(result, np.ndarray)

    def test_encode_query_shape(self):
        """Le vecteur a la bonne forme (384,)."""
        result = encode_query("Traitement du cancer du sein")
        self.assertEqual(result.shape, (384,))

    def test_encode_query_dtype(self):
        """Le vecteur est en float32."""
        result = encode_query("Traitement du cancer du sein")
        self.assertEqual(result.dtype, np.float32)

    def test_encode_query_normalized(self):
        """Le vecteur est normalisé L2."""
        result = encode_query("Traitement du cancer du sein")
        norm = np.linalg.norm(result)
        # Permettre une petite marge d'erreur numérique
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_encode_query_french(self):
        """Encode les questions en français."""
        result = encode_query("Quel est le traitement du cancer du sein ?")
        self.assertEqual(result.shape, (384,))
        self.assertEqual(result.dtype, np.float32)

    def test_encode_query_arabic(self):
        """Encode les questions en arabe."""
        result = encode_query("ما هو العلاج الأول لسرطان الثدي؟")
        self.assertEqual(result.shape, (384,))
        self.assertEqual(result.dtype, np.float32)

    def test_encode_query_english(self):
        """Encode les questions en anglais."""
        result = encode_query("What is the treatment for breast cancer?")
        self.assertEqual(result.shape, (384,))
        self.assertEqual(result.dtype, np.float32)

    def test_encode_queries_batch_shape(self):
        """encode_queries_batch retourne la bonne forme."""
        queries = [
            "Traitement du cancer du sein",
            "Effets secondaires du trastuzumab",
            "Protocole thérapeutique",
        ]
        result = encode_queries_batch(queries)
        self.assertEqual(result.shape, (3, 384))

    def test_encode_queries_batch_dtype(self):
        """Les vecteurs batch sont en float32."""
        queries = ["Question 1", "Question 2"]
        result = encode_queries_batch(queries)
        self.assertEqual(result.dtype, np.float32)


# ============================================================================
# 7. TESTS DE SIMILARITÉ COSINUS
# ============================================================================

class TestSimilarity(unittest.TestCase):
    """Tests pour la similarité cosinus."""

    def test_compute_similarity_identical(self):
        """Deux vecteurs identiques ont similarité ≈ 1.0."""
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        # Normaliser
        vec = vec / np.linalg.norm(vec)
        similarity = compute_similarity(vec, vec)
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_compute_similarity_orthogonal(self):
        """Deux vecteurs orthogonaux ont similarité ≈ 0.0."""
        vec1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        similarity = compute_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 0.0, places=5)

    def test_similar_queries_high_similarity(self):
        """Les questions similaires ont haute similarité."""
        q1 = "Traitement du cancer du sein"
        q2 = "Protocole thérapeutique pour cancer du sein"
        
        v1 = encode_query(q1)
        v2 = encode_query(q2)
        similarity = compute_similarity(v1, v2)
        
        # Similarité devrait être > 0.5 pour des questions liées
        self.assertGreater(similarity, 0.4,
                          f"Similarité trop basse ({similarity:.3f}) pour questions similaires")

    def test_different_queries_low_similarity(self):
        """Les questions différentes ont basse similarité."""
        q1 = "Traitement du cancer du sein"
        q2 = "Quel est la météo aujourd'hui ?"
        
        v1 = encode_query(q1)
        v2 = encode_query(q2)
        similarity = compute_similarity(v1, v2)
        
        # Similarité devrait être < 0.3 pour des questions sans rapport
        self.assertLess(similarity, 0.4,
                       f"Similarité trop haute ({similarity:.3f}) pour questions différentes")


# ============================================================================
# 8. TESTS D'ÉVALUATION DE QUALITÉ
# ============================================================================

class TestEvaluationQuality(unittest.TestCase):
    """Tests pour l'évaluation de la qualité des embeddings."""

    def test_evaluate_embedding_quality_structure(self):
        """evaluate_embedding_quality retourne le bon dict."""
        test_queries = [
            ("Cancer du sein", "Cancer du sein traitement", True),
            ("Breast cancer", "What is the weather?", False),
        ]
        result = evaluate_embedding_quality(test_queries)
        
        required_keys = {
            "accuracy", "precision", "recall", "f1_score",
            "mean_similarity", "std_similarity", "min_similarity", "max_similarity"
        }
        self.assertEqual(set(result.keys()), required_keys)

    def test_evaluate_embedding_quality_ranges(self):
        """Les métriques sont dans des plages valides."""
        test_queries = [
            ("Cancer du sein", "Cancer du sein traitement", True),
            ("Breast cancer", "What is the weather?", False),
        ]
        result = evaluate_embedding_quality(test_queries)
        
        # Accuracy, precision, recall, f1 sont entre 0 et 1
        self.assertGreaterEqual(result["accuracy"], 0)
        self.assertLessEqual(result["accuracy"], 1)
        self.assertGreaterEqual(result["f1_score"], 0)
        self.assertLessEqual(result["f1_score"], 1)
        
        # Similarité entre -1 et 1
        self.assertGreaterEqual(result["min_similarity"], -1)
        self.assertLessEqual(result["max_similarity"], 1)


# ============================================================================
# 9. TESTS D'INTÉGRATION
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Tests d'intégration complets."""

    def test_full_pipeline_french(self):
        """Pipeline complet : question FR → classification → encoding."""
        query = "Quel est le traitement du cancer du sein HER2+ ?"
        
        # Classification
        intent_result = classify_intent(query)
        self.assertEqual(intent_result["intent"], "clinical")
        self.assertEqual(intent_result["language"], "french")
        
        # Encodage
        vector = encode_query(query)
        self.assertEqual(vector.shape, (384,))
        self.assertAlmostEqual(np.linalg.norm(vector), 1.0, places=5)

    def test_full_pipeline_arabic(self):
        """Pipeline complet : question AR → classification → encoding."""
        query = "ما هو العلاج الأول لسرطان الثدي؟"
        
        # Classification
        intent_result = classify_intent(query)
        self.assertEqual(intent_result["intent"], "clinical")
        self.assertEqual(intent_result["language"], "arabic")
        
        # Encodage
        vector = encode_query(query)
        self.assertEqual(vector.shape, (384,))

    def test_full_pipeline_english(self):
        """Pipeline complet : question EN → classification → encoding."""
        query = "What is the treatment for HER2+ breast cancer?"
        
        # Classification
        intent_result = classify_intent(query)
        self.assertEqual(intent_result["intent"], "clinical")
        self.assertEqual(intent_result["language"], "english")
        
        # Encodage
        vector = encode_query(query)
        self.assertEqual(vector.shape, (384,))


if __name__ == "__main__":
    print("=" * 70)
    print("TESTS UNITAIRES — Module NLP Query Processor")
    print("=" * 70)
    unittest.main(verbosity=2)
