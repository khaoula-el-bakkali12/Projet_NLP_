"""
data_pipeline — Module de preprocessing, indexation, retrieval & prompt du dataset oncologique.

Ce module fournit les fonctions pour :
  - Charger et valider le dataset JSON
  - Nettoyer et normaliser le texte (français/arabe)
  - Construire les index de recherche (FAISS + BM25)
  - Exporter les métadonnées d'indexation
  - Recherche hybride FAISS + BM25 avec fusion de scores
  - Construction de prompts (Zero-shot, Few-shot, Chain-of-Thought)
"""

from .indexer import (
    # Chargement & validation
    load_json,
    validate_schema,
    fix_duplicates,
    fix_onc029,
    # Nettoyage texte
    clean_text,
    remove_accents,
    remove_stopwords,
    tokenize,
    # Corpus & embeddings
    build_corpus_text,
    build_bm25_corpus,
    generate_embeddings,
    # Indexation
    build_faiss_index,
    save_faiss_index,
    load_faiss_index,
    build_bm25_index,
    save_bm25_index,
    load_bm25_index,
    # Metadata
    build_index_metadata,
    save_metadata,
    # Recherche
    search_faiss,
    search_bm25,
    # Pipeline
    run_pipeline,
)

from .retrieval import (
    retrieve,
    load_retrieval_resources,
    evaluate_alpha_range,
)

from .prompt_builder import (
    build_prompt,
    format_documents,
    compare_prompts,
    get_available_strategies,
)

__all__ = [
    # Indexer
    "load_json", "validate_schema", "fix_duplicates", "fix_onc029",
    "clean_text", "remove_accents", "remove_stopwords", "tokenize",
    "build_corpus_text", "build_bm25_corpus", "generate_embeddings",
    "build_faiss_index", "save_faiss_index", "load_faiss_index",
    "build_bm25_index", "save_bm25_index", "load_bm25_index",
    "build_index_metadata", "save_metadata",
    "search_faiss", "search_bm25",
    "run_pipeline",
    # Retrieval
    "retrieve", "load_retrieval_resources", "evaluate_alpha_range",
    # Prompt builder
    "build_prompt", "format_documents", "compare_prompts", "get_available_strategies",
]
