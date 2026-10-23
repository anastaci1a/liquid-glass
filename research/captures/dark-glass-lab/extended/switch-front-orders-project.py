"""Map-space feasibility screen; not a target-image fit or accepted pass."""
import sys,json,copy
power=int(sys.argv[1])
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import least_squares
from extended_fit import Study
from switch_front_surface import mapping,FrontSurfaceStudy as BackSurfaceStudy
from crowned_footprint import field
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'physical-front-surface';old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=old['parameters'];items=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);_,_,half,r,_=s.shape(np.array([0.]),np.array([0.]),p)
 y,x=np.mgrid[-half[1]:half[1]:61j,-half[0]:half[0]:81j];T,*_=field(x,y,half,p['crown_softness']);mask=T<.99;x=x[mask];y=y[mask]
 X,Y,_,_=s.geometry_field(x+p['shape_dx'],y+p['shape_dy'],p);items.append((name,s,half,x,y,X-p['shape_dx'],Y-p['shape_dy']))
def params(v):return dict(t=v[0],bx=v[1],by=v[2],g=v[3],n=1.5,edge_power=power)
def residual(v):
 result=[]
 for name,s,half,x,y,X,Y in items:
  A,B,_=mapping(x,y,half,p['crown_softness'],**params(v));result.extend([A-X,B-Y])
 return np.concatenate(result)
fits=[]
for seed in [[.01,.02,.04,10],[.005,.01,.02,25],[.03,.03,.03,5]]:
 fit=least_squares(residual,seed,bounds=([.0002,0.,0.,.25],[.04,.04,.04,50]),max_nfev=100,ftol=1e-10,xtol=1e-10,gtol=1e-10)
 fits.append(dict(seed=seed,parameters=params(fit.x),map_rmse=float(np.sqrt(np.mean(fit.fun**2))),optimality=float(fit.optimality),evaluations=fit.nfev,success=bool(fit.success)))
best=min(fits,key=lambda a:a['map_rmse']);q=copy.deepcopy(p);q['physical_front_surface']=best['parameters'];scores=[]
for name,s,half,x,y,X,Y in items:
 t=BackSurfaceStudy(root/'paired'/name);im=t.render(q,np.array(old['material']));m=t.scores(im,include_ssim=False);scores.append(dict(observation=name,E=float(np.sqrt(m['loss'])),scores=m));cv2.imwrite(str(out/(name+'-front-order-'+str(power)+'-proposal.png')),np.round(np.clip(im,0,1)*255).astype(np.uint8)[:,:,::-1]);print(name,scores[-1]['E'],flush=True)
(out/('edge-order-'+str(power)+'-projection.json')).write_text(json.dumps(dict(method=__doc__,fits=fits,parameters=q,material=old['material'],native=scores,accepted=False,limits='Map closeness is a proposal heuristic; target native guards remain authoritative. No material refit; possible family limitations must be inspected.'),indent=2)+'\n');print(json.dumps(fits),flush=True)
