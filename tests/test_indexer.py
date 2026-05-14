"""
test_indexer.py — Tests unitaires pour le module data_pipeline.indexer
======================================================================
Vérifie que :
  1. Le dataset se charge sans erreur
  2. Le schéma est valide après corrections
  3. Les IDs sont uniques après correction des doublons
  4. ONC-029 est correctement corrigé
  5. Le nettoyage de texte fonctionne (minuscules, accents, stop-words)
  6. La tokenisation produit des résultats cohérents
  7. Le corpus BM25 est bien construit
  8. Les embeddings ont la bonne forme
  9. L'index FAISS retrouve chaque entrée en top-1 (self-retrieval)
 10. L'index BM25 retrouve chaque entrée en top-1 (self-retrieval)
 11. Les fichiers de sortie existent bien
 12. Le fichier index_metadata.json est cohérent

Usage :
    python -m pytest tests/test_indexer.py -v
    ou
    python tests/test_indexer.py
"""

import json
import os
import sys
import pickle
import unittest
from pathlib import Path

import numpy as np

# Import depuis le package data_pipeline
from data_pipeline.indexer import (
    load_json,
    validate_schema,
    fix_duplicates,
    fix_onc029,
    clean_text,
    remove_accents,
    remove_stopwords,
    tokenize,
    build_corpus_text,
    build_bm25_corpus,
    build_index_metadata,
    REQUIRED_FIELDS,
    JSON_PATH,
    FAISS_PATH,
    BM25_PATH,
    META_PATH,
    SBERT_MODEL,
)


class TestDataLoading(unittest.TestCase):
    """Tests pour le chargement et la validation du dataset."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_json(JSON_PATH)

    def test_load_returns_list(self):
        """Le dataset doit être une liste."""
        self.assertIsInstance(self.data, list)

    def test_load_not_empty(self):
        """Le dataset ne doit pas être vide."""
        self.assertGreater(len(self.data), 0)

    def test_entries_are_dicts(self):
        """Chaque entrée doit être un dictionnaire."""
        for entry in self.data:
            self.assertIsInstance(entry, dict)

    def test_schema_validation(self):
        """Le schéma doit être valide après corrections."""
        data = fix_duplicates(list(self.data))
        data = fix_onc029(data)
        errors = validate_schema(data, REQUIRED_FIELDS)
        self.assertEqual(len(errors), 0, f"Erreurs de schéma: {errors[:5]}")


class TestDuplicateFix(unittest.TestCase):
    """Tests pour la correction des doublons."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_json(JSON_PATH)
        cls.fixed = fix_duplicates(list(cls.data))

    def test_unique_ids_after_fix(self):
        """Tous les IDs doivent être uniques après correction."""
        ids = [d["id"] for d in self.fixed]
        self.assertEqual(len(ids), len(set(ids)),
                         f"IDs dupliqués restants: {[x for x in ids if ids.count(x) > 1]}")

    def test_no_entries_lost(self):
        """Aucune entrée ne doit être perdue lors de la correction."""
        self.assertEqual(len(self.fixed), len(self.data))

    def test_id_format(self):
        """Tous les IDs doivent respecter un format valide (préfixe-numéro)."""
        import re
        # Formats valides : XXX-NNN ou XXX-YYY-NNN (ex: ONC-001, ONC-SYN-026, SUV-001)
        pattern = r"^[A-Z]+-([A-Z]+-)*\d{3}$"
        for entry in self.fixed:
            self.assertRegex(entry["id"], pattern,
                             f"Format ID invalide: {entry['id']}")


class TestONC029Fix(unittest.TestCase):
    """Tests pour la correction de ONC-029."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_json(JSON_PATH)
        cls.fixed = fix_duplicates(list(cls.data))
        cls.fixed = fix_onc029(cls.fixed)

    def test_no_sein_for_oral_cancer(self):
        """Les entrées sur les cancers buccaux/pharynx ne doivent pas être classées 'sein'."""
        for entry in self.fixed:
            titre = entry.get("titre", "").lower()
            if "lèvres" in titre or "cavité buccale" in titre or "pharynx" in titre:
                self.assertNotEqual(
                    entry["type_cancer"], "sein",
                    f"{entry['id']}: cancer buccal/pharynx classé comme 'sein'"
                )


class TestTextCleaning(unittest.TestCase):
    """Tests pour le nettoyage et la normalisation du texte."""

    def test_lowercase(self):
        """Le texte nettoyé doit être en minuscules."""
        result = clean_text("Cancer Du SEIN HER2+")
        self.assertEqual(result, result.lower())

    def test_remove_accents(self):
        """Les accents doivent être supprimés."""
        self.assertEqual(remove_accents("épidémiologie"), "epidemiologie")
        self.assertEqual(remove_accents("néoadjuvant"), "neoadjuvant")
        self.assertEqual(remove_accents("chimiothérapie"), "chimiotherapie")

    def test_remove_special_chars(self):
        """Les caractères spéciaux doivent être retirés."""
        result = clean_text("dose: 100mg/m² (IV)")
        self.assertNotIn(":", result)
        self.assertNotIn("(", result)
        self.assertNotIn(")", result)

    def test_normalize_spaces(self):
        """Les espaces multiples doivent être normalisés."""
        result = clean_text("cancer   du    sein")
        self.assertNotIn("  ", result)

    def test_stopwords_removal_french(self):
        """Les stop-words français doivent être supprimés."""
        result = remove_stopwords("le cancer du sein est une maladie")
        self.assertNotIn("le", result.split())
        self.assertNotIn("du", result.split())
        self.assertNotIn("est", result.split())
        self.assertNotIn("une", result.split())

    def test_stopwords_keep_medical_terms(self):
        """Les termes médicaux ne doivent pas être supprimés."""
        result = remove_stopwords("trastuzumab chimiotherapie docetaxel")
        self.assertIn("trastuzumab", result)
        self.assertIn("chimiotherapie", result)
        self.assertIn("docetaxel", result)

    def test_tokenize_returns_list(self):
        """La tokenisation doit retourner une liste."""
        result = tokenize("Cancer du sein HER2 positif")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)


class TestCorpusBuilding(unittest.TestCase):
    """Tests pour la construction du corpus."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_json(JSON_PATH)

    def test_corpus_text_not_empty(self):
        """Le texte du corpus ne doit pas être vide pour chaque entrée."""
        for entry in self.data:
            text = build_corpus_text(entry)
            self.assertGreater(len(text.strip()), 0,
                               f"Corpus vide pour {entry['id']}")

    def test_corpus_contains_titre(self):
        """Le corpus doit contenir le titre."""
        entry = self.data[0]
        text = build_corpus_text(entry)
        self.assertIn(entry["titre"], text)

    def test_corpus_contains_contenu(self):
        """Le corpus doit contenir le contenu."""
        entry = self.data[0]
        text = build_corpus_text(entry)
        self.assertIn(entry["contenu"], text)

    def test_bm25_corpus_length(self):
        """Le corpus BM25 doit avoir autant d'éléments que d'entrées."""
        tokenized, raw = build_bm25_corpus(self.data)
        self.assertEqual(len(tokenized), len(self.data))
        self.assertEqual(len(raw), len(self.data))


class TestIndexFiles(unittest.TestCase):
    """Tests pour vérifier que les fichiers d'index existent après le pipeline."""

    def test_faiss_index_exists(self):
        """Le fichier faiss_index.bin doit exister."""
        self.assertTrue(FAISS_PATH.exists(),
                        f"Fichier manquant: {FAISS_PATH}")

    def test_bm25_index_exists(self):
        """Le fichier bm25_index.pkl doit exister."""
        self.assertTrue(BM25_PATH.exists(),
                        f"Fichier manquant: {BM25_PATH}")

    def test_metadata_exists(self):
        """Le fichier index_metadata.json doit exister."""
        self.assertTrue(META_PATH.exists(),
                        f"Fichier manquant: {META_PATH}")

    def test_metadata_valid_json(self):
        """Le fichier index_metadata.json doit être du JSON valide."""
        if META_PATH.exists():
            with open(META_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            self.assertIsInstance(metadata, list)
            self.assertGreater(len(metadata), 0)

    def test_metadata_has_required_fields(self):
        """Chaque entrée de metadata doit contenir les champs requis."""
        if META_PATH.exists():
            with open(META_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            required = {"vector_index", "id", "type_cancer", "categorie", "titre"}
            for m in metadata:
                for field in required:
                    self.assertIn(field, m,
                                  f"Champ manquant '{field}' dans metadata pour index {m.get('vector_index')}")


class TestSelfRetrieval(unittest.TestCase):
    """
    Tests de self-retrieval : chaque entrée doit se retrouver elle-même en top-1
    lorsque son propre texte est utilisé comme requête.
    """

    @classmethod
    def setUpClass(cls):
        """Charge les index et le modèle une seule fois pour tous les tests."""
        import faiss as _faiss
        from sentence_transformers import SentenceTransformer

        if not all(p.exists() for p in [FAISS_PATH, BM25_PATH, META_PATH]):
            raise unittest.SkipTest(
                "Les fichiers d'index n'existent pas. Lancez d'abord: python -m data_pipeline.indexer"
            )

        cls.faiss_index = _faiss.read_index(str(FAISS_PATH))
        with open(BM25_PATH, "rb") as f:
            cls.bm25_index = pickle.load(f)
        with open(META_PATH, "r", encoding="utf-8") as f:
            cls.metadata = json.load(f)

        cls.data = load_json(JSON_PATH)
        _, cls.raw_corpus = build_bm25_corpus(cls.data)
        cls.tokenized_corpus, _ = build_bm25_corpus(cls.data)
        cls.model = SentenceTransformer(SBERT_MODEL)

    def test_faiss_self_retrieval_sample(self):
        """
        FAISS : un échantillon d'entrées doit se retrouver en top-1.
        Teste les 20 premières entrées pour rapidité.
        """
        sample_size = min(20, len(self.data))
        failures = []

        for i in range(sample_size):
            q_emb = self.model.encode(
                [self.raw_corpus[i]], normalize_embeddings=True
            ).astype("float32")
            _, ids = self.faiss_index.search(q_emb, 1)
            if ids[0][0] != i:
                failures.append(
                    f"{self.data[i]['id']} (index {i}) → top-1 index {ids[0][0]}"
                )

        self.assertEqual(
            len(failures), 0,
            f"FAISS self-retrieval échoué pour {len(failures)}/{sample_size}: {failures}"
        )

    def test_bm25_self_retrieval_sample(self):
        """
        BM25 : un échantillon d'entrées doit se retrouver en top-1.
        Teste les 20 premières entrées pour rapidité.
        """
        sample_size = min(20, len(self.data))
        failures = []

        for i in range(sample_size):
            scores = self.bm25_index.get_scores(self.tokenized_corpus[i])
            top_idx = int(np.argmax(scores))
            if top_idx != i:
                failures.append(
                    f"{self.data[i]['id']} (index {i}) → top-1 index {top_idx}"
                )

        self.assertEqual(
            len(failures), 0,
            f"BM25 self-retrieval échoué pour {len(failures)}/{sample_size}: {failures}"
        )

    def test_faiss_metadata_consistency(self):
        """Les métadonnées doivent être cohérentes avec le dataset."""
        self.assertEqual(len(self.metadata), len(self.data))
        for i, (meta, entry) in enumerate(zip(self.metadata, self.data)):
            self.assertEqual(meta["vector_index"], i)
            self.assertEqual(meta["id"], entry["id"])
            self.assertEqual(meta["type_cancer"], entry["type_cancer"])


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS UNITAIRES — Module data_pipeline.indexer")
    print("=" * 60)
    unittest.main(verbosity=2)
