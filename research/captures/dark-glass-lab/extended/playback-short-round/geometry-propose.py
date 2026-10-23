"""One compact radial edge-power neighborhood from verified playback pass2."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from settled import render,icon_color
from reproduce import CASES,scores
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');assert (root/'pass-02/accepted-verification.json').exists(),'Do not start from an unaccepted candidate'
out=root/'pass-03';out.mkdir(exist_ok=True);assert not (out/'candidate.json').exists()
rec=json.loads((root/'pass-02/replay-record.json').read_text());p0=rec['recipe'];base=json.loads((root/'pass-02/response-candidate.json').read_text())['candidate']['scores'];inputs=Path('/evidence/apple-matches/public-settled-replay');source=np.asarray(Image.open(inputs/'media-source.png'),float)/255;target=np.asarray(Image.open(inputs/'media-target.png'),np.float32)/255;case=CASES['media'];a,b,c,d=case['crop'];L=min(case['half']);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255;safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0;ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p0['icon']['box_over_L'])]
rows=[];best=None
for key,factor in [('amplitude',.999),('amplitude',1.001),('band',.99),('band',1.01)]:
 p=copy.deepcopy(p0);p['parameters'][key]*=factor;M=render(source,case,p);s=scores(M,target[b:d,a:c],case);C=icon_color(M,p['icon'],L)[ib-b:id-b,ia-a:ic-a];s['foreground']=float(np.sqrt(np.mean((C[safe]-target[ib:id,ia:ic][safe])**2))*255);s['glass']=s['all_glass']['rmse'];s['E']=float(np.sqrt(.7*s['glass']**2+.3*s['rim']['rmse']**2));allowed=all(s[k]<=base[k] for k in ['E','glass','foreground']);row=dict(key=key,factor=factor,recipe=p,scores=s,allowed=allowed);rows.append(row);print(key,factor,s['E'],s['glass'],s['foreground'],allowed,flush=True)
 if allowed and s['E']<base['E']-1e-6:best=row;np.save(out/'candidate-material.npy',M);break
(out/'candidate.json').write_text(json.dumps(dict(method=__doc__,baseline=base,trials=rows,candidate=best,accepted=False),indent=2)+'\n')
if best:(out/'replay-record.json').write_text(json.dumps(dict(recipe=best['recipe'],input_sha256=rec['input_sha256']),indent=2)+'\n')
