# EDA Summary — Bio-Oil Pyrolysis Dataset

Raw shape: 320 rows x 19 columns (after dropping empty `Gas_yield`/`Char_yield` columns).

## Missingness by column

|           |   missing |   missing_pct |   n_available |
|:----------|----------:|--------------:|--------------:|
| Hem       |       170 |          53.1 |           150 |
| Cel       |       167 |          52.2 |           153 |
| Vis       |       166 |          51.9 |           154 |
| Lig       |       154 |          48.1 |           166 |
| Temp      |       141 |          44.1 |           179 |
| Oil_yield |       129 |          40.3 |           191 |
| H/C       |        85 |          26.6 |           235 |
| O/C       |        85 |          26.6 |           235 |
| Cal_value |        76 |          23.8 |           244 |
| VM        |        37 |          11.6 |           283 |
| FC        |        37 |          11.6 |           283 |
| N%        |        21 |           6.6 |           299 |
| C%        |        20 |           6.2 |           300 |
| H%        |        20 |           6.2 |           300 |
| O%        |        20 |           6.2 |           300 |
| HR        |        18 |           5.6 |           302 |
| Ash       |        15 |           4.7 |           305 |
| Size      |         5 |           1.6 |           315 |
| PT        |         1 |           0.3 |           319 |

## Primary target: O/C

- Non-null count: 235 / 320 rows (73.4%)
- Mean: 0.337, Median: 0.110, Std: 0.531
- Min: 0.030, Max: 3.570
- IQR upper fence: 0.615 — 32 value(s) above it (max=3.57); see preprocessing report for the decision on whether these are kept.

## Descriptive statistics (available rows per column)

|           |   count |   mean |   std |    min |    25% |    50% |    75% |    max |
|:----------|--------:|-------:|------:|-------:|-------:|-------:|-------:|-------:|
| Cel       |     153 |  37.18 | 10.96 |   8    |  30.71 |  37.92 |  43.1  |  69    |
| Hem       |     150 |  27.68 | 11.91 |   3.47 |  19.8  |  26.55 |  32.1  |  79.5  |
| Lig       |     166 |  24.14 | 11.4  |   2.7  |  17    |  23.04 |  29.08 |  79    |
| VM        |     283 |  72.28 | 14.21 |   0.6  |  70.7  |  74.9  |  80.58 |  92.86 |
| Ash       |     305 |   5.09 |  4.96 |   0.1  |   1.75 |   4.14 |   6.9  |  45.13 |
| FC        |     283 |  17.74 | 12.03 |   0.5  |  12.76 |  16    |  18.03 |  75.4  |
| C%        |     300 |  49.2  |  8.52 |  14.97 |  44.8  |  48.89 |  52.33 |  85.7  |
| H%        |     300 |   8.09 | 31.42 |   1    |   5.71 |   6.1  |   6.64 | 550    |
| O%        |     300 |  41.14 |  9.17 |   0.19 |  37.99 |  42.26 |  45.98 |  75.68 |
| N%        |     299 |   2.09 |  3.32 |   0    |   0.44 |   0.99 |   2.67 |  40    |
| Size      |     315 |   1.41 |  2.8  |   0.08 |   0.43 |   0.75 |   1.3  |  42    |
| HR        |     302 |  44.65 | 89.16 |   1.9  |   7    |  20    |  35    | 540    |
| PT        |     319 | 496.07 | 93.37 | 100    | 450    | 500    | 550    | 800    |
| Temp      |     179 |  42.65 | 61.64 |  10    |  25    |  40    |  40    | 550    |
| O/C       |     235 |   0.34 |  0.53 |   0.03 |   0.09 |   0.11 |   0.3  |   3.57 |
| H/C       |     235 |   4.28 |  3.08 |   0    |   1.97 |   3.47 |   5.66 |  17.5  |
| Cal_value |     244 |  28.25 |  6.35 |   3.02 |  24.66 |  28.52 |  32.81 |  43.54 |
| Oil_yield |     191 |  40.85 | 14.67 |   6.8  |  31.94 |  43.15 |  49.91 |  78.07 |

## Correlation with O/C (Pearson, pairwise-complete)

|           |    O/C |
|:----------|-------:|
| FC        |  0.569 |
| VM        | -0.507 |
| H%        | -0.477 |
| PT        | -0.445 |
| C%        |  0.315 |
| Hem       | -0.301 |
| Ash       |  0.3   |
| N%        | -0.227 |
| Lig       |  0.197 |
| O%        | -0.173 |
| Oil_yield | -0.153 |
| HR        | -0.123 |
| H/C       | -0.116 |
| Cel       |  0.108 |
| Cal_value | -0.091 |
| Size      | -0.079 |
| Temp      | -0.007 |

Cross-check note: the source workbook's `Table 3` sheet reports its own pairwise Pearson coefficients (different variable naming: HTT=PT, FR=O/C-related ratio, etc.) computed over a possibly different row subset. Directional agreement (e.g. PT and O/C negatively associated) was used as a sanity check rather than an exact numeric match, since the row sets and exact target definitions are not guaranteed identical.

## Figures

- `figures/missingness_heatmap.png`
- `figures/O_C_distribution.png`
- `figures/correlation_heatmap.png`
- `figures/key_relationships.png`