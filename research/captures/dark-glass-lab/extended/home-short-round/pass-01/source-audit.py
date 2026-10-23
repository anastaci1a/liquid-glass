import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from source_support import masks,kernel_safe,confidence_at
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'home-short-round/pass-01';r=json.loads((out/'joint-candidate.json').read_text());p=r['parameters'];rows=[]
for obs in ['a','b']:
 s=Study(root/'music-home-vector-corrected/paired'/obs);known,_=masks(s);safe,radius=kernel_safe(known,s,p);bad=[];total=0;scored=0;scored_bad=0
 for row,end,W,x,y in s.raster_tiles(2):
  *_,(sd,_,_)=s.shape(x,y,p);active=sd<=0;X,Y,_,_=s.geometry_field(x,y,p);px=X*s.L+s.case['center'][0];py=Y*s.L+s.case['center'][1];good=confidence_at(safe,px,py)>=.999;total+=int(active.sum());badxy=np.stack([px[active&~good],py[active&~good]],1)
  if len(badxy):bad.append(badxy)
  roi=np.repeat(np.repeat(s.valid,4,axis=0),4,axis=1)[row*2:end*2,:];scored+=int((roi&active).sum());scored_bad+=int((roi&active&~good).sum())
 q=np.concatenate(bad) if bad else np.empty((0,2));report=dict(observation=obs,emitted=total,missing=len(q),missing_fraction=len(q)/total,scored_emitted=scored,scored_missing=scored_bad,kernel_radius=radius,source_bbox=q.min(0).tolist()+q.max(0).tolist() if len(q) else None);rows.append(report)
 im=np.uint8(np.rint(s.source*255));crop=s.crop;Image.fromarray(im[crop[1]-30:crop[3]+30,crop[0]-30:crop[2]+30]).save(out/(obs+'-source-context.png'));print(report,flush=True)
(out/'source-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
