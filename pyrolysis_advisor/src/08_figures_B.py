import os
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep; F=json.load(open(ROOT+'results/tables/final_results.json'))
BLUE,ORANGE,GREY,TXT,TXT2,GRID='#2a78d6','#eb6834','#9b9a94','#0b0b0b','#52514e','#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#bdbcb6','axes.labelcolor':TXT2,'xtick.color':TXT2,'ytick.color':TXT2,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.titlesize':11,'axes.titlecolor':TXT,'figure.dpi':200})
P=F['physics']; T=np.array(P['T'])
fig,ax=plt.subplots(1,3,figsize=(9.6,3.0))
ax[0].plot(T,P['yield_T'],color=BLUE,lw=2); ax[0].axvspan(450,550,color=GRID,lw=0); ax[0].set_title('Yield vs temperature',loc='left'); ax[0].set_ylabel('Average predicted yield (wt%)')
ax[1].plot(T,np.array(P['S_tar'])*100,color=BLUE,lw=2); ax[1].set_title('Kinetics: share to tar',loc='left'); ax[1].set_ylabel('Primary tar selectivity (%)')
ax[2].plot(T,P['OC_T'],color=BLUE,lw=2); ax[2].set_title('O/C vs temperature',loc='left'); ax[2].set_ylabel('Average predicted O/C')
for a in ax: a.set_xlabel('Temperature (°C)'); a.grid(color=GRID); a.set_axisbelow(True)
ax[0].text(500,min(P['yield_T'])+0.3,'literature\noptimum',ha='center',fontsize=8,color=TXT2)
fig.tight_layout(); fig.savefig(ROOT+'results/figures/B1_physics.png'); plt.close()
# B2 calibration yield
C=F['calibration']['Yield']; L=pd.read_csv(ROOT+'results/tables/leakage_study_summary.csv')
mean0=L[(L.target=='Yield')&(L.test=='Grouped by biomass')&(L.model=='Mean (no model)')].MAE.iloc[0]; mod0=F['oof_scores']['Yield']['MAE']
meas=[mean0,C['1']['MAE_measured_only'],C['2']['MAE_measured_only']]; mod=[mod0,C['1']['MAE_model'],C['2']['MAE_model']]
x=np.arange(3); w=0.36; fig,ax=plt.subplots(figsize=(6.2,3.3))
ax.bar(x-w/2-0.01,meas,w,color=GREY,label='No model (average, or the measured value)'); ax.bar(x+w/2+0.01,mod,w,color=BLUE,label='Physics-aware model (+ calibration)')
for xi,v in list(zip(x-w/2-0.01,meas))+list(zip(x+w/2+0.01,mod)): ax.text(xi,v+0.15,f'{v:.1f}',ha='center',fontsize=8,color=TXT)
ax.set_xticks(x); ax.set_xticklabels(['New biomass,\nno experiment','New biomass,\n1 experiment','New biomass,\n2 experiments']); ax.set_ylabel('Average yield error (wt%)')
ax.set_ylim(0,10.5); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True); ax.legend(fontsize=8,frameon=False); ax.set_title('Calibrating with a few experiments',loc='left')
fig.tight_layout(); fig.savefig(ROOT+'results/figures/B2_calibration.png'); plt.close()
# B3 case studies
fig,ax=plt.subplots(1,3,figsize=(9.6,3.0),sharey=False)
for a,c in zip(ax,F['cases']):
    a.plot(c['T'],c['pred'],color=GREY,lw=1.8,label='Model, no experiment'); a.plot(c['T'],c['pred_cal'],color=BLUE,lw=2,label='Model + 1 experiment')
    a.scatter(c['T'],c['actual'],s=26,color=ORANGE,zorder=3,label='Real experiments'); a.scatter([c['T_cal']],[c['actual'][c['T'].index(c['T_cal'])]],s=70,facecolor='none',edgecolor=TXT,zorder=4,lw=1.2)
    a.set_title(f"Biomass {c['FeedID']} (C {c['C']:.0f}%, O {c['O']:.0f}%)",loc='left',fontsize=10); a.set_xlabel('Temperature (°C)'); a.grid(color=GRID); a.set_axisbelow(True)
ax[0].set_ylabel('Yield (wt%)'); h,l=ax[0].get_legend_handles_labels(); fig.legend(h,l,loc='lower center',ncol=3,fontsize=8,frameon=False)
fig.tight_layout(rect=(0,0.08,1,1)); fig.savefig(ROOT+'results/figures/B3_cases.png'); plt.close()
# B4 advisor trade-off for pine-like wood
g=pd.read_csv(ROOT+'results/tables/advisor_pine-like.csv'); b=F['examples']['Pine-like wood']['best']
fig,ax=plt.subplots(figsize=(5.8,4.3))
ax.scatter(g.OC,g['yield'],s=12,color=GREY,alpha=0.6,label='All settings tried'); p=g[g.pareto].sort_values('OC')
ax.plot(p.OC,p['yield'],color=BLUE,lw=1.5,marker='o',ms=4,label='Best trade-offs (Pareto front)')
ax.scatter([b['OC']],[b['yield']],s=140,marker='*',color=ORANGE,edgecolor=TXT,lw=0.6,zorder=5,label=f"Recommended: {b['T']:.0f} °C, {b['HR']:.0f} °C/min")
ax.set_xlabel('Predicted O/C (lower = less oxygen)'); ax.set_ylabel('Predicted yield (wt%)'); ax.grid(color=GRID); ax.set_axisbelow(True)
ax.legend(fontsize=7.5,frameon=False,loc='upper center',bbox_to_anchor=(0.5,-0.17),ncol=2); ax.set_title('Advisor output: pine-like wood',loc='left')
fig.tight_layout(); fig.savefig(ROOT+'results/figures/B4_advisor_pine.png'); plt.close()
print('ok')
