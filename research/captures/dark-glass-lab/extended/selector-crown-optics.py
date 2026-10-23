"""Three bounded sharp optical trials; new crown, frozen inputs, no acceptance mutation."""
import sys,json,copy,time,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from source_support import coverage_report,supported
from progress_gate import evaluate
from crop_diagnostics import diagnostics
from PIL import Image

folder=Path('/evidence/extended/active-segmented-selector');out=folder/'crown-review';out.mkdir(exist_ok=True)
A=Study(folder);B=Study(folder/'second-observation');studies=[A,B]
old=json.loads((folder/'accepted.json').read_text())
baseline=[s.scores(s.render(old['parameters'],np.array(old['material']))) for s in studies]
epoch=hashlib.sha256(json.dumps([s.case for s in studies],sort_keys=True).encode()).hexdigest()
reference={'epoch':epoch,'observations':dict(zip(['A','B'],baseline))}
(out/'frozen-incumbent.json').write_text(json.dumps(reference,indent=2)+'\n')
# A sets the fit; B is a retained diagnostic/non-regression check, not a new blind set.
idx=A.indices;isrim=A.rim.ravel()[idx];A.weights=np.sqrt(.7+.3*(A.valid.sum()/A.rim.sum())*isrim)
p=copy.deepcopy(json.loads((folder/'clear-local-probe/archived-sharp-8.json').read_text())['parameters'])
p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.,crown_softness=.185,shape_dx=0.,shape_dy=0.,half_x_delta=0.,half_y_delta=0.,radius_delta=0.,cap_join_width=0.)
rows=[]
for stage,keys in enumerate([
 [*[f'c{i}' for i in range(7)],'core_x','core_y'],
 ['tangent','tangent_band','tangent_exponent','coupling','cap_normal_gain','cap_tangent_fade','rim_width','thin_width'],
 [*[f'c{i}' for i in range(7)],'core_x','core_y','tangent','tangent_band']],1):
 start=time.time();calls=0;best=[*A.fit(p),copy.deepcopy(p)]
 bounds=[A.parameter_bounds(k) for k in keys]
 def objective(v):
  global calls
  calls+=1;q={**p,**dict(zip(keys,map(float,v)))};loss,co=A.fit(q)
  if loss<best[0]:best[:]=[loss,co,q]
  return loss
 fit=minimize(objective,[p[k] for k in keys],method='Powell',bounds=bounds,options=dict(maxfev=1400,xtol=.00015,ftol=1e-8))
 _,co,p=best
 predictions=[s.render(p,co) for s in studies];scores=[s.scores(im) for s,im in zip(studies,predictions)]
 support=[coverage_report(s,p) for s in studies]
 report=evaluate(reference,{'epoch':epoch,'observations':dict(zip(['A','B'],scores))},visual_review=False,replay_verified=False,source_support_verified=all(supported(s,r) for s,r in zip(studies,support)))
 row=dict(experiment=stage,parameters=p.copy(),material=co.tolist(),scores=scores,support=support,numeric_gate=report,evaluations=calls,seconds=time.time()-start,accepted=False)
 (out/f'optics-{stage:02d}.json').write_text(json.dumps(row,indent=2)+'\n')
 for label,s,pred in zip(['A','B'],studies,predictions):
  # Reconstruct the entire crop from the clean exterior rather than borrowing
  # original shadow. The existing shadow model, when present, is generated.
  x0,y0,x1,y1=s.crop;cov=s.shape_coverage(p);base=s.exterior_source[y0:y1,x0:x1].copy()
  if 'shadow' in p:
   q=p['shadow'];*_,(sd,_,_)=s.shape(s.x-q['offset'][0],s.y-q['offset'][1],p)
   base*=1-q['opacity']*np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2)[...,None]
  image=pred*cov[...,None]+base*(1-cov[...,None]);Image.fromarray(np.uint8(np.rint(np.clip(image,0,1)*255))).save(out/f'optics-{stage:02d}-{label}.png')
  crops={'left-text-and-rim':[.05,.25,.38,.65],'central-text':[.23,.25,.55,.65],'right-text-and-rim':[.70,.25,.94,.65]}
  d=diagnostics(s.target_crop,pred,crops);(out/f'crop-{stage:02d}-{label}.json').write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
 rows.append(row);print(json.dumps(dict(stage=stage,loss=[s['loss'] for s in scores],glass=[s['glass']['rmse'] for s in scores],milestone=[r['passed'] for r in report['observations'].values()],evaluations=calls,seconds=time.time()-start)),flush=True)
(out/'optics-review.json').write_text(json.dumps(dict(trials=rows,review_due=True,qualifying_passes=0,limits='Crown geometry from silhouette. No ordinary blur; same source, material law and parameters on A/B. No independent replay or visual acceptance yet. Private sharp seed is not reset as acceptance baseline.'),indent=2)+'\n')
