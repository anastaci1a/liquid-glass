"""Separate refracted RGB transmission while keeping material lighting fixed.

A dense half-pixel atlas proposes parameters only; every retention requires
full native analytic-field replay. No published model/score masks are changed.
"""
from pathlib import Path
import json,time
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import permitted
from render import shade
from material_context import matrix
from grazing_reflection import apply
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'transmission-dispersion-probe';out.mkdir(exist_ok=True);start=time.time();co=np.array(old['material'])
def weight(s,p,x,v):
 strength,length,angle,center,width=v;axis=(x-p.get('shape_dx',0))/(s.half[0]+p.get('half_x_delta',0));u=np.clip((axis-center)/width+.5,0,1);return strength*(1-u**3*(u*(6*u-15)+10))
class ChromaticStudy(Study):
 def field(self,x,y,p):
  C,J=super().field(x,y,p);v=p.get('directional_transmission')
  if v is None or v[0]==0 or abs(v[1])<1e-12:return C,J
  w=weight(self,p,x,v);_,length,angle,_,_=v;texture=self.blur(self.kernel_sigma(p));D=C.copy()
  for channel,sign in [(0,1),(2,-1)]:
   qx=x+sign*length*np.cos(angle);qy=y+sign*length*np.sin(angle);X,Y,_,_=self.geometry_field(qx,qy,p);*_,(sd,_,_)=self.shape(qx,qy,p);X=np.where(sd<=0,X,qx);Y=np.where(sd<=0,Y,qy)
   sample=cv2.remap(texture[:,:,channel],(X*self.L+self.case['center'][0]+self.backdrop_shift[0]).astype(np.float32),(Y*self.L+self.case['center'][1]+self.backdrop_shift[1]).astype(np.float32),cv2.INTER_LINEAR);D[...,channel]=np.maximum(sample,0)**p['gamma']
  return C*(1-w[...,None])+D*w[...,None],J
class Cache:
 def __init__(self,s):
  self.s=s;self.p=old['parameters'];x0,y0,x1,y1=s.crop;self.H=y1-y0;self.W=x1-x0;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];self.x=(xx-.25-s.case['center'][0])/s.L;self.y=(yy-.25-s.case['center'][1])/s.L;self.C,J=s.field(self.x,self.y,self.p);*_,(sd,_,_)=s.shape(self.x,self.y,self.p);texture=s.blur(s.kernel_sigma(self.p));env=cv2.remap(texture,(xx-.25).astype(np.float32),(yy-.25).astype(np.float32),cv2.INTER_LINEAR);self.atlas=np.where((sd<=0)[...,None],self.C,np.maximum(env,0)**self.p['gamma']);effective=matrix(s,self.p)@co;core=J[...,-1];self.gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:];self.light=effective[3:6]+(J[...,:-1]@effective[6:-3])[...,None];self.iy,self.ix=np.mgrid[:self.H*2,:self.W*2].astype(np.float32)
 def render(self,v):
  s=self.s;p=self.p;w=weight(s,p,self.x,v);_,length,angle,_,_=v;D=self.C.copy()
  if abs(length)>1e-12:
   for c,sign in [(0,1),(2,-1)]:D[...,c]=cv2.remap(self.atlas[:,:,c],self.ix+np.float32(sign*length*np.cos(angle)*s.L*2),self.iy+np.float32(sign*length*np.sin(angle)*s.L*2),cv2.INTER_LINEAR)
  C=self.C*(1-w[...,None])+D*w[...,None];pred=np.clip(C*self.gain+self.light,0,1).reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32);sigma=s.kernel_sigma(p,'post_sigma')
  if sigma>.001:pred=cv2.GaussianBlur(pred,(0,0),sigma)
  return apply(s,p,pred)
studies=[ChromaticStudy(root/n) for n in ['a','b']];caches=[Cache(s) for s in studies]
for s,c in zip(studies,caches):assert np.max(abs(c.render([0,0,0,-.5,.15])-s.render(old['parameters'],co)))<2e-6
calls=0;memo={};best=None;scale=np.mean([m['loss'] for m in old['scores']]);trials=[]
def evaluate(v):
 global calls,best
 key=np.asarray(v).tobytes()
 if key not in memo:
  memo.clear();metrics=[s.scores(c.render(v),include_ssim=False) for s,c in zip(studies,caches)];memo[key]=metrics;calls+=1
  if permitted(metrics,old['scores']) and (best is None or sum(m['loss'] for m in metrics)<sum(m['loss'] for m in best['proposal_scores'])):best=dict(parameters=np.asarray(v).tolist(),proposal_scores=metrics)
  if calls%100==0:(out/'running.json').write_text(json.dumps(dict(calls=calls,best=best,seconds=time.time()-start),indent=2)+'\n');print(json.dumps(dict(calls=calls,best=best)),flush=True)
 return memo[key]
def f(v):return np.mean([m['loss'] for m in evaluate(v)])/scale
def g(v):return np.array([a for m,b in zip(evaluate(v),old['scores']) for a in [(b['loss']-m['loss'])/scale,(b['glass']['rmse']**2-m['glass']['rmse']**2)/scale]])
verified=None
for angle in [np.arctan2(2,1),-np.arctan2(2,1)]:
 for sign in [1,-1]:
  initial=[.6,sign*.025,angle,-.5,.15];fit=minimize(f,initial,method='SLSQP',bounds=[(0,1),(-.08,.08),(angle-.25,angle+.25),(-.8,-.25),(.02,.6)],constraints=[dict(type='ineq',fun=g)],options=dict(maxiter=25,ftol=1e-9,eps=.001));checks=[]
  if best:
   for alpha in [1,.5,.25,.125]:
    v=np.array(best['parameters']);v[0]*=alpha;p={**old['parameters'],'directional_transmission':v.tolist()};metrics=[s.scores(s.render(p,co),include_ssim=False) for s in studies];allowed=permitted(metrics,old['scores']);checks.append(dict(alpha=alpha,scores=metrics,allowed=allowed))
    if allowed and (verified is None or sum(m['loss'] for m in metrics)<sum(m['loss'] for m in verified['scores'])):
     verified=dict(parameters=v.tolist(),scores=metrics)
     for n,s in zip(['a','b'],studies):s.comparison(s.render(p,co),out/f'{n}.png',p)
  trials.append(dict(initial=initial,solver_success=bool(fit.success),native_checks=checks));(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n');(out/'verified.json').write_text(json.dumps(verified,indent=2)+'\n')
report=dict(model='C_lambda=(1-w(x))*B_lambda(F(x))^gamma+w(x)*B_lambda(F(x+s_lambda*length*u))^gamma, s_R=1,s_G=0,s_B=-1. F(q)=q outside footprint for shifted rays. Common lighting remains J(x), no shifted highlight. Output blur and pass23 reflection follow. w is a horizontally fading contribution, not shrinking dispersion length.',baseline=old['scores'],proposal=best,verified=verified,trials=trials,calls=calls,seconds=time.time()-start,status='Private analytic native-verified hypothesis; source-footprint and HQ checks still required before adoption.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
