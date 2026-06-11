"""
run_benchmark.py
================
Standalone benchmark runner for Person 4's LLM module.
Generates results JSON + comparison charts.

Usage:
    python run_benchmark.py [--template zero_shot|few_shot|chain_of_thought]
                            [--test-set benchmark_gold_standard.json]
                            [--output benchmark_results.json]
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# ── B1: ensure data_pipeline package is importable ───────────────────────────
# LLM_cmp/ is a sub-directory of Projet_NLP_/.  data_pipeline/ is a sibling.
# Without this, "from data_pipeline.xxx import" raises ImportError and
# real_retrieval_fn() silently falls back to dummy_retrieval_fn().
_PROJECT_ROOT = Path(__file__).resolve().parent.parent   # → Projet_NLP_/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

logger = logging.getLogger("run_benchmark")

# ── Try to import optional plotting deps ──────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt
    import numpy as np
    PLOTTING = True
except ImportError:
    PLOTTING = False
    logger.warning("matplotlib/numpy not found — charts will be skipped.")


def load_test_set(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dummy_retrieval_fn(question: str):
    """
    Placeholder retrieval function — kept ONLY for offline smoke tests.

    In production (and in the actual benchmark run), this is replaced by
    `real_retrieval_fn()`, which wraps Person 3's hybrid FAISS+BM25 retriever.
    This function is no longer called from `main()` — see B1 fix in the
    remediation plan. It is preserved here so that unit tests / sandboxed
    environments without the indexed dataset can still exercise the
    benchmark machinery.
    """
    from llm_module import Document
    return [
        Document(
            id="ONC-PLACEHOLDER",
            contenu=(
                "Information générale sur les protocoles oncologiques marocains selon "
                "le guide AMFROM 2024. Consultez le document source pour les détails complets."
            ),
            categorie="general",
            source_reference="Guide AMFROM 2024",
        )
    ]


def _dict_to_document(doc: dict):
    """
    Convert an enriched retrieval dict (from data_pipeline.retrieval.retrieve())
    into the llm_module.Document dataclass expected by the LLM module.

    The retrieval module returns rich dicts (categorie, type_cancer, mots_cles,
    protocole, reference, etc.). The LLM module only consumes a subset, but
    we pass everything through so downstream code can use it.
    """
    from llm_module import Document
    return Document(
        id=doc.get("id", ""),
        contenu=doc.get("contenu", ""),
        categorie=doc.get("categorie", ""),
        type_cancer=doc.get("type_cancer", ""),
        mots_cles=list(doc.get("mots_cles", []) or []),
        protocole=(
            doc["protocole"].get("nom", "")   # some protocole dicts omit 'nom'
            if isinstance(doc.get("protocole"), dict)
            else (doc.get("protocole") or "")
        ),
        source_reference=doc.get("reference", ""),
    )


def real_retrieval_fn(question: str, top_k: int = 5, alpha: float = 0.7):
    """
    Real RAG retrieval function used by the benchmark.

    Pipeline (B1 fix):
      1. Encode the question with the multilingual SBERT model used by the
         data pipeline (`paraphrase-multilingual-MiniLM-L12-v2`).
      2. Run the hybrid FAISS + BM25 retriever from
         `data_pipeline.retrieval.retrieve()`.
      3. Optionally apply a cancer-type filter derived from
         `classify_cancer_type()` to tighten retrieval precision for
         single-organ questions (breast, lung, colorectal).
      4. Convert the returned dicts to `llm_module.Document` objects.

    Args:
        question: User question (FR/AR/EN).
        top_k:    Number of documents to return (default 5).
        alpha:    FAISS/BM25 fusion weight (default 0.7 — vector-leaning,
                  which generally outperforms pure BM25 for paraphrased
                  clinical questions).

    Returns:
        List[llm_module.Document] ordered by relevance (most relevant first).
        Returns an empty list on retrieval failure (and logs the error) so
        the benchmark loop never crashes.
    """
    from llm_module import Document

    try:
        # Lazy imports so this module can be imported (e.g., by --help) even
        # if the retrieval stack isn't fully built.
        from data_pipeline.nlp_query_processor import encode_query
        from data_pipeline.retrieval import retrieve
    except Exception as e:  # pragma: no cover — only triggered if package is missing
        logger.error(
            "real_retrieval_fn: data_pipeline package is not importable: %s. "
            "Falling back to dummy_retrieval_fn() so the benchmark can still run.",
            e,
        )
        return dummy_retrieval_fn(question)

    # Optional cancer-type filter (improves precision on organ-specific Qs).
    cancer_type_filter = None
    try:
        from data_pipeline.cancer_classifier import classify_cancer_type
        cls = classify_cancer_type(question)
        if cls.get("cancer") in {"sein", "poumon", "colorectal"}:
            cancer_type_filter = cls["cancer"]
            logger.info(
                "real_retrieval_fn: cancer_type_filter='%s' (method=%s, conf=%.2f)",
                cancer_type_filter, cls.get("method"), cls.get("confidence", 0.0),
            )
    except Exception as e:
        # Classifier is optional — log and continue without filter.
        logger.warning("real_retrieval_fn: cancer classifier unavailable: %s", e)

    try:
        vec = encode_query(question)
        result = retrieve(
            vec,
            question,
            top_k=top_k,
            alpha=alpha,
            cancer_type_filter=cancer_type_filter,
            prompt_strategy="zero_shot",  # prompt is built by the LLM module, not retrieval
        )
        top_docs = result.get("top_k_docs", [])
        if not top_docs:
            logger.warning(
                "real_retrieval_fn: retrieve() returned 0 docs for question=%r",
                question[:80],
            )
            return []
        return [_dict_to_document(d) for d in top_docs]
    except FileNotFoundError as e:
        # Common case: FAISS / BM25 / metadata files haven't been built yet.
        logger.error(
            "real_retrieval_fn: index files missing — %s. "
            "Run `python -m data_pipeline.indexer` to build them. "
            "Falling back to dummy_retrieval_fn().",
            e,
        )
        return dummy_retrieval_fn(question)
    except Exception as e:
        logger.error(
            "real_retrieval_fn: retrieval failed for question=%r — %s. "
            "Falling back to dummy_retrieval_fn().",
            question[:80], e,
        )
        return dummy_retrieval_fn(question)


def plot_metrics(summary: dict, output_dir: str = "."):
    if not PLOTTING:
        return
    metrics = ["bleu", "rouge_l", "bertscore"]
    models = list(summary.keys())
    x = np.arange(len(models))
    width = 0.25

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Benchmark LLM Local — Oncologie RAG", fontsize=14, fontweight="bold")

    # ── Bar chart: BLEU / ROUGE-L / BERTScore ────────────────────────────────
    ax = axes[0]
    for i, metric in enumerate(metrics):
        values = [summary[m].get(metric, 0) for m in models]
        ax.bar(x + i * width, values, width, label=metric.upper())
    ax.set_xticks(x + width)
    ax.set_xticklabels([m.replace("model_", "Modèle ").upper() for m in models])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Métriques automatiques")
    ax.legend()

    # ── Bar chart: latency ────────────────────────────────────────────────────
    ax2 = axes[1]
    latencies = [summary[m].get("latency_seconds", 0) for m in models]
    colors = ["#4C72B0", "#DD8452", "#55A868"]
    ax2.bar(
        [m.replace("model_", "Modèle ").upper() for m in models],
        latencies,
        color=colors,
    )
    ax2.set_ylabel("Latence moyenne (s)")
    ax2.set_title("Temps de réponse moyen")

    plt.tight_layout()
    chart_path = os.path.join(output_dir, "benchmark_chart.png")
    plt.savefig(chart_path, dpi=150)
    logger.info(f"Chart saved to '{chart_path}'.")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Run LLM benchmarking for Oncology RAG")
    parser.add_argument("--template", default="zero_shot",
                        choices=["zero_shot", "few_shot", "chain_of_thought"])
    parser.add_argument("--test-set", default="benchmark_gold_standard.json")
    parser.add_argument("--output", default="benchmark_results.json")
    parser.add_argument(
        "--models", default=None,
        help="Comma-separated model names to benchmark (e.g. model_a,model_b). "
             "Default: all three models. Use model_a alone for a fast ~15-min run on CPU.",
    )
    parser.add_argument(
        "--max-questions", type=int, default=None,
        help="Limit the test set to the first N questions (e.g. 5 for a smoke test).",
    )
    args = parser.parse_args()

    # Validate test set path
    if not os.path.exists(args.test_set):
        logger.error(f"Test set file not found: {args.test_set}")
        sys.exit(1)

    # Parse model selection
    selected_models = None
    if args.models:
        selected_models = [m.strip() for m in args.models.split(",")]
        valid = {"model_a", "model_b", "model_c"}
        bad = [m for m in selected_models if m not in valid]
        if bad:
            logger.error(f"Unknown model(s): {bad}. Choose from {valid}.")
            sys.exit(1)
        logger.info(f"Running only: {selected_models}")

    # Import after arg parsing so --help works without loading models
    from llm_module import run_benchmark, summarize_benchmark, print_comparison_table

    test_set = load_test_set(args.test_set)
    if args.max_questions:
        test_set = test_set[: args.max_questions]
        logger.info(f"Limiting to first {args.max_questions} questions (--max-questions).")
    logger.info(f"Loaded {len(test_set)} questions from '{args.test_set}'.")
    logger.info(f"Prompt template: {args.template}")

    entries = run_benchmark(
        test_set=test_set,
        retrieval_fn=real_retrieval_fn,    # B1 fix: real hybrid FAISS+BM25 retriever
        prompt_template=args.template,
        output_path=args.output,
        models=selected_models,
    )

    summary = summarize_benchmark(entries)
    print("\n")
    print_comparison_table(summary)

    # Save summary alongside full results
    summary_path = args.output.replace(".json", "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    logger.info(f"Summary saved to '{summary_path}'.")

    # Generate chart
    output_dir = os.path.dirname(args.output) or "."
    plot_metrics(summary, output_dir=output_dir)

    logger.info("Done.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
    main()
