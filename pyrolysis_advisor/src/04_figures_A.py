import os
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
BLUE,ORANGE,YEL,GREY,TXT,TXT2,GRID='#2a78d6','#eb6834','#eda100','#9b9a94','#0b0b0b','#52514e','#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#bdbcb6','axes.labelcolor':TXT2,'xtick.color':TXT2,'ytick.color':TXT2,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.titlesize':11,'axes.titlecolor':TXT,'figure.dpi':200})
L=pd.read_csv(ROOT+'results/tables/leakage_study_splits.csv')
S=L.groupby(['target','test','features','model']).agg(R2=('R2','mean'),R2sd=('R2','std'),MAE=('MAE','mean'),MAE_OC=('MAE_OC','mean'),MedAPE=('MedAPE','mean'),n=('R2','size')).reset_index()
S.to_csv(ROOT+'results/tables/leakage_study_summary.csv',index=False)
print(S.round(3).to_string())
def get(t,test,f,m): r=S[(S.target==t)&(S.test==test)&(S.features==f)&(S.model==m)].iloc[0]; return r.R2,r.R2sd
fig,ax=plt.subplots(1,2,figsize=(7.6,3.4),gridspec_kw=dict(width_ratios=[3,2]))
tests=[('Random split','Random\nsplit',ORANGE),('Grouped (exact values)','Grouped by\nexact values',YEL),('Grouped by biomass','Grouped by\nbiomass',BLUE)]
v=[get('Yield',t,'physics','XGBoost') for t,_,_ in tests]
ax[0].bar([l for _,l,_ in tests],[a for a,_ in v],yerr=[b for _,b in v],color=[c for *_,c in tests],width=0.55,error_kw=dict(ecolor=TXT2,lw=0.8,capsize=3))
for i,(a,b) in enumerate(v): ax[0].text(i,max(a+b,0)+0.03,f'{a:.2f}',ha='center',fontsize=9,color=TXT)
ax[0].set_title('Bio-oil yield (XGBoost)',loc='left'); ax[0].set_ylabel('R² on the test set')
tests2=[('Random split','Random\nsplit',ORANGE),('Grouped by biomass','Grouped by\nbiomass',BLUE)]
v2=[get('O/C',t,'physics','GPR') for t,_,_ in tests2]
ax[1].bar([l for _,l,_ in tests2],[a for a,_ in v2],yerr=[b for _,b in v2],color=[c for *_,c in tests2],width=0.5,error_kw=dict(ecolor=TXT2,lw=0.8,capsize=3))
for i,(a,b) in enumerate(v2): ax[1].text(i,max(a+b,0)+0.03,f'{a:.2f}',ha='center',fontsize=9,color=TXT)
ax[1].set_title('Bio-oil O/C (GPR)',loc='left')
for a in ax: a.axhline(0,color=TXT2,lw=0.8); a.grid(axis='y',color=GRID); a.set_axisbelow(True); a.set_ylim(-0.65,0.95)
fig.tight_layout(); fig.savefig(ROOT+'results/figures/A1_leakage.png'); plt.close()
# A2 physics vs raw (grouped O/C)
ms=['Random Forest','XGBoost','GPR']; raw=[get('O/C','Grouped by biomass','raw',m)[0] for m in ms]; ph=[get('O/C','Grouped by biomass','physics',m)[0] for m in ms]
x=np.arange(3); w=0.36; fig,ax=plt.subplots(figsize=(5.6,3.2))
ax.bar(x-w/2-0.01,raw,w,color=GREY,label='Raw inputs (C, H, O, N, T, HR, PS)'); ax.bar(x+w/2+0.01,ph,w,color=BLUE,label='Physics inputs')
for xi,v in zip(x-w/2-0.01,raw): ax.text(xi,max(v,0)+0.01,f'{v:.2f}',ha='center',fontsize=8,color=TXT)
for xi,v in zip(x+w/2+0.01,ph): ax.text(xi,max(v,0)+0.01,f'{v:.2f}',ha='center',fontsize=8,color=TXT)
ax.axhline(0,color=TXT2,lw=0.8); ax.set_xticks(x); ax.set_xticklabels(ms); ax.set_ylabel('R², new biomass'); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
ax.legend(fontsize=8,frameon=False,loc='upper left'); ax.set_ylim(-0.2,0.35); ax.set_title('Physics inputs help on unseen biomass (O/C)',loc='left')
fig.tight_layout(); fig.savefig(ROOT+'results/figures/A2_physics_vs_raw.png'); plt.close()
