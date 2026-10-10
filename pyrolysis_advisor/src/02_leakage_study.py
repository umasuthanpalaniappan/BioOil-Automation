"""Part A: how much does the testing method change the score? (both targets)"""
import os
import sys, numpy as np, pandas as pd, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from features import add_features, RAW, PHYS
from sklearn.metrics import r2_score, mean_absolute_error
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
rows = []

def run(target, X_cols, df, y, splits, model, test, feats, oof_tag=None):
    X = df[X_cols].values; P = np.full(len(y), np.nan)
    for i, (tr, te) in enumerate(splits):
        m = MODELS[model](len(X_cols)).fit(X[tr], y[tr]); p = m.predict(X[te])
        r = dict(target=target, model=model, test=test, features=feats, split=i, n_test=len(te),
                 R2=r2_score(y[te], p), MAE=mean_absolute_error(y[te], p))
        if target == 'O/C':
            ot, op = 10 ** y[te], 10 ** p
            r.update(MAE_OC=mean_absolute_error(ot, op), MedAPE=float(np.median(np.abs(op - ot) / ot) * 100))
        rows.append(r)
        if i < 5: P[te] = p
    if oof_tag: np.save(ROOT + f'results/tables/oof_{oof_tag}.npy', P)
    s = pd.DataFrame([r for r in rows if r['target'] == target and r['model'] == model and r['test'] == test and r['features'] == feats])
    print(f'{target:6s} {test:28s} {feats:8s} {model:16s} R2={s.R2.mean():6.3f}±{s.R2.std():.3f} MAE={s.MAE.mean():.3f}', flush=True)

# ---------- O/C (D1b) ----------
oc = add_features(pd.read_csv(ROOT + 'data_clean/D1b_OC_clean.csv')); y_oc = np.log10(oc['OC'].values)
R_oc = random_splits(len(oc)); G_oc = group_splits(oc['FeedID'].values)
for model in MODELS:
    for feats, cols in [('raw', RAW), ('physics', PHYS)]:
        if model.startswith('Mean') and feats == 'physics': continue
        run('O/C', cols, oc, y_oc, R_oc, model, 'Random split', feats)
        run('O/C', cols, oc, y_oc, G_oc, model, 'Grouped by biomass', feats, oof_tag=f"oc_{model[:3]}_{feats}")
pd.DataFrame(rows).to_csv(ROOT + 'results/tables/leakage_study_splits.csv', index=False)

# ---------- Yield (D3) ----------
yd = add_features(pd.read_csv(ROOT + 'data_clean/D3_yield_clean.csv')); y_y = yd['Y'].values
R_y = random_splits(len(yd)); GE = group_splits(yd['FeedID_exact'].values); GN = group_splits(yd['FeedID'].values)
for model in ['Mean (no model)', 'Random Forest', 'XGBoost']:
    for feats, cols in [('raw', RAW), ('physics', PHYS)]:
        if model.startswith('Mean') and feats == 'physics': continue
        run('Yield', cols, yd, y_y, R_y, model, 'Random split', feats)
        run('Yield', cols, yd, y_y, GE, model, 'Grouped (exact values)', feats)
        run('Yield', cols, yd, y_y, GN, model, 'Grouped by biomass', feats, oof_tag=f"y_{model[:3]}_{feats}")
    pd.DataFrame(rows).to_csv(ROOT + 'results/tables/leakage_study_splits.csv', index=False)
# GPR on yield is slow: fewer splits
run('Yield', PHYS, yd, y_y, R_y[:5], 'GPR', 'Random split', 'physics')
run('Yield', PHYS, yd, y_y, GN[:10], 'GPR', 'Grouped by biomass', 'physics', oof_tag='y_GPR_physics')
pd.DataFrame(rows).to_csv(ROOT + 'results/tables/leakage_study_splits.csv', index=False)
print('done')
