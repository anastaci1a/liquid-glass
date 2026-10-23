"""Complete one filter family with a bounded shared icon-response adjustment."""
import sys,json,copy,itertools
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from settled import icon_color
from reproduce import CASES
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');out=root/'pass-02';assert not (out/'response-candidate.json').exists()
old=json.loads((out/'candidate.json').read_text());rec=json.loads((root/'material-proposal/replay-record.json').read_text());base=old['baseline'];row=next(r for r in old['trials'] if r['sigma_px']==1.6);p0=row['recipe'];L=245.;case=CASES['media'];a,b,c,d=case['crop'];target=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)/255
M=cv2.GaussianBlur(np.load(out/'unfiltered-material.npy'),(0,0),1.6);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255;safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0;ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p0['icon']['box_over_L'])]
rows=[];best=None
for saturation,taper,blur in itertools.product([.2,.21,.19],[.5,.52,.48],[3.,3.1,2.9]):
 p=copy.deepcopy(p0);p['icon'].update(dark_saturation=saturation,taper=taper,final_sigma=blur/L);C=icon_color(M,p['icon'],L)[ib-b:id-b,ia-a:ic-a];fg=float(np.sqrt(np.mean((C[safe]-target[ib:id,ia:ic][safe])**2))*255);s=copy.deepcopy(row['scores']);s['foreground']=fg;allowed=all(s[k]<=base[k] for k in ['E','glass','foreground']);trial=dict(saturation=saturation,taper=taper,icon_sigma_px=blur,foreground=fg,allowed=allowed);rows.append(trial);print(trial,flush=True)
 if allowed:
  best=dict(recipe=p,scores=s);break
record=dict(method=__doc__,baseline=base,ordinary_neighborhood=old['trials'],response_trials=rows,candidate=best,accepted=False)
(out/'response-candidate.json').write_text(json.dumps(record,indent=2)+'\n')
if best:
 np.save(out/'candidate-material.npy',M);(out/'replay-record.json').write_text(json.dumps(dict(recipe=best['recipe'],input_sha256=rec['input_sha256']),indent=2)+'\n')
