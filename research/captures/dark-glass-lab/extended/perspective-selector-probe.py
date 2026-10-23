"""Perspective two-interface transmission with a screen-centered camera.

Background coordinates are projected back to the input image plane; n=1 must
be identity. This is a physical-map hypothesis, not an acceptance promotion.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.optimize import least_squares
from extended_fit import Study
from crowned_footprint import field
from solid import interface
from PIL import Image
folder=Path('/evidence/extended/active-segmented-selector');out=folder/'perspective-crown-probe';out.mkdir(exist_ok=True)

class Perspective(Study):
 def height(self,x,y,p):
  T,Tx,Ty=field(x,y,self.half,p['crown_softness']);inside=T<=1
  T0=np.clip(T,0,1);m=p['shoulder'];S=1-T0**m
  C=1-p['crown_x']*(x/self.half[0])**2-p['crown_y']*(y/self.half[1])**2
  H=p['height'];hx=H*(-m*T0**(m-1)*Tx*C-S*2*p['crown_x']*x/self.half[0]**2)
  hy=H*(-m*T0**(m-1)*Ty*C-S*2*p['crown_y']*y/self.half[1]**2)
  return np.where(inside,H*S*C,0),hx,hy,inside
 def raymap(self,x,y,p):
  H=p['height'];D=H+p['gap'];n=p['ior']
  # Same camera in both frames, specified in units of the video's half-height.
  camera=(np.array(self.source.shape[1::-1])/2-np.array(self.case['center']))/self.L
  Z=p['camera_z']*(self.source.shape[0]/2)/self.L
  I=np.stack([x-camera[0],y-camera[1],np.full_like(x,-Z)],-1);I/=np.linalg.norm(I,axis=-1,keepdims=True)
  N=np.zeros_like(I);N[...,2]=1
  inside,_,_,valid=interface(I,N,1/n)
  lo=np.zeros_like(x);hi=np.full_like(x,H)/(-inside[...,2])
  for _ in range(22):
   t=(lo+hi)/2;xx=x+t*inside[...,0];yy=y+t*inside[...,1];h,*_=self.height(xx,yy,p)
   f=t*inside[...,2]+h;lo=np.where(f>0,t,lo);hi=np.where(f>0,hi,t)
  t=(lo+hi)/2;xx=x+t*inside[...,0];yy=y+t*inside[...,1];z=t*inside[...,2]
  h,hx,hy,mask=self.height(xx,yy,p)
  N=np.stack([hx,hy,np.ones_like(x)],-1);N/=np.linalg.norm(N,axis=-1,keepdims=True)
  O,_,_,valid=interface(inside,N,n)
  front=self.height(x,y,p)[3]
  if np.any(front&~valid):raise ValueError('TIR')
  O=np.nan_to_num(O);travel=np.divide(-D-z,O[...,2],out=np.zeros_like(z),where=O[...,2]<-1e-8)
  if np.any(front&(O[...,2]>=-1e-8)):raise ValueError('No background intersection')
  X=xx+travel*O[...,0];Y=yy+travel*O[...,1]
  X=camera[0]+(X-camera[0])*Z/(Z+D);Y=camera[1]+(Y-camera[1])*Z/(Z+D)
  return np.where(front,X,x),np.where(front,Y,y)
 def geometry_field(self,x,y,p):
  q={**p,'spline':False,'amplitude':0.,'core_x':0.,'core_y':0.,'tangent':0.,'coupling':0.}
  _,_,d,J=super().geometry_field(x,y,q);X,Y=self.raymap(x,y,p)
  return X,Y,d,J

A=Perspective(folder);B=Perspective(folder/'second-observation')
p=copy.deepcopy(json.loads((folder/'crown-review/optics-01.json').read_text())['parameters'])
p.update(height=.12,ior=1.3,gap=2.,crown_x=.1,crown_y=.1,shoulder=2.,camera_z=2.)
# Verify projection and interface convention independently before optimizing.
rng=np.random.default_rng(222);x=rng.uniform(-2.4,2.4,100);y=rng.uniform(-.9,.9,100)
xx,yy=A.raymap(x,y,{**p,'ior':1.});assert np.max(np.abs(xx-x))<1e-12 and np.max(np.abs(yy-y))<1e-12
identity_error=max(float(np.max(np.abs(xx-x))),float(np.max(np.abs(yy-y))))
source=np.clip((A.source[:,:,0]-A.source[:,:,1])/.65,0,1);target=np.clip((A.target[:,:,0]-A.target[:,:,1])/.65,0,1)
a,b,c,d=A.crop;near=cv2.dilate((target>.05).astype(np.uint8),np.ones((17,17),np.uint8));general=np.flatnonzero(A.valid);special=np.flatnonzero(A.valid&(near[b:d,a:c]>0));rng.shuffle(general);rng.shuffle(special);idx=np.unique(np.r_[general[:1500],special[:2500]]);x=A.x.ravel()[idx];y=A.y.ravel()[idx]
keys=['height','ior','gap','crown_x','crown_y','shoulder','camera_z'];lo,hi=np.array([(.02,.3),(1.02,1.7),(.05,10.),(0.,.45),(0.,.45),(1.,5.),(.5,12.)]).T
rows=[]
for stage,sigma in enumerate([4.,1.,0.],1):
 S=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;T=cv2.GaussianBlur(target,(0,0),sigma) if sigma else target;expected=T[b:d,a:c].ravel()[idx];calls=0;start=time.time()
 def residual(v):
  global calls
  calls+=1;q={**p,**dict(zip(keys,map(float,v)))}
  try:X,Y=A.raymap(x,y,q)
  except ValueError:return np.full(len(idx),100.)
  pred=cv2.remap(S,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel()
  return (pred-expected).astype(float)
 def jac(v):
  J=np.empty((len(idx),len(v)))
  for i in range(len(v)):
   h=.001;up=v.copy();dn=v.copy();up[i]=min(hi[i],v[i]+h);dn[i]=max(lo[i],v[i]-h);J[:,i]=(residual(up)-residual(dn))/(up[i]-dn[i])
  return J
 fit=least_squares(residual,np.clip([p[k] for k in keys],lo+1e-8,hi-1e-8),jac=jac,bounds=(lo,hi),max_nfev=60,x_scale='jac',ftol=1e-8,xtol=1e-7,gtol=1e-7)
 p.update(zip(keys,map(float,fit.x)));_,co=A.fit(p)
 try:pred=[s.render(p,co) for s in [A,B]];scores=[s.scores(im) for s,im in zip([A,B],pred)]
 except ValueError:
  print('Rejected native TIR stage',stage,flush=True);continue
 row=dict(stage=stage,parameters=p.copy(),material=co.tolist(),scores=scores,evaluations=calls,seconds=time.time()-start,objective_sigma=sigma,rendered_ordinary_blur=0,accepted=False);rows.append(row)
 (out/f'trial-{stage}.json').write_text(json.dumps(row,indent=2)+'\n')
 for label,s,im in zip(['A','B'],[A,B],pred):
  x0,y0,x1,y1=s.crop;cov=s.shape_coverage(p);base=s.exterior_source[y0:y1,x0:x1];result=im*cov[...,None]+base*(1-cov[...,None]);Image.fromarray(np.uint8(np.rint(np.clip(result,0,1)*255))).save(out/f'trial-{stage}-{label}.png')
 print(json.dumps(dict(stage=stage,loss=[s['loss'] for s in scores],glass=[s['glass']['rmse'] for s in scores],parameters={k:p[k] for k in keys},seconds=time.time()-start)),flush=True)
(out/'review.json').write_text(json.dumps(dict(trials=rows,qualified_passes=0,identity_max_error=identity_error,limits='Perspective flat-front/curved-back Snell branch. Screen-center camera shared across frames. No Gaussian in rendered result; coarse registration objective filters separately. TIR rejected, internal reflection omitted, material lighting empirical. No public source/state mutation.'),indent=2)+'\n')
