from pathlib import Path
import json,time
import cv2,numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import minimize
from extended_fit import Study,KNOTS
from source_support import masks,kernel_safe,fraction

class SpectralStudy(Study):
 def field(self,x,y,p):
  X,Y,d,J=self.geometry_field(x,y,p);*_,r,(sd,nx,ny)=self.shape(x,y,p)
  B=BSpline.design_matrix(np.clip(d/r,0,1).ravel(),KNOTS,3).toarray()[:,:7].reshape((*x.shape,7));v=np.array(p['spectral_profile']);a=B@v[:7];dx=a*nx+v[7]*x;dy=a*ny+v[8]*y;texture=self.blur(self.kernel_sigma(p));channels=[]
  for c,sign in enumerate([1,0,-1]):
   xx=((X+sign*dx)*self.L+self.case['center'][0]).astype(np.float32);yy=((Y+sign*dy)*self.L+self.case['center'][1]).astype(np.float32);color=cv2.remap(texture[:,:,c],xx,yy,cv2.INTER_LINEAR)
   if p.get('blur_transition',0)>1e-8:
    clear=cv2.remap(self.source[:,:,c],xx,yy,cv2.INTER_LINEAR);u=np.clip(d/p['blur_transition'],0,1);blend=u**3*(u*(6*u-15)+10);color=clear+(color-clear)*blend
   channels.append(color)
  return np.maximum(np.stack(channels,-1),0)**p['gamma'],J

class SpectralCache:
 def __init__(self,s,p,co):
  from material_context import matrix
  co=matrix(s,p)@co
  self.s=s;self.p=p;self.co=co;self.H=s.crop[3]-s.crop[1];self.W=s.crop[2]-s.crop[0];shape=(self.H*2,self.W*2)
  for n in ['X','Y','x','y','nx','ny','d','light']:setattr(self,n,np.empty(shape))
  self.basis=np.empty((*shape,7));self.gain=np.empty((*shape,3))
  for row,bottom,W,x,y in s.raster_tiles():
   where=slice(2*row,2*bottom);X,Y,d,J=s.geometry_field(x,y,p);*_,r,(sd,nx,ny)=s.shape(x,y,p);core=J[...,-1]
   for n,a in [('X',X),('Y',Y),('x',x),('y',y),('nx',nx),('ny',ny),('d',d)]:getattr(self,n)[where]=a
   self.basis[where]=BSpline.design_matrix(np.clip(d/r,0,1).ravel(),KNOTS,3).toarray()[:,:7].reshape((*x.shape,7));self.gain[where]=(1-core[...,None])*co[:3]+core[...,None]*co[-3:];self.light[where]=J[...,:-1]@co[6:-3]
  self.texture=s.blur(s.kernel_sigma(p));self.blend=None
  if p.get('blur_transition',0)>1e-8:u=np.clip(self.d/p['blur_transition'],0,1);self.blend=u**3*(u*(6*u-15)+10)
 def maps(self,v,native=False):
  if native:
   s=self.s;X,Y,d,J=s.geometry_field(s.x,s.y,self.p);*_,r,(sd,nx,ny)=s.shape(s.x,s.y,self.p);B=BSpline.design_matrix(np.clip(d/r,0,1).ravel(),KNOTS,3).toarray()[:,:7].reshape((*s.x.shape,7));a=B@v[:7];dx=a*nx+v[7]*s.x;dy=a*ny+v[8]*s.y
  else:X,Y=self.X,self.Y;a=self.basis@v[:7];dx=a*self.nx+v[7]*self.x;dy=a*self.ny+v[8]*self.y
  return [(((X+sign*dx)*self.s.L+self.s.case['center'][0]).astype(np.float32),((Y+sign*dy)*self.s.L+self.s.case['center'][1]).astype(np.float32)) for sign in [1,0,-1]]
 def render(self,v):
  channels=[]
  for c,(X,Y) in enumerate(self.maps(v)):
   color=cv2.remap(self.texture[:,:,c],X,Y,cv2.INTER_LINEAR)
   if self.blend is not None:clear=cv2.remap(self.s.source[:,:,c],X,Y,cv2.INTER_LINEAR);color=clear+(color-clear)*self.blend
   channels.append(color)
  C=np.maximum(np.stack(channels,-1),0)**self.p['gamma'];out=np.clip(C*self.gain+self.co[3:6]+self.light[...,None],0,1).reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32);sigma=self.s.kernel_sigma(self.p,'post_sigma')
  if sigma>.001:out=cv2.GaussianBlur(out,(0,0),sigma)
  from grazing_reflection import apply
  return apply(self.s,self.p,out)
 def support(self,v):
  defined,_=masks(self.s);safe,_=kernel_safe(defined,self.s,self.p)
  return min(fraction(safe,X,Y,self.s.valid) for X,Y in self.maps(v,True))

root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'spectral-reflection-probe';out.mkdir(exist_ok=True);start=time.time();co=np.array(old['material']);studies=[Study(root/n) for n in ['a','b']];caches=[SpectralCache(s,old['parameters'],co) for s in studies]
for s,c in zip(studies,caches):assert np.max(abs(s.render(old['parameters'],co)-c.render(np.zeros(9))))<2e-6
memo={};calls=0;best=None;scale=np.mean([m['loss'] for m in old['scores']])
def evaluate(v):
 global calls,best
 key=np.asarray(v).tobytes()
 if key not in memo:
  memo.clear();metrics=[s.scores(c.render(v),include_ssim=False) for s,c in zip(studies,caches)];memo[key]=metrics;calls+=1
  allowed=all(a['loss']<=b['loss']+1e-8 and a['glass']['rmse']<=b['glass']['rmse']+1e-8 for a,b in zip(metrics,old['scores']))
  if allowed and (best is None or sum(m['loss'] for m in metrics)<sum(m['loss'] for m in best['scores'])):
   best=dict(parameters=np.asarray(v).tolist(),scores=metrics)
  if calls%100==0:
   record=dict(calls=calls,seconds=time.time()-start,best=best);(out/'running.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
 return memo[key]
def objective(v):return np.mean([m['loss'] for m in evaluate(v)])/scale
def constraints(v):return np.array([x for a,b in zip(evaluate(v),old['scores']) for x in [(b['loss']-a['loss'])/scale,(b['glass']['rmse']**2-a['glass']['rmse']**2)/scale]])
fit=minimize(objective,np.zeros(9),method='SLSQP',bounds=[(-.5,.5)]*7+[(-.1,.1)]*2,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=35,ftol=1e-9,eps=.001))
verified=None
if best:
 v=np.array(best['parameters']);support=[c.support(v) for c in caches]
 if min(support)>=.999:
  full=[]
  for s,c,n in zip(studies,caches,['a','b']):
   fresh=SpectralStudy(s.folder);p={**old['parameters'],'spectral_profile':v.tolist()};pred=fresh.render(p,co);assert np.max(abs(pred-c.render(v)))<2e-6;full.append(fresh.scores(pred));fresh.comparison(pred,out/f'{n}.png',p)
  if all(a['loss']<=b['loss']+1e-8 and a['glass']['rmse']<=b['glass']['rmse']+1e-8 for a,b in zip(full,old['scores'])):verified=dict(parameters=v.tolist(),scores=full,support=support)
report=dict(baseline_pass=23,baseline=old['scores'],evaluations=calls,seconds=time.time()-start,verified=verified,best_cached=best,model='F_c=F+sign_c*(B(d/r)@beta*n+[kx*x,ky*y]), signs(1,0,-1),7 shared spline derivatives plus2 center derivatives; first-order RGB spectral field, not recovered physical IOR. Fixed shared material.',status='Private unadopted hypothesis; no extra formal pass count.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
