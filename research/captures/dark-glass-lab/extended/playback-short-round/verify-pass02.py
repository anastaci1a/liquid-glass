"""Verify filter/foreground refinement independently; reuse unchanged ray proof."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from settled import icon_color
from playback_replay import high_resolution,composite
from reproduce import CASES,scores
from publish import pair
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');out=root/'pass-02';rec=json.loads((out/'replay-record.json').read_text());p=rec['recipe'];proposal=json.loads((out/'response-candidate.json').read_text());prev=json.loads((root/'material-proposal/replay-record.json').read_text());proof=json.loads((root/'material-proposal/accepted-verification.json').read_text());inputs=Path('/evidence/apple-matches/public-settled-replay')
for n,d in rec['input_sha256'].items():assert hashlib.sha256((inputs/n).read_bytes()).hexdigest()==d
assert all(p[k]==prev['recipe'][k] for k in p if k not in ['icon','post_sigma']);assert all(p['icon'][k]==prev['recipe']['icon'][k] for k in p['icon'] if k!='taper')
source=np.asarray(Image.open(inputs/'media-source.png'),float)/255;target=np.asarray(Image.open(inputs/'media-target.png'),np.float32)/255;case=CASES['media'];a,b,c,d=case['crop'];L=min(case['half']);M=high_resolution(source,case,p,1);assert np.max(np.abs(M-np.load(out/'candidate-material.npy')))==0
s=scores(M,target[b:d,a:c],case);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255;safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0;ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];C=icon_color(M,p['icon'],L)[ib-b:id-b,ia-a:ic-a];fg=float(np.sqrt(np.mean((C[safe]-target[ib:id,ia:ic][safe])**2))*255);now=dict(glass=s['all_glass']['rmse'],rim=s['rim']['rmse'],foreground=fg);now['E']=float(np.sqrt(.7*now['glass']**2+.3*now['rim']**2));old=proposal['baseline'];assert all(now[k]<=old[k] for k in ['E','glass','foreground']);assert now['E']<old['E'];print('NATIVE',now,flush=True)
record=dict(candidate=now,previous={k:old[k] for k in ['E','glass','foreground']},native_pixel_max_difference=0.,source_hashes_verified=True,domain={**proof['domain'],'reused_from':'pass-01-verification.json','reason':'Same source, map, source blur, output extent and AA. Output Gaussian only filters already calculated crop pixels; icon taper is pointwise.'},native_replay=True,visual_review=False,accepted=False)
(out/'verification-pending-visual.json').write_text(json.dumps(record,indent=2)+'\n')
hi=high_resolution(source,case,p,4);whole=composite(source,case,p,hi,4);rgb=np.uint8(np.rint(np.clip(whole,0,1)*255));hq=out/'hq';hq.mkdir(exist_ok=True);Image.fromarray(rgb).save(hq/'render.png');reference=cv2.resize(np.uint8(np.rint(target[b:d,a:c]*255)),(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_LANCZOS4);pair(reference,rgb,('Apple source','Reconstruction (4x)'),font_size=64).save(hq/'comparison.png');np.save(hq/'material.npy',hi)
print('HQ COMPLETE',flush=True)
