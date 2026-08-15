import logging

from fastapi import APIRouter, HTTPException

from app.drift import check_drift
from app.model_registry import registry
from app.physics_validation import validate_feedstock, validate_prediction
from app.schemas import (
    FullPredictionResponse,
    ModelComparisonResponse,
    PredictionRequest,
    SecondaryPredictions,
)

router = APIRouter(tags=["predict"])
logger = logging.getLogger("pyrolysis.predict")


@router.post("/predict", response_model=FullPredictionResponse)
def predict(req: PredictionRequest):
    if not registry.loaded:
        raise HTTPException(503, "Models not loaded on server")

    feature_dict = req.feedstock.model_dump(by_alias=True)
    physics_flags = validate_feedstock(req.feedstock)

    try:
        pred, ci, used = registry.predict_oc(feature_dict, req.model_name or "best")
    except Exception as e:
        logger.exception("prediction failed")
        raise HTTPException(500, f"Prediction failed: {e}")

    physics_flags += validate_prediction(pred, "O/C")
    drift_flags = check_drift(feature_dict)
    secondary_raw = registry.predict_secondary(feature_dict)
    secondary = SecondaryPredictions(**{
        ("H/C" if k == "H/C" else k): v for k, v in secondary_raw.items()
    })

    logger.info("predict model=%s target=O/C pred=%.4f", used, pred)

    return FullPredictionResponse(
        prediction=round(pred, 4),
        confidence_interval_95=[round(c, 4) for c in ci] if ci else None,
        model_used=used,
        physics_flags=physics_flags,
        drift_flags=drift_flags,
        secondary=secondary,
    )


@router.post("/compare-models", response_model=ModelComparisonResponse)
def compare_models(req: PredictionRequest):
    if not registry.loaded:
        raise HTTPException(503, "Models not loaded on server")
    feature_dict = req.feedstock.model_dump(by_alias=True)
    preds = registry.predict_all_models(feature_dict)
    cis = {}
    for name in preds:
        _, ci, _ = registry.predict_oc(feature_dict, name)
        cis[name] = [round(c, 4) for c in ci] if ci else None
    return ModelComparisonResponse(
        feedstock=req.feedstock,
        predictions={k: round(v, 4) for k, v in preds.items()},
        confidence_intervals=cis,
    )
