"""Fixed-length directional spectral separation, distinct from ordinary blur."""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from crop_diagnostics import diagnostics
root=Path('/evidence/extended/active-switch');out=root/'dispersion-neighborhood';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text());S=[Study(root/'paired'/n) for n in ['a','b']];baseline=old['scores'];rows=[];best=None
for angle in [np.pi/3,np.arctan2(2,1),old['parameters']['directional_transmission']['angle'],np.pi/2]:
 for length in [.08,.12]:
  for strength in [old['parameters']['directional_transmission']['strength'],.65,.85]:
   p=copy.deepcopy(old['parameters']);p['directional_transmission'].update(angle=float(angle),length=length,strength=strength)
   pred=[s.render(p,np.asarray(old['material'])) for s in S];sc=[s.scores(v,include_ssim=False) for s,v in zip(S,pred)];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,baseline)];ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,sc,baseline));row=dict(angle=float(angle),length=length,strength=strength,ratios=ratios,scores=sc,numeric_pass=ok);rows.append(row)
   if ok and (best is None or max(ratios)<max(best['ratios'])):best=dict(parameters=p,material=old['material'],scores=sc,ratios=ratios)
   print(json.dumps({k:row[k] for k in ['angle','length','strength','ratios','numeric_pass']}),flush=True)
   (out/'review.json').write_text(json.dumps(dict(trials=rows,candidate=best,accepted=False,limits='Shared RGB lateral-chromatic approximation; source/output ordinary blur unchanged. Frozen baseline revision2. Internal grid points are not qualifying passes.'),indent=2)+'\n')
