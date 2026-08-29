"""Pure-physics baseline for O/C: no ML at all, just the kinetics/energy
equations from physics.py, compared against pure-ML and hybrid physics+ML.

Rationale: `physics_char_fraction` (from Arrhenius kinetics) is a direct
mechanistic proxy for how much of the feedstock stayed solid vs. volatilized
into oil+gas. A higher char fraction at a given process temperature implies
milder/less complete devolatilization, which correlates with retaining more
of the feedstock's original oxygen-bearing structures in the condensed
products. We fit the simplest possible physically-motivated relationship —
a single linear regression of O/C against `physics_char_fraction` and the
feedstock's own O/C (`O_C_feedstock`) alone — deliberately not using any of
the other 12+ statistical features, so this is a genuine "physics-only"
comparison point, not another ML model in disguise.
"""
import json
import warnings
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from preprocessing import build_model_frame

warnings.filterwarnings("ignore")

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
RANDOM_STATE = 42
PHYSICS_ONLY_COLS = ["physics_char_fraction", "O_C_feedstock"]


def run():
    X, y, _ = build_model_frame("O/C")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    Xp_train = X_train[PHYSICS_ONLY_COLS].copy()
    Xp_test = X_test[PHYSICS_ONLY_COLS].copy()
    for c in PHYSICS_ONLY_COLS:
        med = Xp_train[c].median()
        Xp_train[c] = Xp_train[c].fillna(med)
        Xp_test[c] = Xp_test[c].fillna(med)

    model = LinearRegression()
    model.fit(Xp_train, y_train)
    pred_test = model.predict(Xp_test)
    pred_train = model.predict(Xp_train)

    result = {
        "description": "Pure-physics baseline: linear fit of O/C on physics_char_fraction "
                        "(Arrhenius kinetics conversion proxy) and O_C_feedstock only — no "
                        "other statistical features, no tree ensembles.",
        "features_used": PHYSICS_ONLY_COLS,
        "coefficients": dict(zip(PHYSICS_ONLY_COLS, [round(c, 4) for c in model.coef_])),
        "intercept": round(float(model.intercept_), 4),
        "train": {
            "r2": round(r2_score(y_train, pred_train), 4),
            "rmse": round(mean_squared_error(y_train, pred_train) ** 0.5, 4),
            "mae": round(mean_absolute_error(y_train, pred_train), 4),
        },
        "test": {
            "r2": round(r2_score(y_test, pred_test), 4),
            "rmse": round(mean_squared_error(y_test, pred_test) ** 0.5, 4),
            "mae": round(mean_absolute_error(y_test, pred_test), 4),
        },
    }
    (REPORTS_DIR / "physics_baseline.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
