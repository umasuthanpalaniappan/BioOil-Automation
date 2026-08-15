# Preprocessing Report

- Rows before cleaning: 320
- Rows dropped for ultimate-analysis sum integrity (C%+H%+O%+N% outside [80,120]): 4
- Rows after integrity filter: 316

## Target-specific usable sample sizes

- **O/C**: 232 rows with a value
- **H/C**: 232 rows with a value
- **Cal_value**: 241 rows with a value
- **Oil_yield**: 189 rows with a value

## Engineered features

- `Cel_Lig_ratio`
- `O_C_feedstock`
- `H_C_feedstock`
- `Cel_Hem`

## O/C outlier note

O/C max = 3.57 is retained (see preprocessing.py docstring for rationale: not a data-integrity error, tree models are robust to it, and removing literature points from an already-small dataset is a bigger risk than keeping a legitimate high-oxygen sample).