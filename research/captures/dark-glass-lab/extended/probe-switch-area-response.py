"""Geometry-only normalization and fixed-material native area-law screen."""
import sys,json,copy,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_area_response import AreaResponseStudy,relative_area
from extended_fit import Study
from joint_visible_statistics import measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-area-response';out.mkdir(exist_ok=True)
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=old['parameters'];co=np.array(old['material']);base=json.loads((root/'rev5-filter-space/material-run-inputs.json').read_text())['baseline']
S=[AreaResponseStudy(root/'paired'/n) for n in ['a','b']];areas=[relative_area(s,p) for s in S];reference=float(np.sqrt(np.prod(areas)))
protocol=dict(relative_areas=areas,area_reference=reference,reference_rule='Geometric mean of the two measured pose areas; fixed before image scoring, not target-RGB fitted.',exponents=[0.,.5,1.,2.],bounds=[0,2],accepted=False)
with (out/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
rows=[]
for i,(name,s) in enumerate(zip(['a','b'],S)):
 for k in protocol['exponents']:
  q={**p,'area_exponent':k,'area_reference':reference};start=time.time();im=s.render(q,co);m={**s.scores(im,False),**measures(s,q,im)}
  ratio=float(np.sqrt(m['loss']/base[i]['loss']))
  if k==0:assert abs(ratio-1)<1e-9
  row=dict(observation=name,area_exponent=k,transport_scale=float((areas[i]/reference)**(-k)),E_ratio=ratio,scores=m,seconds=time.time()-start);rows.append(row)
  with (out/'trials.ndjson').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps(row),flush=True)
with (out/'screen.json').open('x') as f:json.dump(dict(protocol=protocol,rows=rows,accepted=False),f,indent=2)
