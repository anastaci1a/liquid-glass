"""Check whether adding a smooth illumination nuisance changes the optical fit."""
import json
from pathlib import Path
import cv2
import numpy as np
P=Path(__file__).resolve().parent
A=cv2.imread(str(P/'morph/0001.png')).astype(np.float32)
frames=[65,80,95,225,240,255]
x,y=423,60; yy,xx=np.mgrid[-10:11,-10:11]
plane=np.stack([np.ones_like(xx),xx/10,yy/10],axis=-1).reshape(-1,3).astype(np.float32)
q,_=np.linalg.qr(plane)
B={n:cv2.imread(str(P/'morph'/f'{n+1:04d}.png')).astype(np.float32)[y-10:y+11,x-10:x+11] for n in frames}

def fit(s,t,light_plane=False):
 s=s.reshape(-1,3);t=t.reshape(-1,3)
 basis=q if light_plane else np.ones((441,1))/21
 sp=s-basis@(basis.T@s);tp=t-basis@(basis.T@t)
 gain=np.clip((sp*tp).sum(0)/np.maximum((sp*sp).sum(0),1e-6),0,2)
 pred=s*gain+basis@(basis.T@(t-s*gain))
 return float(np.sqrt(np.mean((pred-t)**2)))

def sample(sigma,dx,dy):
 src=A if sigma==0 else cv2.GaussianBlur(A,(0,0),sigma)
 return cv2.getRectSubPix(src,(21,21),(x+float(dx),y+float(dy)))

# Coarser independent optimization, including smooth additive illumination.
best=(1e9,None);best_zero=(1e9,None)
for sigma in np.arange(0,6.01,.5):
 src=A if sigma==0 else cv2.GaussianBlur(A,(0,0),float(sigma))
 for dy in np.arange(-5,5.01,.5):
  for dx in np.arange(-5,5.01,.5):
   s=cv2.getRectSubPix(src,(21,21),(x+float(dx),y+float(dy)))
   e=fit(s,B[65],True);params=[float(sigma),float(dx),float(dy)]
   if e<best[0]:best=(e,params)
   if dx==0 and dy==0 and e<best_zero[0]:best_zero=(e,params)
models={'light_plane_full':best[1],'light_plane_no_shift':best_zero[1],'previous_fit':[3.,0.,2.5],'identity':[0.,0.,0.]}
out={'training_frame':65,'parameters':models,'rmse':{name:[fit(sample(*params),B[n],True) for n in frames] for name,params in models.items()}}
# Positive-control convention and recovery on a small known grid around truth.
checks=[]
for truth in [(0.,0.,0.),(2.,-1.,2.5)]:
 target=sample(*truth)*np.array([.7,.8,.6],np.float32)+np.array([40,20,50],np.float32)
 winner=(1e9,None)
 for sigma in sorted(set([0.,1.,2.,3.,truth[0]])):
  for dx in [-2.,-1.,0.,1.]:
   for dy in [-1.,0.,1.,2.,2.5,3.]:
    e=fit(sample(sigma,dx,dy),target)
    if e<winner[0]:winner=(e,[sigma,dx,dy])
 checks.append(dict(truth=truth,recovered=winner[1],rmse=winner[0]))
 assert np.allclose(truth,winner[1]) and winner[0]<1e-3
out['synthetic_controls']=checks
(P/'illumination-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
