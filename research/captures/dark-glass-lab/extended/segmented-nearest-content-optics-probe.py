"""Compare full clear optical restarts with/without a shared content scale."""
from pathlib import Path
import sys,json,copy,time,hashlib
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import minimize,lsq_linear
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from vector_foreground import coverage
from paired_fit import permitted
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'nearest-content-optics-probe';out.mkdir(exist_ok=True)
state=json.loads((folder/'accepted.json').read_text());studies=[Study(folder),Study(folder/'second-observation')];original=[s.source.copy() for s in studies]
baseline=[s.scores(s.render(state['parameters'],np.array(state['material']))) for s in studies]
def content(study,source,scale):
 result=source.copy();track=study.case['background_estimate']['track_pose'];camera=track[2]/823.5;ink=np.array([1.,.35,.4],np.float32);background=source[500,400].copy()
 selected=min(study.case['background_estimate']['font_calibration'],key=lambda r:abs((r['selected']['pose'][0]-957.5)*camera+track[0]-study.case['center'][0]))['text']
 for record in study.case['background_estimate']['font_calibration']:
  layer=copy.deepcopy(record['selected']['layer']);box=np.array(layer['vector_box'],float);box[[0,2]]=(box[[0,2]]-957.5)*camera+track[0];box[[1,3]]=(box[[1,3]]-547.5)*camera+track[1]
  center=np.array([(box[0]+box[2])/2,(box[1]+box[3])/2]*2);large=center+(box-center)*1.25
  layer['box']=[int(large[0]-3),int(large[1]-3),int(large[2]+4),int(large[3]+4)];layer['vector_box']=box.tolist();A=coverage(folder,layer)
  layer['vector_box']=(center+(box-center)*(scale if record['text']==selected else 1.)).tolist();B=coverage(folder,layer);a,b,c,d=layer['box'];result[b:d,a:c]+=(B-A)[...,None]*(ink-background)
 return np.clip(result,0,1)
all_rows=[];code_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
for scale in [1.,1.125]:
 for s,source in zip(studies,original):s.source=content(s,source,scale);s.cache.clear()
 for seed_name in ['retained','archived-profile']:
  seed=state['parameters'] if seed_name=='retained' else json.loads((root/'segmented-biased-track-preparation/accepted.json').read_text())['parameters'];p=copy.deepcopy(seed);p.update(sigma=.5,post_sigma=0.,gamma=1.)
  if not p['spline']:
   d=np.linspace(0,1,501);basis=BSpline.design_matrix(d,KNOTS,3).toarray()[:,:7];a=p['amplitude']*np.maximum(1-d/p['band'],0)**p['power'];c=lsq_linear(basis,a,bounds=(-2.5,2.5)).x;p.update({f'c{i}':float(c[i]) for i in range(7)});p['spline']=True
  stages=[('Clear profile and center',[*[f'c{i}' for i in range(7)],'core_x','core_y'],2400),('Source clarity and tangential mapping',['sigma','gamma','tangent','tangent_band','coupling'],1800),('Joint clear optical settlement',[*[f'c{i}' for i in range(7)],'sigma','gamma','core_x','core_y','tangent','tangent_band','coupling'],4000)]
  for index,(name,keys,budget) in enumerate(stages,1):
   t=time.time();best=[float('inf'),None,None];calls=0
   def evaluate(v):
    global calls
    calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,co=studies[0].fit(q)
    if loss<best[0]:best[:]=[float(loss),q,co]
    return float(loss)
   bounds=[(0,4.) if k=='sigma' else studies[0].parameter_bounds(k) for k in keys];x=[np.clip(p[k],a,b) for k,(a,b) in zip(keys,bounds)]
   fit=minimize(evaluate,x,method='Powell',bounds=bounds,options=dict(maxfev=budget,xtol=.001,ftol=1e-8))
   p=best[1];co=best[2];scores=[s.scores(s.render(p,co)) for s in studies];row=dict(content_scale=scale,seed=seed_name,stage=index,experiment=name,evaluations=calls,seconds=time.time()-t,training_loss=best[0],parameters=p,material=co.tolist(),scores=scores,both_allowed=permitted(scores,baseline),execution_code_sha256=code_hash);all_rows.append(row)
   (out/f'scale-{scale}-{seed_name}-{index}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(scale=scale,seed=seed_name,stage=index,loss=[r['loss'] for r in scores],glass=[r['glass']['rmse'] for r in scores],sigma=p['sigma'],both_allowed=row['both_allowed'],calls=calls)),flush=True)
  for j,s in enumerate(studies):s.comparison(s.render(p,co),out/f'scale-{scale}-{seed_name}-{j}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(baseline=state,baseline_scores=baseline,rows=all_rows,limits='Read-only joint restarts; original source files and accepted records unchanged. Only the caption nearest the measured lens center receives the shared selected-content scale. This is an unidentified compositing hypothesis, not a proven Apple typography or refraction stage.'),indent=2)+'\n')
