# BioOil-Automation

Machine learning pipeline and full-stack web application for predicting and
optimizing **biomass pyrolysis conditions to minimize bio-oil oxygen content
(O/C ratio)** — i.e., deoxygenation *during* pyrolysis rather than cleaning
up oxygen after the fact.

```
Biomass → [Pyrolysis reactor] → Crude bio-oil → [Separation/upgrading] → Clean bio-oil
                 ^^^^^^^^^^^^
           this project models this stage
```

Given biomass composition (cellulose/hemicellulose/lignin, proximate &
ultimate analysis) and reactor conditions (particle size, heating rate,
pyrolysis temperature), the model predicts the resulting bio-oil's O/C
ratio (and secondary properties: H/C, calorific value, oil yield), so
conditions can be tuned toward lower-oxygen bio-oil.

> Status: under active development. This README is updated as each phase lands.

## Project layout

```
BioOil-Automation/
├── data/               # source dataset (self-contained copy)
├── ml/                 # EDA, preprocessing, training, model registry
│   ├── notebooks/       or  ml/reports/  — EDA outputs
│   ├── src/             — reusable pipeline code
│   ├── models/          — versioned serialized models
│   └── reports/         — benchmark reports, SHAP plots
├── backend/             # FastAPI service serving the trained models
├── frontend/            # React (Vite + TS) application
└── docs/                # additional documentation
```

## Dataset

Source: compiled literature dataset on biomass pyrolysis (320 rows, `data`
sheet of `data/biooil_pyrolysis_dataset.xlsx`). See
[`ml/reports/eda_summary.md`](ml/reports/eda_summary.md) for missingness,
distributions, and correlation analysis, and
[`ml/reports/preprocessing.md`](ml/reports/preprocessing.md) for how
missing values and outliers were handled.

**Honesty note:** this is compiled multi-study literature data, not a
single clean experiment. Missing data is substantial in several columns,
and the usable sample for the primary target (O/C) is ~235 rows. Model
performance and confidence intervals in the app should be read with that
in mind — see the benchmark report for full details.

## Quickstart

Setup instructions land as each phase is completed (training pipeline →
backend → frontend → Docker). See `ml/README.md`, `backend/README.md`,
`frontend/README.md` once available.

## License

Academic project — see repository owner for reuse terms.
