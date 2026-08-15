from fastapi import APIRouter, HTTPException

from app.model_registry import registry
from app.schemas import ModelInfo, ModelListResponse

router = APIRouter(tags=["models"])


@router.get("/models", response_model=ModelListResponse)
def list_models():
    return ModelListResponse(models=[ModelInfo(**m) for m in registry.model_info()])


@router.get("/diagnostics/{target}")
def diagnostics(target: str):
    target = target.replace("_", "/") if target == "H_C" else target
    summary = registry.benchmark.get(target)
    if not summary:
        raise HTTPException(404, f"No diagnostics for target '{target}'")
    return {
        "target": target,
        "best_model": summary["best_model"],
        "y_test": summary["diagnostics"]["y_test"],
        "y_pred": summary["diagnostics"]["best_model_predictions"],
    }
