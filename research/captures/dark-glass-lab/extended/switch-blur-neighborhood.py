"""Separate source/output ordinary scattering from color dispersion."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
root=Path('/evidence/extended/active-switch');out=root/'blur-neighborhood';out.mkdir(exist_ok=True);old=json.loads((root/'rim-width-review/minimax.json').read_text());S=[Study(root/'paired'/n) for n in ['a','b']];rows=[];best=None
for source,post in [(0,0),(.5,.5),(.75,.75),(.5,1),(1,.5),(1,0),(0,1),(1.25,1.25)]:
 p=copy.deepcopy(old['parameters']);p['sigma']*=source;p['post_sigma']*=post;sc=[s.scores(s.render(p,np.asarray(old['material'])),include_ssim=False) for s in S];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,old['scores'])];ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,sc,old['scores']))
 row=dict(source_factor=source,post_factor=post,scores=sc,ratios=ratios,numeric_pass=ok);rows.append(row)
 if ok and (best is None or max(ratios)<max(best['ratios'])):best=dict(parameters=p,material=old['material'],scores=sc,ratios=ratios)
 print(json.dumps({k:row[k] for k in ['source_factor','post_factor','ratios','numeric_pass']}),flush=True);(out/'review.json').write_text(json.dumps(dict(trials=rows,candidate=best,accepted=False),indent=2)+'\n')
