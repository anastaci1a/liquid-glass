"""Reframe existing accepted pixels; no optical render, fit or pass."""
import json,sys
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from publish import pair
from vector_foreground import _coverage
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'toolbar-response-primary-review';repo=Path('/workspace/docs/liquid-glass');public=repo/'experiments/reconstruction/studies/archive-plus/review-round';inputs=Path('/tmp/agent-toolbar-evidence-package/inputs')
p=json.loads((public/'pass-03.json').read_text());a,b,c,d=p['case']['crop']
T=np.asarray(Image.open(inputs/'target.png'),np.float32)[b:d,a:c]/255
current=np.load(out/'complete.npy');mat=np.load(out/'material.npy');alpha=np.load(out/'alpha.npy');oldmat=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');trans=np.ones_like(alpha)
for layer in p['foreground_layers']:trans*=1-_coverage((inputs/layer['asset']).read_bytes(),tuple(p['case']['crop']),tuple(layer['placement']),1)
previous=current-(mat-oldmat)*alpha[...,None]*trans[...,None]
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');hi=np.asarray(Image.open(out/'hq/render.png'));hiT=cv2.resize(np.uint8(np.rint(T*255)),(hi.shape[1],hi.shape[0]),interpolation=cv2.INTER_LANCZOS4)
rows=[]
for name,box,asset in [('upper rim',[650,369,1270,468],'match-regular-rim.png'),('d-stroke',[960,468,1120,550],'toolbar-d-stroke-current.png')]:
 x0,y0,x1,y1=box;x0-=a;x1-=a;y0-=b;y1-=b;roi=np.zeros(T.shape[:2],bool);roi[y0:y1,x0:x1]=True;mask=roi&masks['glass']
 rows.append(dict(name=name,box_native=box,visible_rmse=[float(np.sqrt(np.mean(((im-T)[roi]*255)**2))) for im in [previous,current]],glass_rmse=[float(np.sqrt(np.mean(((im-T)[mask]*255)**2))) for im in [previous,current]],glass_pixels=int(mask.sum())))
 pair(hiT[y0*4:y1*4,x0*4:x1*4],hi[y0*4:y1*4,x0*4:x1*4],('Apple source','Revision 3 (4x)'),font_size=32).save(repo/'assets'/asset)
record=dict(crops=rows,order=['revision2','revision3'],purpose='Reframed advisory diagnostics requested by Ana; original pass-03-crops.json remains historical. No changed render, full-frame metric, input epoch or qualifying pass.',boundary='Upper rim extended down by 33 native pixels (half original height); d-stroke begins at the same y=468 edge, without a gap or overlap.')
(public/'pass-03-crops-reframed.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
