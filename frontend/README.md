# Frontend (React + Vite + TypeScript)

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL if backend isn't on localhost:8000
```

## Run (dev)

```bash
npm run dev
```

## Build (production)

```bash
npm run build
npm run preview
```

## Features

- **Predict** — real-time O/C prediction with confidence interval, physics
  validation, drift check, SHAP explainability, PDF export.
- **Dashboard** — predicted-vs-actual scatter and residual plots from the
  held-out test set, plus a live pyrolysis-temperature sensitivity sweep.
- **Scenario Simulation** — grid-search over PT/HR/Lignin ranges to find the
  combination that minimizes predicted O/C.
- **Model Comparison** — side-by-side predictions across all trained models.
- **Batch Processing** — CSV/Excel upload, bulk predictions, CSV download.

Requires the backend running (see `../backend/README.md`).
