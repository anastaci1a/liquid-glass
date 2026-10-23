"""Bounded contour-family screen; old optical/material coefficients fixed."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from extended_fit import Study
from PIL import Image
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'crown-screen';out.mkdir(exist_ok=True)
old=json.loads((root/'accepted.json').read_text());S=[Study(root/n) for n in ['a','b']];co=np.asarray(old['material']);rows=[]
for softness in [0,.025,.06,.12,.2,.35,.55]:
 p={**old['parameters'],'crown_softness':softness};pred=[s.render(p,co) for s in S];scores=[s.scores(im) for s,im in zip(S,pred)];row=dict(softness=softness,scores=scores);rows.append(row)
 for label,s,im in zip(['a','b'],S,pred):
  a,b,c,d=s.crop;cov=s.shape_coverage(p);base=s.source[b:d,a:c].copy();q=p['shadow'];*_,(sd,_,_)=s.shape(s.x-q['offset'][0],s.y-q['offset'][1],p);base*=1-q['opacity']*np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2)[...,None];result=im*cov[...,None]+base*(1-cov[...,None]);Image.fromarray(np.uint8(np.rint(np.clip(result,0,1)*255))).save(out/f'{softness}-{label}.png')
 print(json.dumps(dict(softness=softness,loss=[m['loss'] for m in scores],glass=[m['glass']['rmse'] for m in scores])),flush=True)
(out/'screen.json').write_text(json.dumps(dict(rows=rows,accepted=False,limits='One contour-family screening experiment, seven parameter probes; no source, material or pass-count mutation. Shape changes need exterior shadow and silhouette review separately.'),indent=2)+'\n')
