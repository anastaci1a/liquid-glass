import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from extended_fit import Study
from switch_directional_cache import DirectionalCache
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'rev5-directional-weights';out.mkdir(exist_ok=True)
seed=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=seed['parameters'];co=np.array(seed['material']);rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);cache=DirectionalCache(s,p)
 for strength,shift,width in [(1,0,1),(.8,-.05,1.2),(1.2,.05,.8)]:
  q=copy.deepcopy(p);m=q['directional_transmission'];m['strength']*=strength;m['fade_center']+=shift;m['fade_width']*=width
  direct=s.render(q,co);cached=cache.weights(m).render(co);delta=float(np.max(abs(direct-cached)))
  assert delta<2e-6,delta
  rows.append(dict(observation=name,strength_factor=strength,center_shift=shift,width_factor=width,maximum_absolute_difference=delta))
 del s,cache
with (out/'cache-verification.json').open('x') as f:json.dump(dict(rows=rows,limits='Cost-only comparison for existing directional mixture. No new score/pass.'),f,indent=2)
print(json.dumps(rows),flush=True)
