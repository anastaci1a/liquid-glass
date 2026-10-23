import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_gamma_cache import GammaStudy,GammaCache
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-gamma-bound';out.mkdir(exist_ok=True)
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=old['parameters'];co=np.array(old['material']);rows=[]
for name in ['a','b']:
 s=GammaStudy(root/'paired'/name);cache=GammaCache(s,p);cases=[]
 for gamma in [p['gamma'],1.9,2.4]:
  q={**p,'gamma':gamma};direct=s.render(q,co);fast=cache.gamma(gamma).render(co)
  difference=float(np.max(abs(direct-fast)));assert difference<2e-6,difference
  cases.append(dict(gamma=gamma,maximum_render_difference=difference))
 rows.append(dict(observation=name,capture_error=cache.capture_error,cases=cases));print(rows[-1],flush=True)
with (out/'cache-verification.json').open('x') as f:json.dump(dict(rows=rows),f,indent=2)
