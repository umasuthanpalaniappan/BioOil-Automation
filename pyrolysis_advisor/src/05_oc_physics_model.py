"""O/C: GPR ignores temperature. Test physics-constrained alternatives so the advisor responds to temperature correctly."""
import os
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from features import add_features, PHYS
from sklearn.metrics import r2_score, mean_absolute_error
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
oc=add_features(pd.read_csv(ROOT+'data_clean/D1b_OC_clean.csv')); y=np.log10(oc['OC'].values); X=oc[PHYS].values
MONO={'T':-1,'S_tar':-1,'logTSI':-1,'feed_OC':1}
def mono(): return XGBRegressor(n_estimators=500,max_depth=3,learning_rate=0.03,subsample=0.8,colsample_bytree=0.8,min_child_weight=5,reg_lambda=5.0,random_state=0,n_jobs=1,
    monotone_constraints='('+','.join(str(MONO.get(c,0)) for c in PHYS)+')')
class Blend:
    def fit(self,X,y): self.a=gpr(len(PHYS)).fit(X,y); self.b=mono().fit(X,y); return self
    def predict(self,X): return 0.5*self.a.predict(X)+0.5*self.b.predict(X)
G=group_splits(oc['FeedID'].values); R=random_splits(len(oc)); res={}
for name,mk in [('XGBoost + physics constraints',mono),('Blend: GPR + constrained XGBoost',Blend)]:
    for test,sp in [('Grouped by biomass',G),('Random split',R)]:
        s=[]
        for tr,te in sp:
            p=mk().fit(X[tr],y[tr]).predict(X[te]); s.append((r2_score(y[te],p),mean_absolute_error(y[te],p),np.median(np.abs(10**p-10**y[te])/10**y[te])*100))
        s=np.array(s); res[f'{name} | {test}']=dict(R2=s[:,0].mean(),R2sd=s[:,0].std(),MAE=s[:,1].mean(),MedAPE=s[:,2].mean()); print(name,test,{k:round(v,3) for k,v in res[f'{name} | {test}'].items()},flush=True)
M=Blend().fit(X,y); Ts=np.arange(350,701,25); curve=[]
for T in Ts:
    g=oc[['C','H','O','N','HR','PS']].copy(); g['T']=T; curve.append(float((10**M.predict(add_features(g)[PHYS].values)).mean()))
print('blend T curve',np.round(curve,3)); res['blend_T_curve']=dict(T=Ts.tolist(),OC=curve)
json.dump(res,open(ROOT+'results/tables/oc_physics_model.json','w'),indent=1)
