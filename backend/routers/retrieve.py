from fastapi import APIRouter, HTTPException
from backend.models.schemas import RetrieveRequest
from data_pipeline.nlp_query_processor import encode_query
from data_pipeline.retrieval import retrieve

router = APIRouter()


@router.post("/retrieve")
def retrieve_docs(req: RetrieveRequest):
    try:
        query_vector = encode_query(req.question)
        result = retrieve(
            query_vector=query_vector,
            question=req.question,
            top_k=req.top_k,
            alpha=req.alpha,
            categorie_filter=req.categorie_filter,
            cancer_type_filter=req.cancer_type_filter,
            prompt_strategy=req.prompt_strategy,
        )
        return {
            "top_k_docs": result["top_k_docs"],
            "scores": result["scores"],
            "alpha": result["alpha"],
            "num_candidates_faiss": result["num_candidates_faiss"],
            "num_candidates_bm25": result["num_candidates_bm25"],
            "num_after_filter": result["num_after_filter"],
            "filters_applied": result["filters_applied"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
