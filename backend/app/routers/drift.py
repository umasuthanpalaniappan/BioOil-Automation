from fastapi import APIRouter

from app.drift import check_drift
from app.model_registry import registry
from app.schemas import FeedstockInput

router = APIRouter(tags=["drift"])


@router.get("/feature-ranges")
def feature_ranges():
    return registry.feature_ranges


@router.post("/drift-check")
def drift_check(feedstock: FeedstockInput):
    feature_dict = feedstock.model_dump(by_alias=True)
    flags = check_drift(feature_dict)
    return {"in_distribution": len(flags) == 0, "flags": flags}
