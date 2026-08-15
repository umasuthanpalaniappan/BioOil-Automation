"""Preprocessing pipeline for the bio-oil pyrolysis dataset.

Design decisions (see ml/reports/preprocessing.md for the full writeup):

1. Row filtering (data integrity, not statistical outliers):
   - Ultimate analysis (C%+H%+O%+N%) should sum to ~100% by definition.
     Rows where the sum is <80 or >120 are treated as data-entry errors
     (one row has H%=550, N%=40 — physically impossible) and dropped.
   - Rows with a null primary target (O/C) are dropped for O/C model
     training (can't impute the thing we're predicting), but are kept
     available for the secondary-target models where they DO have a value.

2. Target-domain outliers (e.g. O/C=3.57) are NOT removed. They fall
   within physically plausible bounds for high-oxygen feedstocks /
   low-severity pyrolysis and tree-based models handle them without
   distorting the fit; removing literature data points without a
   data-integrity reason would bias the small dataset.

3. Missing feature imputation: median imputation per column, fit on the
   training fold only (to avoid leakage) via sklearn's SimpleImputer
   inside the modeling pipeline. Median is chosen over mean for
   robustness to the skewed proximate/ultimate-analysis columns, and
   over more complex iterative imputation because with ~150-300 rows and
   many features missing >40% of the time, an iterative imputer would be
   fitting on very little signal and risks fabricating false precision.
   This is a documented limitation, not a claim of ideal handling.

4. Feature engineering (chemically motivated):
   - Cel_Lig_ratio = Cel / Lig            (cellulose vs lignin balance)
   - O_C_feedstock = O% / C%              (feedstock oxygen loading)
   - H_C_feedstock = H% / C%              (feedstock hydrogen loading)
   - Cel_Hem = Cel + Hem                  (total holocellulose)
"""
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import FEATURE_COLS, PRIMARY_TARGET, TARGET_COLS, load_raw

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"

ENGINEERED_COLS = ["Cel_Lig_ratio", "O_C_feedstock", "H_C_feedstock", "Cel_Hem"]
ALL_FEATURE_COLS = FEATURE_COLS + ENGINEERED_COLS


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Cel_Lig_ratio"] = df["Cel"] / df["Lig"].replace(0, np.nan)
    df["O_C_feedstock"] = df["O%"] / df["C%"].replace(0, np.nan)
    df["H_C_feedstock"] = df["H%"] / df["C%"].replace(0, np.nan)
    df["Cel_Hem"] = df["Cel"] + df["Hem"]
    return df


def clean_dataset() -> tuple[pd.DataFrame, dict]:
    """Return (cleaned_df, report_dict) with data-integrity filtering only.

    Cleaned df retains rows with missing *features* (imputed later, inside
    the model pipeline) but drops rows failing the ultimate-analysis sum
    sanity check.
    """
    df = load_raw()
    n_start = len(df)

    ua_sum = df["C%"] + df["H%"] + df["O%"] + df["N%"]
    bad_ua = ua_sum.notna() & ((ua_sum < 80) | (ua_sum > 120))
    n_bad_ua = int(bad_ua.sum())
    df = df.loc[~bad_ua].reset_index(drop=True)

    df = _engineer_features(df)

    report = {
        "n_start": n_start,
        "n_dropped_ultimate_analysis_integrity": n_bad_ua,
        "n_after_integrity_filter": len(df),
    }
    return df, report


def build_model_frame(target: str = PRIMARY_TARGET) -> tuple[pd.DataFrame, pd.Series, dict]:
    """Rows with a non-null value for `target`; features left with NaNs for
    the pipeline's imputer to handle."""
    df, report = clean_dataset()
    mask = df[target].notna()
    X = df.loc[mask, ALL_FEATURE_COLS]
    y = df.loc[mask, target]
    report["target"] = target
    report["n_rows_for_target"] = int(mask.sum())
    report["feature_missing_pct"] = (X.isna().mean() * 100).round(1).to_dict()
    return X, y, report


def write_report():
    df, report = clean_dataset()
    lines = [
        "# Preprocessing Report\n",
        f"- Rows before cleaning: {report['n_start']}",
        f"- Rows dropped for ultimate-analysis sum integrity "
        f"(C%+H%+O%+N% outside [80,120]): {report['n_dropped_ultimate_analysis_integrity']}",
        f"- Rows after integrity filter: {report['n_after_integrity_filter']}",
        "",
        "## Target-specific usable sample sizes\n",
    ]
    for target in TARGET_COLS:
        _, y, rep = build_model_frame(target)
        lines.append(f"- **{target}**: {rep['n_rows_for_target']} rows with a value")
    lines.append("")
    lines.append("## Engineered features\n")
    for c in ENGINEERED_COLS:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append(
        "## O/C outlier note\n\n"
        "O/C max = 3.57 is retained (see preprocessing.py docstring for "
        "rationale: not a data-integrity error, tree models are robust to "
        "it, and removing literature points from an already-small dataset "
        "is a bigger risk than keeping a legitimate high-oxygen sample)."
    )
    (REPORTS_DIR / "preprocessing.md").write_text("\n".join(lines))
    print("Preprocessing report written.")


if __name__ == "__main__":
    write_report()
