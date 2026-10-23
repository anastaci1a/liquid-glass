from pathlib import Path
import json,time,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,scores,permitted
from source_support import coverage_report,supported
root=Path('/evidence/extended/music-home-vector');out=root/'tone-bridge-probe';out.mkdir(exist_ok=True)
a=json.loads((root/'accepted.json').read_text());b=json.loads((root/'paired/accepted.json').read_text());targets=[a['scores'],b['scores'][1]];studies=[Study(root/'paired'/n) for n in ['a','b']];results=[]
for label,seed in [('single',a),('paired',b)]:
 start=time.time();p=seed['parameters'];caches=[Cached(s,p) for s in studies];base=np.r_[seed['material'],np.ones(3)];scale=np.r_[np.full(23,.1),np.ones(3)];memo={};best=None;calls=0;norm=np.mean([r['loss'] for r in targets])
 bounds=[(.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4) for k in range(23)]+[(.45,2.2)]*3
 bounds=[((lo-v)/s,(hi-v)/s) for (lo,hi),v,s in zip(bounds,base,scale)]
 def evaluate(u):
  global calls,best
  key=np.asarray(u).tobytes()
  if key not in memo:
   memo.clear();v=base+u*scale;pred=[np.maximum(c.render(v[:23]),0)**v[23:] for c in caches];metric=[s.scores(C,include_ssim=False) for s,C in zip(studies,pred)];calls+=1
   violation=sum(max(0,(r['loss']-t['loss'])/norm)**2+max(0,(r['glass']['rmse']**2-t['glass']['rmse']**2)/norm)**2 for r,t in zip(metric,targets))
   if best is None or violation<best['violation']-1e-14 or (violation<=1e-14 and best['violation']<=1e-14 and sum(r['loss'] for r in metric)<sum(r['loss'] for r in best['scores'])):best=dict(parameters=p,material=v[:23].tolist(),output_gamma=v[23:].tolist(),scores=metric,violation=violation,permitted=permitted(metric,targets))
   memo[key]=metric
  return memo[key]
 def constraints(u):return np.array([x for r,t in zip(evaluate(u),targets) for x in [(t['loss']-r['loss'])/norm,(t['glass']['rmse']**2-r['glass']['rmse']**2)/norm]])
 fit=minimize(lambda u:np.mean([r['loss'] for r in evaluate(u)])/norm,np.zeros(26),method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=70,ftol=1e-10,eps=.001))
 best.update(seed=label,evaluations=calls,seconds=time.time()-start,solver_message=fit.message,source_support=[coverage_report(s,p) for s in studies]);results.append(best)
 for name,s in zip(['a','b'],studies):s.comparison(np.maximum(s.render(p,np.array(best['material'])),0)**np.array(best['output_gamma']),out/(label+'-'+name+'.png'),p)
 report=dict(scope='Private empirical post-material per-channel power response, not physical dispersion or an Apple formula; no source/target/mask/accepted-state changes. Not counted or adopted.',model='C_out=C_existing^gamma_rgb after existing integration/output blur; positive exponent shared on both backgrounds.',targets=targets,results=results)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(seed=label,evaluations=calls,loss=[r['loss'] for r in best['scores']],permitted=best['permitted'],gamma=best['output_gamma'])),flush=True)
