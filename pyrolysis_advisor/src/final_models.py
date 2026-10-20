"""Final physics-aware models used by the Pyrolysis Advisor."""
import numpy as np, pandas as pd
from xgboost import XGBRegressor
from common import gpr
from features import PHYS

COMP = ['feed_OC', 'feed_HC', 'feed_HCeff', 'N']; COND = ['T', 'logHR', 'logPS', 'log_theta', 'S_tar', 'log_Py', 'logTSI']
MONO = {'T': -1, 'S_tar': -1, 'logTSI': -1, 'feed_OC': 1}

class OCModel:
    def fit(self, df, y, g=None):
        self.a = gpr(len(PHYS)).fit(df[PHYS].values, y)
        self.b = XGBRegressor(n_estimators=500, max_depth=3, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                              reg_lambda=5.0, random_state=0, n_jobs=2, monotone_constraints='(' + ','.join(str(MONO.get(c, 0)) for c in PHYS) + ')').fit(df[PHYS].values, y)
        return self
    def predict(self, df): return 0.5 * self.a.predict(df[PHYS].values) + 0.5 * self.b.predict(df[PHYS].values)   # log10(O/C)

class YieldModel:
    def fit(self, df, y, g):
        gm = pd.Series(y).groupby(g).transform('mean').values
        self.level = gpr(len(COMP)).fit(df[COMP].values, y)
        self.shape = XGBRegressor(n_estimators=400, max_depth=3, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
                                  reg_lambda=10, random_state=0, n_jobs=2).fit(df[COND].values, y - gm)
        return self
    def predict(self, df): return self.level.predict(df[COMP].values) + self.shape.predict(df[COND].values)
