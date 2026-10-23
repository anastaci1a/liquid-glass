import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from switch_cap_edge_model import CapEdgeStudy
from revision_replay import clean_composite
from source_support import coverage_report,supported
from publish import pair
root=Path('/evidence/extended/active-switch');out=root/'rev3-cap-edge-review';r=json.loads((out/'interim-candidate.json').read_text());rows=[]
for name in ['a','b']:
 s=CapEdgeStudy(root/'paired'/name);p=r['parameters'];im=s.render(p,np.array(r['material']));C=clean_composite(s,p,im);ext=(s.sd>0)&(s.sd<.35);score=s.scores(im)
 score['shadow']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2)))};support=coverage_report(s,p)
 pair(np.uint8(np.rint(s.target_crop*255)),np.uint8(np.rint(np.clip(C,0,1)*255)),['Apple','Interim cap-depth profile']).save(out/f'interim-{name}.png')
 rows.append(dict(observation=name,scores=score,source_support=support,center_source_pass=supported(s,support)));print(name,score['loss'],score['shadow'],supported(s,support),flush=True)
(out/'interim-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
