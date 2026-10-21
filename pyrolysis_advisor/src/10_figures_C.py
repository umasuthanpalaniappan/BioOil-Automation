"""Figures for Test 1 (random split, literature protocol): O/C model benchmark and parity plots for the final models."""
import os, sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import add_features
from final_models import OCModel, YieldModel
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
FIG = ROOT + 'results/figures/'
THEMES = {'': ('#15191A', '#F1F2ED', '#9A9F9B', '#2A3031', '#C9F36B', '#7D8380'),        # slides (dark)
          '_light': ('#FFFFFF', '#1A1C1E', '#55595C', '#DDE0E2', '#2B6CD4', '#A3A8AC')}   # printed report

# C2: predicted vs actual for the final models, 5-fold random cross-validation (each row predicted once, when held out)
def oof(M, df, y, g):
    P = np.zeros(len(y))
    for tr, te in KFold(5, shuffle=True, random_state=0).split(df):
        P[te] = M().fit(df.iloc[tr], y[tr], g[tr]).predict(df.iloc[te])
    return P
oc = add_features(pd.read_csv(ROOT + 'data_clean/D1b_OC_clean.csv')); y_oc = np.log10(oc['OC'].values)
yd = add_features(pd.read_csv(ROOT + 'data_clean/D3_yield_clean.csv')); y_y = yd['Y'].values
p_oc = oof(OCModel, oc, y_oc, oc['FeedID'].values); p_y = oof(YieldModel, yd, y_y, yd['FeedID'].values)
r_oc, r_y = r2_score(y_oc, p_oc), r2_score(y_y, p_y)

for suffix, (BG, INK, MUTED, GRID, ACC, CTX) in THEMES.items():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'axes.facecolor': BG, 'figure.facecolor': BG, 'axes.edgecolor': GRID,
                         'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED, 'text.color': INK})
    # C1: seven-model O/C benchmark on the 80/20 held-out test set (ml/reports/benchmark_results.json)
    bench = json.load(open(ROOT + '../ml/reports/benchmark_results.json'))
    rows = bench['O/C']['results']
    items = sorted(((m, v['test']['r2']) for m, v in rows.items()), key=lambda t: t[1])
    names = {'xgboost': 'XGBoost', 'random_forest': 'Random Forest', 'gpr': 'GPR', 'lightgbm': 'LightGBM', 'ridge': 'Ridge', 'lasso': 'Lasso', 'mlp': 'MLP'}
    fig, ax = plt.subplots(figsize=(8, 4.2))
    best = max(v for _, v in items)
    for i, (m, v) in enumerate(items):
        ax.barh(i, v, height=0.62, color=ACC if v == best else CTX)
        inside = v > 0.7
        ax.text(v - 0.015 if inside else v + 0.012, i, f'{v:.2f}', va='center', ha='right' if inside else 'left', fontsize=12,
                color=(('#FFFFFF' if suffix else BG) if v == best else '#0E0F10') if inside else INK, fontweight='bold')
    ax.axvline(0.895, color=INK, lw=1.5, ls=(0, (4, 3)))
    ax.text(0.895, len(items) - 0.35, 'Zhang et al. 2022: 0.895', ha='right', va='bottom', fontsize=11, color=INK)
    ax.set_yticks(range(len(items))); ax.set_yticklabels([names.get(m, m) for m, _ in items], color=INK)
    ax.set_xlim(0, 1.05); ax.set_xlabel('Test R² for O/C (held-out 20%)')
    ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0)
    fig.tight_layout(); fig.savefig(FIG + f'C1_oc_benchmark{suffix}.png', dpi=200); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, t, p, lab, r2, log in [(axs[0], 10 ** y_oc, 10 ** p_oc, 'O/C ratio', r_oc, True), (axs[1], y_y, p_y, 'Bio-oil yield (wt%)', r_y, False)]:
        lo, hi = min(t.min(), p.min()), max(t.max(), p.max())
        ax.plot([lo, hi], [lo, hi], color=MUTED, lw=1.5, ls=(0, (4, 3)), zorder=1)
        ax.scatter(t, p, s=26 if log else 14, color=ACC, alpha=0.75 if log else 0.45, edgecolors=BG, linewidths=0.6, zorder=2)
        if log: ax.set_xscale('log'); ax.set_yscale('log')
        ax.set_xlabel(f'Measured {lab}'); ax.set_ylabel(f'Predicted {lab}')
        ax.set_title('Oxygen (O/C ratio)' if log else 'Bio-oil yield', color=INK, fontsize=13, loc='left', fontweight='bold')
        ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ['top', 'right']: ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG + f'C2_parity{suffix}.png', dpi=200); plt.close(fig)

json.dump(dict(parity_R2_OC_log=r_oc, parity_R2_yield=r_y, protocol='5-fold random CV, shuffle seed 0'), open(ROOT + 'results/tables/parity_final.json', 'w'), indent=1)
print('parity R2', round(r_oc, 3), round(r_y, 3))
