from fastapi import APIRouter, HTTPException

from app.explain import explain_prediction
from app.model_registry import registry
from app.schemas import ExplainResponse, PredictionRequest

router = APIRouter(tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
def explain(req: PredictionRequest):
    if not registry.loaded:
        raise HTTPException(503, "Models not loaded on server")
    feature_dict = req.feedstock.model_dump(by_alias=True)
    try:
        return explain_prediction(feature_dict, req.model_name or "best")
    except Exception as e:
        raise HTTPException(500, f"Explanation failed: {e}")
