"""Conditional local fit, NOT a recovered Apple shader. See report limitations."""
from pathlib import Path
import json
import cv2
import numpy as np
P=Path(__file__).resolve().parent
A=cv2.imread(str(P/'morph/0001.png')).astype(np.float32)
x,y=423,60; size=21
frames=[65,80,95,225,240,255]
B={n:cv2.imread(str(P/'morph'/f'{n+1:04d}.png')).astype(np.float32)[y-10:y+11,x-10:x+11] for n in frames}

def fit(source,target):
 s=source.reshape(-1,3);t=target.reshape(-1,3)
 ds=s-s.mean(0);dt=t-t.mean(0)
 gain=np.clip((ds*dt).sum(0)/np.maximum((ds*ds).sum(0),1e-6),0,2) # forbid tone inversion
 bias=t.mean(0)-gain*s.mean(0)
 pred=source*gain+bias
 return float(np.sqrt(np.mean((pred-target)**2))),gain,bias,pred

def sample(sigma,dx,dy):
 src=A if sigma==0 else cv2.GaussianBlur(A,(0,0),sigma)
 return cv2.getRectSubPix(src,(size,size),(x+float(dx),y+float(dy)))
# Select parameters only against frame 65; photometry is nuisance, refitted per frame.
best=(1e9,None); grid=[]
for sigma in np.arange(0,6.01,.25):
 src=A if sigma==0 else cv2.GaussianBlur(A,(0,0),float(sigma))
 for dy in np.arange(-5,5.01,.25):
  for dx in np.arange(-5,5.01,.25):
   patch=cv2.getRectSubPix(src,(size,size),(x+float(dx),y+float(dy)))
   err,g,b,_=fit(patch,B[65]);grid.append([float(sigma),float(dx),float(dy),err])
   if err<best[0]:best=(err,[float(sigma),float(dx),float(dy)])
err,(sigma,dx,dy)=best
near=np.array([r for r in grid if r[3]<=err+.15])
best_blur_only=min((r for r in grid if r[1]==0 and r[2]==0),key=lambda r:r[3])
best_shift_only=min((r for r in grid if r[0]==0),key=lambda r:r[3])
models={'optimized_blur_only':tuple(best_blur_only[:3]),'optimized_shift_only':tuple(best_shift_only[:3]),'trained_blur_and_shift':(sigma,dx,dy),'same_blur_no_shift':(sigma,0,0),'same_shift_no_blur':(0,dx,dy),'identity':(0,0,0)}
results={}
for name,params in models.items():
 patch=sample(*params); results[name]=[]
 for n in frames:
  e,g,b,pred=fit(patch,B[n]);results[name].append(dict(frame=n,rmse=e,gain_bgr=g.tolist(),offset_bgr=b.tolist()))
  if n==80:
   comp=np.hstack([sample(0,0,0),patch,pred,B[n]])
   cv2.imwrite(str(P/f'fit-{name}.png'),cv2.resize(np.clip(comp,0,255).astype(np.uint8),None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST))
out=dict(patch=dict(center=[x,y],size=size),train=65,parameters=dict(sigma=sigma,dx=dx,dy=dy,train_rmse=err),sensitivity_plus_015_rmse=dict(min=near[:,:3].min(0).tolist(),max=near[:,:3].max(0).tolist(),note='Profile sensitivity range, not statistical confidence interval'),baseline_parameters=dict(blur_only=best_blur_only,shift_only=best_shift_only),models=results)
(P/'patch-fit.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='models'},indent=2))
print({name:[round(r['rmse'],3) for r in rows] for name,rows in results.items()})
