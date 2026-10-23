import sys,json
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from extended_fit import Study
from switch_euclidean_surface import EuclideanSurfaceStudy
from joint_visible_statistics import measures
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';saved=json.loads((out/'photometric-progress.json').read_text());assert len(saved['history'])==10;old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());native=[]
for i,n in enumerate(['a','b']):
 s=EuclideanSurfaceStudy(root/'paired'/n);b=Study(s.folder);im=s.render(saved['parameters'],np.array(saved['material']));baseline=b.render(old['parameters'],np.array(old['material']));m={**s.scores(im),**measures(s,saved['parameters'],im)};bm={**b.scores(baseline),**measures(b,old['parameters'],baseline)};E=float(np.sqrt(m['loss']));assert abs(E-[15.276824905112036,16.60570560678378][i])<1e-9
 native.append(dict(E=E,ratio=float(np.sqrt(m['loss']/bm['loss'])),scores=m,baseline=bm,nonregression=all(m[k]['rmse']<=bm[k]['rmse'] for k in ['glass','shadow'])))
saved.update(native=native,accepted=False,numeric_pass=False,recovered_by_independent_replay=True,limits='Original final report overwritten accidentally; exact10-step parameters/material/history survived in progress file. Fresh native replay matches both previously printed E values within1e-9. No accepted artifact or count changed.')
with (out/'first-stage-recovered-report.json').open('x') as f:f.write(json.dumps(saved,indent=2)+'\n')
print('RESTORED',[(v['E'],v['ratio']) for v in native],flush=True)
