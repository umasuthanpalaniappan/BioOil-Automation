"""Step 1: clean both datasets from the original files.
D1b = 'data' sheet of data 1.xlsx (Zhang et al. 2022, Fuel 312:122812) -> bio-oil O/C
D3  = Zenodo copy of Pascarella et al. 2025 (Fuel 394:135000)        -> bio-liquid yield
"""
import os
import pandas as pd, numpy as np, json
from scipy.cluster.hierarchy import linkage, fcluster
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
log = {}

# ---------------- D1b (O/C) ----------------
raw = pd.read_excel(ROOT + 'data_raw/D1_data1.xlsx', sheet_name='data')
d = raw.copy(); d.columns = [c.strip().replace(' ', '') for c in d.columns]
d.insert(0, 'ExcelRow', np.arange(2, len(d) + 2))
for c in d.columns[1:]:   # text typing errors: non-breaking spaces, ' ', '-'
    d[c] = pd.to_numeric(d[c].astype(str).str.replace('\xa0', '').str.strip().replace({'': np.nan, '-': np.nan, 'nan': np.nan}), errors='coerce')
d = d.drop(columns=['Gas_yield', 'Char_yield'])
dup = d.drop(columns='ExcelRow').duplicated()
log['D1b_duplicates_removed'] = d.loc[dup, 'ExcelRow'].tolist(); d = d[~dup].copy()
d.loc[d['Temp'] > 200, 'Temp'] = np.nan          # viscosity temperature held reactor temperature
flag = pd.Series('', index=d.index)
def add(mask, msg): flag.loc[mask] = flag.loc[mask] + msg + ' | '
add((d['H%'] > 15) | (d['N%'] > 30) | (d['Size'] > 20), 'corrupted row')
add(d['C%'] < 25, 'columns shifted (C ~15%)')
add((d['N%'] > 15) & (d['N%'] < 30), 'feed N ~20%')
add((d['C%'] > 75) & (d['PT'] < 200), 'char-like feed at 185 C')
add((d['PT'] < 300) & (d['C%'] <= 75), 'temperature below 300 C')
d['Flag'] = flag.str.rstrip(' |')
d = d.rename(columns={'C%': 'C', 'H%': 'H', 'O%': 'O', 'N%': 'N', 'Size': 'PS', 'PT': 'T', 'O/C': 'OC'})
d['FeedID'] = d.groupby(['C', 'H', 'O', 'N'], dropna=False).ngroup() + 1
need = ['C', 'H', 'O', 'N', 'PS', 'HR', 'T', 'OC']
oc = d[d[need].notna().all(axis=1) & (d['Flag'] == '')].copy()
oc.to_csv(ROOT + 'data_clean/D1b_OC_clean.csv', index=False)
log['D1b_rows_raw'] = len(raw); log['D1b_rows_model'] = len(oc); log['D1b_feedstocks'] = int(oc.FeedID.nunique())
log['D1b_flagged'] = d.loc[d.Flag != '', ['ExcelRow', 'Flag']].values.tolist()

# ---------------- D3 (yield) ----------------
y = pd.read_excel(ROOT + 'data_raw/D3_pascarella_zenodo.xlsx')
y.columns = ['Ash', 'FC', 'VM', 'C', 'HCeff_src', 'H', 'O', 'N', 'Cel', 'Hem', 'Lig', 'T', 'HR', 'PS', 'FR', 'Y', 'W']
log['D3_rows_raw'] = len(y)
y = y.drop_duplicates().reset_index(drop=True); log['D3_rows_after_dedup'] = len(y)
# exact-value groups (what a naive grouped test would use)
y['FeedID_exact'] = y.groupby(['C', 'H', 'O', 'N']).ngroup() + 1
# near-duplicate groups: compositions within 0.2 wt% are the same biomass
Z = linkage(y[['C', 'H', 'O', 'N', 'Ash']].values, 'single')
y['FeedID'] = fcluster(Z, 0.2, 'distance')
log['D3_groups_exact'] = int(y.FeedID_exact.nunique()); log['D3_groups_near_dup'] = int(y.FeedID.nunique())
log['D3_group_counts_by_threshold'] = {str(th): int(len(set(fcluster(Z, th, 'distance')))) for th in [0.05, 0.1, 0.2, 0.3, 0.5]}
y.to_csv(ROOT + 'data_clean/D3_yield_clean.csv', index=False)
json.dump(log, open(ROOT + 'results/tables/cleaning_log.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in log.items() if k != 'D1b_flagged'}, indent=1))
