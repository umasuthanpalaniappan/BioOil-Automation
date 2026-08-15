from fastapi import APIRouter, HTTPException

from app.model_registry import registry
from app.schemas import ModelInfo, ModelListResponse

router = APIRouter(tags=["models"])


@router.get("/models", response_model=ModelListResponse)
def list_models():
    return ModelListResponse(models=[ModelInfo(**m) for m in registry.model_info()])


DIAGNOSTICS_ALIASES = {"O_C": "O/C", "H_C": "H/C"}


@router.get("/diagnostics/{target}")
def diagnostics(target: str):
    target = DIAGNOSTICS_ALIASES.get(target, target)
    summary = registry.benchmark.get(target)
    if not summary:
        raise HTTPException(404, f"No diagnostics for target '{target}'")
    return {
        "target": target,
        "best_model": summary["best_model"],
        "y_test": summary["diagnostics"]["y_test"],
        "y_pred": summary["diagnostics"]["best_model_predictions"],
    }
