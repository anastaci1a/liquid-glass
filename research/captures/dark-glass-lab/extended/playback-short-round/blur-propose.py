"""One short ordinary post-filter neighborhood from verified playback pass1."""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction']
import numpy as np,cv2
from PIL import Image
from settled import render,icon_color
from reproduce import CASES,scores
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');out=root/'pass-02';out.mkdir(exist_ok=True);assert not (out/'candidate.json').exists()
inputs=Path('/evidence/apple-matches/public-settled-replay');source=np.asarray(Image.open(inputs/'media-source.png'),float)/255;target=np.asarray(Image.open(inputs/'media-target.png'),np.float32)/255
rec=json.loads((root/'material-proposal/replay-record.json').read_text());p0=rec['recipe'];case=CASES['media'];a,b,c,d=case['crop'];T=target[b:d,a:c];L=min(case['half']);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255;safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0
ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p0['icon']['box_over_L'])]
p=copy.deepcopy(p0);p['post_sigma']=0;unfiltered=render(source,case,p);np.save(out/'unfiltered-material.npy',unfiltered)
base=json.loads((root/'material-proposal/result.json').read_text())['candidate']['scores'];control=cv2.GaussianBlur(unfiltered,(0,0),p0['post_sigma']*L);assert np.max(np.abs(control-np.load(root/'material-proposal/candidate-material.npy')))==0
rows=[];best=None
for sigma in [1.4,1.6,1.25,1.75]:
 p=copy.deepcopy(p0);p['post_sigma']=sigma/L;M=cv2.GaussianBlur(unfiltered,(0,0),sigma);s=scores(M,T,case);C=icon_color(M,p['icon'],L)[ib-b:id-b,ia-a:ic-a];s['foreground']=float(np.sqrt(np.mean((C[safe]-target[ib:id,ia:ic][safe])**2))*255);s['glass']=s['all_glass']['rmse'];s['E']=float(np.sqrt(.7*s['glass']**2+.3*s['rim']['rmse']**2));allowed=all(s[k]<=base[k] for k in ['E','glass','foreground']);row=dict(sigma_px=sigma,recipe=p,scores=s,allowed=allowed);rows.append(row);print(sigma,s['E'],s['glass'],s['foreground'],allowed,flush=True)
 if allowed and s['E']<base['E']-1e-6:
  best=row;np.save(out/'candidate-material.npy',M);break
record=dict(method=__doc__,baseline=base,trials=rows,candidate=best,zero_control_max_difference=0.,accepted=False)
(out/'candidate.json').write_text(json.dumps(record,indent=2)+'\n')
if best:(out/'replay-record.json').write_text(json.dumps(dict(recipe=best['recipe'],input_sha256=rec['input_sha256']),indent=2)+'\n')
