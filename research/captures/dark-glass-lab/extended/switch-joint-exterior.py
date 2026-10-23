import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');old=json.loads((root/'rim-width-review/minimax.json').read_text());new=json.loads((root/'joint-native-review/batch-01.json').read_text());rows=[]
for n in ['a','b']:
 s=Study(root/'paired'/n);mask=(s.sd>0)&(s.sd<.35);values=[]
 for r in [old,new]:
  C=clean_composite(s,r['parameters'],s.render(r['parameters'],np.array(r['material'])));values.append(float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2))))
 rows.append(dict(observation=n,previous=values[0],candidate=values[1],passed=values[1]<=values[0]));print(rows[-1],flush=True)
(root/'joint-native-review/batch-01-exterior.json').write_text(json.dumps(rows,indent=2)+'\n')
