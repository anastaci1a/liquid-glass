"""Same circle/patch, fixed source models; no Android-renderer/parity claim."""
from pathlib import Path
import cv2,json
import numpy as np
P=Path(__file__).resolve().parent
A=cv2.imread(str(P/'morph/0001.png')).astype(np.float32)
y,x=np.mgrid[50:71,413:434].astype(np.float32)

def offsets(cx,cy,r,kind):
 vx=x-cx;vy=y-cy;rad=np.sqrt(vx*vx+vy*vy);u=rad/r;ix=-vx/rad;iy=-vy/rad
 if kind=='boundary':
  raw=1-u;delta=raw-.15;eff=.15+np.maximum(delta,0)+.01*np.log1p(np.exp(-np.abs(delta)/.01));t=np.clip((eff-.3)/.35,0,1)
  d=r*.14*np.exp(-eff/.5)*(1-t*t*(3-2*t));return ix*d,iy*d
 depth=1.35/np.sqrt(1+1.35**2/4);crown=r*.62*depth;root=np.sqrt(np.maximum(1-u*u,.0004));height=crown*root*(1+.4*u*u)
 slope=crown/r*u/root*(1-.8+1.2*u*u);gx=-ix*slope;gy=-iy*slope;z=1/np.sqrt(1+gx*gx+gy*gy);nx=gx*z;ny=gy*z;eta=1/1.33;factor=eta*z-np.sqrt(np.maximum(1-eta*eta*(1-z*z),0));rz=-eta+factor*z
 insx=nx*factor;insy=ny*factor;outx=insx*1.33;outy=insy*1.33;ez=np.sqrt(np.maximum(1-outx*outx-outy*outy,.01))
 return insx*height/np.maximum(-rz,.12)+outx*(r*.32*depth/ez),insy*height/np.maximum(-rz,.12)+outy*(r*.32*depth/ez)

def fit(s,t):
 s=s.reshape(-1,3);t=t.reshape(-1,3);ds=s-s.mean(0);dt=t-t.mean(0);g=np.clip((ds*dt).sum(0)/np.maximum((ds*ds).sum(0),1e-6),0,2);pred=s*g+t.mean(0)-g*s.mean(0)
 return float(np.sqrt(np.mean((pred-t)**2)))
frames=[65,80,95,225,240,255];B={n:cv2.imread(str(P/'morph'/f'{n+1:04d}.png')).astype(np.float32)[50:71,413:434] for n in frames};out={}
for kind in ['boundary','crown']:
 dx,dy=offsets(429,114,83,kind);best=(1e9,0,None)
 for sigma in np.arange(0,8.01,.25):
  src=A if sigma==0 else cv2.GaussianBlur(A,(0,0),float(sigma));patch=cv2.remap(src,(x+dx).astype(np.float32),(y+dy).astype(np.float32),cv2.INTER_LINEAR);e=fit(patch,B[65])
  if e<best[0]:best=(e,float(sigma),patch)
 sensitivity=[]
 for cx in [427,429,431]:
  for cy in [112,114,116]:
   for r in [81,83,85]:
    ox,oy=offsets(cx,cy,r,kind);sensitivity.append([float(ox[10,10]),float(oy[10,10])])
 out[kind]=dict(center_inverse_offset=[float(dx[10,10]),float(dy[10,10])],best_blur=best[1],rmse=[fit(best[2],B[n]) for n in frames],outline_sensitivity_min=np.min(sensitivity,axis=0).tolist(),outline_sensitivity_max=np.max(sensitivity,axis=0).tolist())
(P/'model-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
