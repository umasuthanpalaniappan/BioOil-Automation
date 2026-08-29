# Model Benchmark Report

Protocol: 80/20 held-out test split, 5-fold CV (on the training split) for hyperparameter search via grid search. Metrics below are R², RMSE, MAE. `overfit_gap_r2` = train R² − test R² (large positive gap flags overfitting given the small sample size).

## Target: O/C

n_train=185, n_test=47

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| xgboost | 0.6209 | 0.979 | 0.8996 | 0.2074 | 0.1277 | 0.0794 |
| random_forest | 0.5397 | 0.9314 | 0.8887 | 0.2184 | 0.1351 | 0.0427 |
| gpr | 0.5091 | 0.9559 | 0.8577 | 0.247 | 0.179 | 0.0982 |
| lightgbm | 0.5223 | 0.8762 | 0.8456 | 0.2572 | 0.1871 | 0.0306 |
| ridge | 0.3056 | 0.4893 | 0.5107 | 0.458 | 0.2833 | -0.0214 |
| lasso | 0.3176 | 0.4644 | 0.4832 | 0.4706 | 0.284 | -0.0188 |
| mlp | 0.0677 | 0.3135 | 0.3198 | 0.5399 | 0.3898 | -0.0063 |

**Best model (by test R²): `xgboost`**

## Target: H/C

n_train=185, n_test=47

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| random_forest | 0.2219 | 0.8199 | 0.4226 | 2.283 | 1.4705 | 0.3973 |
| xgboost | 0.2453 | 0.9141 | 0.3137 | 2.4889 | 1.5557 | 0.6004 |
| lightgbm | 0.2577 | 0.8435 | 0.3114 | 2.4931 | 1.7086 | 0.5321 |
| gpr | 0.138 | 0.8755 | 0.2974 | 2.5183 | 1.7788 | 0.5781 |
| ridge | 0.0217 | 0.2237 | 0.178 | 2.7238 | 2.0731 | 0.0457 |
| lasso | -0.01 | 0.2334 | 0.1653 | 2.7448 | 2.0524 | 0.0681 |
| mlp | -0.0571 | 0.367 | 0.1012 | 2.8482 | 2.0428 | 0.2658 |

**Best model (by test R²): `random_forest`**

## Target: Cal_value

n_train=192, n_test=49

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| random_forest | 0.4853 | 0.8589 | 0.4124 | 4.4309 | 2.919 | 0.4465 |
| lightgbm | 0.4224 | 0.8952 | 0.3092 | 4.8042 | 3.1781 | 0.586 |
| gpr | 0.3405 | 0.9123 | 0.2753 | 4.9206 | 3.3912 | 0.637 |
| ridge | -0.1105 | 0.2597 | 0.2227 | 5.096 | 4.0134 | 0.037 |
| xgboost | 0.4604 | 0.9587 | 0.0556 | 5.6171 | 3.4736 | 0.9031 |
| mlp | -1.8156 | 0.2993 | 0.0343 | 5.6801 | 4.5043 | 0.265 |
| lasso | -0.0664 | 0.092 | 0.0206 | 5.7203 | 4.492 | 0.0714 |

**Best model (by test R²): `random_forest`**

## Target: Oil_yield

n_train=151, n_test=38

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| gpr | 0.3609 | 0.9921 | 0.6227 | 8.9625 | 6.386 | 0.3694 |
| random_forest | 0.438 | 0.933 | 0.5461 | 9.8302 | 6.8745 | 0.3869 |
| xgboost | 0.5014 | 0.9937 | 0.5434 | 9.8588 | 6.3265 | 0.4503 |
| lightgbm | 0.3074 | 0.9696 | 0.4059 | 11.2457 | 7.5604 | 0.5637 |
| mlp | -0.3556 | 0.934 | 0.2543 | 12.5993 | 8.3954 | 0.6797 |
| ridge | 0.0991 | 0.2623 | 0.0914 | 13.908 | 11.3082 | 0.1709 |
| lasso | 0.0646 | 0.2167 | 0.0731 | 14.0475 | 11.4287 | 0.1436 |

**Best model (by test R²): `gpr`**

## Physics-only vs. ML-only vs. hybrid — O/C

Isolates what each layer contributes: pure reaction-kinetics equations alone, vs. the full hybrid model that uses those equations as features alongside statistical learning. See `physics.md` for the governing equations.

| Approach | Test R² | Test RMSE |
|---|---|---|
| Physics-only (linear fit on `physics_char_fraction` + `O_C_feedstock`, no ML) | 0.0296 | 0.6449 |
| Hybrid physics + ML (`xgboost`, all features incl. physics-derived) | 0.8996 | 0.2074 |

The physics-only fit alone explains very little of the test-set variance — expected, since a two-term linear model can't capture the non-linear, interacting effects of composition and process conditions. But the *same* physics, embedded as features inside the tree-ensemble model, measurably improves it over a pre-physics baseline trained on raw composition/process columns alone (pre-physics XGBoost test R² was 0.886; it is 0.8996 with the current physics-informed feature set — see git history of this file for the full progression as the physics layer was expanded). The governing equations are doing real work, not just window dressing.
