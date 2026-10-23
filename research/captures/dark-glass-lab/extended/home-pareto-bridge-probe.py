from pathlib import Path
import copy,json,time,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted,scores
from source_support import coverage_report,supported
root=Path('/evidence/extended/music-home-vector');out=root/'pareto-bridge-probe';out.mkdir(exist_ok=True)
prior=json.loads((root/'boundary-probe/report.json').read_text());seed=prior;desired=prior['thresholds'];targets=[desired[0],prior['scores'][1]];studies=[Study(root/'paired'/n) for n in ['a','b']]
keys=[*[f'c{i}' for i in range(7)],'core_x','gamma','post_sigma','rim_width','thin_width','shape_dx','shape_dy','half_x_delta'];p=seed['parameters'];co=np.array(seed['material']);scale=np.r_[np.full(23,.1),np.ones(len(keys))];point=np.r_[co,[p[k] for k in keys]];start=time.time();calls=0;memo={};best=None
class BudgetReached(Exception):pass
bounds=[(.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4) for k in range(23)]+[studies[0].parameter_bounds(k) for k in keys]
bounds=[((a-v)/s,(b-v)/s) for (a,b),v,s in zip(bounds,point,scale)];norm=np.mean([r['loss'] for r in targets])
def evaluate(u):
 global calls,best
 if calls>=1800:raise BudgetReached()
 key=np.asarray(u).tobytes()
 if key not in memo:
  memo.clear();v=point+u*scale;q={**p,**dict(zip(keys,map(float,v[23:])))};metric=scores([Cached(s,q) for s in studies],v[:23]);calls+=1
  violation=sum(max(0,(r['loss']-t['loss'])/norm)**2+max(0,(r['glass']['rmse']**2-t['glass']['rmse']**2)/norm)**2 for r,t in zip(metric,targets))
  if best is None or (permitted(metric,targets) and (not best['permitted'] or metric[1]['loss']<best['scores'][1]['loss'])):best=dict(parameters=q,material=v[:23].tolist(),scores=metric,violation=violation,permitted=permitted(metric,targets))
  memo[key]=metric
  if calls%100==0:
   (out/'running.json').write_text(json.dumps(dict(evaluations=calls,seconds=time.time()-start,best=best),indent=2)+'\n');print(json.dumps(dict(evaluations=calls,seconds=time.time()-start,loss=[r['loss'] for r in best['scores']],violation=best['violation'])),flush=True)
 return memo[key]
def constraints(u):return np.array([x for r,t in zip(evaluate(u),targets) for x in [(t['loss']-r['loss'])/norm,(t['glass']['rmse']**2-r['glass']['rmse']**2)/norm]])
try:
 fit=minimize(lambda u:evaluate(u)[1]['loss']/norm,np.zeros(len(point)),method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=100,ftol=1e-9,eps=.002));message=fit.message
except BudgetReached:message='Stopped at1800evaluations; retained native-feasible best only'
q=best['parameters'];v=np.array(best['material']);metric=[s.scores(s.render(q,v)) for s in studies];footprints=[coverage_report(s,q) for s in studies];best.update(scores=metric,permitted=permitted(metric,desired) and all(supported(s,r) for s,r in zip(studies,footprints)),source_support=footprints)
for name,s in zip(['a','b'],studies):s.comparison(s.render(q,v),out/(name+'.png'),q)
(out/'report.json').write_text(json.dumps(dict(scope='Private joint feasibility search, not counted or adopted. Frozen inputs, masks and strict desired thresholds; actual metrics remain separate.',targets=desired,optimization_limits=targets,keys=keys,best=best,evaluations=calls,seconds=time.time()-start,solver_message=message),indent=2)+'\n')
print(json.dumps(dict(evaluations=calls,seconds=time.time()-start,loss=[r['loss'] for r in best['scores']],permitted=best['permitted'])),flush=True)
