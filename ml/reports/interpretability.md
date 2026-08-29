# Interpretability Report — O/C Model (best: XGBoost)

SHAP (SHapley Additive exPlanations) values quantify each feature's contribution to individual predictions; averaging their magnitude gives a global importance ranking. Partial dependence plots (PDP) show the model's average predicted O/C as each feature varies, holding others at their observed distribution.

## Feature importance ranking (mean |SHAP value|)

| Rank | Feature | Mean |SHAP| |
|---|---|---|
| 1 | Temp | 0.0840 |
| 2 | HR | 0.0777 |
| 3 | Ash | 0.0476 |
| 4 | Size | 0.0369 |
| 5 | VM | 0.0327 |
| 6 | N% | 0.0307 |
| 7 | Cel_Lig_ratio | 0.0249 |
| 8 | Lig | 0.0248 |
| 9 | physics_cellulose_chargas_fraction | 0.0245 |
| 10 | O% | 0.0202 |
| 11 | FC | 0.0181 |
| 12 | physics_alpha_cellulose_ash_adjusted | 0.0163 |
| 13 | Cel | 0.0134 |
| 14 | H% | 0.0129 |
| 15 | physics_conversion | 0.0120 |
| 16 | physics_hhv_dulong | 0.0068 |
| 17 | C% | 0.0066 |
| 18 | physics_cellulose_volatile_fraction | 0.0062 |
| 19 | O_C_feedstock | 0.0047 |
| 20 | Cel_Hem | 0.0037 |
| 21 | Hem | 0.0023 |
| 22 | physics_alpha_lignin | 0.0019 |
| 23 | physics_residence_time_s | 0.0008 |
| 24 | PT | 0.0006 |
| 25 | physics_tar_cracking_severity | 0.0005 |
| 26 | H_C_feedstock | 0.0003 |
| 27 | physics_alpha_cellulose | 0.0001 |
| 28 | physics_alpha_hemicellulose | 0.0000 |
| 29 | physics_char_fraction | 0.0000 |

## Chemistry interpretation of top features

- **Temp**: A secondary temperature parameter present in only a subset of source studies (44% missing) — its high importance likely reflects a study/dataset-source confound picked up via imputation rather than a clean causal signal; interpret with caution (see limitations note below).
- **HR**: Faster heating rates favor rapid volatile release before repolymerization, changing which oxygenated species end up in the condensed liquid.
- **Ash**: Inorganic ash content can catalyze secondary cracking and dehydration reactions that reduce bio-oil oxygen.
- **Size**: Particle size affects intra-particle heat transfer and vapor residence time, influencing secondary reactions; also missing in ~50%+ of the underlying rows it's estimated from, so wider uncertainty applies.
- **VM**: Volatile matter reflects how much of the feedstock converts to vapor-phase (oil+gas) products rather than staying as char.
- **N%**: Feedstock nitrogen has a plausible secondary chemistry effect via co-produced nitrogenous compounds, but its ranking here may also partly reflect missingness patterns correlated with source study.

## Honesty note: importance ranking vs. correlation analysis

The SHAP importance ranking above is dominated by features with substantial missingness (HR, Temp, Ash, Size — several >40% missing, see `eda_summary.md`), whereas the raw Pearson correlation analysis flagged FC, VM, H%, PT, and C% as most associated with O/C. This discrepancy is expected and worth stating plainly: with median imputation on a small, multi-study dataset, missingness itself can act as a proxy for which study/experimental setup a row came from, and the model can partly learn that confound rather than pure pyrolysis chemistry. PT — the single most mechanistically important process variable in pyrolysis literature — ranks low here (rank 24 of 29) despite a strong negative Pearson correlation (-0.445) with O/C. Its influence is not absent from the model, though: several physics-informed features derived directly from PT (physics_conversion, physics_char_fraction, physics_cellulose_volatile_fraction/chargas_fraction, physics_tar_cracking_severity, physics_alpha_cellulose_ash_adjusted, physics_residence_time_s — all computed by integrating reaction kinetics up to each row's actual PT) rank well above raw PT itself, several in the top half of the table. Read together, this suggests the model is drawing on temperature's effect mainly *through* the physics-informed conversion/cracking features rather than the raw PT column directly — which is arguably the more chemically faithful signal, since it's temperature's effect on reaction extent that actually drives O/C, not temperature alone. Still, this ranking should not be read as a definitive causal explanation — treat it alongside the raw correlation analysis, not as a replacement for it.
## Figures

- `figures/shap_summary.png` — per-feature SHAP value distribution
- `figures/partial_dependence.png` — PDP for top 6 features