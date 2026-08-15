"""Pydantic request/response models for the pyrolysis prediction API."""
from typing import Optional

from pydantic import BaseModel, Field


class FeedstockInput(BaseModel):
    """Biomass composition, proximate/ultimate analysis, and process conditions."""

    Cel: float = Field(..., ge=0, le=100, description="Cellulose content (wt%)")
    Hem: float = Field(..., ge=0, le=100, description="Hemicellulose content (wt%)")
    Lig: float = Field(..., ge=0, le=100, description="Lignin content (wt%)")
    VM: float = Field(..., ge=0, le=100, description="Volatile matter (wt%, proximate)")
    Ash: float = Field(..., ge=0, le=100, description="Ash content (wt%, proximate)")
    FC: float = Field(..., ge=0, le=100, description="Fixed carbon (wt%, proximate)")
    C_pct: float = Field(..., ge=0, le=100, alias="C%", description="Carbon (wt%, ultimate, daf)")
    H_pct: float = Field(..., ge=0, le=30, alias="H%", description="Hydrogen (wt%, ultimate, daf)")
    O_pct: float = Field(..., ge=0, le=100, alias="O%", description="Oxygen (wt%, ultimate, daf)")
    N_pct: float = Field(..., ge=0, le=30, alias="N%", description="Nitrogen (wt%, ultimate, daf)")
    Size: float = Field(..., gt=0, le=50, description="Feedstock particle size (mm)")
    HR: float = Field(..., gt=0, le=1000, description="Heating rate (°C/min)")
    PT: float = Field(..., ge=100, le=1200, description="Pyrolysis temperature (°C)")
    Temp: Optional[float] = Field(None, ge=0, le=1000, description="Secondary temperature parameter")

    model_config = {"populate_by_name": True}


class PredictionRequest(BaseModel):
    feedstock: FeedstockInput
    model_name: Optional[str] = Field(
        "best", description="Model to use: 'best', 'random_forest', 'xgboost', "
        "'lightgbm', 'gpr', 'ridge', 'lasso', 'mlp'"
    )

    model_config = {"protected_namespaces": ()}


class ConstraintFlag(BaseModel):
    field: str
    message: str
    severity: str  # "warning" | "error"


class DriftFlag(BaseModel):
    field: str
    value: float
    training_min: float
    training_max: float
    message: str


class PredictionResponse(BaseModel):
    target: str = "O/C"
    prediction: float
    confidence_interval_95: Optional[list[float]] = None
    model_used: str
    physics_flags: list[ConstraintFlag] = []
    drift_flags: list[DriftFlag] = []

    model_config = {"protected_namespaces": ()}


class SecondaryPredictions(BaseModel):
    H_C: Optional[float] = Field(None, alias="H/C")
    Cal_value: Optional[float] = None
    Oil_yield: Optional[float] = None

    model_config = {"populate_by_name": True}


class FullPredictionResponse(PredictionResponse):
    secondary: Optional[SecondaryPredictions] = None


class ModelComparisonResponse(BaseModel):
    feedstock: FeedstockInput
    predictions: dict[str, float]
    confidence_intervals: dict[str, Optional[list[float]]] = {}


class ExplanationItem(BaseModel):
    feature: str
    value: float
    shap_value: float
    plain_language: str


class ExplainResponse(BaseModel):
    prediction: float
    base_value: float
    top_features: list[ExplanationItem]
    summary: str


class ModelInfo(BaseModel):
    name: str
    target: str
    cv_r2: Optional[float] = None
    test_r2: Optional[float] = None
    test_rmse: Optional[float] = None
    test_mae: Optional[float] = None


class ModelListResponse(BaseModel):
    models: list[ModelInfo]


class BatchPredictionRow(BaseModel):
    row_index: int
    prediction: Optional[float] = None
    error: Optional[str] = None
    physics_flags: list[ConstraintFlag] = []
    drift_flags: list[DriftFlag] = []


class BatchPredictionResponse(BaseModel):
    n_rows: int
    n_succeeded: int
    n_failed: int
    results: list[BatchPredictionRow]
    summary: dict
