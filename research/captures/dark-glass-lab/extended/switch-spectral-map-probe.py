"""RGB effective-wavelength dispersion comparator on frozen switch inputs.

F_lambda=x+(1+k_lambda)*(F_green-x), with optional constant directional
prism displacement. k follows a normalized inverse-wavelength-squared law.
This is an empirical paraxial comparator, not identified Apple spectral optics.
No painted colors, source mutation, or target-dependent spatial correction.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,material_trial
from render import shade
from material_context import effective
from grazing_reflection import apply as reflection
from source_support import coverage_report,supported
from progress_gate import evaluate
from PIL import Image
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'spectral-map-review';out.mkdir(exist_ok=True)
old=json.loads((root/'accepted.json').read_text());studies=[Study(root/n) for n in ['a','b']];co=np.array(old['material']);base=[s.scores(s.render(old['parameters'],co)) for s in studies]
# R/G/B effective wavelengths; scale puts the blue deviation at +1.
wavelength=np.array([.610,.550,.460]);k=(wavelength**-2-.550**-2)/(.460**-2-.550**-2)
class Atlas:
 def __init__(self,s,p):
  self.s=s;self.p=p;a,b,c,d=s.crop;self.H=d-b;self.W=c-a
  yy,xx=np.mgrid[b:d:.5,a:c:.5];self.x=(xx-.25-s.case['center'][0])/s.L;self.y=(yy-.25-s.case['center'][1])/s.L
  self.X,self.Y,self.d,self.J=s.geometry_field(self.x,self.y,p)
  self.dx=self.X-self.x;self.dy=self.Y-self.y;self.material=effective(s,p,co)
  core=self.J[...,-1];self.gain=(1-core[...,None])*self.material[:3]+core[...,None]*self.material[-3:]
  self.light=self.material[3:6]+(self.J[...,:-1]@self.material[6:-3])[...,None]
  # All terms independent of candidate spectral parameters are evaluated once.
  del self.J
  from grazing_reflection import layers
  self.ref_weight,self.environment=layers(s,p)
 def render(self,v):
  amount,prism,angle,left_strength,center,width=v;s=self.s;p=self.p
  u=np.clip((self.x/s.half[0]-center)/width+.5,0,1);w=left_strength*(1-u**3*(u*(6*u-15)+10))
  channels=[]
  for c,disp in enumerate(k):
   X=self.X+disp*(amount*self.dx+prism*np.cos(angle)*w);Y=self.Y+disp*(amount*self.dy+prism*np.sin(angle)*w)
   value=cv2.remap(s.source[:,:,c],(X*s.L+s.case['center'][0]).astype(np.float32),(Y*s.L+s.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR)
   channels.append(np.maximum(value,0)**p['gamma'])
  C=np.stack(channels,-1);pred=np.clip(C*self.gain+self.light,0,1).reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32)
  return pred*(1-self.ref_weight[...,None])+self.environment*self.ref_weight[...,None]
p=copy.deepcopy(old['parameters']);p.pop('directional_transmission');p.update(sigma=0.,post_sigma=0.)
# Thin-rim geometry and photometry frozen during the first diagnostic family.
atlases=[Atlas(s,p) for s in studies];bounds=[(0,.3),(-.15,.15),(.3,1.7),(0,1),(-.8,-.25),(.04,.65)];start=time.time();rows=[];baseline=np.array([b['loss'] for b in base]);best=None;calls=0
for stage,initial in enumerate([[.035,.035,1.1,.6,-.5,.25],[.1,-.045,1.1,.6,-.5,.25],[.01,0.,1.1,0.,-.5,.25]],1):
 local=[float('inf'),None,None]
 def f(v):
  global calls
  metrics=[s.scores(a.render(v),include_ssim=False) for s,a in zip(studies,atlases)];calls+=1
  loss=float(np.mean([m['loss']/b['loss'] for m,b in zip(metrics,base)]))
  if calls%25==0:print(json.dumps(dict(evaluations=calls,objective=loss,seconds=time.time()-start)),flush=True)
  if loss<local[0]:local[:]=[loss,np.array(v),metrics]
  return loss
 fit=minimize(f,initial,method='Powell',bounds=bounds,options=dict(maxfev=220,xtol=.001,ftol=1e-5));loss,v,metrics=local
 row=dict(stage=stage,parameters=v.tolist(),scores=metrics,baseline=base,objective=loss,ordinary_blur=0,accepted=False)
 rows.append(row);(out/f'trial-{stage}.json').write_text(json.dumps(row,indent=2)+'\n')
 for label,s,a in zip(['a','b'],studies,atlases):
  pred=a.render(v);x0,y0,x1,y1=s.crop;cov=s.shape_coverage(p);bg=s.source[y0:y1,x0:x1].copy();q=p['shadow'];*_,(sd,_,_)=s.shape(s.x-q['offset'][0],s.y-q['offset'][1],p);bg*=1-q['opacity']*np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2)[...,None];image=pred*cov[...,None]+bg*(1-cov[...,None]);Image.fromarray(np.uint8(np.rint(np.clip(image,0,1)*255))).save(out/f'trial-{stage}-{label}.png')
 print(json.dumps(dict(stage=stage,parameters=v.tolist(),loss=[m['loss'] for m in metrics],glass=[m['glass']['rmse'] for m in metrics],seconds=time.time()-start)),flush=True)
(out/'review.json').write_text(json.dumps(dict(rows=rows,qualified_passes=0,limits='Shared effective RGB-wavelength map, no ordinary blur, same geometry/material for both backgrounds. Proxy effective wavelengths are not recovered display spectra. No per-pixel correction, acceptance or source mutation.'),indent=2)+'\n')
