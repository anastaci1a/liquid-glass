import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_filter_space import FilterSpaceStudy,decode,encode
from extended_fit import Study
from joint_visible_statistics import measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-filter-space';out.mkdir(exist_ok=True)
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p0=old['parameters'];co=np.array(old['material']);rows=[];controls=[]
grid=np.linspace(0,1,100001)
for kind in ['srgb','bt709']:
 error=float(np.max(abs(encode(decode(grid,kind),kind)-grid)))
 assert error<3e-4 if kind=='bt709' else error<4e-8
 assert np.min(np.diff(decode(grid,kind)))>=-6e-5
 controls.append(dict(transfer=kind,roundtrip_max=error,limits='BT709 rounded normative breakpoints have a small mismatch near .081; no smoothing fitted.'))
for name in ['a','b']:
 s=FilterSpaceStudy(root/'paired'/name);baseline=s.render(p0,co);direct=Study(s.folder).render(p0,co);assert np.array_equal(baseline,direct)
 base={**s.scores(baseline,False),**measures(s,p0,baseline)};trials=[]
 for kind in ['bt709','srgb']:
  for source,output in [(True,False),(False,True),(True,True)]:
   p=copy.deepcopy(p0);p.update(source_filter_space=kind if source else 'encoded',output_filter_space=kind if output else 'encoded')
   im=s.render(p,co);m={**s.scores(im,False),**measures(s,p,im)}
   row=dict(transfer=kind,source=source,output=output,scores=m,ratio=float(np.sqrt(m['loss']/base['loss'])));trials.append(row)
   with (out/'trials.ndjson').open('a') as f:f.write(json.dumps(dict(observation=name,**row))+'\n')
   print(name,kind,source,output,row['ratio'],flush=True)
 rows.append(dict(observation=name,baseline=base,trials=trials))
with (out/'review.json').open('x') as f:json.dump(dict(rows=rows,controls=controls,accepted=False,limits='Six predeclared operator combinations; fixed material/geometry/source/masks. Not a measured Apple transfer pipeline or new pass. Baseline exact.'),f,indent=2)
