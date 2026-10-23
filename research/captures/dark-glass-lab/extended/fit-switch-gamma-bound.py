"""Review an inherited input-gamma bound after geometry/ambient revisions.

The accepted exponent1.549748 is near the old1.55 limit. One shared positive
curve and existing material; no source/geometry/blur/dispersion changes.
"""
import sys,json,copy,time,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from switch_gamma_cache import GammaStudy,GammaCache
from joint_visible_statistics import statistics,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-gamma-bound'
assert (out/'cache-verification.json').exists()
final=out/'settlement.json'
if final.exists():raise FileExistsError(final)
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p0=old['parameters'];S=[GammaStudy(root/'paired'/n) for n in ['a','b']];caches=[GammaCache(s,p0) for s in S]
point=np.r_[p0['gamma'],old['material']];scales=np.r_[.1,np.full(23,.05)]
def images(v):return [c.gamma(v[0]).render(v[1:]) for c in caches]
def params(v):return {**p0,'gamma':float(v[0])}
def metrics(ims,v):return [{**s.scores(im,False),**measures(s,params(v),im)} for s,im in zip(S,ims)]
ims=images(point);met=metrics(ims,point);base=copy.deepcopy(met)
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
def bound(k):
 if k==0:return(.65,2.5)
 j=k-1;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
run=dict(initial_material=point[1:].tolist(),gamma_initial=float(point[0]),gamma_bounds=bound(0),baseline=base,files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),Path('/evidence/extended/switch_gamma_cache.py')]})
with (out/'run-inputs.json').open('x') as f:json.dump(run,f,indent=2)
history=[];trust=1.
for iteration in range(8):
 start=time.time();forms=[]
 for cache,im in zip(caches,ims):
  eps=.0003;dp=cache.gamma(point[0]+eps).render(point[1:]);dm=cache.gamma(point[0]-eps).render(point[1:]);derivative=(dp-dm)/(2*eps)
  cache.gamma(point[0]);forms.append(statistics(cache,point[1:],[derivative],scales,im))
 np.savez_compressed(out/f'form-{iteration+1:02d}.npz',point=point,scales=scales,**{f'{i}_{name}_{kind}':value[j] for i,f in enumerate(forms) for name,value in f.items() for j,kind in enumerate(['H','g'])})
 def value(i,v,kind):
  H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if kind=='loss' else forms[i][kind]
  b=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return b+2*g@d+d@H@d
 def constraints(v):return np.array([q for i,b in enumerate(base) for q in [v[-1]-value(i,v,'loss')/b['loss'],*[1-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(24),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best,bm,bi=point.copy(),met,ims;trials=[]
 for alpha in [1,.5,.25,.125,.0625]:
  v=point+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs,v);allowed=all(a[k]['rmse']<=b[k]['rmse']+1e-7 for a,b in zip(m,base) for k in ['glass','shadow'])
  trial=dict(iteration=iteration+1,alpha=alpha,point=v.tolist(),allowed=allowed,scores=m);trials.append(trial)
  with (out/'trials.ndjson').open('a') as f:f.write(json.dumps(trial)+'\n')
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi
 history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)]
 record=dict(parameters=params(point),material=point[1:].tolist(),scores=met,baseline=base,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios),accepted=False,history=history,method=__doc__)
 (out/'progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,'gamma',point[0],'gain',gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,flush=True)
