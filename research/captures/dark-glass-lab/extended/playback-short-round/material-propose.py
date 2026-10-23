"""One compact shared exposure neighborhood; geometry/filters/source fixed."""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction']
import numpy as np,cv2
from PIL import Image
from settled import RECIPES,render,icon_color
from reproduce import CASES,scores
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');out=root/'material-proposal';out.mkdir(exist_ok=True);assert not (out/'result.json').exists()
inputs=Path('/evidence/apple-matches/public-settled-replay');source=np.asarray(Image.open(inputs/'media-source.png'),float)/255;target=np.asarray(Image.open(inputs/'media-target.png'),np.float32)/255;p0=copy.deepcopy(RECIPES['media']);case=CASES['media'];a,b,c,d=case['crop'];T=target[b:d,a:c];L=min(case['half']);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255;safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0
ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p0['icon']['box_over_L'])]
def score(M,p):
 s=scores(M,T,case);C=icon_color(M,p['icon'],L)[ib-b:id-b,ia-a:ic-a];s['foreground']=float(np.sqrt(np.mean((C[safe]-target[ib:id,ia:ic][safe])**2))*255);s['glass']=s['all_glass']['rmse'];s['E']=float(np.sqrt(.7*s['glass']**2+.3*s['rim']['rmse']**2));return s
old=json.loads((root/'pass-01/candidate.json').read_text());base=old['baseline'];rows=[];best=None
for factor in [.999,1.001,.995,1.005,.99,1.01]:
 p=copy.deepcopy(p0);p['material']=(np.array(p0['material'])*factor).tolist();M=render(source,case,p);s=score(M,p);allowed=all(s[k]<=base[k] for k in ['E','glass','foreground']);row=dict(factor=factor,recipe=p,scores=s,allowed=allowed);rows.append(row);print(factor,s['E'],s['glass'],s['foreground'],allowed,flush=True)
 if allowed and (best is None or s['E']<best['scores']['E']):best=row;np.save(out/'candidate-material.npy',M)
 if best and best['scores']['E']<base['E']*.999:break
(out/'result.json').write_text(json.dumps(dict(baseline=base,trials=rows,candidate=best,accepted=False),indent=2)+'\n')
