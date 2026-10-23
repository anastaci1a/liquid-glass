"""Separate ordinary source/output blur sensitivity on accepted revision4.

The cap profile now differs materially from revision3; test whether inherited
kernel widths still over-soften its edges. Directional dispersion is fixed.
One family; screen proposals are not verified passes. Native scoring unchanged.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'rev4-kernel-review';out.mkdir(exist_ok=True)
base=json.loads((root/'rev3-cap-edge-review/candidate.json').read_text());v=json.loads((root/'rev3-cap-edge-review/hq/verification.json').read_text());old=[v['candidate']['observations'][n] for n in ['A','B']]
S=[Study(root/'paired'/n) for n in ['a','b']];co=np.array(base['material']);rows=[]
trials=[('sigma',1.)]+[(key,factor) for key in ['sigma','post_sigma'] for factor in [.6,.8,1.2,1.4]]
for key,factor in trials:
 p=copy.deepcopy(base['parameters']);p[key]*=factor;t=time.time();scores=[]
 for i,s in enumerate(S):
  im=s.render(p,co);m=s.scores(im,include_ssim=False);C=clean_composite(s,p,im);mask=(s.sd>0)&(s.sd<.35);m['shadow']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2)))};scores.append(m)
  if factor==1:assert abs(m['loss']-old[i]['loss'])<1e-8
 ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(scores,old)];guards=[all(a[k]['rmse']<=b[k]['rmse']+1e-8 for k in ['glass','rim','shadow']) for a,b in zip(scores,old)]
 rows.append(dict(parameter=key,factor=factor,scores=scores,ratios=ratios,guards=guards,numeric_pass=all(r<=.995 and g for r,g in zip(ratios,guards))))
 (out/'screen.json').write_text(json.dumps(dict(method=__doc__,baseline=base,baseline_scores=old,trials=rows,accepted=False),indent=2)+'\n');print(key,factor,ratios,guards,round(time.time()-t,2),flush=True)
