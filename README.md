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

## Quickstart

```bash
# 1. Train the models (writes ml/models/*.joblib + ml/reports/benchmark_results.md)
cd ml && pip install -r requirements.txt
cd src && python3 eda.py && python3 preprocessing.py && python3 train.py

# 2. Start the backend
cd ../../backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000   # http://localhost:8000/docs

# 3. Start the frontend (separate terminal)
cd ../frontend
npm install
cp .env.example .env
npm run dev   # http://localhost:5173
```

Or via Docker, once models are trained locally:

```bash
docker-compose up --build
```

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

## Physics-informed modeling

Beyond a purely statistical fit, the models are fed physics-derived
features computed from actual pyrolysis reaction kinetics (Arrhenius
Independent Parallel Reactions for cellulose/hemicellulose/lignin,
integrated against each row's real heating rate and process temperature)
and a combustion-engineering energy correlation (Modified Dulong formula).
Full equations, literature citations, and a physics-only vs. ML-only vs.
hybrid comparison: [`ml/reports/physics.md`](ml/reports/physics.md) and
[`ml/reports/benchmark_results.md`](ml/reports/benchmark_results.md).

**Honesty note:** this is compiled multi-study literature data, not a
single clean experiment. Missing data is substantial in several columns,
and the usable sample for the primary target (O/C) is ~235 rows. Model
performance and confidence intervals in the app should be read with that
in mind — see the benchmark report for full details.

## Quickstart

Setup instructions land as each phase is completed (training pipeline →
backend → frontend → Docker). See `ml/README.md`, `backend/README.md`,
`frontend/README.md` once available.

## Application features

- Real-time O/C prediction with 95% confidence interval
- Predicted-vs-actual & residual diagnostics, live PT sensitivity sweep
- Scenario simulation to find feedstock/condition combinations that minimize O/C
- Rule-based physics validation (biomass composition sums, training-regime bounds)
- Batch CSV/Excel upload with downloadable results
- Model comparison sandbox (RF vs XGBoost vs LightGBM vs GPR vs linear vs MLP)
- Per-prediction SHAP explainability in pyrolysis-chemistry terms
- Data drift detection against training feature ranges
- PDF/CSV export

## Limitations (read before trusting any number this app gives you)

- Training sample is small (~230 rows for the primary O/C target) and compiled
  from multiple literature studies with heterogeneous reporting — not one
  controlled experiment. Treat R² and confidence intervals as directional, not
  as guarantees.
- A handful of rows had internally inconsistent ultimate-analysis values
  (e.g. elemental percentages not summing near 100%) and were dropped; see
  `ml/reports/preprocessing.md`.
- Missing features are median-imputed inside the training pipeline, which is a
  pragmatic choice for a small, sparse dataset, not a claim of full data
  recovery.
- Predictions outside the training data's PT/HR/composition ranges are
  extrapolations — the app flags these but cannot make them reliable.

## License

Academic project — see repository owner for reuse terms.
