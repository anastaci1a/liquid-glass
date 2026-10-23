"""Native replay and analytic domain control for one pointwise material pass."""
import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from settled import render,RECIPES,icon_color,radial
from reproduce import CASES,scores
from playback_replay import high_resolution
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');out=root/'material-proposal';proposal=json.loads((out/'result.json').read_text());rec=json.loads((out/'replay-record.json').read_text());p=rec['recipe'];case=CASES['media'];inputs=Path('/evidence/apple-matches/public-settled-replay')
for name,digest in rec['input_sha256'].items():assert hashlib.sha256((inputs/name).read_bytes()).hexdigest()==digest
source=np.asarray(Image.open(inputs/'media-source.png'),float)/255;target=np.asarray(Image.open(inputs/'media-target.png'),np.float32)/255;M=high_resolution(source,case,p,1);saved=np.load(out/'candidate-material.npy');difference=float(np.max(np.abs(M-saved)));assert difference==0
# Nonnegative monotonically decreasing transition bounds every radial lookup,
# including outside-footprint samples used by the output kernel.
A,b,power,k,q=[p['parameters'][n] for n in ['amplitude','band','power','width','inner_power']]
assert q-power*k<0 and q-power*k*k<0 and A>=0
L=min(case['half']);a,b0,c,d=case['crop'];cx,cy=case['center'];rmax=max(np.hypot(x-cx,y-cy)/L for x in [a-.5,c-.5] for y in [b0-.5,d-.5]);radius=max(rmax,A)*L
margin=min(cx,source.shape[1]-1-cx,cy,source.shape[0]-1-cy)-radius;kernel=int(np.ceil(3*p['source_sigma']*L));assert margin>kernel+1
s=scores(M,target[b0:d,a:c],case);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255;ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0;C=icon_color(M,p['icon'],L)[ib-b0:id-b0,ia-a:ic-a];foreground=float(np.sqrt(np.mean((C[safe]-target[ib:id,ia:ic][safe])**2))*255)
metric=dict(glass=s['all_glass']['rmse'],rim=s['rim']['rmse'],foreground=foreground);metric['E']=float(np.sqrt(.7*metric['glass']**2+.3*metric['rim']**2));expected=proposal['candidate']['scores'];assert all(metric[n]==expected[n] for n in ['glass','E','foreground'])
control=dict(native_pixel_max_difference=difference,source_hashes_verified=True,changed_stages=['one shared exposure multiplier on existing material coefficients'],fixed_stages=['source','reference','radial map','source/output blur','icon geometry and color function'],domain=dict(method='Analytic enclosure of every native/HQ query over entire output crop; 0<=radial displacement<=A, |r-a|<=max(r,A). Output blur reflects only already calculated crop pixels.',minimum_frame_margin_px=margin,source_kernel_3sigma_px=kernel,passed=True),candidate=metric,previous={n:proposal['baseline'][n] for n in ['glass','E','foreground']},native_replay=True,visual_review=False,accepted=False)
(out/'verification-pending-visual.json').write_text(json.dumps(control,indent=2)+'\n');print(json.dumps(control))
