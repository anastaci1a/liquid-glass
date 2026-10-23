"""Primary-agent independent replay from frozen files, no fitting."""
import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from PIL import Image
from crowned_tensor import render,mapping,gaussian_coverage_shadow
from settled import render as archived_render
from reproduce import CASES,scores
from progress_gate import evaluate
root=Path('/evidence/../unused')
# Separate copy supplied by lead; no agent scratch imports or rendered pixels used.
root=Path('/tmp/lead-toolbar-input');out=Path('/evidence/extended/toolbar-primary-review/final');out.mkdir(exist_ok=True)
hashes=json.loads((root/'epoch-input-hashes.json').read_text())
for name,digest in hashes.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,(name,'changed')
epoch=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest();before=json.loads((root/'incumbent.json').read_text());assert epoch==before['epoch']
source=np.array(Image.open(root/'source.png'),dtype=float)/255;target=np.array(Image.open(root/'target.png'),dtype=np.float32)/255
p=json.loads((root/'candidate-with-shadow-recipe.json').read_text());old=json.loads((root/'incumbent-recipe.json').read_text());case=CASES['regular'];x0,y0,x1,y1=case['crop'];T=target[y0:y1,x0:x1];B=source[y0:y1,x0:x1];masks=np.load(root/'frozen-masks.npz')
I,oldAlpha=render(source,case,old);archived=archived_render(source,case,old);assert np.max(np.abs(I-archived))<1e-7
R,A=render(source,case,p);sc=scores(R,T,case);image=R*A[...,None]+B*(1-gaussian_coverage_shadow(case,p)[...,None])*(1-A[...,None]);shadow=float(np.sqrt(np.mean(((image-T)[masks['exterior']]*255)**2)))
current={'epoch':epoch,'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':shadow}}}
saved=json.loads((root/'candidate-with-shadow.json').read_text());assert abs(current['observations']['A']['glass']['rmse']-saved['observations']['A']['glass']['rmse'])<1e-7
# Check EVERY emitted subpixel lookup in entire output crop, plus source kernel.
margin=3*p['source_sigma']*170+1;low=np.array([np.inf,np.inf]);high=-low;support=True
for row in range(y0,y1,16):
 yy,xx=np.mgrid[row:min(row+16,y1):.25,x0:x1:.25];X,Y=mapping((xx-.375-960)/170,(yy-.375-542)/170,p);X=X*170+960;Y=Y*170+542
 low=np.minimum(low,[X.min(),Y.min()]);high=np.maximum(high,[X.max(),Y.max()]);support &= bool(np.all((X>=margin)&(X<source.shape[1]-margin)&(Y>=margin)&(Y<source.shape[0]-margin)))
# Additional independent convergence diagnostic; fixed acceptance still uses4x4.
R8,A8=render(source,case,p,samples=8);sc8=scores(R8,T,case)
report={'epoch':epoch,'candidate':current,'fixed_grid':4,'diagnostic_grid':8,'diagnostic_scores':sc8,'source_support':{'all_emitted_subpixel_rays_inside_defined_image':support,'margin_native_px':margin,'bounds':[low.tolist(),high.tolist()],'hidden_background_estimated':True},'archived_baseline_max_difference':float(np.max(np.abs(I-archived))),'gate':evaluate(before,current,visual_review=False,replay_verified=True,source_support_verified=support),'limits':'Optical candidate replayed independently without optimization. Generated neutral shadow now independent of target; its fitted width reaches the documented bound. Foreground checked separately; no final acceptance inferred.'}
(out/'replay.json').write_text(json.dumps(report,indent=2)+'\n');Image.fromarray(np.uint8(np.clip(image,0,1)*255)).save(out/'candidate.png');print(json.dumps(report),flush=True)
