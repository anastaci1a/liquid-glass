"""Five predeclared fixed-material native probes; one geometry family."""
import sys,json,copy,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from switch_curvature_cap import CurvatureCapStudy
from joint_visible_statistics import measures
from source_support import coverage_report,supported
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev6-curvature-cap';model=json.loads((root/'rev5-joint-existing/candidate.json').read_text());base=json.loads((root/'rev5-joint-existing/independent-resumed/verification.json').read_text())['candidate']['observations'];S=[CurvatureCapStudy(root/'paired'/n) for n in ['a','b']];rows=[]
# Uniform-input optical field test, independent of target and material.
checks=[]
for s in S:
 source=s.source.copy();s.source=np.full_like(source,.4);s.cache.clear();p=copy.deepcopy(model['parameters']);x,y=np.meshgrid(np.linspace(-1.4,1.4,31),np.linspace(-1.,1.,23));A,_=s.field(x,y,p);p['curvature_cap_mix']=.02;B,_=s.field(x,y,p);error=float(abs(A-B).max());assert error<1e-6
 s.source=source;s.cache.clear();checks.append(dict(observation=s.folder.name,uniform_field_max_difference=error))
(out/'screen-controls.json').write_text(json.dumps(checks,indent=2)+'\n')
for amplitude in [0.,.002,-.002,.02,-.02]:
 p=copy.deepcopy(model['parameters']);p['curvature_cap_mix']=amplitude;metrics=[];supports=[];start=time.time()
 for s in S:
  im=s.render(p,np.array(model['material']));m={**s.scores(im,False),**measures(s,p,im)};metrics.append(m);support=coverage_report(s,p);supports.append(dict(observation=s.folder.name,passed=supported(s,support),details=support))
  np.save(out/f'screen-{amplitude:+.3f}-{s.folder.name}.npy',im)
  if amplitude==0:assert abs(m['loss']-base[s.folder.name.upper()]['loss'])<1e-9
 old=[base[s.folder.name.upper()] for s in S];ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(metrics,old)];guards=[a['glass']['rmse']<=b['glass']['rmse'] and a['shadow']['rmse']<=b['shadow']['rmse'] for a,b in zip(metrics,old)]
 row=dict(amplitude=amplitude,scores=metrics,ratios=ratios,guards=guards,center_support=supports,numeric_pass=amplitude!=0 and all(r<=.995 and g for r,g in zip(ratios,guards)),accepted=False,seconds=time.time()-start);rows.append(row);print('PROBE',amplitude,ratios,guards,row['numeric_pass'],round(time.time()-start,2),flush=True)
 (out/'native-screen.json').write_text(json.dumps(dict(protocol=__doc__,rows=rows,accepted=False,limits='Native sensitivity, original sources/masks/material. Source center checks are not a complete HQ ray proof. No new count or physical-solid claim.'),indent=2)+'\n')
