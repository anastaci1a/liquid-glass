import sys,json,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_euclidean_surface import EuclideanSurfaceStudy
from switch_euclidean_fast import FastEuclideanSurfaceStudy
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';q=json.loads((out/'coupling-settlement.json').read_text());p=q['parameters'];co=np.array(q['material']);rows=[]
for name in ['a','b']:
 s=EuclideanSurfaceStudy(root/'paired'/name);f=FastEuclideanSurfaceStudy(root/'paired'/name)
 # All native emitted coordinates; no image resize or score approximation.
 elapsed=[0.,0.];errors=[0.,0.]
 for row,bottom,W,x,y in s.raster_tiles():
  start=time.time();a=s.field(x,y,p);elapsed[0]+=time.time()-start
  start=time.time();b=f.field(x,y,p);elapsed[1]+=time.time()-start
  errors=[max(errors[i],float(np.max(abs(a[i]-b[i])))) for i in [0,1]]
 assert errors==[0.,0.],errors
 rows.append(dict(observation=name,field_max_errors=errors,original_seconds=elapsed[0],cost_only_seconds=elapsed[1],timing_limit='Single interleaved run under concurrent fit load, not a stable benchmark'))
 del s,f,a,b

with (out/'fast-field-verification.json').open('x') as f:json.dump(dict(passed=True,rows=rows,method='Exact comparison at every original native emitted sample; no score/model/source change.'),f,indent=2);f.write('\n')
print(json.dumps(rows),flush=True)
