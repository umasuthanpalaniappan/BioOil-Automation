# Physics-Aware ML for Bio-Oil Pyrolysis (Pyrolysis Advisor)

Umasuthan Palaniappan, 24AIM201 Mechanics and Fluidized Systems, guided by Dr. Akhil Mohan.

## What this project does
1. **Part A, honest benchmark:** shows how random train/test splits inflate ML accuracy for bio-oil yield and O/C, including a hidden near-duplicate problem in the yield data.
2. **Part B, Pyrolysis Advisor:** physics-aware models (heat transfer, kinetics, molar ratios, physical constraints) that recommend reactor settings for more oil with less oxygen, with honest uncertainty, an "outside my knowledge" check and calibration from 1 to 2 experiments.

## Data
- `data_raw/D1_data1.xlsx`: "data" sheet = Zhang et al. 2022, Fuel 312, 122812 (bio-oil O/C).
- `data_raw/D3_pascarella_zenodo.xlsx`: Pascarella et al. 2025, Fuel 394, 135000, Zenodo copy 10.5281/zenodo.19205977 (bio-liquid yield).

## Documents
- `docs/BioOil_Pyrolysis_Advisor_Report.docx`: full project report (10 pages)
- `docs/BioOil_Pyrolysis_Advisor.pptx`: 5-slide presentation

## Run order (from this folder: `pip install -r requirements.txt`, then `python src/<script>.py`)
| Step | Script | Output |
|---|---|---|
| 1 | `src/01_clean.py` | `data_clean/*.csv`, `results/tables/cleaning_log.json` |
| 2 | `src/02_leakage_study.py` (about 15 min) | `results/tables/leakage_study_*.csv` |
| 3 | `src/04_figures_A.py` | Part A figures |
| 4 | `src/05_oc_physics_model.py`, `src/06_yield_hybrid.py` | model selection tables |
| 5 | `src/07_final_advisor.py` (about 5 min) | final models, `results/tables/final_results.json`, advisor CSVs |
| 6 | `src/08_figures_B.py` | Part B figures |
`src/03_advisor.py` is an earlier version kept for reference (GPR-only models).

## Key results
| | Random split | Grouped by biomass (new biomass) |
|---|---|---|
| Yield R2 (XGBoost) | 0.66 | -0.18 (0.23 if near-duplicates are missed) |
| O/C R2, log scale (GPR) | 0.63 | 0.23 (final blend 0.26) |

- Yield optimum predicted at 525 C (41.6 wt%), O/C falls 0.28 to 0.21 from 350 to 700 C.
- With 1 or 2 experiments on a new biomass, yield error drops to 5.3 or 4.2 wt% (vs about 8 wt% without).

## Using the advisor
`advise(C, H, O, N, PS, measured=None)` in `src/07_final_advisor.py` returns a table of temperature x heating-rate settings with predicted yield, O/C, Pareto flags and a balanced score, plus an in-domain check. `measured` takes a list of `(T, HR, yield)` from real experiments.
