"""One runtime-budgeted projection of a real positive spline height."""
from pathlib import Path
import datetime,json
import numpy as np
from scipy.optimize import minimize,LinearConstraint
from spline_height_back import SplineFootprintBack
from geometric_optics import trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'inference.json').exists();bud=p['budgets'];scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];a,b=scene['surface_half'];radius=scene['surface_radius'];breaks=np.array(p['parameters']['breaks']);t=np.r_[np.zeros(3),breaks,np.ones(3)];nc=len(t)-4;nv=nc-2;B=np.zeros((nc,nv));B[0,0]=B[1,0]=1
for i in range(2,nc-1):B[i,i-1]=1
D=np.diff(B,axis=0)*3/(t[4:4+nc-1]-t[1:1+nc-1])[:,None];cap=.88*radius
profile=json.loads((ROOT/'research/experiments/expanded-map-diagnostic-01/result.json').read_text())['profile'];r=np.linspace(0,.9997,129);target=np.interp(r,profile['rho'],np.asarray(profile['diagnostic_displacement_over_L'])[:,1]);y=b-radius+radius*r;greville=np.array([np.mean(t[i+1:i+4]) for i in range(nc)]);seed=.2*(1-greville*greville);seed[1]=seed[0];v0=seed[np.r_[0,np.arange(2,nc-1)]];model_count=0;ray_count=0;height_calls=0;ledger=[];best=None
class BudgetStop(Exception):pass
class CountedSurface(SplineFootprintBack):
 def height_gradient(self,x,y):
  global height_calls
  n=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size
  if height_calls+n>bud['total_height_adapter_calls']:raise BudgetStop('Height adapter cap, including nested boundary calls')
  height_calls+=n
  return super().height_gradient(x,y)
def objective(v):
 global model_count,ray_count,best
 if model_count>=bud['model_evaluations'] or datetime.datetime.now(datetime.timezone.utc)>=deadline:raise BudgetStop('Model/deadline cap')
 model_count+=1;c=B@v;finite=np.isfinite(c).all();bound=bool(finite and (c[:-1]>=.000001).all() and c.max()<=.25 and np.max(abs(D@v))<=cap);entry=dict(evaluation=model_count,heights=c.tolist(),feasible=bound)
 if not bound:
  entry['penalty']=1000.;ledger.append(entry);return 1000.
 s=CountedSurface((a,b),radius,breaks,c)
 if ray_count+len(r)>bud['calibration_rays']:raise BudgetStop('Calibration ray cap')
 ray_count+=len(r);q=trace_flat_front_orthographic(s,np.zeros_like(r),y,1.5,2.1);assert q['complete'].all();loss=float(np.mean((q['Y']-y-target)**2));entry['map_MSE']=loss;ledger.append(entry)
 if best is None or loss<best['map_MSE']:best=dict(heights=c.tolist(),map_MSE=loss,maximum_height=s.maximum_height,slope_bound=s.slope_bound,source_displacement=(q['Y']-y).tolist())
 return loss
success=False;message=''
try:
 result=minimize(objective,v0,method='SLSQP',bounds=[(.000001,.25)]*nv,constraints=[LinearConstraint(D,-cap,cap)],options=dict(maxiter=30,ftol=1e-10));success=bool(result.success);message=str(result.message)
except BudgetStop as e:message=str(e)
assert best is not None
result=dict(status='GEOMETRIC_PROJECTION_ONLY_NO_IMAGE',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),model_evaluations=model_count,calibration_rays=ray_count,height_adapter_calls=height_calls,solver_success=success,solver_message=message,best=best,breaks=breaks.tolist(),normalized_r=r.tolist(),diagnostic_target=target.tolist(),ledger=ledger,RGB_queries=0,native_images=0,fits=1,limits=['All proposed height vectors retained; infeasible proposals are not traced.','Global B-spline height and derivative bounds certify the actual surface, not image correspondence.','No RGB/image/source adoption or convergence claim.']);(OUT/'inference.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k] for k in ['status','model_evaluations','calibration_rays','height_adapter_calls','solver_success','solver_message','best']}),flush=True)
