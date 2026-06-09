import os
import sys
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(tags=["upload"])

ROOT       = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(ROOT, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

_DATASET_JSON = os.path.join(ROOT, "data", "raw", "dataset_oncologie_FINAL_v6.json")


def _ensure_paths():
    for p in [ROOT, os.path.join(ROOT, "LLM_cmp")]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _extract_text(path: str, filename: str) -> str:
    if filename.lower().endswith(".txt"):
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()

    try:
        import pdfplumber
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        extracted = "\n".join(text).strip()
        if extracted:
            return extracted
    except Exception as e:
        print(f"[upload] pdfplumber error: {type(e).__name__}: {e}")

    raise HTTPException(
        status_code=422,
        detail="Impossible d'extraire le texte du PDF. Le fichier est peut-être scanné (image) ou corrompu."
    )


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words  = text.split()
    chunks = []
    i      = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + chunk_size]))
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


def _get_dataset_light():
    """Return in-memory dataset if already cached, else read from JSON — no heavy model loading."""
    _ensure_paths()
    try:
        import data_pipeline.retrieval as _ret
        if _ret._CACHED_RESOURCES is not None:
            return _ret._CACHED_RESOURCES["dataset"]
    except Exception:
        pass
    try:
        with open(_DATASET_JSON, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _sync_documents_router(new_entries: list[dict] | None = None, removed_ids: set | None = None):
    """Keep documents.py module-level cache in sync after upload/delete."""
    try:
        import backend.routers.documents as _docs
        if new_entries:
            _docs._DATASET.extend(new_entries)
            _docs._BY_ID.update({d["id"]: d for d in new_entries})
        if removed_ids:
            # Filter in place
            keep = [d for d in _docs._DATASET if d["id"] not in removed_ids]
            _docs._DATASET.clear()
            _docs._DATASET.extend(keep)
            for rid in removed_ids:
                _docs._BY_ID.pop(rid, None)
    except Exception as e:
        print(f"[upload] documents cache sync failed: {e}")


# ── List uploaded documents ────────────────────────────────────────────────────

@router.get("/uploaded-documents")
def list_uploaded_documents():
    dataset = _get_dataset_light()
    # Index chunks per source file
    chunks_by_file: dict[str, int] = {}
    for d in dataset:
        sf = d.get("source_file")
        if sf:
            chunks_by_file[sf] = chunks_by_file.get(sf, 0) + 1

    files = []
    for fname in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        stat = os.stat(fpath)
        files.append({
            "filename":    fname,
            "size":        stat.st_size,
            "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "chunks":      chunks_by_file.get(fname, 0),
        })

    return sorted(files, key=lambda x: x["uploaded_at"], reverse=True)


# ── Delete uploaded document ───────────────────────────────────────────────────

@router.delete("/uploaded-documents/{filename:path}")
def delete_uploaded_document(filename: str):
    fpath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(fpath):
        raise HTTPException(status_code=404, detail="Fichier non trouvé.")

    index_error = None
    removed_ids: set = set()

    try:
        _ensure_paths()
        from data_pipeline.retrieval import load_retrieval_resources
        from data_pipeline.indexer import build_corpus_text, tokenize
        from data_pipeline.nlp_query_processor import get_sbert_model
        from rank_bm25 import BM25Okapi
        import numpy as np
        import faiss
        import pickle

        resources     = load_retrieval_resources()
        dataset       = resources["dataset"]
        metadata_list = resources["metadata"]

        # Identify entries belonging to this file
        removed_ids = {d["id"] for d in dataset if d.get("source_file") == filename}

        if removed_ids:
            keep_dataset  = [d for d in dataset  if d["id"] not in removed_ids]
            keep_metadata = [m for m in metadata_list if m["id"] not in removed_ids]

            # Re-number vector indices (they must match rebuild order)
            for i, m in enumerate(keep_metadata):
                m["vector_index"] = i

            # Rebuild FAISS from scratch
            sbert        = get_sbert_model()
            corpus_texts = [build_corpus_text(e) for e in keep_dataset]
            vectors      = sbert.encode(corpus_texts, normalize_embeddings=True, show_progress_bar=False)
            dim          = vectors.shape[1] if len(vectors) else resources["faiss_index"].d
            new_faiss    = faiss.IndexFlatIP(dim)
            if len(vectors):
                new_faiss.add(np.array(vectors, dtype="float32"))

            # Rebuild BM25
            full_corpus = [tokenize(build_corpus_text(e)) for e in keep_dataset]
            new_bm25    = BM25Okapi(full_corpus) if full_corpus else BM25Okapi([[]])

            # Update in-memory resources (mutate the cached objects in place)
            dataset.clear()
            dataset.extend(keep_dataset)
            metadata_list.clear()
            metadata_list.extend(keep_metadata)
            resources["faiss_index"] = new_faiss
            resources["bm25_index"]  = new_bm25

            # Persist to disk
            idx_dir = os.path.join(ROOT, "data", "indexes")
            faiss.write_index(new_faiss, os.path.join(idx_dir, "faiss_index.bin"))
            with open(os.path.join(idx_dir, "index_metadata.json"), "w", encoding="utf-8") as mf:
                json.dump(keep_metadata, mf, ensure_ascii=False, indent=2)
            with open(os.path.join(idx_dir, "bm25_index.pkl"), "wb") as bf:
                pickle.dump(new_bm25, bf)
            with open(_DATASET_JSON, "w", encoding="utf-8") as df:
                json.dump(keep_dataset, df, ensure_ascii=False, indent=2)

            _sync_documents_router(removed_ids=removed_ids)

    except Exception as exc:
        import traceback
        traceback.print_exc()
        index_error = str(exc)

    # Always remove the file from disk
    os.remove(fpath)

    msg = f"Document '{filename}' supprimé avec succès."
    if index_error:
        msg += f" (Avertissement index : {index_error})"
    return {"message": msg, "removed_chunks": len(removed_ids)}


# ── Upload document ────────────────────────────────────────────────────────────

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    allowed = {"application/pdf", "text/plain"}
    if file.content_type not in allowed and not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF et TXT sont acceptés.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    contents  = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 20 MB).")

    with open(save_path, "wb") as f:
        f.write(contents)

    text   = _extract_text(save_path, file.filename)
    chunks = _chunk_text(text)

    if not chunks:
        raise HTTPException(status_code=422, detail="Aucun texte extractible trouvé dans le document.")

    try:
        _ensure_paths()
        from data_pipeline.retrieval import load_retrieval_resources
        from data_pipeline.indexer import build_corpus_text, tokenize
        from data_pipeline.nlp_query_processor import get_sbert_model
        from rank_bm25 import BM25Okapi
        import numpy as np
        import faiss
        import pickle

        resources     = load_retrieval_resources()
        faiss_index   = resources["faiss_index"]
        metadata_list = resources["metadata"]
        dataset       = resources["dataset"]

        sbert     = get_sbert_model()
        source    = os.path.splitext(file.filename)[0]
        start_idx = len(dataset)

        new_dataset  = []
        new_metadata = []
        for i, chunk in enumerate(chunks):
            doc_id = f"upload_{source}_{uuid.uuid4().hex[:8]}"
            titre  = f"{source} — partie {i + 1}"
            entry  = {
                "id":                doc_id,
                "categorie":         "Document Importé",
                "type_cancer":       "",
                "sous_type":         "",
                "stade":             "",
                "titre":             titre,
                "contenu":           chunk,
                "protocole":         None,
                "effets_secondaires": [],
                "mots_cles":         [],
                "scenario_patient":  "",
                "reference":         source,
                "est_synthetique":   False,
                "metastase":         "",
                "source_file":       file.filename,
            }
            new_dataset.append(entry)
            new_metadata.append({
                "vector_index": start_idx + i,
                "id":           doc_id,
                "type_cancer":  "",
                "categorie":    "Document Importé",
                "sous_type":    "",
                "stade":        "",
                "titre":        titre,
                "reference":    source,
                "est_synthetique": False,
            })

        corpus_texts = [build_corpus_text(e) for e in new_dataset]
        vectors      = sbert.encode(corpus_texts, normalize_embeddings=True)
        faiss_index.add(np.array(vectors, dtype="float32"))

        dataset.extend(new_dataset)
        metadata_list.extend(new_metadata)

        full_corpus = [tokenize(build_corpus_text(e)) for e in dataset]
        new_bm25    = BM25Okapi(full_corpus)
        resources["bm25_index"] = new_bm25

        idx_dir = os.path.join(ROOT, "data", "indexes")
        faiss.write_index(faiss_index, os.path.join(idx_dir, "faiss_index.bin"))
        with open(os.path.join(idx_dir, "index_metadata.json"), "w", encoding="utf-8") as mf:
            json.dump(metadata_list, mf, ensure_ascii=False, indent=2)
        with open(os.path.join(idx_dir, "bm25_index.pkl"), "wb") as bf:
            pickle.dump(new_bm25, bf)
        with open(_DATASET_JSON, "w", encoding="utf-8") as df:
            json.dump(dataset, df, ensure_ascii=False, indent=2)

        _sync_documents_router(new_entries=new_dataset)

        return {
            "message":      f"Document '{file.filename}' indexé avec succès.",
            "chunks_added": len(new_dataset),
            "total_docs":   len(dataset),
        }

    except Exception as exc:
        import traceback
        traceback.print_exc()
        return {
            "message":      f"Fichier sauvegardé mais indexation échouée : {exc}",
            "chunks_added": 0,
            "total_docs":   0,
        }
