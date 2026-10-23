"""Compact shared exposure test on both frozen Search observations."""
import sys,json,copy,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction']
import cv2,numpy as np
from extended_fit import Study
from extended_shadow import shadow
cv2.setNumThreads(1)
root=Path('/evidence/extended');inputs=root/'music-search-vector-paired-replay';out=root/'search-short-round/pass-01';out.mkdir(parents=True,exist_ok=True);assert not (out/'candidate.json').exists()
S=[Study(inputs/n) for n in ['a','b']];old=json.loads((inputs/'a/accepted.json').read_text());p=old['parameters'];co=np.asarray(old['material']);accepted=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/music-search-vector/paired/accepted.json').read_text())
def metrics(s,im):
 m=s.scores(im,False);m['E']=float(np.sqrt(m['loss']));a,b,c,d=s.crop
 # Preserve the historical exterior-only mask; no foreground or glass pixels.
 *_,(sd,_,_)=s.shape(s.x,s.y,p)
 known=cv2.imread(str(s.folder/'known.png'),cv2.IMREAD_GRAYSCALE)[b:d,a:c]>0
 ext=(sd>1.5/s.L)&(sd<.20)&known
 X=s.x*s.L+s.case['center'][0];Y=s.y*s.L+s.case['center'][1]
 for x,y,x1,y1 in s.case.get('exterior_exclusions',[]):ext&=~((X>=x)&(X<=x1)&(Y>=y)&(Y<=y1))
 exterior=s.source if s.exterior_source is None else s.exterior_source
 B=exterior[b:d,a:c]*(1-shadow(s,p,s.x,s.y))[...,None]
 m['shadow']=float(np.sqrt(np.mean(((B-s.target_crop)[ext]*255)**2)));allfg=s.apply_foreground(im.copy())
 fg=[]
 for layer in s.case['foreground_layers']:
  if 'vector_asset' in layer and layer['mode']!='transmission' and layer.get('fit_style',True):
   x,y,X,Y=layer['box'];fg.append(float(np.mean((allfg[y-b:Y-b,x-a:X-a]-s.target[y:Y,x:X])**2))*255**2)
 assert len(fg)==1;m['foreground']=float(np.sqrt(fg[0]));return m
base=[]
for i,s in enumerate(S):
 im=s.render(p,co);m=metrics(s,im);assert abs(m['glass']['rmse']-accepted['scores'][i]['glass']['rmse'])<1e-6;assert abs(m['foreground']**2-accepted['foreground_style_scores']['after_mse'][i])<1e-3;base.append(m);np.save(out/f'baseline-{i}.npy',im);print('BASE',i,m,flush=True)
rows=[];best=None
for factor in [.999,1.001,.995,1.005,.99,1.01]:
 c=co*factor;imgs=[s.render(p,c) for s in S];ms=[metrics(s,im) for s,im in zip(S,imgs)]
 allowed=all(a['E']<=b['E'] and a['glass']['rmse']<=b['glass']['rmse'] and all(a[k]<=b[k] for k in ['shadow','foreground']) for a,b in zip(ms,base));ratios=[a['E']/b['E'] for a,b in zip(ms,base)];row=dict(factor=factor,material=c.tolist(),scores=ms,ratios=ratios,allowed=allowed);rows.append(row);print('TRIAL',factor,ratios,allowed,flush=True)
 if allowed and any(r<1-1e-7 for r in ratios):
  best=row
  for i,im in enumerate(imgs):np.save(out/f'candidate-{i}.npy',im)
  break
record=dict(parameters=p,baseline=base,trials=rows,candidate=best,accepted=False,method=__doc__,limits='Two backdrops from one source video, no new source or glyph geometry. Existing standard material terms only; no Apple-parity claim. Historical exterior-only mask and generated shadow retained exactly; previous generic no-glyph replay assertion correctly rejected the first preflight, before any candidate. No guard removed.')
(out/'candidate.json').write_text(json.dumps(record,indent=2)+'\n')
