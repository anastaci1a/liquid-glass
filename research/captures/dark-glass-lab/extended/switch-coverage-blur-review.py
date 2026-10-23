"""Test normalized covered-color blur instead of filtering nonexistent exterior glass.

F = G_sigma(alpha*C)/max(G_sigma(alpha),epsilon), with sharp alpha retained
for the final composite. Reflection stays after blur. No new fit parameter.
"""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from grazing_reflection import apply
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'coverage-blur-review';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text());co=np.array(old['material']);p=old['parameters'];rows=[]
for name in ['a','b']:
    s=Study(root/'paired'/name);q=copy.deepcopy(p);q['post_sigma']=0.;q.pop('grazing_reflection',None)
    color=s.render(q,co);alpha=s.shape_coverage(p);sigma=s.kernel_sigma(p,'post_sigma')
    result=cv2.GaussianBlur(color*alpha[...,None],(0,0),sigma)/np.maximum(cv2.GaussianBlur(alpha,(0,0),sigma)[...,None],1e-10)
    result=apply(s,p,result);scores=s.scores(result);whole=clean_composite(s,p,result)
    ext=(s.sd>0)&(s.sd<.35);scores['shadow']=dict(rmse=float(np.sqrt(np.mean(((whole-s.target_crop)[ext]*255)**2))))
    baseline=old['scores'][len(rows)];ratio=np.sqrt(scores['loss']/baseline['loss']);rows.append(dict(observation=name,scores=scores,ratio=ratio))
    cv2.imwrite(str(out/f'{name}.png'),cv2.cvtColor(np.uint8(np.clip(whole,0,1)*255),cv2.COLOR_RGB2BGR))
    print(name,ratio,scores['shadow'],flush=True)
(out/'review.json').write_text(json.dumps(dict(observations=rows,model=__doc__,accepted=False),indent=2)+'\n')
