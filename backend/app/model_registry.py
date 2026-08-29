"""Loads trained model artifacts once at startup and serves predictions."""
import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np

DEFAULT_MODELS_DIR = Path(__file__).resolve().parents[2] / "ml" / "models"
MODELS_DIR = Path(os.environ.get("MODELS_DIR", str(DEFAULT_MODELS_DIR)))

# Reuse the exact same feature-engineering code the training pipeline used,
# so a live prediction is engineered identically to the training data
# (ratios + physics-informed kinetics/HHV features from ml/src/physics.py).
ML_SRC_DIR = Path(os.environ.get("ML_SRC_DIR", str(Path(__file__).resolve().parents[2] / "ml" / "src")))
if str(ML_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(ML_SRC_DIR))
from feature_engineering import engineer_features_row  # noqa: E402

VERSION = "v1"
SECONDARY_TARGETS = ["H/C", "Cal_value", "Oil_yield"]
MODEL_ALIASES = ["random_forest", "xgboost", "lightgbm", "gpr", "ridge", "lasso", "mlp"]


class ModelRegistry:
    def __init__(self):
        self.feature_columns: list[str] = []
        self.feature_ranges: dict = {}
        self.oc_models: dict = {}
        self.secondary_models: dict = {}
        self.benchmark: dict = {}
        self.loaded = False

    def load(self):
        if not MODELS_DIR.exists():
            self.loaded = False
            return

        feat_path = MODELS_DIR / "feature_columns.json"
        if feat_path.exists():
            self.feature_columns = json.loads(feat_path.read_text())

        ranges_path = MODELS_DIR / "feature_ranges.json"
        if ranges_path.exists():
            self.feature_ranges = json.loads(ranges_path.read_text())

        bench_path = MODELS_DIR.parent / "reports" / "benchmark_results.json"
        if bench_path.exists():
            self.benchmark = json.loads(bench_path.read_text())

        for alias in MODEL_ALIASES:
            p = MODELS_DIR / f"O_C__{alias}__{VERSION}.joblib"
            if p.exists():
                self.oc_models[alias] = joblib.load(p)

        best_path = MODELS_DIR / f"O_C__best__{VERSION}.joblib"
        if best_path.exists():
            self.oc_models["best"] = joblib.load(best_path)

        for target in SECONDARY_TARGETS:
            p = MODELS_DIR / f"{target.replace('/', '_')}__best__{VERSION}.joblib"
            if p.exists():
                self.secondary_models[target] = joblib.load(p)

        # xgboost's __sklearn_tags__() can return estimator_type=None on some
        # xgboost/scikit-learn version combinations; patch it so any
        # sklearn internals relying on is_regressor() (e.g. inspection
        # utilities) see these fitted regressors correctly.
        for pipe in [*self.oc_models.values(), *self.secondary_models.values()]:
            inner = pipe.named_steps.get("model") if hasattr(pipe, "named_steps") else None
            if inner is not None and hasattr(inner, "__sklearn_tags__"):
                original = inner.__sklearn_tags__

                def _patched(original=original):
                    tags = original()
                    if tags.estimator_type is None:
                        tags.estimator_type = "regressor"
                    return tags

                inner.__sklearn_tags__ = _patched

        self.loaded = len(self.oc_models) > 0

    def available_models(self) -> list[str]:
        return sorted(self.oc_models.keys())

    def to_feature_frame(self, feature_dict: dict):
        import pandas as pd

        enriched = {**feature_dict, **engineer_features_row(feature_dict)}
        row = {c: enriched.get(c, np.nan) for c in self.feature_columns}
        return pd.DataFrame([row])

    def predict_oc(self, feature_dict: dict, model_name: str = "best"):
        model = self.oc_models.get(model_name) or self.oc_models.get("best")
        used = model_name if model_name in self.oc_models else "best"
        X = self.to_feature_frame(feature_dict)
        pred = float(model.predict(X)[0])

        ci = None
        inner = model.named_steps.get("model") if hasattr(model, "named_steps") else None
        if inner is not None and inner.__class__.__name__ == "GaussianProcessRegressor":
            X_t = model[:-1].transform(X)
            mean, std = inner.predict(X_t, return_std=True)
            ci = [float(mean[0] - 1.96 * std[0]), float(mean[0] + 1.96 * std[0])]
        elif inner is not None and inner.__class__.__name__ == "RandomForestRegressor":
            X_t = model[:-1].transform(X)
            tree_preds = np.array([t.predict(X_t)[0] for t in inner.estimators_])
            std = tree_preds.std()
            ci = [float(pred - 1.96 * std), float(pred + 1.96 * std)]

        return pred, ci, used

    def predict_secondary(self, feature_dict: dict) -> dict:
        X = self.to_feature_frame(feature_dict)
        out = {}
        for target, model in self.secondary_models.items():
            out[target] = float(model.predict(X)[0])
        return out

    def predict_all_models(self, feature_dict: dict) -> dict:
        X = self.to_feature_frame(feature_dict)
        return {name: float(m.predict(X)[0]) for name, m in self.oc_models.items() if name != "best"}

    def model_info(self) -> list[dict]:
        infos = []
        for target, summary in self.benchmark.items():
            for name, r in summary.get("results", {}).items():
                infos.append({
                    "name": name,
                    "target": target,
                    "cv_r2": r.get("cv_r2_mean"),
                    "test_r2": r.get("test", {}).get("r2"),
                    "test_rmse": r.get("test", {}).get("rmse"),
                    "test_mae": r.get("test", {}).get("mae"),
                })
        return infos


registry = ModelRegistry()
