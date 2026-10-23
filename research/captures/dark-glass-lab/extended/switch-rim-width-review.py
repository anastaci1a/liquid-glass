"""One bounded family: narrow overly broad rim lighting, keep optics fixed."""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
root=Path('/evidence/extended/active-switch');out=root/'rim-width-review';out.mkdir(exist_ok=True)
old=json.loads((root/'crown-material-review/candidate.json').read_text());S=[Study(root/'paired'/n) for n in ['a','b']];baseline=old['scores'];records=[];best=None
for factor in [.3,.5,.7,.85,1.,1.15]:
 p=copy.deepcopy(old['parameters']);p['rim_width']*=factor;sc=[s.scores(s.render(p,np.asarray(old['material'])),include_ssim=False) for s in S]
 ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,baseline)];ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,sc,baseline))
 row=dict(factor=factor,scores=sc,ratios=ratios,numeric_pass=ok);records.append(row);print(json.dumps(row),flush=True)
 if ok and (best is None or max(ratios)<max(best['ratios'])):best=dict(parameters=p,material=old['material'],scores=sc,ratios=ratios)
 (out/'review.json').write_text(json.dumps(dict(family='Shared neutral rim lighting width; optics and color-dispersion model frozen',trials=records,candidate=best,accepted=False),indent=2)+'\n')
