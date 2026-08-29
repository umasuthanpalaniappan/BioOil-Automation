# Model Benchmark Report

Protocol: 80/20 held-out test split, 5-fold CV (on the training split) for hyperparameter search via grid search. Metrics below are R², RMSE, MAE. `overfit_gap_r2` = train R² − test R² (large positive gap flags overfitting given the small sample size).

## Target: O/C

n_train=185, n_test=47

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| xgboost | 0.6374 | 0.9771 | 0.8915 | 0.2157 | 0.126 | 0.0856 |
| random_forest | 0.5274 | 0.9271 | 0.8866 | 0.2205 | 0.1327 | 0.0405 |
| gpr | 0.4887 | 0.9549 | 0.8621 | 0.2431 | 0.1756 | 0.0928 |
| lightgbm | 0.5431 | 0.8966 | 0.8531 | 0.2509 | 0.1841 | 0.0435 |
| lasso | 0.3023 | 0.452 | 0.4982 | 0.4638 | 0.2807 | -0.0462 |
| ridge | 0.2963 | 0.4055 | 0.4478 | 0.4865 | 0.3088 | -0.0423 |
| mlp | -0.0166 | 0.2113 | 0.2039 | 0.5841 | 0.4029 | 0.0074 |

**Best model (by test R²): `xgboost`**

## Target: H/C

n_train=185, n_test=47

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| xgboost | 0.1939 | 0.8895 | 0.4815 | 2.1633 | 1.4854 | 0.408 |
| random_forest | 0.2319 | 0.8773 | 0.4645 | 2.1986 | 1.4924 | 0.4128 |
| lightgbm | 0.2832 | 0.9382 | 0.3608 | 2.4019 | 1.6686 | 0.5774 |
| gpr | 0.159 | 0.8811 | 0.3238 | 2.4705 | 1.7658 | 0.5573 |
| ridge | 0.005 | 0.2032 | 0.1391 | 2.7875 | 2.1306 | 0.0641 |
| lasso | -0.0211 | 0.0234 | 0.0223 | 2.9707 | 2.1146 | 0.0011 |
| mlp | -0.0353 | 0.1433 | -0.1027 | 3.1548 | 2.3731 | 0.246 |

**Best model (by test R²): `xgboost`**

## Target: Cal_value

n_train=192, n_test=49

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| random_forest | 0.4827 | 0.8579 | 0.424 | 4.3867 | 2.8587 | 0.4339 |
| gpr | 0.3307 | 0.8873 | 0.274 | 4.925 | 3.3176 | 0.6133 |
| ridge | -0.1297 | 0.2493 | 0.2418 | 5.0329 | 3.9698 | 0.0075 |
| lightgbm | 0.4321 | 0.9505 | 0.1437 | 5.3486 | 3.4357 | 0.8068 |
| xgboost | 0.4703 | 0.9599 | 0.0739 | 5.5625 | 3.2859 | 0.886 |
| lasso | -0.0664 | 0.092 | 0.0206 | 5.7203 | 4.492 | 0.0714 |
| mlp | -8.6051 | 0.0484 | -0.3911 | 6.8174 | 5.3233 | 0.4395 |

**Best model (by test R²): `random_forest`**

## Target: Oil_yield

n_train=151, n_test=38

| Model | CV R² (train folds) | Train R² | Test R² | Test RMSE | Test MAE | Overfit gap |
|---|---|---|---|---|---|---|
| gpr | 0.3691 | 0.9921 | 0.6138 | 9.0676 | 6.2076 | 0.3783 |
| xgboost | 0.4945 | 0.9937 | 0.5916 | 9.3248 | 5.9567 | 0.4021 |
| random_forest | 0.4502 | 0.9329 | 0.5553 | 9.7295 | 6.8218 | 0.3776 |
| lightgbm | 0.2977 | 0.8763 | 0.3779 | 11.5081 | 8.1228 | 0.4984 |
| ridge | 0.0693 | 0.2321 | 0.0752 | 14.0315 | 11.307 | 0.1569 |
| lasso | 0.0605 | 0.2005 | 0.0577 | 14.1635 | 11.404 | 0.1428 |
| mlp | -1.0404 | 0.7458 | 0.0569 | 14.1697 | 9.7096 | 0.6889 |

**Best model (by test R²): `gpr`**
