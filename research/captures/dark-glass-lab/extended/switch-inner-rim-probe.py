"""Private shared nonnegative thin-reflection experiment; frozen gates unchanged."""
from pathlib import Path
import json,time
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted,scores
from material_local import statistics
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-22.json').read_text())['current'];out=root.parent/'inner-rim-probe';out.mkdir(exist_ok=True)
start=time.time();studies=[Study(root/n) for n in ['a','b']];caches=[Cached(s,old['parameters']) for s in studies]
point=np.array(old['material']);metric=old['scores'];history=[];best=None
# A nonnegative first-order angular thin-light lobe: a>=hypot(b,c).
# This removes negative scalar radiance from this one reflection component.
# Broad signed nuisance components stay unchanged in definition and are refit.
for iteration in range(12):
 forms=[statistics(c,point) for c in caches];scale=np.mean([m['loss'] for m in metric]);radius=2 if iteration==0 else .2
 def value(i,v,kind='loss'):
  d=v-point;gH,gg=forms[i]['glass'];rH,rg=forms[i]['rim'];H,g=(.7*gH+.3*rH,.7*gg+.3*rg) if kind=='loss' else (gH,gg)
  return (metric[i]['loss'] if kind=='loss' else metric[i]['glass']['rmse']**2)+2*g@d+d@H@d
 def f(v):return np.mean([value(i,v) for i in range(2)])/scale
 constraints=[dict(type='ineq',fun=lambda v:v[6]-np.hypot(v[7],v[8]))]
 def bound(k):return (.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4)
 bounds=[(max(bound(k)[0],point[k]-radius),min(bound(k)[1],point[k]+radius)) for k in range(23)]
 fit=minimize(f,point,method='SLSQP',bounds=bounds,constraints=constraints,options=dict(maxiter=120,ftol=1e-10))
 trial=fit.x;actual=scores(caches,trial);allowed=permitted(actual,old['scores']);cone=float(trial[6]-np.hypot(trial[7],trial[8]));row=dict(iteration=iteration,losses=[m['loss'] for m in actual],glass=[m['glass']['rmse'] for m in actual],cone=cone,allowed=allowed,success=bool(fit.success));history.append(row);print(json.dumps(row),flush=True)
 if allowed and cone>=-1e-7 and (best is None or sum(m['loss'] for m in actual)<sum(m['loss'] for m in best['scores'])):best=dict(material=trial.tolist(),scores=actual)
 point,metric=trial,actual
 (out/'running.json').write_text(json.dumps(dict(history=history,best=best,seconds=time.time()-start),indent=2)+'\n')
 if iteration>1 and abs(sum(m['loss'] for m in actual)-sum(history[-2]['losses']))<1e-5:break
for n,s,c in zip(['a','b'],studies,caches):
 co=np.array(best['material']) if best else point;pred=s.render(old['parameters'],co);assert np.max(abs(pred-c.render(co)))<2e-6;s.comparison(pred,out/f'{n}.png',old['parameters'])
report=dict(model='a*thin+b*nx*thin+c*ny*thin, constrained a>=hypot(b,c); all23 coefficients shared. No channel split, no edge-specific painting.',baseline_pass=22,baseline=old['scores'],history=history,best=best,final=dict(material=point.tolist(),scores=metric),seconds=time.time()-start,status='Private hypothesis; do not replace incumbent unless frozen per-sample loss/glass gates and visual artifact check pass.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
