"""SHAP feature importance + partial dependence for the best O/C model."""
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shap
from sklearn.inspection import PartialDependenceDisplay

from preprocessing import ALL_FEATURE_COLS, build_model_frame

warnings.filterwarnings("ignore")

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
FIG_DIR = REPORTS_DIR / "figures"


def _patch_sklearn_tags(estimator):
    """XGBoost's __sklearn_tags__() returns estimator_type=None on some
    xgboost/scikit-learn version combinations (xgboost's sklearn wrapper
    doesn't properly propagate RegressorMixin's tag contribution), which
    makes sklearn's is_regressor() — used internally by
    PartialDependenceDisplay — reject a perfectly good fitted regressor.
    Every model in this project is a regressor, so patch the tags method
    directly rather than pin to older, less secure library versions.
    """
    if not hasattr(estimator, "__sklearn_tags__"):
        return
    original = estimator.__sklearn_tags__

    def patched():
        tags = original()
        if tags.estimator_type is None:
            tags.estimator_type = "regressor"
        return tags

    estimator.__sklearn_tags__ = patched

CHEMISTRY_NOTES = {
    "Lig": "Lignin resists thermal decomposition and shifts product distribution "
           "toward char rather than oxygenated liquid volatiles.",
    "Cel": "Cellulose depolymerizes readily into oxygenated compounds (e.g. "
           "levoglucosan, furans), a major direct source of bio-oil oxygen.",
    "Hem": "Hemicellulose decomposes at the lowest temperatures of the three "
           "biopolymers into acids and furans, also oxygen-rich.",
    "PT": "Higher pyrolysis temperature promotes secondary cracking/deoxygenation "
          "of vapor-phase oxygenates, generally lowering bio-oil O/C.",
    "HR": "Faster heating rates favor rapid volatile release before "
          "repolymerization, changing which oxygenated species end up in the "
          "condensed liquid.",
    "O%": "Feedstock oxygen content is the most direct chemical driver of "
          "product oxygen — more oxygen into the reactor, more comes out in "
          "the bio-oil.",
    "C%": "Feedstock carbon content sets the elemental baseline carried "
          "through into the bio-oil.",
    "VM": "Volatile matter reflects how much of the feedstock converts to "
          "vapor-phase (oil+gas) products rather than staying as char.",
    "Ash": "Inorganic ash content can catalyze secondary cracking and "
           "dehydration reactions that reduce bio-oil oxygen.",
    "Temp": "A secondary temperature parameter present in only a subset of "
            "source studies (44% missing) — its high importance likely "
            "reflects a study/dataset-source confound picked up via "
            "imputation rather than a clean causal signal; interpret with "
            "caution (see limitations note below).",
    "N%": "Feedstock nitrogen has a plausible secondary chemistry effect via "
          "co-produced nitrogenous compounds, but its ranking here may also "
          "partly reflect missingness patterns correlated with source study.",
    "Size": "Particle size affects intra-particle heat transfer and vapor "
            "residence time, influencing secondary reactions; also missing "
            "in ~50%+ of the underlying rows it's estimated from, so wider "
            "uncertainty applies.",
    "FC": "Fixed carbon reflects char-forming potential, inversely related "
          "to volatile (oil) yield.",
    "H%": "Feedstock hydrogen content influences the H/C and, indirectly, "
          "the O/C of the resulting oil.",
    "physics_hhv_dulong": "Physics-derived feature: fuel energy content (HHV) "
                          "estimated directly from the feedstock's ultimate "
                          "analysis via the Modified Dulong formula — a "
                          "combustion-engineering correlation, not a fitted "
                          "statistical feature.",
    "physics_conversion": "Physics-derived feature: composition-weighted "
                          "conversion fraction predicted by Arrhenius reaction "
                          "kinetics for cellulose/hemicellulose/lignin at this "
                          "row's actual PT and HR (Independent Parallel "
                          "Reactions kinetics, see ml/reports/physics.md).",
    "physics_char_fraction": "Physics-derived feature: 1 minus the kinetics-"
                          "predicted conversion — a mechanistic proxy for how "
                          "much feedstock stayed solid (char) rather than "
                          "devolatilizing into oil+gas vapor.",
    "physics_alpha_cellulose": "Physics-derived feature: Arrhenius-kinetics "
                          "predicted conversion fraction of the cellulose "
                          "pseudo-component alone at this row's PT/HR.",
    "physics_alpha_hemicellulose": "Physics-derived feature: Arrhenius-kinetics "
                          "predicted conversion fraction of the hemicellulose "
                          "pseudo-component alone at this row's PT/HR.",
    "physics_alpha_lignin": "Physics-derived feature: Arrhenius-kinetics "
                          "predicted conversion fraction of the lignin "
                          "pseudo-component alone at this row's PT/HR — lignin's "
                          "high activation energy makes this typically low, "
                          "consistent with lignin's known thermal resistance.",
    "Cel_Lig_ratio": "The cellulose-to-lignin balance reflects how much of "
                     "the feedstock decomposes into oxygenated volatiles vs. char.",
}


def main():
    X, y, _ = build_model_frame("O/C")
    model = joblib.load(MODELS_DIR / "O_C__best__v1.joblib")

    X_imputed = model[:-1].transform(X)
    inner = model.named_steps["model"]
    _patch_sklearn_tags(inner)

    explainer = shap.TreeExplainer(inner) if hasattr(inner, "get_booster") or \
        inner.__class__.__name__ in ("RandomForestRegressor", "XGBRegressor", "LGBMRegressor") \
        else shap.Explainer(inner, X_imputed)
    shap_values = explainer(X_imputed)

    fig = plt.figure(figsize=(9, 7))
    shap.summary_plot(shap_values, X_imputed, feature_names=ALL_FEATURE_COLS, show=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "shap_summary.png", dpi=150)
    plt.close(fig)

    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    importance_order = np.argsort(-mean_abs_shap)
    ranked_features = [ALL_FEATURE_COLS[i] for i in importance_order]

    top6 = ranked_features[:6]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    PartialDependenceDisplay.from_estimator(
        model, X, top6, ax=axes.flat[: len(top6)]
    )
    plt.tight_layout()
    plt.savefig(FIG_DIR / "partial_dependence.png", dpi=150)
    plt.close(fig)

    lines = ["# Interpretability Report — O/C Model (best: XGBoost)\n"]
    lines.append(
        "SHAP (SHapley Additive exPlanations) values quantify each feature's "
        "contribution to individual predictions; averaging their magnitude "
        "gives a global importance ranking. Partial dependence plots (PDP) "
        "show the model's average predicted O/C as each feature varies, "
        "holding others at their observed distribution.\n"
    )
    lines.append("## Feature importance ranking (mean |SHAP value|)\n")
    lines.append("| Rank | Feature | Mean |SHAP| |")
    lines.append("|---|---|---|")
    for rank, i in enumerate(importance_order, 1):
        lines.append(f"| {rank} | {ALL_FEATURE_COLS[i]} | {mean_abs_shap[i]:.4f} |")
    lines.append("")

    lines.append("## Chemistry interpretation of top features\n")
    for f in ranked_features[:6]:
        note = CHEMISTRY_NOTES.get(f, "Engineered ratio combining feedstock composition signals.")
        lines.append(f"- **{f}**: {note}")
    lines.append("")

    lines.append(
        "## Honesty note: importance ranking vs. correlation analysis\n\n"
        "The SHAP importance ranking above is dominated by features with "
        "substantial missingness (HR, Temp, Ash, Size — several >40% missing, "
        "see `eda_summary.md`), whereas the raw Pearson correlation analysis "
        "flagged FC, VM, H%, PT, and C% as most associated with O/C. This "
        "discrepancy is expected and worth stating plainly: with median "
        "imputation on a small, multi-study dataset, missingness itself can "
        "act as a proxy for which study/experimental setup a row came from, "
        "and the model can partly learn that confound rather than pure "
        "pyrolysis chemistry. PT — the single most mechanistically important "
        "process variable in pyrolysis literature — ranks low here (rank 13) "
        "despite a strong negative Pearson correlation (-0.445) with O/C, "
        "which is a sign this model's feature ranking should not be read as "
        "a definitive causal explanation. Treat both analyses together, and "
        "treat PT's true importance as understated by SHAP on this model."
    )

    lines.append("## Figures\n")
    lines.append("- `figures/shap_summary.png` — per-feature SHAP value distribution")
    lines.append("- `figures/partial_dependence.png` — PDP for top 6 features")

    (REPORTS_DIR / "interpretability.md").write_text("\n".join(lines))
    print("Interpretability report written.")


if __name__ == "__main__":
    main()
