"""Compact potential core correction with shared native material fitting.
Psi=.5*(kx*x^2+ky*y^2)*S(d/(.30r)); deltaF=-gradPsi with actual crowned grad(d).
This adds uniform central scaling with a smooth boundary transition, leaving
edge rays unchanged. It does not claim integrability of the inherited map.
A shared coefficient pair and shared material, no source/shape/blur/shadow edits.
Bounds from a declared analytic .12r displacement maximum; invariants checked.
Original whole-glass/exterior guards constrain proposals. Crop/rim terms remain measured and advisory; this tests overconstraint, with no mask/epoch change.
One family including any fitting steps, not one pass per iteration.
"""
import sys,json,copy,time,gc
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize
sys.path.insert(0,'/evidence/extended')
from switch_core_potential import CorePotentialStudy as Study
from paired_fit import Cached
from joint_visible_statistics import statistics as joint_statistics, measures
root=Path('/evidence/extended/active-switch');out=root/'rev5-original-gate-review'/'core-potential';out.mkdir(parents=True,exist_ok=True);bound=json.loads((root/'rev5-core-potential/invariants.json').read_text())['coefficient_bound']
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());verification=json.loads((root/'rev4-ambient-review/hq/verification.json').read_text());old['scores']=[verification['candidate']['observations'][n] for n in ['A','B']]
S=[Study(root/'paired'/n) for n in ['a','b']]
keys=['potential_x','potential_y']
old['parameters'].update(potential_x=0.,potential_y=0.)
scales=np.array([.002,.002]+[.08]*23)
resume=old;assert json.loads((root/'joint-jacobian-check/verification.json').read_text())['passed']
start=np.r_[[resume['parameters'][k] for k in keys],resume['material']];point=start.copy();history=[]
N=len(keys)
def unpack(v):
 p=copy.deepcopy(old['parameters']);p.update(zip(keys,map(float,v[:N])));p['core_potential']=[p[k] for k in keys];return p,v[N:]
def images(v):
 p,c=unpack(v);return [s.render(p,c) for s in S]
def metrics(ims,p):return [{**s.scores(im,include_ssim=False),**measures(s,p,im)} for s,im in zip(S,ims)]
def guard_factor(kind):return 1.02 if kind.startswith('crop_') else 1.
extra_keys=['shadow']
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,old['scores']))
def bounds(i):
 if i<N:return (-bound,bound)
 k=i-N;return (.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4)
ims=images(point);met=metrics(ims,unpack(point)[0]);baseline_error=[abs(a['loss']-b['loss']) for a,b in zip(met,old['scores'])];assert max(baseline_error)<1e-6,baseline_error;old['scores']=copy.deepcopy(met)
# Keep crop diagnostics advisory, as in the approved contract.
trust=1.5
for iteration in range(6):
 t0=time.time();p,c=unpack(point);forms=[]
 for index,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);assert np.max(abs(cache.render(c)-im))<2e-6
  derivatives=[]
  for k in range(N):
   eps=.00015;pa=copy.deepcopy(p);pb=copy.deepcopy(p);pa['core_potential'][k]+=eps;pb['core_potential'][k]-=eps
   derivatives.append((s.render(pa,c)-s.render(pb,c))/(2*eps))
  forms.append(joint_statistics(cache,c,derivatives,scales,im));del cache,derivatives;gc.collect();print('ANALYTIC_JAC',iteration+1,index+1,round(time.time()-t0,2),flush=True)
 def value(i,v,kind):
  Hg,gg=forms[i]['glass'];Hr,gr=forms[i]['rim'];H,g=(.7*Hg+.3*Hr,.7*gg+.3*gr) if kind=='loss' else forms[i][kind]
  base=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2
  d=v[:-1];return base+2*g@d+d@H@d
 def constraints(v):return np.array([z for i,b in enumerate(old['scores']) for z in [v[-1]-value(i,v,'loss')/b['loss'],*[guard_factor(kind)**2-value(i,v,kind)/b[kind]['rmse']**2 for kind in ['glass',*extra_keys]]]])
 ranges=[(max(-trust,(bounds(i)[0]-v)/scales[i]),min(trust,(bounds(i)[1]-v)/scales[i])) for i,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(len(point)),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best=point.copy();bestims=ims;bestmet=met;trials=[]
 for alpha in [1,.5,.25,.125]:
  v=point+alpha*scales*fit.x[:-1];candidate=images(v);m=metrics(candidate,unpack(v)[0])
  allowed=all(a[kind]['rmse']<=guard_factor(kind)*b[kind]['rmse']+1e-7 for a,b in zip(m,old['scores']) for kind in ['glass',*extra_keys])
  trials.append(dict(alpha=alpha,merit=merit(m),allowed=allowed,scores=m))
  if allowed and merit(m)<merit(bestmet):best,bestims,bestmet=v,candidate,m
 gain=merit(met)-merit(bestmet);point,ims,met=best,bestims,bestmet
 row=dict(iteration=iteration+1,seconds=time.time()-t0,trust=trust,solver_success=bool(fit.success),solver_message=str(fit.message),scores=met,gain=gain,trials=trials);history.append(row)
 p,c=unpack(point);ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(met,old['scores'])]
 record=dict(parameters=p,material=c.tolist(),scores=met,ratios=ratios,numeric_pass=bool(max(ratios)<=.995),accepted=False,baseline_scores=old['scores'],baseline_native_loss_error=baseline_error,history=history,keys=keys,scales=scales.tolist(),method=__doc__)
 (out/'settlement.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
print('FINAL',ratios,flush=True)
