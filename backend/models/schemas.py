from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict


class AskRequest(BaseModel):
    """Request model for the /ask endpoint."""
    query: str = Field(..., description="User query")
    model_name: str = Field("model_a", description="LLM to use for generation")
    prompt_template: str = Field("zero_shot", description="Prompt strategy")
    alpha: float = Field(0.3, description="FAISS/BM25 blend weight")
    top_k: int = Field(5, description="Number of documents to retrieve")
    categorie_filter: Optional[str] = None
    cancer_type_filter: Optional[str] = None

    @property
    def question(self) -> str:
        return self.query


class RetrieveRequest(BaseModel):
    """Request model for the /retrieve endpoint."""
    question: str
    top_k: int = 5
    alpha: float = 0.5
    categorie_filter: Optional[str] = None
    cancer_type_filter: Optional[str] = None
    prompt_strategy: str = "default"


class RetrievedDoc(BaseModel):
    """Retrieved document from FAISS or BM25."""
    id: str
    score: float
    title: str
    content: str


class ClassifyRequest(BaseModel):
    """Request model for the /classify endpoint."""
    question: str


class ClassifyResponse(BaseModel):
    """Response model for the /classify endpoint."""
    intent: str
    confidence: float
    language: str
    matched_patterns: List[str]


class ClassifyCancerRequest(BaseModel):
    """Request model for the /classify-cancer endpoint."""
    question: str


class ClassifyCancerResponse(BaseModel):
    """Response model for the /classify-cancer endpoint."""
    cancer: str
    confidence: float
    method: str
    scores: Optional[Dict[str, float]] = None


class SourceDoc(BaseModel):
    """A retrieved document returned in the /ask response."""
    id: str
    titre: str = ""
    categorie: str = ""
    type_cancer: str = ""
    score_final: float = 0.0
    score_faiss_norm: float = 0.0
    score_bm25_norm: float = 0.0
    reference: str = ""
    contenu: str = ""


class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    response: str
    model: str = ""
    model_id: str = ""
    latency: float = 0.0
    safe: bool = True
    prompt_template: str = ""
    language: str = ""
    intent: str = ""
    intent_confidence: float = 0.0
    sources: List[SourceDoc] = []
    error: Optional[str] = None


class HybridRequest(BaseModel):
    """Request model for the /hybrid-treatment endpoint."""
    cancer_type: str = Field(..., description="Type de cancer (ex: sein, poumon)")
    stage: str = Field("", description="Stade (I, II, III, IV, métastatique)")
    markers: List[str] = Field(default_factory=list, description="Marqueurs (HER2+, ER+…)")
    comorbidities: List[str] = Field(default_factory=list, description="Comorbidités")
    model_name: str = Field("model_b", description="LLM à utiliser (model_b recommandé)")


class HybridPhase(BaseModel):
    """A single sequenced step of a proposed hybrid treatment plan."""
    phase: int
    label: str
    modality: str
    recommendation: str
    sources: List[str] = []


class HybridResponse(BaseModel):
    """Response model for the /hybrid-treatment endpoint."""
    plan: str
    modalities_found: List[str] = []
    sources: List[SourceDoc] = []
    model: str = ""
    latency: float = 0.0
    error: Optional[str] = None
    # Enriched structured proposal (deterministic, always populated)
    recommended_sequence: List[HybridPhase] = []
    caveats: List[str] = []
    intent: str = ""        # "localise" | "metastatique"
    summary: str = ""       # LLM pedagogical reformulation (optional)
