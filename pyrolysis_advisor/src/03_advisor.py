"""Part B: final models, honest uncertainty, calibration study, physics checks, advisor and case studies."""
import os
import sys, json, numpy as np, pandas as pd, joblib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from features import add_features, PHYS, kinetics
from sklearn.metrics import r2_score, mean_absolute_error
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
out = {}
oc = add_features(pd.read_csv(ROOT + 'data_clean/D1b_OC_clean.csv')); y_oc = np.log10(oc['OC'].values)
yd = add_features(pd.read_csv(ROOT + 'data_clean/D3_yield_clean.csv')); y_y = yd['Y'].values
L = pd.read_csv(ROOT + 'results/tables/leakage_study_splits.csv')
def pick(target):
    s = L[(L.target == target) & (L.test == 'Grouped by biomass') & (L.features == 'physics') & ~L.model.str.startswith('Mean')]
    return s.groupby('model')['MAE'].mean().idxmin()
best = {'O/C': pick('O/C'), 'Yield': pick('Yield')}; out['final_models'] = best; print('final models', best, flush=True)
make = {t: (lambda m=best[t]: MODELS[m](len(PHYS))) for t in best}

# ---------- honest uncertainty: grouped out-of-fold residuals (split conformal) ----------
def oof(target, df, y, groups, splits):
    X = df[PHYS].values; P = np.full(len(y), np.nan)
    for tr, te in splits:
        P[te] = make[target]().fit(X[tr], y[tr]).predict(X[te])
    return P
G_oc = group_splits(oc['FeedID'].values, n_rep=1); G_y = group_splits(yd['FeedID'].values, n_rep=1)
P_oc = oof('O/C', oc, y_oc, oc['FeedID'].values, G_oc); P_y = oof('Yield', yd, y_y, yd['FeedID'].values, G_y)
q_oc = float(np.quantile(np.abs(y_oc - P_oc), 0.8)); q_y = float(np.quantile(np.abs(y_y - P_y), 0.8))
out['interval80_logOC'] = q_oc; out['interval80_yield'] = q_y
print('80% band: O/C x/÷', round(10 ** q_oc, 2), ' yield ±', round(q_y, 2), flush=True)

# ---------- calibration study: new biomass + 1 or 2 measured experiments ----------
def calib_study(target, df, y, groups, n_cal, seeds=3):
    X = df[PHYS].values; res = []
    for rep in range(seeds):
        rng = np.random.default_rng(rep)
        for tr, te in group_splits(groups, n_rep=1, k=5):
            p = make[target]().fit(X[tr], y[tr]).predict(X[te]); yt = y[te]; g = groups[te]
            pm, pb, keep = p.copy(), np.zeros(len(te)), np.ones(len(te), bool)
            for gg in np.unique(g):
                idx = np.where(g == gg)[0]
                if len(idx) <= n_cal: keep[idx] = False; continue
                cal = rng.choice(idx, n_cal, replace=False)
                pm[idx] = p[idx] + (yt[cal] - p[cal]).mean(); pb[idx] = yt[cal].mean(); keep[cal] = False
            res.append(dict(n_cal=n_cal, MAE_model=mean_absolute_error(yt[keep], pm[keep]), MAE_measured_only=mean_absolute_error(yt[keep], pb[keep]),
                            R2_model=r2_score(yt[keep], pm[keep]), R2_measured_only=r2_score(yt[keep], pb[keep])))
    return pd.DataFrame(res).mean().to_dict()
cal = {}
for t, df, y, g in [('O/C', oc, y_oc, oc['FeedID'].values), ('Yield', yd, y_y, yd['FeedID'].values)]:
    cal[t] = [calib_study(t, df, y, g, n, seeds=3 if t == 'O/C' else 1) for n in (1, 2)]
    print(t, [{k: round(v, 3) for k, v in c.items()} for c in cal[t]], flush=True)
out['calibration'] = cal

# ---------- final fits on all data ----------
M_oc = make['O/C']().fit(oc[PHYS].values, y_oc); M_y = make['Yield']().fit(yd[PHYS].values, y_y)
joblib.dump(dict(model=M_oc, features=PHYS, target='log10(O/C)', band80=q_oc), ROOT + 'models/oc_model.joblib')
joblib.dump(dict(model=M_y, features=PHYS, target='yield wt%', band80=q_y), ROOT + 'models/yield_model.joblib')

# ---------- physics check: average effect of temperature ----------
def temp_curve(M, df, Ts):
    vals = []
    for T in Ts:
        g = df[['C', 'H', 'O', 'N', 'HR', 'PS']].copy(); g['T'] = T; vals.append(M.predict(add_features(g)[PHYS].values).mean())
    return np.array(vals)
Ts = np.arange(350, 701, 25)
out['temp_curve'] = dict(T=Ts.tolist(), yield_=temp_curve(M_y, yd, Ts).tolist(), OC=(10 ** temp_curve(M_oc, oc, Ts)).tolist())
kg, kt, kc = kinetics(Ts); out['temp_curve']['S_tar'] = (kt / (kg + kt + kc)).tolist()
print('T curve yield', np.round(out['temp_curve']['yield_'], 1), '\nT curve O/C', np.round(out['temp_curve']['OC'], 3), flush=True)

# ---------- applicability domain (is this biomass like the training biomasses?) ----------
def comp(df): return np.c_[df['feed_OC'], df['feed_HC'], df['N'] / 10]
feeds = pd.concat([oc[['feed_OC', 'feed_HC', 'N']], yd[['feed_OC', 'feed_HC', 'N']]]).drop_duplicates().values
feeds[:, 2] /= 10
from scipy.spatial import cKDTree
tree = cKDTree(feeds); dnn = tree.query(feeds, k=2)[0][:, 1]; dom_lim = float(np.quantile(dnn, 0.95))
out['domain_limit'] = dom_lim

# ---------- the advisor ----------
GRID_T = np.arange(400, 651, 10); GRID_HR = np.array([5, 10, 20, 50, 100, 300])
def advise(C, H, O, N, PS, measured=None, M_y=M_y, M_oc=M_oc):
    g = pd.DataFrame([(C, H, O, N, T, HR, PS) for T in GRID_T for HR in GRID_HR], columns=['C', 'H', 'O', 'N', 'T', 'HR', 'PS'])
    f = add_features(g); Y = M_y.predict(f[PHYS].values); OC = 10 ** M_oc.predict(f[PHYS].values)
    if measured:   # list of (T, HR, yield) actually measured for this biomass
        m = add_features(pd.DataFrame([(C, H, O, N, T, HR, PS) for T, HR, _ in measured], columns=['C', 'H', 'O', 'N', 'T', 'HR', 'PS']))
        Y = Y + np.mean([v for *_, v in measured] - M_y.predict(m[PHYS].values))
    g['yield'] = Y; g['OC'] = OC
    d = tree.query(np.c_[f['feed_OC'].iloc[:1], f['feed_HC'].iloc[:1], f['N'].iloc[:1] / 10])[0][0]
    yn = (Y - Y.min()) / (np.ptp(Y) + 1e-9); on = (OC.max() - OC) / (np.ptp(OC) + 1e-9)
    g['score'] = 0.5 * yn + 0.5 * on
    # Pareto front: no other setting has both higher yield and lower O/C
    vals = g[['yield', 'OC']].values
    g['pareto'] = [not np.any((vals[:, 0] >= a) & (vals[:, 1] <= b) & ((vals[:, 0] > a) | (vals[:, 1] < b))) for a, b in vals]
    return g, dict(in_domain=bool(d <= dom_lim), distance=float(d))

# ---------- case studies: three biomasses held out completely ----------
cases = []
for fid in [11, 108, 99]:
    sub = yd[yd.FeedID == fid]; hr = sub['HR'].mode()[0]; ps = sub.loc[sub.HR == hr, 'PS'].mode()[0]
    pts = sub[(sub.HR == hr) & (sub.PS == ps)].groupby('T')['Y'].mean()
    tr = yd.FeedID != fid
    Mh = make['Yield']().fit(yd.loc[tr, PHYS].values, y_y[tr.values])
    comp_ = sub[['C', 'H', 'O', 'N']].mean()
    g = pd.DataFrame({'C': comp_.C, 'H': comp_.H, 'O': comp_.O, 'N': comp_.N, 'T': pts.index.values, 'HR': hr, 'PS': ps})
    pred = Mh.predict(add_features(g)[PHYS].values)
    T_cal = pts.index.values[len(pts) // 2]; off = pts.loc[T_cal] - pred[len(pts) // 2]
    keep = pts.index.values != T_cal
    cases.append(dict(FeedID=int(fid), HR=float(hr), PS=float(ps), C=float(comp_.C), O=float(comp_.O), T=pts.index.tolist(), actual=pts.values.tolist(),
                      pred=pred.tolist(), pred_cal=(pred + off).tolist(), T_cal=float(T_cal),
                      MAE_raw=float(np.mean(np.abs(pts.values - pred)[keep])), MAE_cal=float(np.mean(np.abs(pts.values - pred - off)[keep])),
                      best_T_actual=float(pts.idxmax()), best_T_pred=float(pts.index.values[np.argmax(pred)])))
    print('case', fid, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in cases[-1].items() if k in ('HR', 'PS', 'MAE_raw', 'MAE_cal', 'best_T_actual', 'best_T_pred')}, flush=True)
out['cases'] = cases

# ---------- example advisor runs ----------
examples = {'Pine-like wood': (50.0, 6.1, 43.5, 0.2, 0.5), 'Rice husk-like': (41.5, 5.6, 51.5, 0.6, 0.5), 'Microalgae-like (outside data?)': (52.0, 7.5, 31.0, 8.5, 0.5)}
ex = {}
for name, (C, H, O, N, PS) in examples.items():
    g, info = advise(C, H, O, N, PS); top = g.sort_values('score', ascending=False).iloc[0]
    ex[name] = dict(info=info, best=top[['T', 'HR', 'yield', 'OC']].to_dict(), maxY=g.loc[g['yield'].idxmax(), ['T', 'HR', 'yield', 'OC']].to_dict(),
                    minOC=g.loc[g['OC'].idxmin(), ['T', 'HR', 'yield', 'OC']].to_dict(), n_pareto=int(g.pareto.sum()))
    g.to_csv(ROOT + f"results/tables/advisor_{name.split()[0].lower()}.csv", index=False)
    print(name, ex[name], flush=True)
out['examples'] = ex
json.dump(out, open(ROOT + 'results/tables/partB_results.json', 'w'), indent=1, default=float)
print('done')
