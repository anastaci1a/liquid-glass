"""Native comparison of two declared true-distance transport initializations."""
import sys,json,copy,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_distance_transport import DistanceTransportStudy
from joint_visible_statistics import measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-distance-transport';old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());projection=json.loads((out/'proposal.json').read_text());base=json.loads((root/'rev5-filter-space/material-run-inputs.json').read_text())['baseline'];records=[]
plain=copy.deepcopy(old['parameters']);plain['distance_transport']=True
for index,name in enumerate(['a','b']):
 s=DistanceTransportStudy(root/'paired'/name)
 for label,p in [('unchanged-coefficients',plain),('map-projected',projection['parameters'])]:
  start=time.time();im=s.render(p,np.array(old['material']));m={**s.scores(im,False),**measures(s,p,im)}
  row=dict(observation=name,variant=label,scores=m,E_ratio=float(np.sqrt(m['loss']/base[index]['loss'])),seconds=time.time()-start)
  with (out/'native-initializations.ndjson').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps(row),flush=True);records.append(row)
with (out/'native-initializations.json').open('x') as f:json.dump(dict(rows=records,accepted=False),f,indent=2)
