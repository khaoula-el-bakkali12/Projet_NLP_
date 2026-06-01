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
    Placeholder retrieval function.
    In production, replace this with Person 3's retrieve() call:

        from retrieval_module import retrieve
        from nlp_module import encode_query

        def retrieval_fn(question):
            vec, intent, entities = encode_query(question)
            return retrieve(vec, question)
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
    args = parser.parse_args()

    # Validate test set path
    if not os.path.exists(args.test_set):
        logger.error(f"Test set file not found: {args.test_set}")
        sys.exit(1)

    # Import after arg parsing so --help works without loading models
    from llm_module import run_benchmark, summarize_benchmark, print_comparison_table

    test_set = load_test_set(args.test_set)
    logger.info(f"Loaded {len(test_set)} questions from '{args.test_set}'.")
    logger.info(f"Prompt template: {args.template}")

    entries = run_benchmark(
        test_set=test_set,
        retrieval_fn=dummy_retrieval_fn,
        prompt_template=args.template,
        output_path=args.output,
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
