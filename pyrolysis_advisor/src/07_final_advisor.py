"""Part B (final): physics-aware models, honest uncertainty, calibration, case studies and the Pyrolysis Advisor.
O/C model  = 0.5 x GPR + 0.5 x XGBoost with physics constraints (O/C falls with T, rises with feed O/C)
Yield model = level (GPR on biomass composition) + shape (XGBoost on how yield deviates with reactor conditions)
"""
import os
import sys, json, numpy as np, pandas as pd, joblib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from features import add_features, PHYS, kinetics
from sklearn.metrics import r2_score, mean_absolute_error
from scipy.spatial import cKDTree
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
from final_models import COMP, COND, MONO, OCModel, YieldModel

oc = add_features(pd.read_csv(ROOT + 'data_clean/D1b_OC_clean.csv')); y_oc = np.log10(oc['OC'].values); g_oc = oc['FeedID'].values
yd = add_features(pd.read_csv(ROOT + 'data_clean/D3_yield_clean.csv')); y_y = yd['Y'].values; g_y = yd['FeedID'].values
out = {}

# ---- grouped out-of-fold predictions -> honest 80% bands + calibration study ----
def oof_and_calib(M, df, y, g, seed=0):
    P = np.full(len(y), np.nan); cal = {1: [], 2: []}
    for i, (tr, te) in enumerate(group_splits(g, n_rep=1, k=5)):
        p = M().fit(df.iloc[tr], y[tr], g[tr]).predict(df.iloc[te]); P[te] = p; yt = y[te]; gg = g[te]
        for n in (1, 2):
            rng = np.random.default_rng(seed + i + 10 * n); pm, pb, keep = p.copy(), np.zeros(len(te)), np.ones(len(te), bool)
            for b in np.unique(gg):
                idx = np.where(gg == b)[0]
                if len(idx) <= n: keep[idx] = False; continue
                c = rng.choice(idx, n, replace=False); pm[idx] = p[idx] + (yt[c] - p[c]).mean(); pb[idx] = yt[c].mean(); keep[c] = False
            cal[n].append((mean_absolute_error(yt[keep], pm[keep]), mean_absolute_error(yt[keep], pb[keep])))
    return P, {n: dict(MAE_model=float(np.mean([a for a, _ in v])), MAE_measured_only=float(np.mean([b for _, b in v]))) for n, v in cal.items()}
P_oc, cal_oc = oof_and_calib(OCModel, oc, y_oc, g_oc); P_y, cal_y = oof_and_calib(YieldModel, yd, y_y, g_y)
out['oof_scores'] = dict(OC=dict(R2_log=r2_score(y_oc, P_oc), MAE_log=mean_absolute_error(y_oc, P_oc), MedAPE=float(np.median(np.abs(10 ** P_oc - 10 ** y_oc) / 10 ** y_oc) * 100)),
                         Yield=dict(R2=r2_score(y_y, P_y), MAE=mean_absolute_error(y_y, P_y)))
out['band80'] = dict(OC_factor=float(10 ** np.quantile(np.abs(y_oc - P_oc), 0.8)), yield_pm=float(np.quantile(np.abs(y_y - P_y), 0.8)))
out['calibration'] = dict(OC=cal_oc, Yield=cal_y)
np.save(ROOT + 'results/tables/oof_final_oc.npy', P_oc); np.save(ROOT + 'results/tables/oof_final_yield.npy', P_y)
print(json.dumps({k: out[k] for k in ['oof_scores', 'band80', 'calibration']}, indent=1, default=float), flush=True)

# ---- final fits ----
M_oc = OCModel().fit(oc, y_oc); M_y = YieldModel().fit(yd, y_y, g_y)
joblib.dump(dict(model=M_oc, note='predicts log10(O/C)'), ROOT + 'models/oc_model.joblib')
joblib.dump(dict(model=M_y, note='predicts bio-liquid yield wt%'), ROOT + 'models/yield_model.joblib')

# ---- physics checks: average response to temperature, heating rate, particle size ----
def curve(M, df, col, vals, tf=lambda v: v):
    r = []
    for v in vals:
        g = df[['C', 'H', 'O', 'N', 'T', 'HR', 'PS']].copy(); g[col] = v; r.append(float(np.mean(tf(M.predict(add_features(g))))));
    return r
Ts = np.arange(350, 701, 25); HRs = [5, 10, 20, 50, 100, 300]; PSs = [0.2, 0.5, 1.0, 2.0]
kg, kt, kc = kinetics(Ts)
out['physics'] = dict(T=Ts.tolist(), S_tar=(kt / (kg + kt + kc)).tolist(),
                      yield_T=curve(M_y, yd, 'T', Ts), OC_T=curve(M_oc, oc, 'T', Ts, lambda v: 10 ** v),
                      HR=HRs, yield_HR=curve(M_y, yd, 'HR', HRs), OC_HR=curve(M_oc, oc, 'HR', HRs, lambda v: 10 ** v),
                      PS=PSs, yield_PS=curve(M_y, yd, 'PS', PSs), OC_PS=curve(M_oc, oc, 'PS', PSs, lambda v: 10 ** v))
print('physics', {k: np.round(v, 3).tolist() for k, v in out['physics'].items()}, flush=True)

# ---- applicability check: is a new biomass similar to the training biomasses? ----
feeds = pd.concat([oc[COMP[:2] + ['N']], yd[COMP[:2] + ['N']]]).drop_duplicates()
mu, sd = feeds.mean(), feeds.std(); Fz = ((feeds - mu) / sd).values
tree = cKDTree(Fz); dnn = tree.query(Fz, k=2)[0][:, 1]; lim = float(np.quantile(dnn, 0.95)); out['domain_limit'] = lim
def similarity(C, H, O, N):
    f = add_features(pd.DataFrame([dict(C=C, H=H, O=O, N=N, T=500, HR=10, PS=0.5)]))[COMP[:2] + ['N']]
    d = tree.query(((f - mu) / sd).values)[0][0]; return float(d), bool(d <= lim)

# ---- the advisor ----
GT = np.arange(400, 651, 10); GHR = np.array([5, 10, 20, 50, 100, 300])
def advise(C, H, O, N, PS, measured=None):
    g = pd.DataFrame([dict(C=C, H=H, O=O, N=N, T=T, HR=HR, PS=PS) for T in GT for HR in GHR]); f = add_features(g)
    g['yield'] = M_y.predict(f); g['OC'] = 10 ** M_oc.predict(f)
    if measured:
        m = add_features(pd.DataFrame([dict(C=C, H=H, O=O, N=N, T=T, HR=HR, PS=PS) for T, HR, _ in measured]))
        g['yield'] += np.mean(np.array([v for *_, v in measured]) - M_y.predict(m))
    v = g[['yield', 'OC']].values
    g['pareto'] = [not np.any((v[:, 0] >= a) & (v[:, 1] <= b) & ((v[:, 0] > a) | (v[:, 1] < b))) for a, b in v]
    g['score'] = 0.5 * (g['yield'] - g['yield'].min()) / (np.ptp(g['yield']) + 1e-9) + 0.5 * (g['OC'].max() - g['OC']) / (np.ptp(g['OC']) + 1e-9)
    d, ok = similarity(C, H, O, N)
    return g, dict(distance=d, in_domain=ok)

# ---- case studies: three biomasses held out completely, compared with their real experiments ----
cases = []
for fid in [11, 108, 99]:
    sub = yd[yd.FeedID == fid]; hr = sub['HR'].mode()[0]; ps = sub.loc[sub.HR == hr, 'PS'].mode()[0]
    pts = sub[(sub.HR == hr) & (sub.PS == ps)].groupby('T')['Y'].mean(); tr = (yd.FeedID != fid).values
    Mh = YieldModel().fit(yd[tr], y_y[tr], g_y[tr]); comp_ = sub[['C', 'H', 'O', 'N']].mean()
    q = add_features(pd.DataFrame(dict(C=comp_.C, H=comp_.H, O=comp_.O, N=comp_.N, T=pts.index.values, HR=hr, PS=ps)))
    pred = Mh.predict(q); k = len(pts) // 2; off = pts.values[k] - pred[k]; keep = np.arange(len(pts)) != k
    cases.append(dict(FeedID=int(fid), HR=float(hr), PS=float(ps), C=float(comp_.C), H=float(comp_.H), O=float(comp_.O), N=float(comp_.N),
                      T=pts.index.tolist(), actual=pts.values.tolist(), pred=pred.tolist(), pred_cal=(pred + off).tolist(), T_cal=float(pts.index[k]),
                      MAE_raw=float(np.mean(np.abs(pts.values - pred)[keep])), MAE_cal=float(np.mean(np.abs(pts.values - pred - off)[keep])),
                      MAE_flat=float(np.mean(np.abs(pts.values - pts.values[k])[keep])),
                      best_T_actual=float(pts.idxmax()), best_T_pred=float(pts.index[np.argmax(pred)])))
    c = cases[-1]; print('case', fid, {x: round(c[x], 2) for x in ['HR', 'PS', 'MAE_raw', 'MAE_cal', 'MAE_flat', 'best_T_actual', 'best_T_pred']}, flush=True)
out['cases'] = cases

# ---- example runs ----
EX = {'Pine-like wood': (50.0, 6.1, 43.5, 0.2, 0.5), 'Rice husk-like': (41.5, 5.6, 51.5, 0.6, 0.5), 'Microalgae-like': (52.0, 7.5, 31.0, 8.5, 0.5),
      'Coal-like (should be flagged)': (80.0, 4.5, 14.0, 1.5, 0.5)}
out['examples'] = {}
for name, args in EX.items():
    g, info = advise(*args); top = g.sort_values('score', ascending=False).iloc[0]
    out['examples'][name] = dict(info=info, best=top[['T', 'HR', 'yield', 'OC']].astype(float).to_dict(),
                                 maxY=g.loc[g['yield'].idxmax(), ['T', 'HR', 'yield', 'OC']].astype(float).to_dict(),
                                 minOC=g.loc[g['OC'].idxmin(), ['T', 'HR', 'yield', 'OC']].astype(float).to_dict(),
                                 yield_range=[float(g['yield'].min()), float(g['yield'].max())], OC_range=[float(g['OC'].min()), float(g['OC'].max())])
    g.to_csv(ROOT + f"results/tables/advisor_{name.split()[0].lower()}.csv", index=False)
    print(name, out['examples'][name], flush=True)
json.dump(out, open(ROOT + 'results/tables/final_results.json', 'w'), indent=1, default=float)
print('done')
