from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    ClassifyRequest, ClassifyResponse,
    ClassifyCancerRequest, ClassifyCancerResponse,
)
from data_pipeline.nlp_query_processor import classify_intent
from data_pipeline.cancer_classifier import classify_cancer_type

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


@router.post("/classify-cancer", response_model=ClassifyCancerResponse)
def classify_cancer(req: ClassifyCancerRequest):
    """
    Classify the cancer type evoked in a clinical question.

    Hybrid keyword + SBERT classifier covering the 3 main cancers
    (sein / poumon / colorectal) named in the project brief, with an
    "inconnu" fallback for questions outside that scope.
    """
    try:
        result = classify_cancer_type(req.question)
        return ClassifyCancerResponse(
            cancer=result["cancer"],
            confidence=result["confidence"],
            method=result["method"],
            scores=result.get("scores"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
