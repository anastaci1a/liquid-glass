"""True-distance height map projection; map fit only proposes geometry."""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.interpolate import BSpline
from scipy.optimize import least_squares
from extended_fit import Study,KNOTS
from switch_euclidean_surface import EuclideanSurfaceStudy
from crowned_footprint import field
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';checked=json.loads((out/'invariants.json').read_text());assert checked['passed'];old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=old['parameters'];items=[];AA=[];DD=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);v=EuclideanSurfaceStudy(s.folder);_,_,half,r,_=s.shape(np.array([0.]),np.array([0.]),p)
 y,x=np.mgrid[-half[1]:half[1]:61j,-half[0]:half[0]:81j];T,*_=field(x,y,half,p['crown_softness']);mask=T<.99;x=x[mask];y=y[mask]
 X,Y,_,_=s.geometry_field(x+p['shape_dx'],y+p['shape_dy'],p);X-=p['shape_dx'];Y-=p['shape_dy'];inside,d,nx,ny=v.distance(x,y,half,p['crown_softness'],.75*r)
 B=BSpline.design_matrix(np.clip(d/(.75*r),0,1),KNOTS,3).toarray()[:,:7]
 Ax=np.column_stack([2*x/r,np.zeros_like(x),-B*nx[:,None]])*5*r;Ay=np.column_stack([np.zeros_like(x),2*y/r,-B*ny[:,None]])*5*r
 AA.extend([Ax,Ay]);DD.extend([X-x,Y-y]);items.append((name,s,v,half,x,y,X,Y))
seed=np.linalg.lstsq(np.concatenate(AA),np.concatenate(DD),rcond=None)[0];lo=np.r_[[-.08,-.08],np.full(7,-.35)];hi=-lo;seed=np.clip(seed,lo+1e-7,hi-1e-7)
def params(v):
 q=copy.deepcopy(p);q['euclidean_surface']=dict(t0=.8,bx=float(v[0]),by=float(v[1]),profile=v[2:].tolist(),width=.75,n=1.5,gap=10.8);return q
def residual(v):
 result=[];q=params(v)
 for name,s,t,half,x,y,X,Y in items:
  A,B,_,_=t.geometry_field(x+p['shape_dx'],y+p['shape_dy'],q);result.extend([A-p['shape_dx']-X,B-p['shape_dy']-Y])
 return np.concatenate(result)
fit=least_squares(residual,seed,bounds=(lo,hi),max_nfev=80,ftol=1e-9,xtol=1e-9,gtol=1e-9);q=params(fit.x);scores=[]
for name,s,t,half,x,y,X,Y in items:
 im=t.render(q,np.array(old['material']));m=t.scores(im);bm=s.scores(s.render(p,np.array(old['material'])));scores.append(dict(observation=name,E=float(np.sqrt(m['loss'])),ratio=float(np.sqrt(m['loss']/bm['loss'])),scores=m));print(name,scores[-1]['E'],flush=True)
(out/'projection.json').write_text(json.dumps(dict(parameters=q,material=old['material'],seed=seed.tolist(),native=scores,map_rmse=float(np.sqrt(np.mean(fit.fun**2))),evaluations=fit.nfev,optimality=float(fit.optimality),success=bool(fit.success),accepted=False,limits=__doc__),indent=2)+'\n');print('MAP',np.sqrt(np.mean(fit.fun**2)),fit.optimality,flush=True)
