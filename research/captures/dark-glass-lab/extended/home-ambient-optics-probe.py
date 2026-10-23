"""Joint geometry + shared source-luma rim response; strict historical gates.
Private probe, no accepted-state mutation or pass count. Frozen masks/targets.
"""
from pathlib import Path
import copy,json,time
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted
from source_support import coverage_report,supported
root=Path('/evidence/extended/music-home-vector');out=root/'ambient-optics-probe';out.mkdir(exist_ok=True)
a=json.loads((root/'accepted.json').read_text());b=json.loads((root/'paired/accepted.json').read_text());targets=[a['scores'],b['scores'][1]];studies=[Study(root/'paired'/n) for n in ['a','b']];scale=np.mean([r['loss'] for r in targets]);ambient=json.loads((root/'ambient-bridge-probe/report.json').read_text());results=[];start=time.time();calls=0
keys=['sigma','post_sigma','shape_dx','shape_dy','half_x_delta','core_x','rim_width','thin_width',*[f'c{i}' for i in range(7)]]
def merit(m):return sum(max(0,(r['loss']-t['loss'])/scale)**2+max(0,(r['glass']['rmse']**2-t['glass']['rmse']**2)/scale)**2 for r,t in zip(m,targets))
for seed in ambient['results']:
 p=copy.deepcopy(seed['parameters']);N=len(keys);point=np.r_[[p[k] for k in keys],seed['material'],seed['ambient_rim_response']];best=None;memo={};cachekey=None;caches=None;means=None
 def evaluate(v):
  global calls,cachekey,caches,means,best
  key=np.asarray(v).tobytes()
  if key not in memo:
   optical=np.asarray(v[:N]).tobytes()
   q={**p,**dict(zip(keys,v[:N]))}
   if optical!=cachekey:
    caches=[Cached(s,q) for s in studies];means=[]
    for s in studies:
     x0,y0,x1,y1=s.crop;*_,(sd,_,_)=s.shape(s.x,s.y,q);mu=s.source[y0:y1,x0:x1][sd<0].mean(0,dtype=np.float64);means.append(mu@np.array([.2126,.7152,.0722])-.5)
    cachekey=optical
   metrics=[]
   for s,c,mu in zip(studies,caches,means):
    co=v[N:N+23].copy();co[[6,9,12]]+=mu*v[N+23:];metrics.append(s.scores(c.render(co),include_ssim=False))
   calls+=1;memo.clear();memo[key]=metrics
   if best is None or merit(metrics)<merit(best['scores'])-1e-14 or (merit(metrics)<=1e-14 and sum(r['loss'] for r in metrics)<sum(r['loss'] for r in best['scores'])):best=dict(parameters=q,material=v[N:N+23].tolist(),ambient_rim_response=v[N+23:].tolist(),source_luma_offset=[float(x) for x in means],scores=metrics,permitted=permitted(metrics,targets))
   if calls%200==0:(out/'running.json').write_text(json.dumps(dict(seed=seed['seed'],calls=calls,best=best,seconds=time.time()-start),indent=2)+'\n');print(json.dumps(dict(calls=calls,losses=[r['loss'] for r in best['scores']],allowed=best['permitted'])),flush=True)
  return memo[key]
 def objective(v):return np.mean([r['loss'] for r in evaluate(v)])/scale
 def constraints(v):return np.array([x for m,t in zip(evaluate(v),targets) for x in [(t['loss']-m['loss'])/scale,(t['glass']['rmse']**2-m['glass']['rmse']**2)/scale]])
 bounds=[studies[0].parameter_bounds(k) for k in keys]+[(.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4) for k in range(23)]+[(-4,4)]*3
 fit=minimize(objective,point,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=70,ftol=1e-10,eps=1e-4))
 evaluate(fit.x);row=dict(seed=seed['seed'],solver_success=bool(fit.success),message=str(fit.message),best=best)
 footprints=[]
 for s,mu,n in zip(studies,best['source_luma_offset'],['a','b']):
  co=np.array(best['material']);co[[6,9,12]]+=mu*np.array(best['ambient_rim_response']);q=best['parameters'];pred=s.render(q,co);s.comparison(pred,out/(seed['seed']+'-'+n+'.png'),q);r=coverage_report(s,q);footprints.append(r)
 row['source_support']=footprints;row['permitted']=best['permitted'] and all(supported(s,r) for s,r in zip(studies,footprints));results.append(row)
 (out/'report.json').write_text(json.dumps(dict(model='One source-luma dependent three-coefficient neutral rim response plus one shared radial map and26 material/response coefficients. Empirical; no per-background recipe. Desired historic gates kept separate from actual seed scores.',targets=targets,results=results,calls=calls,seconds=time.time()-start),indent=2)+'\n')
 print(json.dumps(dict(seed=seed['seed'],best=best)),flush=True)
