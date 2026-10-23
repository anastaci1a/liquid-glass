"""One budgeted fit of actual height curvature to diagnostic map points."""
import datetime,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from footprint_curvature_back import FootprintCurvatureBack
from geometric_optics import trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'inference.json').exists()
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];a,b=scene['surface_half'];radius=scene['surface_radius'];knots=np.asarray(p['physical_parameters']['curvature_knots']);profile=json.loads((ROOT/'research/experiments/expanded-map-diagnostic-01/result.json').read_text())['profile'];r=np.linspace(0,.9997,129);target=np.interp(r,profile['rho'],np.asarray(profile['diagnostic_displacement_over_L'])[:,1]);y=(b-radius)+radius*r;cap=radius*(1/np.sqrt(1.5**2-1)-1e-4);weights=np.diff(knots);area=np.zeros(len(knots));area[:-1]+=weights/2;area[1:]+=weights/2
count=0;rays=0;best=None;ledger=[]
class BudgetStop(Exception):pass
def objective(v):
 global count,rays,best
 if count>=p['budgets']['cheap_model_evaluations'] or datetime.datetime.now(datetime.timezone.utc)>=deadline:raise BudgetStop()
 count+=1;k=np.r_[0.,v];feasible=np.isfinite(k).all() and (k>=0).all() and area@k<=cap
 if not feasible:ledger.append(dict(evaluation=count,feasible=False,curvature=k.tolist()));return 1e6+float(np.sum(np.maximum(-k,0)**2)+max(area@k-cap,0)**2)
 surface=FootprintCurvatureBack((a,b),radius,knots,k);q=trace_flat_front_orthographic(surface,np.zeros_like(r),y,1.5,2.1);rays+=len(r);assert rays<=p['budgets']['calibration_rays'] and q['complete'].all();loss=float(np.mean((q['Y']-y-target)**2));ledger.append(dict(evaluation=count,feasible=True,map_MSE=loss,curvature=k.tolist()))
 if best is None or loss<best['map_MSE']:best=dict(curvature=k.tolist(),map_MSE=loss,maximum_height=surface.maximum_height,slope_bound=surface.slope_bound,source_displacement=(q['Y']-y).tolist())
 return loss
initial=np.full(len(knots)-1,.6/(area[1:].sum()));success=False;message=''
try:
 result=minimize(objective,initial,method='SLSQP',bounds=[(0,100)]*len(initial),constraints=[dict(type='ineq',fun=lambda v:cap-area[1:]@v)],options=dict(maxiter=30,ftol=1e-10));success=bool(result.success);message=str(result.message)
except BudgetStop:message='Declared model-evaluation/deadline stop; retained best actually evaluated feasible geometry.'
assert best is not None
out=dict(status='GEOMETRIC_INITIALIZATION_ONLY_NO_IMAGE_ACCEPTANCE',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),model_evaluations=count,calibration_rays=rays,solver_success=success,solver_message=message,knots=knots.tolist(),best=best,normalized_r=r.tolist(),diagnostic_target_displacement=target.tolist(),ledger=ledger,RGB_queries=0,native_images=0,limits='Best feasible map projection only; diagnostic map is not optical truth or a convergence/performance bound.')
(OUT/'inference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','model_evaluations','calibration_rays','solver_success','solver_message','best']}))
