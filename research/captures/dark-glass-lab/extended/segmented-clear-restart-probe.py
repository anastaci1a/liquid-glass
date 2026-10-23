"""Read-only multi-start probe; do not mutate an accepted checkpoint."""
from pathlib import Path
import sys,json,copy
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from extended_fit import Study
from paired_fit import permitted
root=Path('/evidence/extended/active-segmented-selector');out=root/'clear-restart-probe';out.mkdir(exist_ok=True)
state=json.loads((root/'accepted.json').read_text());s=Study(root);rows=[]
for family in ['retained-normal','clear-center']:
 for sigma in [0.,1.,2.,4.,8.,16.]:
  for cx in [0.,.05,.1,.15,.18]:
   for cy in [0.,.05,.1,.15,.18]:
    p=copy.deepcopy(state['parameters']);p.update(sigma=sigma,core_x=cx,core_y=cy)
    if family=='clear-center':p.update(amplitude=0.,tangent=0.,coupling=0.,spline=False)
    loss,co=s.fit(p);rows.append(dict(family=family,training_loss=float(loss),parameters=p,material=co.tolist()))
 rows.sort(key=lambda r:r['training_loss']);print('Completed family',family,'best training',rows[0]['training_loss'],flush=True)
best=[]
for i,row in enumerate(sorted(rows,key=lambda r:r['training_loss'])[:10]):
 pred=s.render(row['parameters'],np.array(row['material']));q={**row,'scores':s.scores(pred)};q['allowed']=permitted([q['scores']],[state['scores']]);best.append(q)
 if i<3:s.comparison(pred,out/f'candidate-{i}.png',row['parameters'],context_completed=True)
(out/'report.json').write_text(json.dumps(dict(baseline=state,proposal_count=len(rows),native_finalists=best,limits='Read-only restart experiment on one frozen reference. No accepted-state mutation or completed-pass count. Final retention must recheck the then-current incumbent and the second reference.'),indent=2)+'\n')
print(json.dumps([dict(family=r['family'],loss=r['scores']['loss'],glass=r['scores']['glass']['rmse'],sigma=r['parameters']['sigma'],cx=r['parameters']['core_x'],cy=r['parameters']['core_y'],allowed=r['allowed']) for r in best]),flush=True)
