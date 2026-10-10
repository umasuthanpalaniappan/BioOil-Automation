"""Yield: GPR alone ignores reactor conditions for new biomass. Test models that separate
'level' (which biomass) from 'shape' (how yield responds to temperature, heating rate, particle size)."""
import os
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from features import add_features, PHYS
from sklearn.metrics import r2_score, mean_absolute_error
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
yd=add_features(pd.read_csv(ROOT+'data_clean/D3_yield_clean.csv')); y=yd['Y'].values; grp=yd['FeedID'].values
COMP=['feed_OC','feed_HC','feed_HCeff','N']; COND=['T','logHR','logPS','log_theta','S_tar','log_Py','logTSI']
def shape_model(): return XGBRegressor(n_estimators=400,max_depth=3,learning_rate=0.03,subsample=0.8,colsample_bytree=0.8,min_child_weight=10,reg_lambda=10,random_state=0,n_jobs=2)
class Hybrid:
    """yield = level(biomass composition, GPR) + shape(conditions, XGBoost on within-biomass deviations)"""
    def fit(self, df, y, g):
        gm=pd.Series(y).groupby(g).transform('mean').values
        self.level=gpr(len(COMP)).fit(df[COMP].values,y)          # composition only
        self.shape=shape_model().fit(df[COND].values,y-gm)       # deviation from that biomass' average
        return self
    def predict(self, df): return self.level.predict(df[COMP].values)+self.shape.predict(df[COND].values)
class Blend:
    def fit(self, df, y, g): self.a=gpr(len(PHYS)).fit(df[PHYS].values,y); self.b=xgb().fit(df[PHYS].values,y); return self
    def predict(self, df): return 0.5*self.a.predict(df[PHYS].values)+0.5*self.b.predict(df[PHYS].values)
class GPRonly:
    def fit(self, df, y, g): self.a=gpr(len(PHYS)).fit(df[PHYS].values,y); return self
    def predict(self, df): return self.a.predict(df[PHYS].values)
S=group_splits(grp)[:10]; res={}
for name,M in [('Hybrid: level (GPR) + shape (XGBoost)',Hybrid),('Blend: GPR + XGBoost',Blend),('GPR only',GPRonly)]:
    rows=[]
    for i,(tr,te) in enumerate(S):
        m=M().fit(yd.iloc[tr],y[tr],grp[tr]); p=m.predict(yd.iloc[te]); yt=y[te]; g=grp[te]
        # within-biomass shape: compare centred prediction vs centred truth
        pc=p-pd.Series(p).groupby(g).transform('mean').values; tc=yt-pd.Series(yt).groupby(g).transform('mean').values
        # one-experiment calibration
        rng=np.random.default_rng(i); pcal=p.copy(); keep=np.ones(len(te),bool)
        for gg in np.unique(g):
            idx=np.where(g==gg)[0]
            if len(idx)<2: keep[idx]=False; continue
            c=rng.choice(idx); pcal[idx]=p[idx]+yt[c]-p[c]; keep[c]=False
        rows.append(dict(R2=r2_score(yt,p),MAE=mean_absolute_error(yt,p),shape_R2=r2_score(tc,pc),MAE_cal1=mean_absolute_error(yt[keep],pcal[keep])))
        print(name,i,{k:round(v,3) for k,v in rows[-1].items()},flush=True)
    res[name]=pd.DataFrame(rows).mean().to_dict(); print('==>',name,{k:round(v,3) for k,v in res[name].items()},flush=True)
json.dump(res,open(ROOT+'results/tables/yield_hybrid.json','w'),indent=1)
