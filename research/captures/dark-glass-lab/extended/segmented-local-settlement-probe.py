"""Test local, bounded optimizer neighborhoods against frozen native gates."""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'local-settlement-probe';out.mkdir(exist_ok=True);state=json.loads((folder/'accepted.json').read_text());s=Study(folder);second=Study(root/'segmented-matched-state-preparation/second-observation');p=copy.deepcopy(state['parameters']);co=np.array(state['material']);native=state['scores'];rows=[]
for stage in range(1,9):
 keys=([*[f'c{i}' for i in range(7)],'core_x','core_y','sigma','post_sigma'] if stage%2 else ['tangent','tangent_band','coupling','cap_normal_gain','cap_join_width','rim_width','thin_width','sigma','post_sigma'])
 steps={k:(.045 if k.startswith('c') else .015) for k in keys};steps.update(sigma=.8,post_sigma=.7,cap_normal_gain=.15,coupling=.15,cap_join_width=.05,rim_width=.04,thin_width=.008,tangent_band=.08,tangent=.03)
 bounds=[]
 for k in keys:
  a,b=s.parameter_bounds(k);bounds.append((max(a,p[k]-steps[k]),min(b,p[k]+steps[k])))
 best=[s.fit(p)[0],p,co];calls=0;t=time.time();proposals=[]
 def evaluate(v):
  global calls
  calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,c=s.fit(q)
  if loss<best[0]:best[:]=[loss,q,c]
  if calls%100==0:proposals.append((float(loss),q,c))
  return float(loss)
 minimize(evaluate,[p[k] for k in keys],method='Powell',bounds=bounds,options=dict(maxfev=4500,xtol=.00008,ftol=1e-9))
 proposals.append(tuple(best));trial=[]
 for _,q,c in sorted(proposals,key=lambda row:row[0])[:5]:
  sc=s.scores(s.render(q,c));trial.append((sc,q,c))
 winner=min(trial,key=lambda row:row[0]['loss']);sc,q,c=winner;ok=sc['loss']<=native['loss']+1e-8 and sc['glass']['rmse']<=native['glass']['rmse']+1e-8 and supported(s,coverage_report(s,q))
 if ok:p=copy.deepcopy(q);co=c.copy();native=sc
 scores=[native,second.scores(second.render(p,co))];row=dict(stage=stage,experiment='Local native-gated profile settlement' if stage%2 else 'Local native-gated cap and clarity settlement',parameters=p,material=co.tolist(),scores=scores,candidate_scores=sc,retained=ok,training_loss=best[0],evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{stage}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(stage=stage,loss=[v['loss'] for v in scores],glass=[v['glass']['rmse'] for v in scores],sigma=p['sigma'],post_sigma=p['post_sigma'],retained=ok,calls=calls)),flush=True)
 if ok or stage==8:s.comparison(s.render(p,co),out/f'{stage}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(baseline=state,rows=rows,limits='Read-only optimizer diagnostic. Native A loss/glass nonregression enforced on proposals; B scores observed but not yet paired-calibrated. No input/accepted/public state mutation.'),indent=2)+'\n')
