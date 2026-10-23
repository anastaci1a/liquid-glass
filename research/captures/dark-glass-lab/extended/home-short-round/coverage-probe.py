"""Single target-independent coverage-integration diagnostic; no pass claim."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from render import shade
from material_context import effective
from grazing_reflection import apply
from vector_revision import composite
cv2.setNumThreads(1)
def covered(s,p,co,scale=1):
 co=effective(s,p,co);a,b,c,d=s.crop;H,W=(d-b)*scale,(c-a)*scale;C=np.zeros((H,W,3),np.float32);A=np.zeros((H,W),np.float32)
 for row,end,w,x,y in s.raster_tiles(scale):
  *_,(sd,_,_)=s.shape(x,y,p);inside=sd<=0;sample,light=s.field(np.where(inside,x,0),np.where(inside,y,0),p);q=shade(sample,light,co)*inside[...,None];C[row:end]=q.reshape(end-row,2,w,2,3).mean((1,3));A[row:end]=inside.reshape(end-row,2,w,2).mean((1,3))
 sigma=s.kernel_sigma(p,'post_sigma')*scale
 if sigma>.001:C=cv2.GaussianBlur(C,(0,0),sigma);weight=cv2.GaussianBlur(A,(0,0),sigma)
 else:weight=A
 material=np.divide(C,weight[...,None],out=np.zeros_like(C),where=weight[...,None]>1e-8)
 return apply(s,p,material,scale),A
root=Path('/evidence/extended/home-short-round');r=json.loads((root/'boundary-epoch/pass-01/joint-candidate.json').read_text());p=r['parameters'];co=np.asarray(r['candidate']['material']);rows=[]
for i,n in enumerate(['a','b']):
 s=Study(root/'input-boundary-replay-proposal'/n);M,A=covered(s,p,co);old=r['candidate']['scores'][i];new=s.scores(M,False);new['E']=float(np.sqrt(new['loss']));full=s.apply_foreground(M.copy());box=s.case['foreground_layers'][0]['box'];a,b,c,d=box;x0,y0,_,_=s.crop;new['foreground']=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2)))*255;rows.append(dict(observation=n,previous=old,candidate=new));print(n,old['E'],new['E'],old['foreground'],new['foreground'],flush=True)
 hq,_=covered(s,p,co,2);rgb=np.uint8(np.rint(np.clip(composite(s,p,hq,2),0,1)*255));Image.fromarray(rgb).save(root/(n+'-covered-probe.png'))
(root/'coverage-probe.json').write_text(json.dumps(dict(status='DIAGNOSTIC ONLY',model='Subpixel source-over coverage: C=sum(inside*material)/sum(inside); post-material blur is normalized convolution G(inside*material)/G(inside). Pixel coverage remains independently integrated. No target or per-crop terms.',observations=rows),indent=2)+'\n')
