"""Necessary local flat-front single-back-surface check of accepted green map.
No image fit, score mutation, or claim about alternative surface/camera families.
"""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from extended_fit import Study
from surface_compatibility import compatibility_terms
root=Path('/evidence/extended/active-switch');out=root/'rev5-map-compatibility'
model=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=model['parameters'];rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);hx,hy=s.half
 x,y=np.meshgrid(np.linspace(-hx+.003,hx-.003,181),np.linspace(-hy+.003,hy-.003,121))
 *_,(sd,_,_)=s.shape(x,y,p);inside=sd<-.002
 def mapping(x,y):
  X,Y,_,_=s.geometry_field(x,y,p);return np.stack([X-x,Y-y],-1)
 v=mapping(x,y);results=[]
 for step in [2e-4,1e-4,5e-5]:
  dx=(mapping(x+step,y)-mapping(x-step,y))/(2*step);dy=(mapping(x,y+step)-mapping(x,y-step))/(2*step)
  c,m,k=compatibility_terms(v,dx,dy);Q=k-m*c
  det=(1+dx[...,0])*(1+dy[...,1])-dy[...,0]*dx[...,1]
  results.append((c,m,Q,det))
 c,m,Q,det=results[-1];dc=np.maximum(abs(c-results[-2][0]),abs(results[-2][0]-results[-3][0]));dq=np.maximum(abs(Q-results[-2][2]),abs(results[-2][2]-results[-3][2]))
 reliable=inside&(abs(c)>np.maximum(1e-7,100*dc))&(abs(Q)>np.maximum(1e-8,100*dq))
 impossible=reliable&(Q*c<0);possible=reliable&(Q*c>0)
 rows.append(dict(observation=name.upper(),sampled_inside=int(inside.sum()),reliable_nonzero_curl=int(reliable.sum()),necessary_branch_violation=int(impossible.sum()),necessary_branch_admitted=int(possible.sum()),unresolved=int((inside&~reliable).sum()),violation_fraction_of_all_inside=float(impossible.sum()/inside.sum()),negative_map_determinant_fraction=float(np.mean(det[inside]<0)),max_curl_derivative_step_difference=float(dc[inside].max()),max_Q_derivative_step_difference=float(dq[inside].max())))
 np.savez_compressed(out/f'{name}-diagnostics.npz',x=x,y=y,inside=inside,curl=c,Q=Q,reliable=reliable,violation=impossible,determinant=det)
record=dict(method=__doc__,parameters_sha256=hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),grid=[181,121],steps=[.0002,.0001,.00005],criterion='For reliable nonzero curl c, rho=K/c must exceed M; equivalently (K-Mc)*c>0. Necessary for every n>1 on the strictly transmitted branch. Unresolved small/step-sensitive quantities are not failures.',observations=rows,limits='Only sampled accepted unshifted green inverse map and declared orthographic flat-front/single-back surface. Fold is not total internal reflection. Violation rules out exact local reproduction in this family at reliable sampled points, not approximate image agreement, other cameras/front shapes, complete solids or Apple physics. Fixed image masks/scores untouched.')
with (out/'audit.json').open('x') as f:json.dump(record,f,indent=2)
print(json.dumps(rows),flush=True)
