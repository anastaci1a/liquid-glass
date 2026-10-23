import sys,json,copy,time,gc
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from switch_native_cache import NativeCachedStudy
root=Path('/evidence/extended/active-switch');recipe=json.loads((root/'rim-width-review/minimax.json').read_text());p=recipe['parameters'];co=np.array(recipe['material']);records=[]
for label in ['a','b']:
 s=Study(root/'paired'/label);fast=NativeCachedStudy(root/'paired'/label,p)
 for variant in [0,1]:
  q=copy.deepcopy(p)
  if variant:q['c3']+=.013;q['core_x']-=.017;q['cap_normal_gain']+=.04
  t=time.time();a=s.render(q,co);slow_time=time.time()-t;t=time.time();b=fast.render(q,co);fast_time=time.time()-t
  error=float(np.max(abs(a-b)));assert error==0,'Cached renderer differs from original'
  records.append(dict(observation=label,variant=variant,max_absolute_difference=error,original_seconds=slow_time,cached_seconds=fast_time,cache_bytes=fast.template_bytes,templates=len(fast.templates)));print(records[-1],flush=True)
 del s,fast;gc.collect()
(root/'joint-native-review/cache-verification.json').write_text(json.dumps(records,indent=2)+'\n')
