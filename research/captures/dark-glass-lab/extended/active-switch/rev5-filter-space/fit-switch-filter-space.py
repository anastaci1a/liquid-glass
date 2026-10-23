"""One shared-material fit for the predeclared BT.709 filtering hypothesis.

Geometry, blur widths, directional mixture, reflection, source and masks stay
fixed. Infeasible intermediate proposals are logged, never counted as passes.
"""
import sys,json,copy,time,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from switch_filter_space import FilterSpaceStudy
from switch_filter_cache import FilterSpaceCache,material_statistics
from joint_visible_statistics import measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-filter-space'
assert (out/'cache-verification.json').exists(),'Verify cached renderer and derivative first'
final=out/'material-settlement.json'
if final.exists():raise FileExistsError(final)
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=copy.deepcopy(old['parameters']);co=np.array(old['material']);base=[]
for n in ['a','b']:
 s=Study(root/'paired'/n);im=s.render(p,co);base.append({**s.scores(im,False),**measures(s,p,im)})
p.update(source_filter_space='bt709',output_filter_space='bt709')
S=[FilterSpaceStudy(root/'paired'/n) for n in ['a','b']];caches=[FilterSpaceCache(s,p) for s in S]
def images(v):return [c.render(v) for c in caches]
def metrics(ims):return [{**s.scores(im,False),**measures(s,p,im)} for s,im in zip(S,ims)]
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
def guards(m):return all(a[k]['rmse']<=b[k]['rmse']+1e-7 for a,b in zip(m,base) for k in ['glass','shadow'])
ims=images(co);met=metrics(ims);initial=copy.deepcopy(met);scales=np.full(23,.05);trust=1.;history=[]
run=dict(parameters=p,initial_material=co.tolist(),baseline=base,initial=initial,
 files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),Path('/evidence/extended/switch_filter_cache.py'),Path('/evidence/extended/switch_filter_space.py')]})
with (out/'material-run-inputs.json').open('x') as f:json.dump(run,f,indent=2)
for iteration in range(6):
 start=time.time();forms=[material_statistics(c,co,scales,im) for c,im in zip(caches,ims)]
 np.savez_compressed(out/f'material-form-{iteration+1:02d}.npz',point=co,scales=scales,**{f'{i}_{name}_{kind}':value[j] for i,f in enumerate(forms) for name,value in f.items() for j,kind in enumerate(['H','g'])})
 def value(i,v,kind):
  H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if kind=='loss' else forms[i][kind]
  b=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return b+2*g@d+d@H@d
 # During restoration only, do not worsen either current violation. Final
 # acceptance still uses the unchanged original guards, not these ceilings.
 ceilings=[{k:max(a[k]['rmse'],b[k]['rmse'])**2 for k in ['glass','shadow']} for a,b in zip(met,base)]
 def constraints(v):return np.array([q for i,b in enumerate(base) for q in [v[-1]-value(i,v,'loss')/b['loss'],*[1-value(i,v,k)/ceilings[i][k] for k in ['glass','shadow']]]])
 def bound(k):return (.05,1.5) if k<3 or k>=20 else(-.8,.8) if k<6 else(-4,4)
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(co)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(23),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best,bm,bi=co.copy(),met,ims;trials=[]
 for alpha in [1,.5,.25,.125,.0625]:
  v=co+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs)
  restoration=all(a[k]['rmse']**2<=ceilings[i][k]+1e-6 for i,a in enumerate(m) for k in ['glass','shadow'])
  trial=dict(iteration=iteration+1,alpha=alpha,material=v.tolist(),restoration_permitted=restoration,original_guards=guards(m),scores=m);trials.append(trial)
  with (out/'material-trials.ndjson').open('a') as f:f.write(json.dumps(trial)+'\n')
  if restoration and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);co,met,ims=best,bm,bi
 history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)]
 record=dict(parameters=p,material=co.tolist(),scores=met,baseline=base,initial=initial,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios) and guards(met),accepted=False,history=history,method=__doc__)
 (out/'material-progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,'gain',gain,'original guards',guards(met),flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(2.,trust*1.4)
 if trust<.1 or record['numeric_pass']:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,'numeric_pass',record['numeric_pass'],flush=True)
