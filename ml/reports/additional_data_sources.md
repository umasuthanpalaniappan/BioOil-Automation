# Additional Data — What Was Found, and What's Blocked

Per review feedback to "take more data and explore," this documents the
search for supplementary pyrolysis data and its outcome, honestly.

## What I found

Searching the pyrolysis kinetics/ML literature surfaced a very likely
match for the **original source** of this project's dataset:

> **"Machine learning prediction of the yield and oxygen content of bio-oil
> via biomass characteristics and pyrolysis conditions"**, *Energy*
> journal, 2022 (ScienceDirect ID `S0360544222012233`).

Evidence this is the same (or a closely related) source:
- Same feature set exactly: cellulose/hemicellulose/lignin composition,
  ultimate + proximate analysis, particle size, heating rate, pyrolysis
  temperature.
- Same target variables: bio-oil yield, viscosity, O/C, H/C.
- Their reported O/C model performance (**R² = 0.895**, "Ultimate-O
  model") is almost identical to this project's own result (**R² =
  0.891**, XGBoost with the physics-informed features) — strong external
  validation that our result is in the right range for this exact
  prediction task, not an artifact of this particular pipeline.

A second candidate, a Mendeley Data repository (`data.mendeley.com/datasets/bx88ymgbbv/1`),
covers 34 biomasses with a similar variable set and may contain additional
usable rows beyond what's in the current spreadsheet.

## What's blocked, and why

This project is developed inside a sandboxed cloud environment with a
network allowlist — `sciencedirect.com` and `data.mendeley.com` are both
blocked at the network level here, so I could not fetch either dataset's
actual data table (Supplementary Table S1 for the Energy paper; the CSV
export for the Mendeley set) automatically.

## Next step (needs your access, not mine)

If you or a teammate has university/library access:
1. Search the *Energy* journal paper above (DOI resolvable via
   `S0360544222012233`) and download its **Supplementary Material** —
   likely a Table S1 with the underlying row-level data.
2. Visit `data.mendeley.com/datasets/bx88ymgbbv/1` directly in a normal
   browser and download the dataset (Mendeley Data is typically open
   access, no institutional login needed).
3. Send either file back and I will: check its columns against this
   project's schema, merge any genuinely new rows (with the same
   integrity checks already applied to the current data — see
   `preprocessing.md`), and retrain.

**Not pursued:** Phyllis2 (`phyllis.nl`), a public biomass composition
database, was also considered — it has extensive proximate/ultimate
analysis data for many feedstocks, but it does **not** include pyrolysis
product properties (O/C of the resulting bio-oil, yield, etc.), so on its
own it can't extend the target-side of this dataset — only the
feedstock-characterization side, without matching experiment outcomes.
