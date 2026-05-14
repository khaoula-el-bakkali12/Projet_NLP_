# Projet NLP — Assistant Médical spécialiste en Oncologie

Pipeline de preprocessing et d'indexation pour un système RAG (Retrieval-Augmented Generation) spécialisé en oncologie dans le contexte marocain.

## 📁 Structure du projet

```
Projet_NLP_/
├── data/
│   ├── raw/                          # Données sources (non modifiées)
│   │   ├── dataset_oncologie_FINAL_v6.json
│   │   ├── dataset_oncologie_FINAL_v6.csv
│   │   └── Guide des protocoles 2024.pdf
│   └── indexes/                      # Index générés (régénérables)
│       ├── faiss_index.bin
│       ├── bm25_index.pkl
│       └── index_metadata.json
├── data_pipeline/                    # Module Python : preprocessing & indexation
│   ├── __init__.py
│   └── indexer.py
├── tests/                            # Tests unitaires
│   ├── __init__.py
│   └── test_indexer.py
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## ⚙️ Utilisation

### Lancer le pipeline complet (preprocessing + indexation)

```bash
python -m data_pipeline.indexer
```

Ce pipeline exécute :
1. **Chargement & validation** du dataset JSON (schéma, types)
2. **Correction** des doublons d'ID et de l'entrée ONC-029
3. **Nettoyage du texte** : minuscules, suppression accents, stop-words FR/AR
4. **Construction du corpus** BM25 (titre + contenu + mots_clés)
5. **Génération des embeddings** avec Sentence-BERT multilingue
6. **Indexation FAISS** (recherche vectorielle, cosine similarity)
7. **Indexation BM25** (recherche lexicale)
8. **Export** du fichier `index_metadata.json`
9. **Vérification** self-retrieval top-1 sur FAISS et BM25

### Lancer les tests

```bash
python -m pytest tests/ -v
```

## 📦 Dépendances principales

| Package | Rôle |
|---------|------|
| `sentence-transformers` | Embeddings multilingues (Sentence-BERT) |
| `faiss-cpu` | Recherche vectorielle rapide |
| `rank-bm25` | Recherche lexicale BM25 |
| `unidecode` | Normalisation des accents |
| `numpy` | Calcul numérique |
