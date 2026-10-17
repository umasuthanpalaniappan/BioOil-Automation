# Pyrolysis Advisor — frontend

A standalone, frontend-only product page and interactive demo for the Pyrolysis Advisor
(see `pyrolysis_advisor/`). Built with React, TypeScript and Vite.

This is **not** wired to a live backend — the demo in `src/data/demoData.ts` runs entirely
in the browser against sample scenarios taken from the project's own validation results
(`pyrolysis_advisor/results/tables/final_results.json`). For a live `/predict` API, see
`backend/` and the original `frontend/` app in the repo root.

## Run locally

```bash
npm install
npm run dev      # dev server
npm run build    # production build (type-checks, then builds)
npm run preview  # preview the production build
npm run lint     # oxlint
```
