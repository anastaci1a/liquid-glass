"""Combine continuous crown with shared post-reflection material settlement."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from progress_gate import evaluate
from PIL import Image
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'crown-material-review';out.mkdir(exist_ok=True)
old=json.loads((root/'accepted.json').read_text());settled=json.loads((root.parent/'material-settlement-review/candidate.json').read_text());S=[Study(root/n) for n in ['a','b']];co=np.array(settled['material']);rows=[];best=None
for softness in [.035,.05,.065,.08,.1,.12]:
 p={**old['parameters'],'crown_softness':softness};pred=[s.render(p,co) for s in S];scores=[s.scores(im) for s,im in zip(S,pred)];ratios=[np.sqrt(m['loss']/b['loss']) for m,b in zip(scores,old['scores'])];passed=all(r<=.995 and m['glass']['rmse']<=b['glass']['rmse'] for r,m,b in zip(ratios,scores,old['scores']));row=dict(softness=softness,parameters=p,material=co.tolist(),scores=scores,baseline=old['scores'],ratios=ratios,numeric_pass=passed,accepted=False);rows.append(row)
 if passed and (best is None or max(ratios)<max(best['ratios'])):
  best=row
  for label,s,im in zip(['a','b'],S,pred):
   a,b,c,d=s.crop;cov=s.shape_coverage(p);base=s.source[b:d,a:c].copy();q=p['shadow'];*_,(sd,_,_)=s.shape(s.x-q['offset'][0],s.y-q['offset'][1],p);base*=1-q['opacity']*np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2)[...,None];result=im*cov[...,None]+base*(1-cov[...,None]);Image.fromarray(np.uint8(np.rint(np.clip(result,0,1)*255))).save(out/f'candidate-{label}.png')
 print(json.dumps(dict(softness=softness,loss=[m['loss'] for m in scores],ratios=ratios,numeric_pass=passed)),flush=True)
(out/'review.json').write_text(json.dumps(dict(rows=rows,accepted=False),indent=2)+'\n');(out/'candidate.json').write_text(json.dumps(best,indent=2)+'\n')
