import io
import logging

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.drift import check_drift
from app.model_registry import registry
from app.physics_validation import validate_feedstock, validate_prediction
from app.schemas import BatchPredictionResponse, BatchPredictionRow, FeedstockInput

router = APIRouter(tags=["batch"])
logger = logging.getLogger("pyrolysis.batch")

REQUIRED_ALIASES = ["Cel", "Hem", "Lig", "VM", "Ash", "FC", "C%", "H%", "O%", "N%",
                     "Size", "HR", "PT"]


async def _read_table(file: UploadFile) -> pd.DataFrame:
    content = await file.read()
    if file.filename.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    return pd.read_excel(io.BytesIO(content))


@router.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(file: UploadFile = File(...)):
    if not registry.loaded:
        raise HTTPException(503, "Models not loaded on server")

    try:
        df = await _read_table(file)
    except Exception as e:
        raise HTTPException(400, f"Could not parse uploaded file: {e}")

    missing_cols = [c for c in REQUIRED_ALIASES if c not in df.columns]
    if missing_cols:
        raise HTTPException(400, f"Missing required columns: {missing_cols}")

    results = []
    preds = []
    for idx, row in df.iterrows():
        try:
            feedstock = FeedstockInput(**{c: row[c] for c in df.columns if c in FeedstockInput.model_fields or c in REQUIRED_ALIASES})
            feature_dict = feedstock.model_dump(by_alias=True)
            physics_flags = validate_feedstock(feedstock)
            pred, _, _ = registry.predict_oc(feature_dict, "best")
            physics_flags += validate_prediction(pred, "O/C")
            drift_flags = check_drift(feature_dict)
            results.append(BatchPredictionRow(
                row_index=int(idx), prediction=round(pred, 4),
                physics_flags=physics_flags, drift_flags=drift_flags,
            ))
            preds.append(pred)
        except (ValidationError, Exception) as e:
            results.append(BatchPredictionRow(row_index=int(idx), error=str(e)))

    n_ok = len(preds)
    summary = {
        "mean_prediction": round(sum(preds) / n_ok, 4) if n_ok else None,
        "min_prediction": round(min(preds), 4) if n_ok else None,
        "max_prediction": round(max(preds), 4) if n_ok else None,
    }
    logger.info("batch_predict rows=%d ok=%d failed=%d", len(df), n_ok, len(df) - n_ok)

    return BatchPredictionResponse(
        n_rows=len(df), n_succeeded=n_ok, n_failed=len(df) - n_ok,
        results=results, summary=summary,
    )


@router.post("/batch-predict/download")
async def batch_predict_download(file: UploadFile = File(...)):
    response = await batch_predict(file)
    rows = []
    for r in response.results:
        rows.append({
            "row_index": r.row_index,
            "prediction_O_C": r.prediction,
            "error": r.error,
            "n_physics_flags": len(r.physics_flags),
            "n_drift_flags": len(r.drift_flags),
        })
    out_df = pd.DataFrame(rows)
    buf = io.StringIO()
    out_df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=batch_predictions.csv"},
    )
