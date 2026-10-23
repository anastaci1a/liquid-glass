"""Compact fixed-input playback profile calibration; no source reconstruction."""
import sys,json,copy,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction']
import numpy as np,cv2
from PIL import Image
from settled import RECIPES,render,icon_color
from reproduce import CASES,scores
cv2.setNumThreads(1)
root=Path('/evidence/extended/playback-short-round');out=root/'pass-01';out.mkdir(exist_ok=True)
assert not (out/'candidate.json').exists()
inputs=Path('/evidence/apple-matches/public-settled-replay');source=np.asarray(Image.open(inputs/'media-source.png'),float)/255;target=np.asarray(Image.open(inputs/'media-target.png'),np.float32)/255
case=CASES['media'];a,b,c,d=case['crop'];T=target[b:d,a:c];L=min(case['half']);p0=copy.deepcopy(RECIPES['media']);mask=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'))/255
ix0,iy0,ix1,iy1=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p0['icon']['box_over_L'])];safe=cv2.erode(np.uint8(mask>.99),np.ones((7,7),np.uint8))>0
cache={}
def evaluate(p,tag):
 key=json.dumps(p,sort_keys=True)
 if key in cache:return cache[key]
 mat=render(source,case,p);s=scores(mat,T,case);C=icon_color(mat,p['icon'],L)[iy0-b:iy1-b,ix0-a:ix1-a];s['foreground']=float(np.sqrt(np.mean((C[safe]-target[iy0:iy1,ix0:ix1][safe])**2))*255)
 s['glass']=s['all_glass']['rmse'];s['E']=float(np.sqrt(.7*s['glass']**2+.3*s['rim']['rmse']**2))
 np.save(out/f'{tag}-material.npy',mat);cache[key]=(s,tag);print(tag,s['E'],s['glass'],s['foreground'],flush=True);return s,tag
base,base_tag=evaluate(p0,'baseline');expected=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/settled-scores.json').read_text())['media']['scores'];assert abs(base['glass']-expected['all_glass']['rmse'])<1e-6
rows=[];best=None
for k,w in enumerate([4.48,4.52,4.4,4.6]):
 p=copy.deepcopy(p0);p['parameters']['width']=w;s,tag=evaluate(p,f'trial-{k+1}')
 allowed=all(s[n]<=base[n] for n in ['E','glass','foreground']);row=dict(recipe=p,scores=s,allowed=allowed,tag=tag);rows.append(row)
 if allowed and s['E']<base['E']-1e-6 and (best is None or s['E']<best['scores']['E']):best=row
 # Short bounded neighborhood; stop at first meaningful non-regressive point.
 if best is not None:break
record=dict(method=__doc__,baseline_recipe=p0,baseline=base,trials=rows,candidate=best,input_sha256={n:hashlib.sha256((inputs/n).read_bytes()).hexdigest() for n in ['media-source.png','media-target.png']},accepted=False,limits='Single active reference only; existing empirical radial map, not recovered Apple surface. Source, icons, filters/material and masks fixed. No copied exterior used for scoring.')
(out/'candidate.json').write_text(json.dumps(record,indent=2)+'\n');print('DONE',bool(best),flush=True)
