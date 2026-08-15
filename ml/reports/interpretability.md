# Interpretability Report — O/C Model (best: XGBoost)

SHAP (SHapley Additive exPlanations) values quantify each feature's contribution to individual predictions; averaging their magnitude gives a global importance ranking. Partial dependence plots (PDP) show the model's average predicted O/C as each feature varies, holding others at their observed distribution.

## Feature importance ranking (mean |SHAP value|)

| Rank | Feature | Mean |SHAP| |
|---|---|---|
| 1 | HR | 0.0890 |
| 2 | Temp | 0.0778 |
| 3 | Ash | 0.0501 |
| 4 | N% | 0.0430 |
| 5 | Size | 0.0428 |
| 6 | VM | 0.0417 |
| 7 | Lig | 0.0287 |
| 8 | O% | 0.0261 |
| 9 | Cel_Lig_ratio | 0.0212 |
| 10 | FC | 0.0186 |
| 11 | H% | 0.0168 |
| 12 | Cel | 0.0115 |
| 13 | PT | 0.0103 |
| 14 | C% | 0.0081 |
| 15 | Hem | 0.0028 |
| 16 | O_C_feedstock | 0.0028 |
| 17 | H_C_feedstock | 0.0023 |
| 18 | Cel_Hem | 0.0023 |

## Chemistry interpretation of top features

- **HR**: Faster heating rates favor rapid volatile release before repolymerization, changing which oxygenated species end up in the condensed liquid.
- **Temp**: A secondary temperature parameter present in only a subset of source studies (44% missing) — its high importance likely reflects a study/dataset-source confound picked up via imputation rather than a clean causal signal; interpret with caution (see limitations note below).
- **Ash**: Inorganic ash content can catalyze secondary cracking and dehydration reactions that reduce bio-oil oxygen.
- **N%**: Feedstock nitrogen has a plausible secondary chemistry effect via co-produced nitrogenous compounds, but its ranking here may also partly reflect missingness patterns correlated with source study.
- **Size**: Particle size affects intra-particle heat transfer and vapor residence time, influencing secondary reactions; also missing in ~50%+ of the underlying rows it's estimated from, so wider uncertainty applies.
- **VM**: Volatile matter reflects how much of the feedstock converts to vapor-phase (oil+gas) products rather than staying as char.

## Honesty note: importance ranking vs. correlation analysis

The SHAP importance ranking above is dominated by features with substantial missingness (HR, Temp, Ash, Size — several >40% missing, see `eda_summary.md`), whereas the raw Pearson correlation analysis flagged FC, VM, H%, PT, and C% as most associated with O/C. This discrepancy is expected and worth stating plainly: with median imputation on a small, multi-study dataset, missingness itself can act as a proxy for which study/experimental setup a row came from, and the model can partly learn that confound rather than pure pyrolysis chemistry. PT — the single most mechanistically important process variable in pyrolysis literature — ranks low here (rank 13) despite a strong negative Pearson correlation (-0.445) with O/C, which is a sign this model's feature ranking should not be read as a definitive causal explanation. Treat both analyses together, and treat PT's true importance as understated by SHAP on this model.
## Figures

- `figures/shap_summary.png` — per-feature SHAP value distribution
- `figures/partial_dependence.png` — PDP for top 6 features