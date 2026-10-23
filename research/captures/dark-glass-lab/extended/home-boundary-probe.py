from pathlib import Path
import copy,json,time,numpy as np
from extended_fit import Study
from paired_fit import Cached,scores
from material_local import trial
root=Path('/evidence/extended/music-home-vector');out=root/'boundary-probe';out.mkdir(exist_ok=True)
single=json.loads((root/'accepted.json').read_text());paired=json.loads((root/'paired/accepted.json').read_text());studies=[Study(root/'paired'/name) for name in ['a','b']];p=single['parameters'];co=np.array(single['material']);caches=[Cached(s,p) for s in studies];actual=scores(caches,co)
assert abs(actual[0]['loss']-single['scores']['loss'])<1e-6
old=dict(parameters=p,material=co.tolist(),scores=actual);print(json.dumps(dict(start=actual,old_paired=paired['scores'])),flush=True)
start=time.time();v,metric,calls=trial(caches,old,list(range(23)),iterations=30,progress=lambda row:print(json.dumps(row),flush=True))
full=[s.scores(s.render(p,v)) for s in studies]
from paired_fit import permitted
thresholds=[single['scores'],paired['scores'][1]]
report=dict(scope='Private feasibility probe, not a counted pass or published calibration. Starts with actual scores of retained single map/material on both inputs; no silently substituted scores.',baseline=old,thresholds=thresholds,parameters=p,material=v.tolist(),scores=full,permitted=permitted(full,thresholds),evaluations=calls,seconds=time.time()-start)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for name,s in zip(['a','b'],studies):s.comparison(s.render(p,v),out/(name+'.png'),p)
print(json.dumps(report),flush=True)
