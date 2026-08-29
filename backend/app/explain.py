"""Per-prediction SHAP explanations translated into pyrolysis-chemistry language."""
import numpy as np

from app.model_registry import registry
from app.schemas import ExplainResponse, ExplanationItem

CHEMISTRY_NOTES = {
    "Lig": "higher lignin resists thermal decomposition and tends to shift "
           "product distribution toward char, indirectly affecting bio-oil oxygen content",
    "Cel": "cellulose depolymerizes readily into oxygenated compounds (e.g. levoglucosan), "
           "raising bio-oil oxygen content",
    "Hem": "hemicellulose decomposes at lower temperatures into acids and furans, "
           "contributing oxygenated species to the bio-oil",
    "PT": "higher pyrolysis temperature promotes secondary cracking of oxygenated "
          "vapors, generally lowering bio-oil O/C",
    "HR": "faster heating rates favor volatile release before repolymerization, "
          "influencing oxygen retention in the liquid product",
    "VM": "volatile matter content reflects how much of the feedstock converts to "
          "vapor-phase (oil+gas) products during pyrolysis",
    "Ash": "higher ash (inorganic content) can catalyze secondary cracking and "
           "dehydration reactions that reduce bio-oil oxygen",
    "FC": "fixed carbon reflects char-forming potential, inversely related to "
          "volatile (oil) yield",
    "C%": "feedstock carbon content sets the baseline elemental composition "
          "carried into the bio-oil",
    "H%": "feedstock hydrogen content influences the H/C and, indirectly, O/C "
          "of the resulting oil",
    "O%": "feedstock oxygen content is the most direct driver of bio-oil oxygen — "
          "more oxygen in, more oxygen out",
    "N%": "feedstock nitrogen has a secondary effect via co-produced nitrogenous compounds",
    "Size": "particle size affects heat transfer within the biomass particle, "
            "influencing vapor residence time and secondary reactions",
    "Temp": "secondary temperature parameter reflects additional thermal severity "
            "in some source studies (e.g. vapor residence temperature)",
    "Cel_Lig_ratio": "the cellulose-to-lignin balance reflects how much of the "
                     "feedstock decomposes into oxygenated volatiles vs. char",
    "O_C_feedstock": "the feedstock's own O/C ratio is a direct chemical proxy "
                     "for how oxygenated the resulting bio-oil is likely to be",
    "H_C_feedstock": "the feedstock's H/C ratio relates to its degree of "
                     "saturation and hydrogen availability during pyrolysis",
    "Cel_Hem": "total holocellulose (cellulose+hemicellulose) represents the "
               "volatile-prone fraction of the feedstock",
    "physics_hhv_dulong": "physics-derived feature: fuel energy content (HHV) "
                          "estimated from ultimate analysis via the Modified "
                          "Dulong combustion-engineering formula",
    "physics_conversion": "physics-derived feature: composition-weighted "
                          "conversion fraction predicted by Arrhenius reaction "
                          "kinetics for cellulose/hemicellulose/lignin at this "
                          "prediction's actual PT and HR",
    "physics_char_fraction": "physics-derived feature: 1 minus the kinetics-"
                          "predicted conversion — a mechanistic proxy for how "
                          "much feedstock would stay solid (char) rather than "
                          "devolatilize into oil+gas vapor",
    "physics_alpha_cellulose": "physics-derived feature: Arrhenius-kinetics "
                          "predicted conversion of the cellulose pseudo-component "
                          "alone at this prediction's PT/HR",
    "physics_alpha_hemicellulose": "physics-derived feature: Arrhenius-kinetics "
                          "predicted conversion of the hemicellulose "
                          "pseudo-component alone at this prediction's PT/HR",
    "physics_alpha_lignin": "physics-derived feature: Arrhenius-kinetics "
                          "predicted conversion of the lignin pseudo-component "
                          "alone — lignin's high activation energy keeps this "
                          "typically low, consistent with its known thermal "
                          "resistance",
    "physics_cellulose_volatile_fraction": "physics-derived feature: from the "
                          "competitive Broido-Shafizadeh cellulose reaction scheme, "
                          "the predicted fraction of cellulose converting to "
                          "oxygenated volatile products (e.g. levoglucosan-type "
                          "compounds) rather than char",
    "physics_cellulose_chargas_fraction": "physics-derived feature: the "
                          "competing char+gas-forming pathway from the same "
                          "Broido-Shafizadeh cellulose scheme — higher values mean "
                          "less oxygenated liquid product from cellulose specifically",
    "physics_tar_cracking_severity": "physics-derived feature: a dimensionless "
                          "index (secondary tar-cracking rate constant x residence "
                          "time) for how much primary pyrolysis vapor undergoes "
                          "further gas-phase deoxygenation reactions — the "
                          "mechanistic reason higher temperature tends to lower "
                          "bio-oil O/C",
    "physics_alpha_cellulose_ash_adjusted": "physics-derived feature: cellulose "
                          "conversion re-computed with an ash-catalysis correction "
                          "to its activation energy, reflecting how alkali/alkaline-"
                          "earth metals in ash catalytically accelerate cellulose "
                          "decomposition",
    "physics_residence_time_s": "physics-derived feature: estimated time (s) for "
                          "the bed to reach the process temperature at the given "
                          "heating rate — a proxy for how long vapors are exposed "
                          "to secondary reactions",
}


def explain_prediction(feature_dict: dict, model_name: str = "best") -> ExplainResponse:
    import shap

    model = registry.oc_models.get(model_name) or registry.oc_models["best"]
    X = registry.to_feature_frame(feature_dict)
    X_imputed = model[:-1].transform(X) if len(model.steps) > 1 else X.values

    inner = model.named_steps["model"]
    try:
        explainer = shap.Explainer(inner, feature_names=registry.feature_columns)
        sv = explainer(X_imputed)
        shap_values = np.array(sv.values[0])
        base_value = float(np.array(sv.base_values).reshape(-1)[0])
    except Exception:
        # Fallback for model types SHAP's fast path doesn't support directly.
        background = np.nan_to_num(X_imputed)
        explainer = shap.KernelExplainer(inner.predict, background)
        shap_values = np.array(explainer.shap_values(X_imputed, nsamples=100))[0]
        base_value = float(explainer.expected_value)

    pred = float(model.predict(X)[0])

    order = np.argsort(-np.abs(shap_values))[:6]
    items = []
    for i in order:
        fname = registry.feature_columns[i]
        val = float(X.iloc[0, i]) if not np.isnan(X.iloc[0, i]) else float(X_imputed[0, i])
        direction = "increases" if shap_values[i] > 0 else "decreases"
        note = CHEMISTRY_NOTES.get(fname, "affects product distribution during pyrolysis")
        items.append(ExplanationItem(
            feature=fname,
            value=round(val, 3),
            shap_value=round(float(shap_values[i]), 4),
            plain_language=f"{fname}={val:.2f} {direction} predicted O/C "
                            f"(contribution {shap_values[i]:+.3f}); {note}.",
        ))

    top = items[0].feature if items else "the input features"
    summary = (
        f"Predicted O/C = {pred:.3f}. The strongest driver in this prediction is "
        f"{top}. See top_features for the full ranked breakdown."
    )
    return ExplainResponse(prediction=pred, base_value=base_value, top_features=items, summary=summary)
