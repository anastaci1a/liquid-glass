from pathlib import Path
import json,cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from foreground_response import response,fit_response
root=Path('/evidence/extended/music-home-vector');out=root/'bridge-foreground';out.mkdir(exist_ok=True);bridge=json.loads((root/'ambient-optics-slack/report.json').read_text())['best'];old=json.loads((root/'paired/accepted.json').read_text());samples=[]
for n,mu in zip(['a','b'],bridge['source_luma']):
 s=Study(root/'paired'/n);co=np.array(bridge['material']);co[[6,9,12]]+=(mu-.5)*np.array(bridge['ambient_rim_response']);prediction=s.render(bridge['parameters'],co);x0,y0,_,_=s.crop
 for l in s.transmission_layers:
  a,b,c,d=l['box'];B=prediction[b-y0:d-y0,a-x0:c-x0];inside=cv2.erode(l['seed'].astype(np.uint8),np.ones((3,3),np.uint8))>0;samples.append((B[inside],l['target'][inside]))
limits=np.array(old['foreground_scores']['after_mse']);scale=limits.mean()
def errors(v):return np.array([float(np.mean((response(A,v)-T)**2))*255**2 for A,T in samples])
initial=fit_response(np.concatenate([a for a,b in samples]),np.concatenate([b for a,b in samples]));best=None;trials=[]
for seed in [initial,np.array(old['foreground_response'])]:
 fit=minimize(lambda v:np.mean(errors(v))/scale,seed.ravel(),method='SLSQP',bounds=[b for _ in range(3) for b in [(0,1),(0,1),(.1,16)]],constraints=[dict(type='ineq',fun=lambda v:(limits-errors(v))/scale)],options=dict(maxiter=200,ftol=1e-12,eps=2e-5));m=errors(fit.x);allowed=bool(np.all(m<=limits+1e-8));trials.append(dict(solver_success=bool(fit.success),after_mse=m.tolist(),permitted=allowed,parameters=fit.x.reshape(3,3).tolist()))
 if allowed and (best is None or m.sum()<sum(best['after_mse'])):best=trials[-1]
r=dict(baseline_on_new_glass=errors(old['foreground_response']).tolist(),protected_old_mse=limits.tolist(),trials=trials,best=best,limits='Private shared-response test only; no independent per-background color. Public bridge implementation and full replay still required.');(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
