"""
evaluate_retrieval.py — Script d'évaluation de la recherche hybride et comparaison des prompts
=============================================================================================

Ce script :
  1. Définit un jeu de test de 17 questions d'oncologie variées (catégories, cancers, français/arabe).
  2. Effectue un sweep du paramètre α de 0.0 (BM25 pur) à 1.0 (FAISS pur) par pas de 0.1.
  3. Calcule les métriques de recherche : Hit Rate@k, MRR@k et Precision@k (k=5).
  4. Compare structurellement les trois stratégies de prompt (Zero-shot, Few-shot, Chain-of-Thought)
     sur des questions clés (longueur, nombre de tokens estimé, composition).
  5. Exporte les résultats détaillés de l'évaluation au format JSON.
  6. Affiche un rapport complet dans la console.

Usage :
    python evaluate_retrieval.py
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from data_pipeline.retrieval import (
    evaluate_alpha_range,
    load_retrieval_resources,
    retrieve,
)
from data_pipeline.prompt_builder import compare_prompts

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("evaluate_retrieval")

# ---------------------------------------------------------------------------
# 1. JEU DE TEST (17 QUESTIONS REPRÉSENTATIVES)
# ---------------------------------------------------------------------------
TEST_QUESTIONS = [
    # --- CANCER DU SEIN (French) ---
    {
        "id": "Q01",
        "question": "Quels sont les critères diagnostiques du cancer du sein HER2+ ?",
        "expected_id": "ONC-001",
        "category": "diagnostic",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q02",
        "question": "Quel est le protocole de chimiothérapie néoadjuvante standard pour un cancer du sein HER2+ ?",
        "expected_id": "ONC-002",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q03",
        "question": "Quelle est la stratégie thérapeutique post-néoadjuvante en cas de résidu tumoral (non-pCR) après traitement néoadjuvant d'un cancer du sein HER2+ ?",
        "expected_id": "ONC-003",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q04",
        "question": "Quel est le schéma de désescalade thérapeutique de Tolaney pour les petites tumeurs HER2 positives ?",
        "expected_id": "ONC-004",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q05",
        "question": "Quelles sont les modalités de surveillance cardiaque et de suivi post-traitement pour un cancer du sein HER2+ ?",
        "expected_id": "ONC-005",
        "category": "suivi",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q06",
        "question": "Quels sont les critères diagnostiques du cancer du sein triple négatif (TNBC) ?",
        "expected_id": "ONC-006",
        "category": "diagnostic",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q07",
        "question": "En quoi consiste le protocole Keynote-522 pour le traitement néoadjuvant du cancer du sein triple négatif ?",
        "expected_id": "ONC-007",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q08",
        "question": "Quelles sont les options de traitement adjuvant de rattrapage en cas de non-pCR pour le cancer du sein triple négatif ?",
        "expected_id": "ONC-008",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q09",
        "question": "Quel est le schéma standard d'hormonothérapie adjuvante selon le statut ménopausique pour le cancer du sein RH+/HER2- ?",
        "expected_id": "ONC-009",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q10",
        "question": "Dans quels cas utilise-t-on les inhibiteurs de CDK4/6 en adjuvant pour le cancer du sein RH+ HER2- à haut risque ?",
        "expected_id": "ONC-010",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    {
        "id": "Q11",
        "question": "Quel est le traitement standard de première ligne pour le cancer du sein HER2 positif métastatique (CLEOPATRA) ?",
        "expected_id": "ONC-011",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "fr"
    },
    # --- GYNECOLOGIQUE & DIGESTIF (French) ---
    {
        "id": "Q12",
        "question": "Quels examens et biomarqueurs font partie du bilan diagnostique des cancers épithéliaux de l'ovaire ?",
        "expected_id": "ONC-012",
        "category": "diagnostic",
        "cancer_type": "ovaire",
        "lang": "fr"
    },
    {
        "id": "Q13",
        "question": "Quel est le protocole de chimiothérapie standard de première ligne pour le cancer de l'ovaire avancé ?",
        "expected_id": "ONC-013",
        "category": "traitement",
        "cancer_type": "ovaire",
        "lang": "fr"
    },
    {
        "id": "Q14",
        "question": "Quel est le protocole de radio-chimiothérapie concomitante standard pour le cancer du col de l'utérus localement avancé ?",
        "expected_id": "ONC-014",
        "category": "traitement",
        "cancer_type": "col_uterin",
        "lang": "fr"
    },
    {
        "id": "Q15",
        "question": "Quels sont les biomarqueurs moléculaires obligatoires à rechercher avant de traiter un cancer colorectal métastatique ?",
        "expected_id": "ONC-015",
        "category": "diagnostic",
        "cancer_type": "colorectal",
        "lang": "fr"
    },
    # --- ARABIC TRANSLATED QUESTIONS ---
    {
        "id": "Q16",
        "question": "ما هو بروتوكول العلاج الكيميائي قبل الجراحة لسرطان الثدي HER2+ ؟",
        "expected_id": "ONC-AR-001",
        "category": "traitement",
        "cancer_type": "sein",
        "lang": "ar"
    },
    {
        "id": "Q17",
        "question": "ما هي الفحوصات الجزيئية الإلزامية قبل البدء في علاج سرطان الرئة غير صغير الخلايا (CBNPC)؟",
        "expected_id": "ONC-AR-002",
        "category": "diagnostic",
        "cancer_type": "poumon",
        "lang": "ar"
    },
]

# ---------------------------------------------------------------------------
# 2. RUN EVALUATION
# ---------------------------------------------------------------------------
def run_evaluation() -> Dict[str, Any]:
    logger.info("Démarrage de l'évaluation du module de recherche...")
    start_time = time.time()

    # Charger les ressources de retrieval pour s'assurer que tout est prêt
    resources = load_retrieval_resources()

    # 1. Sweep d'Alpha de 0.0 à 1.0
    alpha_values = [round(a * 0.1, 1) for a in range(11)]
    top_k = 5

    logger.info("Exécution du sweep d'alpha sur les %d questions de test...", len(TEST_QUESTIONS))
    sweep_results = evaluate_alpha_range(TEST_QUESTIONS, alpha_values, top_k=top_k)

    # Identifier le meilleur alpha (basé sur le MRR, puis Hit Rate)
    best_sweep = max(sweep_results, key=lambda x: (x["mrr"], x["hit_rate"]))
    best_alpha = best_sweep["alpha"]
    logger.info("★ Meilleur α identifié : %.1f", best_alpha)

    # 2. Évaluation détaillée par question avec le meilleur alpha
    detailed_questions_results = []
    from data_pipeline.nlp_query_processor import encode_query

    for q_info in TEST_QUESTIONS:
        question = q_info["question"]
        expected_id = q_info["expected_id"]

        # Vectorisation
        q_vec = encode_query(question)

        # Retrieval hybride avec le meilleur alpha
        res = retrieve(
            query_vector=q_vec,
            question=question,
            top_k=top_k,
            alpha=best_alpha,
            prompt_strategy="zero_shot"
        )

        retrieved_ids = [doc["id"] for doc in res["top_k_docs"]]
        hit = expected_id in retrieved_ids
        rank = retrieved_ids.index(expected_id) + 1 if hit else -1
        rr = 1.0 / rank if hit else 0.0

        detailed_questions_results.append({
            "id": q_info["id"],
            "question": question,
            "expected_id": expected_id,
            "category": q_info["category"],
            "cancer_type": q_info["cancer_type"],
            "lang": q_info["lang"],
            "retrieved_ids": retrieved_ids,
            "hit": hit,
            "rank": rank,
            "mrr": rr,
            "top_doc_score": res["scores"][0] if res["scores"] else 0.0
        })

    # 3. Comparaison structurelle des stratégies de prompts
    # On prend une question représentative de test (Q02 - Protocole standard de chimio néoadjuvante)
    rep_q_info = TEST_QUESTIONS[1]
    rep_q_vector = encode_query(rep_q_info["question"])
    rep_retrieval = retrieve(
        query_vector=rep_q_vector,
        question=rep_q_info["question"],
        top_k=top_k,
        alpha=best_alpha,
        prompt_strategy="zero_shot"
    )

    prompt_comparison = compare_prompts(
        question=rep_q_info["question"],
        documents=rep_retrieval["top_k_docs"],
        max_docs=3 # On limite à 3 pour le prompt de test
    )

    # 4. Compilation des résultats d'évaluation
    eval_duration = time.time() - start_time
    evaluation_report = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": round(eval_duration, 2),
        "num_test_questions": len(TEST_QUESTIONS),
        "top_k_evaluated": top_k,
        "best_alpha": best_alpha,
        "sweep_results": sweep_results,
        "detailed_results": detailed_questions_results,
        "prompt_comparison_details": {
            "representative_question": rep_q_info["question"],
            "strategies": prompt_comparison["strategies"]
        }
    }

    # 5. Sauvegarde au format JSON
    output_path = Path("evaluation_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, ensure_ascii=False, indent=2)

    logger.info("✓ Résultats de l'évaluation enregistrés dans %s", output_path)

    # 6. Affichage du rapport dans la console
    print_console_report(evaluation_report)

    return evaluation_report

# ---------------------------------------------------------------------------
# 3. CONSOLE REPORT FORMATTING
# ---------------------------------------------------------------------------
def print_console_report(report: Dict[str, Any]):
    print("\n" + "=" * 80)
    print("      RAPPORT D'ÉVALUATION DU MODULE DE RECHERCHE HYBRIDE & PROMPTS")
    print("=" * 80)
    print(f"Date de l'évaluation : {report['evaluation_timestamp']}")
    print(f"Durée totale         : {report['duration_seconds']} secondes")
    print(f"Taille du jeu de test : {report['num_test_questions']} questions")
    print(f"Top-k énuméré        : {report['top_k_evaluated']}")
    print(f"Meilleur α (pondération FAISS) : {report['best_alpha']} "
          f"(Score combiné : α × FAISS + (1-α) × BM25)")
    print("-" * 80)

    # Tableau du Sweep d'Alpha
    print("\n[1] RESULTATS DU SWEEP D'ALPHA (Tunabilité de la recherche hybride)")
    print("-" * 65)
    print("   Alpha (α)   |   Hit Rate @5   |     MRR @5      |  Precision @5 ")
    print("-" * 65)
    for r in report["sweep_results"]:
        marker = " ★ " if r["alpha"] == report["best_alpha"] else "   "
        print(f"{marker} α = {r['alpha']:<4.1f}  |     {r['hit_rate']:<9.1%}   |    {r['mrr']:<9.3f}    |    {r['precision_at_k']:<9.3f}")
    print("-" * 65)
    print("   ★ = Meilleure configuration identifiée")

    # Synthèse par langue et catégorie
    detailed = report["detailed_results"]
    hits_fr = sum(1 for d in detailed if d["lang"] == "fr" and d["hit"])
    total_fr = sum(1 for d in detailed if d["lang"] == "fr")
    hits_ar = sum(1 for d in detailed if d["lang"] == "ar" and d["hit"])
    total_ar = sum(1 for d in detailed if d["lang"] == "ar")

    print("\n[2] PERFORMANCES PAR LANGUE (Avec meilleur α = %.1f)" % report["best_alpha"])
    print("-" * 65)
    print(f"   Français : {hits_fr}/{total_fr} Hit Rate ({(hits_fr/total_fr if total_fr else 0):.1%})")
    print(f"   Arabe    : {hits_ar}/{total_ar} Hit Rate ({(hits_ar/total_ar if total_ar else 0):.1%})")
    print("-" * 65)

    # Analyse des stratégies de prompt
    print("\n[3] ANALYSE ET COMPARAISON DE LA STRUCTURE DES PROMPTS")
    print("-" * 80)
    print(f"Question test : \"{report['prompt_comparison_details']['representative_question']}\"")
    print("-" * 80)
    print("   Stratégie        | Longueur (chars) | Nb de Tokens (estimé) | Composition")
    print("-" * 80)
    comp_details = report["prompt_comparison_details"]["strategies"]
    
    # Description de composition simplifiée
    desc = {
        "zero_shot": "Instructions directes + Contexte brut (3 docs)",
        "few_shot": "Instructions + 2 paires Q/R réelles + Contexte (3 docs)",
        "chain_of_thought": "Instructions détaillées + Gabarit de raisonnement + Contexte"
    }

    for strat, data in comp_details.items():
        print(f"   {strat:<16} | {data['length']:<16d} | {data['estimated_tokens']:<21d} | {desc[strat]}")
    print("-" * 80)
    print("\n" + "=" * 80)

if __name__ == "__main__":
    run_evaluation()
