"""Compare a center-flat C2 front edge to the failed broad elliptical crown.
Low-cost proposal only, with fixed material/backside/source/blur and guards.
"""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_two_surface import TwoSurfaceStudy
from material_context import effective
from grazing_reflection import layers
from render import shade
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'physical-two-surface'
seed=json.loads((root/'physical-euclidean-surface/native-settlement.json').read_text());p0=seed['parameters'];co=np.array(seed['material']);rows=[]
for name in ['a','b']:
 s=TwoSurfaceStudy(root/'paired'/name);idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];target=s.target_crop.reshape(-1,3)[idx];rim=s.rim.ravel()[idx]
 w,env=layers(s,p0);w=w.ravel()[idx,None];env=env.reshape(-1,3)[idx];h=np.sqrt(2)*s.kernel_sigma(p0,'post_sigma')/s.L
 dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);values=[]
 for a in [0.,-.01,-.002,.002,.01]:
  p=copy.deepcopy(p0);p.update(front_crown=a,front_profile='rim',front_width=.3)
  try:
   C,J=s.field(x[:,None]+dx.ravel(),y[:,None]+dy.ravel(),p);im=shade(C,J,effective(s,p,co)).mean(1);im=im*(1-w)+env*w;e=(im-target)*255
   glass=float(np.mean(e**2));edge=float(np.mean(e[rim]**2));row=dict(amplitude=a,proposal_E=float(np.sqrt(.7*glass+.3*edge)),glass_rmse=float(np.sqrt(glass)),rim_rmse=float(np.sqrt(edge)))
  except ValueError as e:row=dict(amplitude=a,rejected=str(e))
  values.append(row);print(name,row,flush=True);s.distance_cache.clear()
 rows.append(dict(observation=name,trials=values))
with (out/'front-rim-proposal.json').open('x') as f:json.dump(dict(rows=rows,method=__doc__,accepted=False),f,indent=2)
