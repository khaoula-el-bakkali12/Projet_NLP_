"""
test_prompt_builder.py — Tests unitaires pour le module de construction de prompts
===================================================================================

Couvre :
  - Stratégies disponibles
  - Formatage des documents
  - Templates Zero-shot, Few-shot, Chain-of-Thought
  - Comparaison des prompts
  - Gestion des cas limites
"""

import pytest

from data_pipeline.prompt_builder import (
    AVAILABLE_STRATEGIES,
    FEW_SHOT_EXAMPLES,
    build_prompt,
    compare_prompts,
    format_documents,
    get_available_strategies,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_documents():
    """Documents de test simulant des résultats de retrieval."""
    return [
        {
            "rank": 1,
            "id": "ONC-001",
            "categorie": "diagnostic",
            "type_cancer": "sein",
            "sous_type": "HER2 positif",
            "stade": "tout stade",
            "titre": "Critères diagnostiques du cancer du sein HER2+",
            "contenu": "Le cancer du sein HER2 positif est défini par une surexpression "
                       "du gène HER2, présent dans 15 à 20% des cancers du sein.",
            "mots_cles": ["sein", "HER2", "IHC", "FISH", "diagnostic"],
            "scenario_patient": "Femme de 48 ans, masse mammaire gauche.",
            "protocole": None,
            "effets_secondaires": [],
            "metastase": "",
            "reference": "Guide AMFROM 2024, Chapitre I",
            "score_final": 0.92,
            "score_faiss_norm": 0.95,
            "score_bm25_norm": 0.85,
        },
        {
            "rank": 2,
            "id": "ONC-005",
            "categorie": "traitement",
            "type_cancer": "sein",
            "sous_type": "HER2 positif",
            "stade": "stade précoce",
            "titre": "Protocole de traitement néoadjuvant du cancer du sein HER2+",
            "contenu": "Le traitement néoadjuvant du cancer du sein HER2+ repose sur "
                       "la chimiothérapie associée au trastuzumab et pertuzumab.",
            "mots_cles": ["sein", "HER2", "trastuzumab", "néoadjuvant"],
            "scenario_patient": "",
            "protocole": "TCHP (Docétaxel, Carboplatine, Trastuzumab, Pertuzumab)",
            "effets_secondaires": ["cardiotoxicité", "neutropénie"],
            "metastase": "",
            "reference": "Guide AMFROM 2024, Chapitre I",
            "score_final": 0.88,
            "score_faiss_norm": 0.90,
            "score_bm25_norm": 0.82,
        },
    ]


@pytest.fixture
def sample_question():
    """Question de test."""
    return "Quel est le traitement du cancer du sein HER2+ ?"


# ============================================================================
# 1. TESTS DES STRATÉGIES DISPONIBLES
# ============================================================================

class TestAvailableStrategies:
    """Tests pour les stratégies de prompt."""

    def test_three_strategies(self):
        """Il y a exactement 3 stratégies."""
        assert len(AVAILABLE_STRATEGIES) == 3

    def test_strategy_names(self):
        """Les noms des stratégies sont corrects."""
        assert "zero_shot" in AVAILABLE_STRATEGIES
        assert "few_shot" in AVAILABLE_STRATEGIES
        assert "chain_of_thought" in AVAILABLE_STRATEGIES

    def test_get_available_strategies(self):
        """get_available_strategies() retourne les bonnes stratégies."""
        strategies = get_available_strategies()
        assert strategies == AVAILABLE_STRATEGIES

    def test_invalid_strategy_raises(self, sample_question, sample_documents):
        """Stratégie invalide → ValueError."""
        with pytest.raises(ValueError, match="Stratégie inconnue"):
            build_prompt(sample_question, sample_documents, strategy="invalid")


# ============================================================================
# 2. TESTS DE FORMATAGE DES DOCUMENTS
# ============================================================================

class TestFormatDocuments:
    """Tests pour format_documents()."""

    def test_includes_title(self, sample_documents):
        """Le formatage inclut les titres."""
        result = format_documents(sample_documents)
        assert "Critères diagnostiques" in result
        assert "Protocole de traitement" in result

    def test_includes_content(self, sample_documents):
        """Le formatage inclut le contenu."""
        result = format_documents(sample_documents)
        assert "cancer du sein HER2 positif" in result

    def test_includes_cancer_type(self, sample_documents):
        """Le formatage inclut le type de cancer."""
        result = format_documents(sample_documents)
        assert "sein" in result

    def test_includes_category(self, sample_documents):
        """Le formatage inclut la catégorie."""
        result = format_documents(sample_documents)
        assert "diagnostic" in result

    def test_includes_keywords(self, sample_documents):
        """Le formatage inclut les mots-clés."""
        result = format_documents(sample_documents)
        assert "HER2" in result
        assert "IHC" in result

    def test_includes_score(self, sample_documents):
        """Le formatage inclut les scores."""
        result = format_documents(sample_documents)
        assert "0.92" in result or "Score" in result

    def test_includes_reference(self, sample_documents):
        """Le formatage inclut la référence."""
        result = format_documents(sample_documents)
        assert "Guide AMFROM 2024" in result

    def test_includes_protocol(self, sample_documents):
        """Le formatage inclut le protocole (si présent)."""
        result = format_documents(sample_documents)
        assert "TCHP" in result

    def test_includes_side_effects(self, sample_documents):
        """Le formatage inclut les effets secondaires."""
        result = format_documents(sample_documents)
        assert "cardiotoxicité" in result

    def test_includes_scenario(self, sample_documents):
        """Le formatage inclut le scénario patient."""
        result = format_documents(sample_documents)
        assert "Femme de 48 ans" in result

    def test_max_docs_limiting(self, sample_documents):
        """max_docs limite le nombre de documents formatés."""
        result = format_documents(sample_documents, max_docs=1)
        assert "ONC-001" in result
        assert "ONC-005" not in result

    def test_empty_documents(self):
        """Documents vides → message approprié."""
        result = format_documents([])
        assert "Aucun document" in result

    def test_document_numbering(self, sample_documents):
        """Les documents sont numérotés avec leur rang."""
        result = format_documents(sample_documents)
        assert "Document 1" in result
        assert "Document 2" in result


# ============================================================================
# 3. TESTS ZERO-SHOT
# ============================================================================

class TestZeroShotPrompt:
    """Tests pour le template Zero-Shot."""

    def test_contains_question(self, sample_question, sample_documents):
        """Le prompt contient la question."""
        prompt = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        assert sample_question in prompt

    def test_contains_context(self, sample_question, sample_documents):
        """Le prompt contient le contexte des documents."""
        prompt = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        assert "cancer du sein HER2" in prompt

    def test_contains_system_instruction(self, sample_question, sample_documents):
        """Le prompt contient l'instruction système."""
        prompt = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        assert "assistant médical" in prompt.lower() or "oncologie" in prompt.lower()

    def test_contains_response_marker(self, sample_question, sample_documents):
        """Le prompt se termine par le marqueur de réponse."""
        prompt = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        assert "Réponse" in prompt

    def test_no_examples(self, sample_question, sample_documents):
        """Le Zero-shot ne contient PAS d'exemples."""
        prompt = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        assert "Exemple 1" not in prompt
        assert "Exemple 2" not in prompt

    def test_no_reasoning_steps(self, sample_question, sample_documents):
        """Le Zero-shot ne contient PAS d'étapes de raisonnement."""
        prompt = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        assert "Étape 1" not in prompt
        assert "Raisonnement" not in prompt


# ============================================================================
# 4. TESTS FEW-SHOT
# ============================================================================

class TestFewShotPrompt:
    """Tests pour le template Few-Shot."""

    def test_contains_exactly_two_examples(self, sample_question, sample_documents):
        """Le Few-shot contient exactement 2 exemples."""
        prompt = build_prompt(sample_question, sample_documents, strategy="few_shot")
        assert "Exemple 1" in prompt
        assert "Exemple 2" in prompt
        assert "Exemple 3" not in prompt

    def test_contains_question(self, sample_question, sample_documents):
        """Le prompt contient la question."""
        prompt = build_prompt(sample_question, sample_documents, strategy="few_shot")
        assert sample_question in prompt

    def test_contains_context(self, sample_question, sample_documents):
        """Le prompt contient le contexte des documents."""
        prompt = build_prompt(sample_question, sample_documents, strategy="few_shot")
        assert "cancer du sein HER2" in prompt

    def test_examples_are_medical(self, sample_question, sample_documents):
        """Les exemples sont du domaine médical/oncologique."""
        prompt = build_prompt(sample_question, sample_documents, strategy="few_shot")
        # Vérifier qu'au moins un terme médical des exemples est présent
        medical_terms = ["IHC", "FISH", "chimiothérapie", "trastuzumab",
                         "cancer", "diagnostic", "traitement"]
        found = sum(1 for term in medical_terms if term.lower() in prompt.lower())
        assert found >= 3

    def test_examples_have_qa_format(self, sample_question, sample_documents):
        """Les exemples ont le format Question/Réponse."""
        prompt = build_prompt(sample_question, sample_documents, strategy="few_shot")
        assert "Question" in prompt
        assert "Réponse" in prompt

    def test_few_shot_examples_content(self):
        """Les exemples FEW_SHOT_EXAMPLES ont le bon format."""
        assert len(FEW_SHOT_EXAMPLES) == 2
        for example in FEW_SHOT_EXAMPLES:
            assert "question" in example
            assert "answer" in example
            assert len(example["question"]) > 10
            assert len(example["answer"]) > 50

    def test_longer_than_zero_shot(self, sample_question, sample_documents):
        """Le Few-shot est plus long que le Zero-shot."""
        zero_shot = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        few_shot = build_prompt(sample_question, sample_documents, strategy="few_shot")
        assert len(few_shot) > len(zero_shot)


# ============================================================================
# 5. TESTS CHAIN-OF-THOUGHT
# ============================================================================

class TestChainOfThoughtPrompt:
    """Tests pour le template Chain-of-Thought."""

    def test_contains_reasoning_steps(self, sample_question, sample_documents):
        """Le CoT contient des étapes de raisonnement."""
        prompt = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert "Étape 1" in prompt
        assert "Étape 2" in prompt

    def test_contains_question(self, sample_question, sample_documents):
        """Le prompt contient la question."""
        prompt = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert sample_question in prompt

    def test_contains_context(self, sample_question, sample_documents):
        """Le prompt contient le contexte."""
        prompt = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert "cancer du sein HER2" in prompt

    def test_contains_final_answer_marker(self, sample_question, sample_documents):
        """Le CoT contient un marqueur pour la réponse finale."""
        prompt = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert "Réponse finale" in prompt

    def test_step_by_step_instruction(self, sample_question, sample_documents):
        """Le CoT demande un raisonnement étape par étape."""
        prompt = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert "étape par étape" in prompt.lower() or "étape" in prompt.lower()

    def test_no_examples(self, sample_question, sample_documents):
        """Le CoT ne contient PAS d'exemples Q/R."""
        prompt = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert "Exemple 1" not in prompt

    def test_longer_than_zero_shot(self, sample_question, sample_documents):
        """Le CoT est plus long que le Zero-shot."""
        zero_shot = build_prompt(sample_question, sample_documents, strategy="zero_shot")
        cot = build_prompt(sample_question, sample_documents, strategy="chain_of_thought")
        assert len(cot) > len(zero_shot)


# ============================================================================
# 6. TESTS DE COMPARAISON
# ============================================================================

class TestComparePrompts:
    """Tests pour compare_prompts()."""

    def test_returns_all_strategies(self, sample_question, sample_documents):
        """compare_prompts() retourne les 3 stratégies."""
        result = compare_prompts(sample_question, sample_documents)

        assert "strategies" in result
        for strategy in AVAILABLE_STRATEGIES:
            assert strategy in result["strategies"]

    def test_each_strategy_has_prompt(self, sample_question, sample_documents):
        """Chaque stratégie a un prompt non-vide."""
        result = compare_prompts(sample_question, sample_documents)

        for strategy, info in result["strategies"].items():
            assert "prompt" in info
            assert len(info["prompt"]) > 0

    def test_each_strategy_has_length(self, sample_question, sample_documents):
        """Chaque stratégie a une longueur."""
        result = compare_prompts(sample_question, sample_documents)

        for strategy, info in result["strategies"].items():
            assert "length" in info
            assert info["length"] > 0

    def test_each_strategy_has_token_estimate(self, sample_question, sample_documents):
        """Chaque stratégie a une estimation de tokens."""
        result = compare_prompts(sample_question, sample_documents)

        for strategy, info in result["strategies"].items():
            assert "estimated_tokens" in info
            assert info["estimated_tokens"] > 0

    def test_prompts_are_different(self, sample_question, sample_documents):
        """Les 3 prompts sont différents."""
        result = compare_prompts(sample_question, sample_documents)

        prompts = [info["prompt"] for info in result["strategies"].values()]
        # Vérifier que tous les prompts sont uniques
        assert len(set(prompts)) == 3

    def test_includes_question(self, sample_question, sample_documents):
        """Le résultat inclut la question posée."""
        result = compare_prompts(sample_question, sample_documents)
        assert result["question"] == sample_question

    def test_includes_doc_count(self, sample_question, sample_documents):
        """Le résultat inclut le nombre de documents."""
        result = compare_prompts(sample_question, sample_documents)
        assert result["num_documents"] == len(sample_documents)


# ============================================================================
# 7. TESTS DE CAS LIMITES
# ============================================================================

class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_single_document(self, sample_question):
        """Fonctionne avec un seul document."""
        doc = [{
            "rank": 1, "id": "ONC-001", "categorie": "test",
            "type_cancer": "test", "titre": "Test", "contenu": "Contenu test",
            "mots_cles": [], "scenario_patient": "", "protocole": None,
            "effets_secondaires": [], "metastase": "", "reference": "",
            "sous_type": "", "stade": "",
            "score_final": 0.9, "score_faiss_norm": 0.9, "score_bm25_norm": 0.9,
        }]

        for strategy in AVAILABLE_STRATEGIES:
            prompt = build_prompt(sample_question, doc, strategy=strategy)
            assert len(prompt) > 0
            assert sample_question in prompt

    def test_empty_documents(self, sample_question):
        """Fonctionne avec une liste de documents vide."""
        for strategy in AVAILABLE_STRATEGIES:
            prompt = build_prompt(sample_question, [], strategy=strategy)
            assert len(prompt) > 0
            assert "Aucun document" in prompt

    def test_long_question(self, sample_documents):
        """Fonctionne avec une très longue question."""
        long_q = "Quel est le traitement " * 50 + "?"
        prompt = build_prompt(long_q, sample_documents, strategy="zero_shot")
        assert long_q in prompt

    def test_arabic_question(self, sample_documents):
        """Fonctionne avec une question en arabe."""
        q_ar = "ما هو العلاج الأول لسرطان الثدي؟"
        prompt = build_prompt(q_ar, sample_documents, strategy="zero_shot")
        assert q_ar in prompt

    def test_max_docs_respected(self, sample_question):
        """max_docs est respecté dans le prompt."""
        docs = [{
            "rank": i + 1, "id": f"ONC-{i:03d}", "categorie": "test",
            "type_cancer": "test", "titre": f"Document {i}",
            "contenu": f"Contenu {i}", "mots_cles": [],
            "scenario_patient": "", "protocole": None,
            "effets_secondaires": [], "metastase": "", "reference": "",
            "sous_type": "", "stade": "",
            "score_final": 0.9 - i * 0.1,
            "score_faiss_norm": 0.9, "score_bm25_norm": 0.9,
        } for i in range(10)]

        prompt = build_prompt(sample_question, docs, strategy="zero_shot", max_docs=2)
        assert "Document 0" in prompt
        assert "Document 1" in prompt
        # Document 2 ne devrait pas être dans le prompt
        assert "Document 9" not in prompt


# ============================================================================
# 8. TESTS DE SÉLECTION DYNAMIQUE FEW-SHOT
# ============================================================================

class TestDynamicFewShotSelection:
    """Tests pour la sélection dynamique des exemples few-shot."""

    def test_french_clinical_diagnostic(self, sample_documents):
        """Sélectionne des exemples cliniques de diagnostic en français."""
        q = "Quels sont les critères diagnostiques du cancer du sein ?"
        prompt = build_prompt(q, sample_documents, strategy="few_shot")
        # Doit contenir des exemples de diagnostic en français
        assert "critères diagnostiques" in prompt
        assert "Comment diagnostique-t-on" in prompt

    def test_french_clinical_treatment(self, sample_documents):
        """Sélectionne des exemples cliniques de traitement en français."""
        q = "Quel est le traitement ou chimiothérapie du cancer ?"
        prompt = build_prompt(q, sample_documents, strategy="few_shot")
        assert "effets secondaires de la chimiothérapie" in prompt
        assert "première ligne" in prompt or "adjuvant" in prompt

    def test_arabic_clinical_diagnostic(self, sample_documents):
        """Sélectionne des exemples cliniques de diagnostic en arabe."""
        q = "كيف يتم تشخيص سرطان الثدي؟"
        prompt = build_prompt(q, sample_documents, strategy="few_shot")
        assert "تشخيص سرطان الثدي" in prompt
        assert "سرطان القولون" in prompt or "المتابعة" in prompt or "علاج" in prompt

    def test_english_general(self, sample_documents):
        """Sélectionne des exemples généraux en anglais."""
        q = "What is cancer definition?"
        prompt = build_prompt(q, sample_documents, strategy="few_shot")
        assert "What is cancer and how does it develop?" in prompt

    def test_custom_examples_override(self, sample_documents, sample_question):
        """Un exemple personnalisé passé manuellement outrepasse la sélection dynamique."""
        custom = [
            {"question": "Custom Q1?", "answer": "Custom A1."},
            {"question": "Custom Q2?", "answer": "Custom A2."},
        ]
        prompt = build_prompt(sample_question, sample_documents, strategy="few_shot", examples=custom)
        assert "Custom Q1?" in prompt
        assert "Custom A2." in prompt
        assert "critères diagnostiques" not in prompt  # Ne doit pas avoir pris les exemples par défaut

