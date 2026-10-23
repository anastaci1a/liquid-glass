"""Worst-reference material fit with frozen per-reference glass guards."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize
from switch_deformation_model import DeformationStudy as Study
from paired_fit import Cached,scores
from material_local import statistics
root=Path('/evidence/extended/active-switch');out=root/'deformation-review';old=json.loads((root/'rim-width-review/minimax.json').read_text());S=[Study(root/'paired'/n) for n in ['a','b']]
p=json.loads((out/'review.json').read_text())['trials'][-1]['parameters'];C=[Cached(s,p) for s in S];point=np.asarray(old['material']);metrics=scores(C,point);base=old['scores'];history=[]
def merit(sc):return max(a['loss']/b['loss'] for a,b in zip(sc,base))
def bounds(k):return (.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4)
for iteration in range(7):
 forms=[statistics(c,point) for c in C]
 def value(i,v,kind):
  d=v[:23]-point;gH,gg=forms[i]['glass'];rH,rg=forms[i]['rim'];H,g=(.7*gH+.3*rH,.7*gg+.3*rg) if kind=='loss' else (gH,gg)
  initial=metrics[i]['loss'] if kind=='loss' else metrics[i]['glass']['rmse']**2
  return initial+2*g@d+d@H@d
 def constraints(v):return np.array([x for i in range(2) for x in [v[-1]-value(i,v,'loss')/base[i]['loss'],1-value(i,v,'glass')/base[i]['glass']['rmse']**2]])
 ranges=[(max(bounds(k)[0],point[k]-.15),min(bounds(k)[1],point[k]+.15)) for k in range(23)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[point,merit(metrics)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=160,ftol=1e-10))
 best=point.copy();best_sc=metrics
 for t in [1,.5,.25,.125,.0625]:
  q=point+t*(fit.x[:23]-point);sc=scores(C,q)
  if merit(sc)<merit(best_sc):best,best_sc=q,sc
 gain=merit(metrics)-merit(best_sc);point,metrics=best,best_sc
 row=dict(iteration=iteration+1,losses=[m['loss'] for m in metrics],maximum_relative_squared_error=merit(metrics),solver_success=bool(fit.success));history.append(row);print(json.dumps(row),flush=True)
 if gain<1e-7:break
native=[s.scores(s.render(p,point)) for s in S];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(native,base)];ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,native,base))
report=dict(parameters=p,material=point.tolist(),scores=native,ratios=ratios,numeric_pass=ok,accepted=False,history=history,method='Shared23-term material with minimax normalized error and separate whole-glass constraints; deformation-aware displacement using fixed-volume height/radius approximation, no per-reference coefficients or altered inputs')
(out/'minimax.json').write_text(json.dumps(report,indent=2)+'\n');print('FINAL',ratios,ok,flush=True)
