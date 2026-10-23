"""Source-derived directional grazing reflection blended with transmission."""
from pathlib import Path
import json,time
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from render import shade
from material_context import matrix
from paired_fit import permitted
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-22.json').read_text())['current'];out=root.parent/'grazing-probe';out.mkdir(exist_ok=True);start=time.time();studies=[Study(root/n) for n in ['a','b']]
class Cache:
 def __init__(self,s):
  self.s=s;p=old['parameters'];x0,y0,x1,y1=s.crop;self.H=y1-y0;self.W=x1-x0;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-s.case['center'][0])/s.L;y=(yy-.25-s.case['center'][1])/s.L;C,J=s.field(x,y,p);self.base=shade(C,J,matrix(s,p)@np.array(old['material']));*_,(sd,self.nx,self.ny)=s.shape(x,y,p);self.d=np.maximum(-sd,0)
  # The local incident field is an explicitly approximate environment proxy:
  # lightly scattered unrefracted source RGB at the footprint, not target RGB.
  E=cv2.GaussianBlur(s.source,(0,0),s.L*.007)
  self.env=cv2.remap(E,(xx-.25).astype(np.float32),(yy-.25).astype(np.float32),cv2.INTER_LINEAR)
 def render(self,v):
  a,w,power=v;f=a*np.exp(-(self.d/w)**2)*np.maximum((1+self.ny)*.5,0)**power
  z=self.base*(1-f[...,None])+self.env*f[...,None];pred=z.reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32);sigma=self.s.kernel_sigma(old['parameters'],'post_sigma');return cv2.GaussianBlur(pred,(0,0),sigma) if sigma>.001 else pred
caches=[Cache(s) for s in studies]
for s,c in zip(studies,caches):assert np.max(abs(s.render(old['parameters'],np.array(old['material']))-c.render([0,.01,1])))<2e-6
calls=0;best=None;trials=[];memo={};scale=np.mean([m['loss'] for m in old['scores']])
def evaluate(v):
 global calls,best
 key=np.asarray(v).tobytes()
 if key not in memo:
  memo.clear();metric=[s.scores(c.render(v),include_ssim=False) for s,c in zip(studies,caches)];memo[key]=metric;calls+=1;allowed=permitted(metric,old['scores'])
  if allowed and (best is None or sum(m['loss'] for m in metric)<sum(m['loss'] for m in best['scores'])):best=dict(parameters=np.asarray(v).tolist(),scores=metric)
 return memo[key]
def obj(v):return np.mean([m['loss'] for m in evaluate(v)])/scale
def constraints(v):return np.array([x for m,b in zip(evaluate(v),old['scores']) for x in [(b['loss']-m['loss'])/scale,(b['glass']['rmse']**2-m['glass']['rmse']**2)/scale]])
for width in [.003,.006,.012,.024,.05]:
 for amplitude in [.1,.3,.6,1.]:
  v=[amplitude,width,1.];m=evaluate(v);trials.append(dict(parameters=v,losses=[q['loss'] for q in m],allowed=permitted(m,old['scores'])))
 fit=minimize(obj,[.3,width,1],method='SLSQP',bounds=[(0,1),(.001,.1),(.2,8)],constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=30,ftol=1e-10,eps=.0001));evaluate(fit.x);print(json.dumps(dict(width=width,calls=calls,best=best)),flush=True)
for n,s,c in zip(['a','b'],studies,caches):
 v=best['parameters'] if best else [0,.01,1];s.comparison(c.render(v),out/f'{n}.png',old['parameters'])
report=dict(baseline_pass=22,baseline=old['scores'],model='Cout=(1-F)Ctransmitted+F E; F=a exp(-(d/w)^2)*((1+ny)/2)^p,0<=a<=1. E=Gaussian(unrefracted source,sigma=.007L), an incident-environment proxy. Normal orientation expresses one shared directional light lobe; no target pixels or region-specific correction.',best=best,trials=trials,evaluations=calls,seconds=time.time()-start,limits='Empirical reflected-field approximation, not a ray-traced environmental reconstruction or Apple formula. New source coverage/HQ/cache equations require verification before adoption.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
