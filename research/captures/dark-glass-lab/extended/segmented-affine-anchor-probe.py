"""Read-only shared label-anchored magnification plus a refracting capsule rim."""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'affine-anchor-probe';out.mkdir(exist_ok=True)
class Anchored(Study):
 def __init__(self,path):
  super().__init__(path);track=self.case['background_estimate']['track_pose'];camera=track[2]/823.5;poses=self.case['background_estimate']['font_calibration'];pose=min(poses,key=lambda r:abs((r['selected']['pose'][0]-957.5)*camera+track[0]-self.case['center'][0]))['selected']['pose'];self.anchor=((pose[0]-957.5)*camera+track[0]-self.case['center'][0],(pose[1]-547.5)*camera+track[1]-self.case['center'][1]);self.anchor=np.array(self.anchor)/self.L
 def geometry_field(self,x,y,p):
  q={**p,'core_x':0.,'core_y':0.};X,Y,d,J=super().geometry_field(x,y,q);X+=(x-self.anchor[0])*(1/p['magnify_x']-1);Y+=(y-self.anchor[1])*(1/p['magnify_y']-1);return X,Y,d,J
state=json.loads((folder/'accepted.json').read_text());studies=[Anchored(folder),Anchored(root/'segmented-matched-state-preparation/second-observation'),Anchored(folder/'changed-shape-stress-reference')];s=studies[0];rows=[]
for name in ['retained','outer-band','archived']:
 p=copy.deepcopy(state['parameters'] if name!='archived' else json.loads((root/'segmented-biased-track-preparation/accepted.json').read_text())['parameters']);p.update(cap_normal_gain=p.get('cap_normal_gain',0.),cap_join_width=p.get('cap_join_width',0.),sigma=.5,post_sigma=0.,magnify_x=1.125,magnify_y=1.125,gamma=1.,core_x=0.,core_y=0.,shape_dx=0.,shape_dy=0.,half_x_delta=0.,half_y_delta=0.,radius_delta=0.)
 if name=='outer-band':p.update(c0=.55,c1=.59,c2=.54,c3=.42,c4=.3,c5=0.,c6=0.,tangent=0.,coupling=0.,cap_join_width=0.)
 stages=[('Anchored magnification and rim profile',[*[f'c{i}' for i in range(7)],'magnify_x','magnify_y'],3000),('Tangential and cap response',['tangent','tangent_band','coupling','cap_normal_gain','cap_join_width','sigma'],2000),('Joint profile and magnification',[*[f'c{i}' for i in range(7)],'magnify_x','magnify_y','sigma'],3500)]
 for stage,(label,keys,budget) in enumerate(stages,1):
  best=[float('inf'),None,None];calls=0;t=time.time()
  def evaluate(v):
   global calls
   calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,co=s.fit(q)
   if loss<best[0]:best[:]=[loss,q,co]
   return float(loss)
  bounds=[(1.,1.3) if k.startswith('magnify') else (0.,2.) if k=='sigma' else s.parameter_bounds(k) for k in keys]
  # Include the actual seed so bounded Powell cannot silently lose a good start.
  evaluate([p[k] for k in keys]);fit=minimize(evaluate,[np.clip(p[k],a,b) for k,(a,b) in zip(keys,bounds)],method='Powell',bounds=bounds,options=dict(maxfev=budget,xtol=.0002,ftol=1e-8));p=best[1];co=best[2];scores=[q.scores(q.render(p,co)) for q in studies];row=dict(seed=name,stage=stage,experiment=label,parameters=p,material=co.tolist(),scores=scores,training_loss=best[0],evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{name}-{stage}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(seed=name,stage=stage,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],magnify=[p['magnify_x'],p['magnify_y']],sigma=p['sigma'],calls=calls)),flush=True)
 for j,q in enumerate(studies):q.comparison(q.render(p,co),out/f'{name}-{j}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(baseline=state,rows=rows,limits='Empirical nearest-label anchored magnification hypothesis. No source/reference/accepted file mutation. Magnification is a disclosed content/optical ambiguity; no claim that Apple uses this stage.'),indent=2)+'\n')
