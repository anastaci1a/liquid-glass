"""Effective phase centered on the selected control value; no text rescaling.

F = identity - grad[V(d) + .5 W(d)(kx*(x-ax)^2+ky*(y-ay)^2)].
V'=-a and grad(d)=-normal. This is an integrable image-map hypothesis,
not a certified convex solid or an identified Apple implementation.
"""
from pathlib import Path
import sys,json,copy,time,hashlib
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize,lsq_linear
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'anchored-potential-probe';out.mkdir(exist_ok=True)
class Anchored(Study):
 def __init__(self,path):
  super().__init__(path);track=self.case['background_estimate']['track_pose'];camera=track[2]/823.5
  positions=[((r['selected']['pose'][0]-957.5)*camera+track[0],(r['selected']['pose'][1]-547.5)*camera+track[1]) for r in self.case['background_estimate']['font_calibration']]
  anchor=min(positions,key=lambda q:abs(q[0]-self.case['center'][0]));self.anchor=(np.array(anchor)-self.case['center'])/self.L
 def geometry_field(self,x,y,p):
  q={**p,'core_x':0.,'core_y':0.,'tangent':0.,'coupling':0.,'cap_normal_gain':0.,'cap_join_width':0.}
  X,Y,d,light=super().geometry_field(x,y,q);*_,(sd,nx,ny)=self.shape(x,y,q)
  rx=x-self.anchor[0];ry=y-self.anchor[1];u=np.clip(d/p['anchor_band'],0,1)
  W=u**3*(u*(6*u-15)+10);Wd=30*u*u*(u-1)**2/p['anchor_band'];P=.5*(p['anchor_x']*rx*rx+p['anchor_y']*ry*ry)
  return X-p['anchor_x']*W*rx+Wd*P*nx,Y-p['anchor_y']*W*ry+Wd*P*ny,d,light
state=json.loads((folder/'accepted.json').read_text());paths=[folder,root/'segmented-matched-state-preparation/second-observation',folder/'second-observation'];studies=[Anchored(p) for p in paths];baseline=[Study(p).scores(Study(p).render(state['parameters'],np.array(state['material']))) for p in paths];rows=[]
for seed_name in ['retained','archived']:
 p=copy.deepcopy(state['parameters'] if seed_name=='retained' else json.loads((root/'segmented-biased-track-preparation/accepted.json').read_text())['parameters']);p.update(sigma=.5,post_sigma=0.,gamma=1.,core_x=0.,core_y=0.,tangent=0.,coupling=0.,cap_normal_gain=0.,cap_join_width=0.,anchor_x=.1,anchor_y=.1,anchor_band=.9)
 if not p['spline']:
  d=np.linspace(0,1,501);basis=BSpline.design_matrix(d,KNOTS,3).toarray()[:,:7];a=p['amplitude']*np.maximum(1-d/p['band'],0)**p['power'];c=lsq_linear(basis,a,bounds=(-2.5,2.5)).x;p.update({f'c{i}':float(c[i]) for i in range(7)});p['spline']=True
 stages=[('Selected-axis phase',[*[f'c{i}' for i in range(7)],'anchor_x','anchor_y','anchor_band'],2600),('Clear-source phase refinement',['sigma','gamma','rim_width','thin_width'],1600),('Joint phase refinement',[*[f'c{i}' for i in range(7)],'anchor_x','anchor_y','anchor_band','sigma','gamma'],4000)]
 for stage,(name,keys,budget) in enumerate(stages,1):
  best=[float('inf'),None,None];calls=0;t=time.time();s=studies[0]
  def evaluate(v):
   global calls
   calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,co=s.fit(q)
   if loss<best[0]:best[:]=[float(loss),q,co]
   return float(loss)
  custom={'anchor_x':(-.15,.3),'anchor_y':(-.15,.3),'anchor_band':(.25,.95),'sigma':(0,4.)};bounds=[custom[k] if k in custom else s.parameter_bounds(k) for k in keys]
  fit=minimize(evaluate,[np.clip(p[k],a,b) for k,(a,b) in zip(keys,bounds)],method='Powell',bounds=bounds,options=dict(maxfev=budget,xtol=.001,ftol=1e-8));p=best[1];co=best[2]
  scores=[s.scores(s.render(p,co)) for s in studies];sources=[coverage_report(s,p) for s in studies];supported_all=[supported(s,q) for s,q in zip(studies,sources)]
  row=dict(seed=seed_name,stage=stage,experiment=name,parameters=p,material=co.tolist(),training_loss=best[0],scores=scores,source_support=sources,supported=supported_all,evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{seed_name}-{stage}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(seed=seed_name,stage=stage,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],supported=supported_all,sigma=p['sigma'],calls=calls)),flush=True)
 for j,s in enumerate(studies):s.comparison(s.render(p,co),out/f'{seed_name}-{j}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(baseline=state,baseline_scores=baseline,rows=rows,anchors=[s.anchor.tolist() for s in studies],source='Original frozen incident RGB, with no glyph-size or background changes.',limits='Anchor is inferred from the nearest control label. Integrable thin-phase mapping, not proof of Apple optics or physical convexity. Third reference changes interaction shape; no accepted-state mutation.'),indent=2)+'\n')
