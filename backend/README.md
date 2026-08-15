# Backend (FastAPI)

Serves the trained models from `ml/models/` behind a REST API.

## Setup

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # optional
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Requires `ml/models/` to already be populated — run the training pipeline
in `ml/` first (`python3 src/train.py`). By default the backend looks for
models at `../ml/models` relative to `backend/`; override with the
`MODELS_DIR` environment variable.

API docs: http://localhost:8000/docs

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service + model load status |
| `/predict` | POST | Single prediction (O/C + secondary targets + CI + flags) |
| `/compare-models` | POST | Predict with every available model side by side |
| `/batch-predict` | POST | CSV/Excel upload, bulk predictions |
| `/batch-predict/download` | POST | Same, returns a CSV file |
| `/models` | GET | Benchmark metrics for every trained model |
| `/diagnostics/{target}` | GET | Held-out test y_true/y_pred for plotting |
| `/explain` | POST | SHAP-based per-prediction explanation |
| `/feature-ranges` | GET | Training data min/max per feature |
| `/drift-check` | POST | Check a feedstock against training data ranges |
| `/export/pdf` | POST | PDF prediction report |
