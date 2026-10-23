"""Bounded direct photometric proposals, avoiding unsupported map-space targets.
Frozen train positions/16-offset output-kernel quadrature propose only; full
native4sample render and original glass/rim/masks decide. Material stays fixed.
"""
import sys,json,copy,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from switch_front_surface import FrontSurfaceStudy
from material_context import effective
from render import shade
from grazing_reflection import layers
cv2.setNumThreads(1);power=int(sys.argv[1]);root=Path('/evidence/extended/active-switch');out=root/'physical-front-surface';old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p0=old['parameters'];co=np.array(old['material']);S=[Study(root/'paired'/n) for n in ['a','b']];P=[FrontSurfaceStudy(s.folder) for s in S];probes=[]
for s in S:
 idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];h=np.sqrt(2)*s.kernel_sigma(p0,'post_sigma')/s.L;dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);w,env=layers(s,p0)
 probes.append(dict(x=x[:,None]+dx.ravel(),y=y[:,None]+dy.ravel(),target=s.target_crop.reshape(-1,3)[idx],rim=s.rim.ravel()[idx],co=effective(s,p0,co),w=w.ravel()[idx,None],env=env.reshape(-1,3)[idx]))
def measure(studies,p):
 vals=[]
 for s,q in zip(studies,probes):
  C,J=s.field(q['x'],q['y'],p);rgb=shade(C,J,q['co']).mean(1);rgb=rgb*(1-q['w'])+q['env']*q['w'];e=(rgb-q['target'])*255;vals.append(.7*np.mean(e**2)+.3*np.mean(e[q['rim']]**2))
 return np.array(vals)
base=measure(S,p0);rows=[];calls=0;best=(np.inf,None)
lo=np.array([.0002,0.,0.,.25]);hi=np.array([.04,.04,.04,50.]);scales=np.array([.02,.02,.02,10.])
def params(v):
 p=copy.deepcopy(p0);p['physical_front_surface']=dict(zip(['t','bx','by','g'],map(float,v)));p['physical_front_surface'].update(n=1.5,edge_power=power);return p
def objective(v):
 global calls,best
 calls+=1;value=float(np.max(measure(P,params(v*scales))/base))
 if value<best[0]:best=(value,v.copy()*scales)
 if calls%20==0:print('PROPOSAL',power,calls,value,best[0],flush=True)
 return value
for seed in [[.005,.02,.04,10],[.015,.015,.03,5]]:
 before=calls;fit=minimize(objective,np.array(seed)/scales,method='Powell',bounds=list(zip(lo/scales,hi/scales)),options=dict(maxfev=150,xtol=.0005,ftol=1e-5));rows.append(dict(seed=seed,evaluations=calls-before,success=bool(fit.success),message=str(fit.message),proposal_ratio=float(fit.fun),solution=(fit.x*scales).tolist()))
p=params(best[1]);native=[]
for s,b in zip(P,S):
 im=s.render(p,co);m=s.scores(im);bm=b.scores(b.render(p0,co));native.append(dict(scores=m,E=float(np.sqrt(m['loss'])),ratio=float(np.sqrt(m['loss']/bm['loss'])),whole_glass_nonregression=m['glass']['rmse']<=bm['glass']['rmse']))
report=dict(parameters=p,material=co.tolist(),method=__doc__,initial_proposal_losses=base.tolist(),proposals=rows,best_proposal_ratio=best[0],native=native,accepted=False,numeric_pass=all(v['ratio']<=.995 and v['whole_glass_nonregression'] for v in native),limits='Photometric proposal bounded/local, no global exhaustion claim. Existing source/masks unchanged. Original exterior/actual-source/HQ/visual checks additionally required if qualified.')
(out/('edge-order-'+str(power)+'-photometric.json')).write_text(json.dumps(report,indent=2)+'\n');print('NATIVE',power,[(v['E'],v['ratio']) for v in native],flush=True)
