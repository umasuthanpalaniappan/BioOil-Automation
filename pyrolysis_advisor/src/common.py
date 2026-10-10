import numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel as CK
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from xgboost import XGBRegressor

class Mean:
    def fit(self, X, y): self.m = float(np.mean(y)); return self
    def predict(self, X): return np.full(len(X), self.m)

def rf(): return RandomForestRegressor(n_estimators=400, min_samples_leaf=2, max_features=0.6, random_state=0, n_jobs=2)
def xgb(): return XGBRegressor(n_estimators=500, max_depth=3, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8,
                               min_child_weight=5, reg_lambda=5.0, random_state=0, n_jobs=2)
def gpr(n):
    k = CK(1.0) * Matern(length_scale=np.ones(n), length_scale_bounds=(1e-2, 1e3), nu=1.5) + WhiteKernel(0.1, (1e-4, 1))
    return make_pipeline(StandardScaler(), GaussianProcessRegressor(kernel=k, normalize_y=True, n_restarts_optimizer=0, random_state=0))
MODELS = {'Mean (no model)': lambda n: Mean(), 'Random Forest': lambda n: rf(), 'XGBoost': lambda n: xgb(), 'GPR': gpr}

def random_splits(n, n_rep=10, frac=0.2):
    out = []
    for r in range(n_rep):
        idx = np.random.default_rng(r).permutation(n); k = int(round(frac * n)); out.append((idx[k:], idx[:k]))
    return out

def group_splits(groups, n_rep=5, k=5):
    ug = np.unique(groups); out = []
    for r in range(n_rep):
        perm = np.random.default_rng(100 + r).permutation(ug)
        for f in np.array_split(perm, k):
            te = np.isin(groups, f); out.append((np.where(~te)[0], np.where(te)[0]))
    return out
