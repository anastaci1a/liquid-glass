"""Sharp-only geometry investigation. No source or accepted-state mutation."""
from pathlib import Path
import sys,json,copy,time,hashlib
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'clear-local-probe';out.mkdir(exist_ok=True);state=json.loads((folder/'accepted.json').read_text());A=Study(folder);B=Study(folder/'second-observation');rows=[]
# Match the native loss's area-normalized glass/rim weighting in the training
# surrogate. The fixed native score/masks themselves are never changed.
idx=A.indices;isrim=A.rim.ravel()[idx];A.weights=np.sqrt(.7+.3*(A.valid.sum()/A.rim.sum())*isrim)
for seed in ['retained-sharp','measured-outline','archived-sharp']:
 p=copy.deepcopy(state['parameters'] if seed!='archived-sharp' else json.loads((root/'segmented-biased-track-preparation/accepted.json').read_text())['parameters'])
 for key in state['parameters']:p.setdefault(key,state['parameters'][key])
 p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.)
 if seed!='retained-sharp':p.update(shape_dx=0.,shape_dy=0.,half_x_delta=0.,half_y_delta=0.,radius_delta=0.,cap_join_width=0.)
 _,co=A.fit(p);native=A.scores(A.render(p,co));base_native=copy.deepcopy(native)
 for stage in range(1,9):
  keys=([*[f'c{i}' for i in range(7)],'core_x','core_y'] if stage%2 else ['tangent','tangent_band','coupling','cap_normal_gain','cap_tangent_fade','cap_join_width','rim_width','thin_width'])
  steps={k:.08 for k in keys};steps.update(core_x=.045,core_y=.045,tangent=.06,tangent_band=.15,coupling=.2,cap_normal_gain=.3,cap_tangent_fade=.2,cap_join_width=.07,rim_width=.05,thin_width=.01)
  bounds=[(max(A.parameter_bounds(k)[0],p[k]-steps[k]),min(A.parameter_bounds(k)[1],p[k]+steps[k])) for k in keys];t=time.time();calls=0;best=[A.fit(p)[0],p,co];proposals=[tuple(best)]
  def evaluate(v):
   global calls
   calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,c=A.fit(q)
   if loss<best[0]:best[:]=[loss,q,c]
   if calls%200==0:proposals.append((loss,q,c))
   return float(loss)
  minimize(evaluate,[p[k] for k in keys],method='Powell',bounds=bounds,options=dict(maxfev=2400,xtol=.0001,ftol=1e-9));proposals.append(tuple(best));finalists=[]
  for _,q,c in sorted(proposals,key=lambda r:r[0])[:5]:
   sc=A.scores(A.render(q,c));valid=supported(A,coverage_report(A,q));finalists.append((sc,q,c,valid))
  viable=[t for t in finalists if t[3] and t[0]['loss']<=native['loss']+1e-8 and t[0]['glass']['rmse']<=native['glass']['rmse']+1e-8]
  if viable:native,p,co,_=min(viable,key=lambda r:r[0]['loss'])
  scoreB=B.scores(B.render(p,co));row=dict(seed=seed,stage=stage,parameters=p,material=co.tolist(),scores=[native,scoreB],clear_seed_score=base_native,retained_within_clear_family=bool(viable),beats_published_A=native['loss']<=state['scores']['loss'] and native['glass']['rmse']<=state['scores']['glass']['rmse'],evaluations=calls,seconds=time.time()-t,training_objective='Area-normalized0.7glass+0.3rim; unchanged frozen native masks and scores.',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());rows.append(row);(out/f'{seed}-{stage}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(seed=seed,stage=stage,loss=[native['loss'],scoreB['loss']],glass=[native['glass']['rmse'],scoreB['glass']['rmse']],beats_published=row['beats_published_A'],calls=calls)),flush=True)
  if stage in (1,4,8):A.comparison(A.render(p,co),out/f'{seed}-{stage}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(baseline=state,rows=rows,limits='Sigma and post_sigma fixedZERO. Clear-family improvements are not accepted improvements over the previous blurry fit unless BOTH frozen A gates pass. Original inputs and all accepted/public records unchanged. No proprietary-shader or selected-content claim.'),indent=2)+'\n')
