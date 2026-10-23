import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from extended_fit import Study
from switch_rim_width_cache import RimWidthCache
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'rev5-light-width';out.mkdir(exist_ok=True)
seed=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=seed['parameters'];co=np.array(seed['material']);rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);cache=RimWidthCache(s,p)
 for r,t in [(1,1),(.8,1.2),(1.2,.8)]:
  q=copy.deepcopy(p);q['rim_width']*=r;q['thin_width']*=t
  direct=s.render(q,co);cached=cache.widths(q['rim_width'],q['thin_width']).render(co);delta=float(np.max(abs(direct-cached)))
  assert delta<2e-6,delta
  rows.append(dict(observation=name,rim_factor=r,thin_factor=t,maximum_absolute_difference=delta))
 del s,cache
with (out/'cache-verification.json').open('x') as f:json.dump(dict(rows=rows,limits='Cost-only comparison for existing lighting basis. No new score/pass.'),f,indent=2)
print(json.dumps(rows),flush=True)
