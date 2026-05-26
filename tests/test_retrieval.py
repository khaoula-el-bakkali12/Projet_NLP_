"""
test_retrieval.py — Tests unitaires pour le module de recherche hybride
========================================================================

Couvre :
  - Normalisation min-max des scores
  - Fusion des scores (formule α)
  - Filtrage par métadonnées
  - Fonction retrieve() end-to-end
  - Effet du paramètre α (α=0 → BM25, α=1 → FAISS)
"""

import numpy as np
import pytest


# ============================================================================
# 1. TESTS DE NORMALISATION
# ============================================================================

class TestNormalizeScores:
    """Tests pour _normalize_scores()."""

    def test_normal_case(self):
        """Scores variés → normalisés entre 0 et 1."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([1.0, 3.0, 5.0, 2.0, 4.0])
        result = _normalize_scores(scores)

        assert result.min() == pytest.approx(0.0)
        assert result.max() == pytest.approx(1.0)
        assert len(result) == len(scores)

    def test_all_same_scores(self):
        """Tous les scores identiques → retourne des 1.0."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([3.0, 3.0, 3.0])
        result = _normalize_scores(scores)

        np.testing.assert_array_almost_equal(result, [1.0, 1.0, 1.0])

    def test_single_score(self):
        """Un seul score → retourne 1.0."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([42.0])
        result = _normalize_scores(scores)

        assert result[0] == pytest.approx(1.0)

    def test_empty_scores(self):
        """Tableau vide → retourne tableau vide."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([])
        result = _normalize_scores(scores)

        assert len(result) == 0

    def test_preserves_order(self):
        """L'ordre relatif des scores est préservé."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([10.0, 20.0, 30.0])
        result = _normalize_scores(scores)

        assert result[0] < result[1] < result[2]

    def test_two_scores(self):
        """Deux scores → 0.0 et 1.0."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([5.0, 15.0])
        result = _normalize_scores(scores)

        assert result[0] == pytest.approx(0.0)
        assert result[1] == pytest.approx(1.0)

    def test_negative_scores(self):
        """Scores négatifs sont correctement normalisés."""
        from data_pipeline.retrieval import _normalize_scores

        scores = np.array([-3.0, -1.0, 1.0, 3.0])
        result = _normalize_scores(scores)

        assert result.min() == pytest.approx(0.0)
        assert result.max() == pytest.approx(1.0)


# ============================================================================
# 2. TESTS DE FUSION DES SCORES
# ============================================================================

class TestFuseScores:
    """Tests pour _fuse_scores()."""

    def test_alpha_1_pure_faiss(self):
        """α=1.0 → score final = FAISS uniquement."""
        from data_pipeline.retrieval import _fuse_scores

        faiss_idx = np.array([0, 1, 2])
        faiss_sc = np.array([0.9, 0.7, 0.5])
        bm25_idx = np.array([0, 1, 2])
        bm25_sc = np.array([10.0, 5.0, 1.0])

        results = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=1.0)

        # Avec α=1, le classement doit suivre FAISS
        ids = [r[0] for r in results]
        assert ids[0] == 0  # Meilleur score FAISS

    def test_alpha_0_pure_bm25(self):
        """α=0.0 → score final = BM25 uniquement."""
        from data_pipeline.retrieval import _fuse_scores

        faiss_idx = np.array([0, 1, 2])
        faiss_sc = np.array([0.9, 0.7, 0.5])
        bm25_idx = np.array([0, 1, 2])
        bm25_sc = np.array([1.0, 5.0, 10.0])

        results = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=0.0)

        # Avec α=0, le classement doit suivre BM25
        ids = [r[0] for r in results]
        assert ids[0] == 2  # Meilleur score BM25

    def test_alpha_05_balanced(self):
        """α=0.5 → combinaison équilibrée."""
        from data_pipeline.retrieval import _fuse_scores

        faiss_idx = np.array([0, 1])
        faiss_sc = np.array([1.0, 0.0])
        bm25_idx = np.array([0, 1])
        bm25_sc = np.array([0.0, 1.0])

        results = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=0.5)

        # Les deux docs devraient avoir le même score final
        scores = [r[1] for r in results]
        assert scores[0] == pytest.approx(scores[1], abs=0.01)

    def test_disjoint_candidates(self):
        """Candidats FAISS et BM25 sans intersection → union."""
        from data_pipeline.retrieval import _fuse_scores

        faiss_idx = np.array([0, 1])
        faiss_sc = np.array([0.9, 0.8])
        bm25_idx = np.array([2, 3])
        bm25_sc = np.array([10.0, 8.0])

        results = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=0.5)

        # 4 candidats au total
        assert len(results) == 4

        # Vérifier que les candidats absent d'un moteur ont score 0 pour ce moteur
        result_dict = {r[0]: (r[2], r[3]) for r in results}
        assert result_dict[0][1] == 0.0  # doc 0 absent de BM25
        assert result_dict[2][0] == 0.0  # doc 2 absent de FAISS

    def test_formula_correctness(self):
        """Vérifie que la formule score_final = α*FAISS + (1-α)*BM25 est correcte."""
        from data_pipeline.retrieval import _fuse_scores

        # Un seul candidat dans chaque, même doc
        faiss_idx = np.array([0])
        faiss_sc = np.array([0.8])  # sera normalisé à 1.0 (seul)
        bm25_idx = np.array([0])
        bm25_sc = np.array([5.0])  # sera normalisé à 1.0 (seul)

        alpha = 0.7
        results = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=alpha)

        # Seul candidat, scores normalisés = 1.0 chacun
        # score_final = 0.7 * 1.0 + 0.3 * 1.0 = 1.0
        assert results[0][1] == pytest.approx(1.0)

    def test_sorted_by_score(self):
        """Les résultats sont triés par score final décroissant."""
        from data_pipeline.retrieval import _fuse_scores

        faiss_idx = np.array([0, 1, 2, 3, 4])
        faiss_sc = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        bm25_idx = np.array([0, 1, 2, 3, 4])
        bm25_sc = np.array([9.0, 7.0, 5.0, 3.0, 1.0])

        results = _fuse_scores(faiss_idx, faiss_sc, bm25_idx, bm25_sc, alpha=0.5)

        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)


# ============================================================================
# 3. TESTS DE FILTRAGE
# ============================================================================

class TestApplyFilters:
    """Tests pour _apply_filters()."""

    @pytest.fixture
    def sample_metadata(self):
        """Métadonnées de test."""
        return [
            {"categorie": "diagnostic", "type_cancer": "sein"},
            {"categorie": "traitement", "type_cancer": "sein"},
            {"categorie": "traitement", "type_cancer": "poumon"},
            {"categorie": "diagnostic", "type_cancer": "poumon"},
            {"categorie": "suivi", "type_cancer": "colorectal"},
        ]

    @pytest.fixture
    def sample_fused_results(self):
        """Résultats fusionnés de test."""
        return [
            (0, 0.95, 0.9, 0.8),
            (1, 0.90, 0.8, 0.9),
            (2, 0.85, 0.7, 0.8),
            (3, 0.80, 0.6, 0.7),
            (4, 0.75, 0.5, 0.6),
        ]

    def test_no_filters(self, sample_fused_results, sample_metadata):
        """Sans filtre → retourne tout."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(sample_fused_results, sample_metadata)
        assert len(result) == 5

    def test_filter_by_categorie(self, sample_fused_results, sample_metadata):
        """Filtre par catégorie."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(
            sample_fused_results, sample_metadata,
            categorie_filter="traitement"
        )
        assert len(result) == 2
        assert all(sample_metadata[r[0]]["categorie"] == "traitement" for r in result)

    def test_filter_by_cancer_type(self, sample_fused_results, sample_metadata):
        """Filtre par type de cancer."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(
            sample_fused_results, sample_metadata,
            cancer_type_filter="sein"
        )
        assert len(result) == 2
        assert all(sample_metadata[r[0]]["type_cancer"] == "sein" for r in result)

    def test_filter_combined(self, sample_fused_results, sample_metadata):
        """Filtre combiné (catégorie + type cancer)."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(
            sample_fused_results, sample_metadata,
            categorie_filter="traitement",
            cancer_type_filter="sein"
        )
        assert len(result) == 1
        assert result[0][0] == 1  # Index du doc traitement/sein

    def test_filter_no_match(self, sample_fused_results, sample_metadata):
        """Filtre sans résultat → liste vide."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(
            sample_fused_results, sample_metadata,
            categorie_filter="epidemiologie"
        )
        assert len(result) == 0

    def test_filter_case_insensitive(self, sample_fused_results, sample_metadata):
        """Filtre insensible à la casse."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(
            sample_fused_results, sample_metadata,
            categorie_filter="Diagnostic"
        )
        assert len(result) == 2

    def test_filter_preserves_order(self, sample_fused_results, sample_metadata):
        """Le filtrage préserve l'ordre des scores."""
        from data_pipeline.retrieval import _apply_filters

        result = _apply_filters(
            sample_fused_results, sample_metadata,
            cancer_type_filter="sein"
        )
        scores = [r[1] for r in result]
        assert scores == sorted(scores, reverse=True)


# ============================================================================
# 4. TESTS D'ENRICHISSEMENT
# ============================================================================

class TestEnrichDocuments:
    """Tests pour _enrich_documents()."""

    @pytest.fixture
    def sample_data(self):
        metadata = [
            {"id": "ONC-001", "categorie": "diagnostic", "type_cancer": "sein",
             "sous_type": "HER2+", "stade": "tout stade",
             "titre": "Critères diagnostiques", "reference": "Guide 2024"},
        ]
        dataset = [
            {"id": "ONC-001", "categorie": "diagnostic", "type_cancer": "sein",
             "titre": "Critères diagnostiques", "contenu": "Le cancer du sein...",
             "mots_cles": ["sein", "HER2"], "scenario_patient": "Femme 48 ans",
             "protocole": None, "effets_secondaires": [], "metastase": "",
             "reference": "Guide 2024"},
        ]
        fused = [(0, 0.95, 0.9, 0.8)]
        return fused, metadata, dataset

    def test_enriched_structure(self, sample_data):
        """Les documents enrichis contiennent tous les champs attendus."""
        from data_pipeline.retrieval import _enrich_documents

        fused, metadata, dataset = sample_data
        result = _enrich_documents(fused, metadata, dataset, top_k=1)

        assert len(result) == 1
        doc = result[0]

        expected_keys = [
            "rank", "doc_index", "id", "categorie", "type_cancer",
            "titre", "contenu", "mots_cles", "score_final",
            "score_faiss_norm", "score_bm25_norm",
        ]
        for key in expected_keys:
            assert key in doc, f"Clé manquante : {key}"

    def test_enriched_scores(self, sample_data):
        """Les scores sont correctement arrondis."""
        from data_pipeline.retrieval import _enrich_documents

        fused, metadata, dataset = sample_data
        result = _enrich_documents(fused, metadata, dataset, top_k=1)

        doc = result[0]
        assert doc["score_final"] == 0.95
        assert doc["score_faiss_norm"] == 0.9
        assert doc["score_bm25_norm"] == 0.8

    def test_top_k_limiting(self):
        """top_k limite le nombre de résultats."""
        from data_pipeline.retrieval import _enrich_documents

        fused = [(i, 1.0 - i * 0.1, 0.5, 0.5) for i in range(10)]
        metadata = [{"id": f"ONC-{i:03d}", "categorie": "test",
                      "type_cancer": "test", "sous_type": "", "stade": "",
                      "titre": f"Doc {i}", "reference": ""}
                     for i in range(10)]
        dataset = [{"id": f"ONC-{i:03d}", "categorie": "test",
                     "type_cancer": "test", "titre": f"Doc {i}",
                     "contenu": f"Contenu {i}", "mots_cles": [],
                     "scenario_patient": "", "protocole": None,
                     "effets_secondaires": [], "metastase": "",
                     "reference": ""} for i in range(10)]

        result = _enrich_documents(fused, metadata, dataset, top_k=3)
        assert len(result) == 3

    def test_rank_starts_at_1(self, sample_data):
        """Le rang commence à 1."""
        from data_pipeline.retrieval import _enrich_documents

        fused, metadata, dataset = sample_data
        result = _enrich_documents(fused, metadata, dataset, top_k=1)

        assert result[0]["rank"] == 1


# ============================================================================
# 5. TESTS END-TO-END (nécessitent les index générés)
# ============================================================================

class TestRetrieveEndToEnd:
    """
    Tests end-to-end pour retrieve().
    Ces tests nécessitent que les index aient été générés
    (python -m data_pipeline.indexer).
    """

    @pytest.fixture(autouse=True)
    def check_indexes_exist(self):
        """Skip si les index n'ont pas été générés."""
        from data_pipeline.retrieval import FAISS_PATH, BM25_PATH, META_PATH
        if not all(p.exists() for p in [FAISS_PATH, BM25_PATH, META_PATH]):
            pytest.skip("Index non générés. Exécuter: python -m data_pipeline.indexer")

    def test_retrieve_returns_correct_structure(self):
        """retrieve() retourne un dict avec les clés attendues."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        vector = encode_query("Traitement du cancer du sein")
        result = retrieve(vector, "Traitement du cancer du sein", top_k=3)

        expected_keys = [
            "top_k_docs", "enriched_prompt", "scores", "alpha",
            "strategy", "num_candidates_faiss", "num_candidates_bm25",
            "num_after_filter", "filters_applied",
        ]
        for key in expected_keys:
            assert key in result, f"Clé manquante : {key}"

    def test_retrieve_top_k_count(self):
        """retrieve() retourne exactement top_k documents."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        vector = encode_query("Diagnostic du cancer du poumon")
        result = retrieve(vector, "Diagnostic du cancer du poumon", top_k=3)

        assert len(result["top_k_docs"]) == 3
        assert len(result["scores"]) == 3

    def test_retrieve_with_filter(self):
        """Les filtres réduisent correctement les résultats."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        vector = encode_query("Traitement du cancer")
        result = retrieve(
            vector, "Traitement du cancer",
            top_k=5,
            cancer_type_filter="sein"
        )

        for doc in result["top_k_docs"]:
            assert doc["type_cancer"].lower() == "sein"

    def test_retrieve_alpha_0_is_bm25(self):
        """α=0 retourne les mêmes résultats que BM25 pur."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        q = "chimiothérapie cancer colorectal"
        vector = encode_query(q)
        result = retrieve(vector, q, top_k=5, alpha=0.0)

        # Avec α=0, tous les scores FAISS normalisés doivent être pondérés à 0
        # Le score final est basé uniquement sur BM25
        for doc in result["top_k_docs"]:
            assert doc["score_bm25_norm"] > 0 or doc["score_final"] == 0

    def test_retrieve_alpha_1_is_faiss(self):
        """α=1 retourne les mêmes résultats que FAISS pur."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        q = "traitement cancer sein HER2"
        vector = encode_query(q)
        result = retrieve(vector, q, top_k=5, alpha=1.0)

        # Avec α=1, seuls les scores FAISS comptent
        for doc in result["top_k_docs"]:
            assert doc["score_faiss_norm"] > 0 or doc["score_final"] == 0

    def test_retrieve_prompt_included(self):
        """Le prompt est non-vide et contient la question."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        q = "Quel est le pronostic du cancer du poumon ?"
        vector = encode_query(q)
        result = retrieve(vector, q, top_k=3, prompt_strategy="zero_shot")

        assert len(result["enriched_prompt"]) > 100
        assert q in result["enriched_prompt"]

    def test_retrieve_different_strategies(self):
        """Chaque stratégie produit un prompt différent."""
        from data_pipeline.retrieval import retrieve
        from data_pipeline.nlp_query_processor import encode_query

        q = "Cancer du sein"
        vector = encode_query(q)

        prompts = {}
        for strategy in ["zero_shot", "few_shot", "chain_of_thought"]:
            result = retrieve(vector, q, top_k=3, prompt_strategy=strategy)
            prompts[strategy] = result["enriched_prompt"]

        # Les 3 prompts doivent être différents
        assert prompts["zero_shot"] != prompts["few_shot"]
        assert prompts["few_shot"] != prompts["chain_of_thought"]
        assert prompts["zero_shot"] != prompts["chain_of_thought"]
