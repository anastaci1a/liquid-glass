"""Same actual surface/paths, scientific sections only; zero new optical rays."""
from pathlib import Path
import sys,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h1';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
g=json.loads((O/'geometry-checkpoint.json').read_text())['scene'];s=ExpandedHarmonicBack(tuple(g['surface_half']),g['surface_radius']);q=np.load(O/'checkpoint-paths.npz');fig,axes=plt.subplots(2,2,figsize=(12,7))
for row,(axis,extent) in enumerate([('x',s.half[0]),('y',s.half[1])]):
 v=np.linspace(-extent,extent,801);sec=s.section(v,axis);h=sec['back'][:,2]
 ax=axes[row,0];ax.plot(v,np.zeros_like(v),'k-',label='flat front z=0');ax.plot(v,h,label='actual back z=-h');ax.fill_between(v,h,0,alpha=.12);ax.set(xlabel=f'{axis}/L',ylabel='z/L',title=f'Actual {axis} section (axis scales explicitly differ)');ax.legend()
 ax=axes[row,1]
 if axis=='x':ix=np.linspace(2,q['x'].shape[1]-3,9,dtype=int);iy=np.full(9,q['x'].shape[0]//2)
 else:iy=np.linspace(2,q['x'].shape[0]-3,9,dtype=int);ix=np.full(9,q['x'].shape[1]//2)
 coord=0 if axis=='x' else 1
 for j,i in zip(iy,ix):
  if not q['complete'][j,i] or not q['inside'][j,i]:continue
  p0=q[axis][j,i];back=q['back'][j,i];end=q['X' if axis=='x' else 'Y'][j,i]
  ax.plot([p0,p0,back[coord],end],[.1,0,back[2],-2],lw=.8)
 ax.plot(v,h,'k');ax.axhline(0,color='black',lw=.5);ax.axhline(-2,color='gray',ls='--');ax.set(xlabel=f'{axis}/L',ylabel='z/L',title=f'Saved actual {axis}-section paths, background D=2L')
fig.suptitle('Expanded H1: one surface supplies sections, gradients and Snell paths; orthographic n=1/1.5/1')
fig.tight_layout();fig.savefig(O/'same-surface-sections.png',dpi=140);fig.savefig(O/'same-surface-sections.svg');plt.close(fig)
