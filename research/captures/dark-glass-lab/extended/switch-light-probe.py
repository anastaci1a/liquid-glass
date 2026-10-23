from pathlib import Path
import json,numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study

class LightProbe:
 def __init__(self,study,p,co):
  self.study=study;self.p=p;self.H=study.crop[3]-study.crop[1];self.W=study.crop[2]-study.crop[0]
  self.z=np.empty((self.H*2,self.W*2,3),np.float32);self.d=np.empty((self.H*2,self.W*2),np.float32);self.angular=np.empty((self.H*2,self.W*2,5),np.float32)
  for row,bottom,W,x,y in study.raster_tiles():
   C,J=study.field(x,y,p);*_,(sd,nx,ny)=study.shape(x,y,p);core=J[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:]
   self.z[2*row:2*bottom]=C*gain+co[3:6]+(J[...,:-1]@co[6:-3])[...,None]
   self.d[2*row:2*bottom]=np.maximum(-sd,0);self.angular[2*row:2*bottom]=np.stack([np.ones_like(nx),nx,ny,nx*nx-ny*ny,2*nx*ny],-1)
 def set_width(self,w):self.basis=self.angular*np.exp(-(self.d/w)**2)[...,None]
 def render(self,v):
  q=self.basis@np.asarray(v,dtype=np.float32).reshape(5,2)
  extra=np.stack([q[...,0],-.5*q[...,0]+q[...,1],-.5*q[...,0]-q[...,1]],-1)
  out=np.clip(self.z+extra,0,1).reshape(self.H,2,self.W,2,3).mean((1,3))
  sigma=self.study.kernel_sigma(self.p,'post_sigma')
  return cv2.GaussianBlur(out,(0,0),sigma) if sigma>.001 else out

root=Path('/evidence/extended/active-switch/paired');state=json.loads((root/'pass-06.json').read_text())['current'];out=root.parent/'colored-light-probe';out.mkdir(exist_ok=True)
studies=[Study(root/n) for n in ['a','b']];p=state['parameters'];co=np.array(state['material']);probes=[LightProbe(s,p,co) for s in studies];records=[]
for width in [.015,.04,.1]:
 for probe in probes:probe.set_width(width)
 for s,probe in zip(studies,probes):assert np.max(abs(probe.render(np.zeros(10))-s.render(p,co)))<2e-6
 calls=0;cache={}
 def evaluate(v):
  global calls
  key=np.asarray(v).tobytes()
  if key not in cache:
   cache.clear();cache[key]=[s.scores(probe.render(v),include_ssim=False) for s,probe in zip(studies,probes)];calls+=1
  return cache[key]
 scale=np.mean([s['loss'] for s in state['scores']])
 def objective(v):return np.mean([s['loss'] for s in evaluate(v)])/scale
 def constraints(v):return np.array([t for a,b in zip(evaluate(v),state['scores']) for t in [(b['loss']-a['loss'])/scale,(b['glass']['rmse']**2-a['glass']['rmse']**2)/scale]])
 fit=minimize(objective,np.zeros(10),method='SLSQP',bounds=[(-.2,.2)]*10,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=35,ftol=1e-9,eps=2e-5))
 best=None
 for factor in [1,.5,.25,.125,.0625,.03125]:
  v=fit.x*factor;scores=evaluate(v);allowed=all(a['loss']<=b['loss']+1e-8 and a['glass']['rmse']<=b['glass']['rmse']+1e-8 for a,b in zip(scores,state['scores']))
  if allowed and (best is None or sum(s['loss'] for s in scores)<sum(s['loss'] for s in best['scores'])):best=dict(coefficients=v.tolist(),scores=scores)
 record=dict(width=width,evaluations=calls,best=best);records.append(record);print(json.dumps(record),flush=True)
 (out/'running.json').write_text(json.dumps(records,indent=2)+'\n')
valid=[r for r in records if r['best']];best=min(valid,key=lambda r:sum(s['loss'] for s in r['best']['scores'])) if valid else None
if best:
 for s,probe,n in zip(studies,probes,['a','b']):probe.set_width(best['width']);s.comparison(probe.render(best['best']['coefficients']),out/f'{n}.png',p)
report=dict(baseline_pass=6,baseline=state['scores'],trials=records,best=best,model='Add before clipping/subpixel integration/output blur: exp(-(d/width)^2)*[1,nx,ny,nx^2-ny^2,2nxny] @ V @ Q, V5x2, Q=[[1,-.5,-.5],[0,1,-1]]. One shared chromatic directional illumination layer; zero mean RGB before clipping, not a recovered Fresnel environment.',status='Exploratory, unadopted and uncounted. Fixed geometry/source/transmission, both native loss/glass gates; retest current state before adoption.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
