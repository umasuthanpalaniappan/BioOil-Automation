# Model Benchmark Report

Protocol: 80/20 held-out test split, 5-fold CV (on the training split) for hyperparameter search via grid search. Metrics below are R², RMSE, MAE. `overfit_gap_r2` = train R² − test R² (large positive gap flags overfitting given the small sample size).

## Target: O/C

n_train=185, n_test=47

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| xgboost | 0.6339 | 0.9786 | 0.886 | 0.221 | 0.1298 | 0.0926 |
| lightgbm | 0.5067 | 0.8692 | 0.8439 | 0.2587 | 0.194 | 0.0253 |
| random_forest | 0.5209 | 0.7676 | 0.8364 | 0.2648 | 0.1355 | -0.0688 |
| gpr | 0.5899 | 0.9821 | 0.8327 | 0.2677 | 0.1742 | 0.1494 |
| mlp | 0.259 | 0.6917 | 0.6216 | 0.4027 | 0.3158 | 0.0701 |
| lasso | 0.3075 | 0.4499 | 0.4935 | 0.4659 | 0.2836 | -0.0436 |
| ridge | 0.3089 | 0.4049 | 0.4463 | 0.4871 | 0.3086 | -0.0414 |

**Best model (by test R²): `xgboost`**

## Target: H/C

n_train=185, n_test=47

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| lightgbm | 0.2001 | 0.789 | 0.3937 | 2.3393 | 1.4893 | 0.3953 |
| gpr | 0.19 | 0.8783 | 0.3868 | 2.3527 | 1.6633 | 0.4915 |
| random_forest | 0.2482 | 0.813 | 0.3864 | 2.3533 | 1.5121 | 0.4266 |
| xgboost | 0.2149 | 0.9022 | 0.2999 | 2.5138 | 1.5699 | 0.6023 |
| ridge | 0.0121 | 0.1891 | 0.1159 | 2.8249 | 2.0553 | 0.0732 |
| lasso | -0.0211 | 0.0234 | 0.0223 | 2.9707 | 2.1146 | 0.0011 |
| mlp | -0.1148 | 0.7731 | -0.1511 | 3.2234 | 2.0659 | 0.9242 |

**Best model (by test R²): `lightgbm`**

## Target: Cal_value

n_train=192, n_test=49

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| random_forest | 0.469 | 0.8546 | 0.4254 | 4.3816 | 2.9331 | 0.4292 |
| lightgbm | 0.4025 | 0.8737 | 0.3951 | 4.4955 | 2.9431 | 0.4786 |
| gpr | 0.4044 | 0.8963 | 0.319 | 4.7699 | 3.1662 | 0.5773 |
| xgboost | 0.4809 | 0.96 | 0.186 | 5.215 | 3.2365 | 0.774 |
| ridge | -0.1648 | 0.2339 | 0.1829 | 5.2249 | 4.1084 | 0.051 |
| lasso | -0.0857 | 0.0771 | 0.0216 | 5.7174 | 4.487 | 0.0555 |
| mlp | -4.6107 | -0.0953 | -0.3717 | 6.7696 | 5.085 | 0.2764 |

**Best model (by test R²): `random_forest`**

## Target: Oil_yield

n_train=151, n_test=38

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| gpr | 0.449 | 0.9922 | 0.6299 | 8.8765 | 6.0616 | 0.3623 |
| xgboost | 0.5129 | 0.9937 | 0.6171 | 9.0289 | 6.2321 | 0.3766 |
| random_forest | 0.4455 | 0.9341 | 0.5317 | 9.9851 | 7.0175 | 0.4024 |
| lightgbm | 0.3087 | 0.8736 | 0.4995 | 10.3222 | 7.7043 | 0.3741 |
| ridge | 0.0461 | 0.205 | 0.0999 | 13.8426 | 11.2908 | 0.1051 |
| lasso | 0.0428 | 0.1819 | 0.0852 | 13.9555 | 11.2192 | 0.0967 |
| mlp | -0.0355 | 0.4391 | 0.0753 | 14.0305 | 11.9145 | 0.3638 |

**Best model (by test R²): `gpr`**
