"""Raw source/halo observations; no fit, recolor or rendering correction."""
from pathlib import Path
import os,json,hashlib
import numpy as np
from PIL import Image
os.umask(0o002);D=Path('/evidence/extended/blue-slider-short-round')
load=lambda p:np.asarray(Image.open(p).convert('RGB')).astype(float)
donor=load(D/'sequence/frame-00.png');A=load('/evidence/apple-matches/public-settled-replay/slider-target.png');B=load(D/'sequence/frame-07.png');original=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/contour.json').read_text())['geometry'];gray=json.loads((D/'gray-outline.json').read_text())['geometry'];rows=[]
for name,T,g in [('A-blue',A,original),('B-gray-min',B,gray)]:
 cx,cy=g['center'];a,b=g['half'];profiles=[]
 for q in [.05,.1,.2,.3,.5,.7,1.,1.5,2.]:
  px=int(round(cx));py=int(round(cy+b+q*b));padx=max(3,int(round(.12*b)));r=(px-padx,py-2,px+padx+1,py+3);x0,y0,x1,y1=r
  t=T[y0:y1,x0:x1].mean((0,1));s=donor[y0:y1,x0:x1].mean((0,1));delta=t-s
  profiles.append(dict(outward_distance_over_L=q,box=list(r),target_rgb=t.tolist(),uncovered_donor_rgb=s.tolist(),raw_delta_rgb=delta.tolist(),blue_minus_red_delta=float(delta[2]-delta[0])))
 controls=[]
 for px in [400,900,1200,1600]:
  for py in [740,800,900]:
   delta=(T[py-3:py+4,px-3:px+4]-donor[py-3:py+4,px-3:px+4]).mean((0,1));controls.append(dict(center=[px,py],raw_delta_rgb=delta.tolist()))
 rows.append(dict(reference=name,geometry=g,profiles=profiles,far_paper_controls=controls,mean_control_delta_rgb=np.array([r['raw_delta_rgb'] for r in controls]).mean(0).tolist()))
files=['sequence/frame-00.png','sequence/frame-07.png','gray-outline.json'];(D/'halo-profiles.json').write_text(json.dumps(dict(observations=rows,input_sha256={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in files},limits='Raw encodedRGB native patches, no input recoloring/alignment/pixel edits/optical trial. Donor precedes active press. Gray B is a clamped deformation, not a matched-state benchmark; bottom boundary uses upper-ridge symmetry/track-center assumption. Residual blue relative to exposed gray is compatible with tint, nonlocal/environment reflection, interaction history or processing; not proof of a specific cause. No new source adopted, no model pass.'),indent=2)+'\n');print([(r['reference'],r['mean_control_delta_rgb'],[(v['outward_distance_over_L'],v['blue_minus_red_delta']) for v in r['profiles']]) for r in rows],flush=True)
