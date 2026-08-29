"""Single source of truth for engineered + physics-informed features.

Used by BOTH the training pipeline (ml/src/preprocessing.py) and the live
backend (backend/app/model_registry.py, via sys.path) so that a prediction
served by the API is computed from features engineered exactly the same
way the model was trained on. Previously the deployed app was silently
missing the engineered ratio columns at prediction time (they fell back to
imputed medians); this module fixes that by making feature engineering a
single shared function instead of pipeline-only logic.
"""
import numpy as np
import pandas as pd

from physics import PHYSICS_FEATURE_COLS, physics_features_for_row

RATIO_FEATURE_COLS = ["Cel_Lig_ratio", "O_C_feedstock", "H_C_feedstock", "Cel_Hem"]
ENGINEERED_COLS = RATIO_FEATURE_COLS + PHYSICS_FEATURE_COLS


def engineer_features_row(row: dict) -> dict:
    """Compute all engineered features for a single raw feedstock dict.
    Keys expected: Cel, Hem, Lig, C%, H%, O%, N%, PT, HR (VM/Ash/FC/Size/Temp
    pass through unused here but are part of the raw feature set elsewhere).
    """
    def safe_div(a, b):
        if a is None or b is None:
            return np.nan
        a, b = float(a), float(b)
        return a / b if b not in (0, None) else np.nan

    out = {
        "Cel_Lig_ratio": safe_div(row.get("Cel"), row.get("Lig")),
        "O_C_feedstock": safe_div(row.get("O%"), row.get("C%")),
        "H_C_feedstock": safe_div(row.get("H%"), row.get("C%")),
        "Cel_Hem": (row.get("Cel") or 0) + (row.get("Hem") or 0) if row.get("Cel") is not None and row.get("Hem") is not None else np.nan,
    }
    out.update(physics_features_for_row(row))
    return out


def engineer_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Apply engineer_features_row across a DataFrame and append the new columns."""
    df = df.copy()
    records = df.to_dict("records")
    engineered = [engineer_features_row(r) for r in records]
    eng_df = pd.DataFrame(engineered, index=df.index)
    return pd.concat([df, eng_df], axis=1)
