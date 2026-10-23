"""Private output-space chromatic dispersion with a fading contribution.

Kernel direction/length do not vary with x; blend weight fades horizontally.
Reflection remains the accepted separate pass23 field. This is an empirical
post-refraction model, not an inferred proprietary shader or physical solid.
"""
from pathlib import Path
import json,time
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import permitted
from grazing_reflection import layers
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'directional-clear-dispersion-probe';out.mkdir(exist_ok=True);studies=[Study(root/n) for n in ['a','b']];co=np.array(old['material']);start=time.time()
class Cache:
 def __init__(self,s):
  self.s=s;p={k:v for k,v in old['parameters'].items() if k!='grazing_reflection'};self.T=s.render(p,co);self.F,self.E=layers(s,old['parameters']);x0,y0,x1,y1=s.crop;Y,X=np.mgrid[y0:y1,x0:x1].astype(np.float32);self.X=X-x0;self.Y=Y-y0;self.axis=(X-s.case['center'][0])/(s.L*(s.half[0]+p.get('half_x_delta',0)));self.cov=s.shape_coverage(p);B=cv2.remap(s.source,X,Y,cv2.INTER_LINEAR);self.clear=s.render({**p,'sigma':0.},co);self.H=self.clear*self.cov[...,None]+B*(1-self.cov[...,None]);self.H=np.asarray(self.H,np.float32)
 def render(self,v):
  strength,length,angle,center,width=v;u=np.clip((self.axis-center)/width+.5,0,1);S=u**3*(u*(6*u-15)+10);weight=strength*(1-S);direction=np.array([np.cos(angle),np.sin(angle)])*length*self.s.L
  if abs(length)<1e-12:D=self.clear
  else:
   D=np.stack([cv2.remap(self.H[:,:,c],self.X+np.float32(sign*direction[0]),self.Y+np.float32(sign*direction[1]),cv2.INTER_LINEAR) for c,sign in enumerate([1,0,-1])],-1)
  T=self.T*(1-weight[...,None])+D*weight[...,None];return (T*(1-self.F[...,None])+self.E*self.F[...,None]).astype(np.float32)
caches=[Cache(s) for s in studies]
for s,c in zip(studies,caches):assert np.max(abs(s.render(old['parameters'],co)-c.render([0,0,0,-.5,.1])))<2e-6
calls=0;memo={};best=None;scale=np.mean([m['loss'] for m in old['scores']]);history=[]
def evaluate(v):
 global calls,best
 key=np.asarray(v).tobytes()
 if key not in memo:
  memo.clear();metric=[s.scores(c.render(v),include_ssim=False) for s,c in zip(studies,caches)];memo[key]=metric;calls+=1
  if permitted(metric,old['scores']) and (best is None or sum(m['loss'] for m in metric)<sum(m['loss'] for m in best['scores'])):
   best=dict(parameters=np.asarray(v).tolist(),scores=metric)
   (out/'best.json').write_text(json.dumps(best,indent=2)+'\n')
  if calls%100==0:
   (out/'running.json').write_text(json.dumps(dict(calls=calls,seconds=time.time()-start,best=best),indent=2)+'\n');print(json.dumps(dict(calls=calls,best=best)),flush=True)
 return memo[key]
def obj(v):return np.mean([m['loss'] for m in evaluate(v)])/scale
def g(v):return np.array([x for a,b in zip(evaluate(v),old['scores']) for x in [(b['loss']-a['loss'])/scale,(b['glass']['rmse']**2-a['glass']['rmse']**2)/scale]])
# First test the reported orientation, its mirrored screen-coordinate reading,
# then the earlier vertical/diagonal controls. No painted colored patch.
for angle in [np.arctan2(2,1),-np.arctan2(2,1),np.pi/2]:
 for sign in [1,-1]:
  initial=np.array([.7,sign*.02,angle,-.5,.15]);raw=evaluate(initial);fit=minimize(obj,initial,method='SLSQP',bounds=[(0,1),(-.08,.08),(angle-.12,angle+.12),(-.8,-.25),(.02,.6)],constraints=[dict(type='ineq',fun=g)],options=dict(maxiter=25,ftol=1e-9,eps=.001));metric=evaluate(fit.x);history.append(dict(initial=initial.tolist(),initial_losses=[m['loss'] for m in raw],final=fit.x.tolist(),final_losses=[m['loss'] for m in metric],success=bool(fit.success)));(out/'trials.json').write_text(json.dumps(history,indent=2)+'\n')
 if best:
  for n,s,c in zip(['a','b'],studies,caches):s.comparison(c.render(best['parameters']),out/f'{n}.png',old['parameters'])
report=dict(model='Ctrans=(1-w(x))*T_sourceblur+w(x)*RGB[T_clear_R(x+length*u),T_clear_G(x),T_clear_B(x-length*u)],w=a*(1-S((x/halfwidth-center)/width+.5)); kernel fixed, contribution fades. Exterior context supplies shifted samples outside the footprint. Pass23 reflected field follows this operation.',baseline=old['scores'],best=best,trials=history,calls=calls,seconds=time.time()-start,status='Private unadopted hypothesis; normalized lengths, native gates, no physical/proprietary exactness claim.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
