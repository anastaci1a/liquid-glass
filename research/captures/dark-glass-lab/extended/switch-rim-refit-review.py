"""Shared material re-fit for narrower rim basis; unchanged source/geometry."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from paired_fit import Cached,scores
from material_local import trial
root=Path('/evidence/extended/active-switch');out=root/'rim-width-review';old=json.loads((root/'crown-material-review/candidate.json').read_text());S=[Study(root/'paired'/n) for n in ['a','b']];rows=[];best=None
for factor in [.7,.85]:
 p=copy.deepcopy(old['parameters']);p['rim_width']*=factor;C=[Cached(s,p) for s in S];start=dict(material=old['material'],scores=scores(C,old['material']))
 co,sc,calls=trial(C,start,list(range(23)),iterations=7,progress=lambda r:print(json.dumps(dict(factor=factor,**r)),flush=True))
 native=[s.scores(s.render(p,co)) for s in S];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(native,old['scores'])];ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,native,old['scores']))
 row=dict(factor=factor,parameters=p,material=co.tolist(),scores=native,ratios=ratios,numeric_pass=ok,accepted=False);rows.append(row)
 if ok and (best is None or max(ratios)<max(best['ratios'])):best=row
 (out/'refit.json').write_text(json.dumps(dict(trials=rows,candidate=best),indent=2)+'\n');print('FINAL',factor,ratios,ok,flush=True)
 del C
