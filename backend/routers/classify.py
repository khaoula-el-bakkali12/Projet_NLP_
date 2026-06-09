from fastapi import APIRouter, HTTPException
from backend.models.schemas import ClassifyRequest, ClassifyResponse
from data_pipeline.nlp_query_processor import classify_intent

router = APIRouter()


@router.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    try:
        result = classify_intent(req.question)
        return ClassifyResponse(
            intent=result["intent"],
            confidence=result["confidence"],
            language=result["language"],
            matched_patterns=result["matched_patterns"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
