# ML Pipeline

## Setup

```bash
cd ml
pip install -r requirements.txt   # or use the root backend/requirements.txt, same deps
```

## Run the pipeline

```bash
cd src
python3 eda.py            # writes ml/reports/eda_summary.md + figures
python3 preprocessing.py  # writes ml/reports/preprocessing.md
python3 train.py          # trains all models, writes ml/models/*.joblib +
                           # ml/reports/benchmark_results.{json,md}
```

## Layout

- `src/data_loader.py` — raw data loading + column cleanup
- `src/eda.py` — exploratory analysis
- `src/preprocessing.py` — integrity filtering, imputation strategy, feature engineering
- `src/train.py` — model training, hyperparameter search, benchmarking
- `models/` — versioned serialized models (`{target}__{model}__v1.joblib`) +
  `feature_columns.json` + `feature_ranges.json` (used by the backend for
  drift detection)
- `reports/` — EDA summary, preprocessing report, benchmark report, figures

See `reports/eda_summary.md`, `reports/preprocessing.md`, and
`reports/benchmark_results.md` for the full writeups.
