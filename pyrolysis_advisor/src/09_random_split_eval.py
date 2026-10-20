"""Test 1 (literature protocol): final models scored on 10 random 80/20 splits, as in Zhang et al. (2022) and most published work.
Biomasses can appear in both train and test, so this measures accuracy on familiar feedstocks; Test 2 (grouped by biomass, 07) measures new ones."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import random_splits
from features import add_features
from final_models import OCModel, YieldModel
from sklearn.metrics import r2_score, mean_absolute_error
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep

oc = add_features(pd.read_csv(ROOT + 'data_clean/D1b_OC_clean.csv')); y_oc = np.log10(oc['OC'].values); g_oc = oc['FeedID'].values
yd = add_features(pd.read_csv(ROOT + 'data_clean/D3_yield_clean.csv')); y_y = yd['Y'].values; g_y = yd['FeedID'].values

def evaluate(M, df, y, g, metrics):
    rows = []
    for tr, te in random_splits(len(y), n_rep=10, frac=0.2):
        p = M().fit(df.iloc[tr], y[tr], g[tr]).predict(df.iloc[te])
        rows.append({k: f(y[te], p) for k, f in metrics.items()})
    r = pd.DataFrame(rows)
    return {k: dict(mean=float(r[k].mean()), sd=float(r[k].std()), best=float(r[k].max() if k.startswith('R2') else r[k].min())) for k in r}

out = dict(
    protocol='10 random 80/20 train/test splits (seeds 0-9); mean, sd and best split reported',
    OC=evaluate(OCModel, oc, y_oc, g_oc, {
        'R2_log': r2_score,
        'R2_linear': lambda t, p: r2_score(10 ** t, 10 ** p),
        'MAE_linear': lambda t, p: mean_absolute_error(10 ** t, 10 ** p),
        'MedAPE': lambda t, p: float(np.median(np.abs(10 ** p - 10 ** t) / 10 ** t) * 100)}),
    Yield=evaluate(YieldModel, yd, y_y, g_y, {'R2': r2_score, 'MAE': mean_absolute_error}),
    n=dict(OC=int(len(y_oc)), Yield=int(len(y_y))),
)
json.dump(out, open(ROOT + 'results/tables/random_split_final.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
