"""Zero-blur prism/tilt term, separated from central power and rim curvature.

A constant ray deflection is the gradient of a linear phase; it can translate
content without conflating that translation with magnification. This is an
optical hypothesis, not proof of Apple's surface/interaction model.
"""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'prismatic-clear-probe';out.mkdir(exist_ok=True)
class Prism(Study):
 def geometry_field(self,x,y,p):
  X,Y,d,J=super().geometry_field(x,y,p);return X+p['prism_x'],Y+p['prism_y'],d,J
A=Prism(folder);B=Prism(folder/'second-observation');idx=A.indices;A.weights=np.sqrt(.7+.3*(A.valid.sum()/A.rim.sum())*A.rim.ravel()[idx]);old=json.loads((folder/'accepted.json').read_text());rows=[]
for name,file in [('current',folder/'clear-local-probe/retained-sharp-8.json'),('measured',folder/'clear-local-probe/measured-outline-1.json')]:
 p=copy.deepcopy(json.loads(file.read_text())['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,prism_x=0.,prism_y=0.);_,co=A.fit(p);native=A.scores(A.render(p,co))
 for stage in range(1,7):
  keys=(['prism_x','prism_y','core_x','core_y'] if stage in [1,4] else [*[f'c{i}' for i in range(7)],'prism_x','prism_y','core_x','core_y'] if stage in [2,5] else ['tangent','tangent_band','coupling','cap_normal_gain','cap_tangent_fade','cap_join_width','rim_width','thin_width'])
  bounds=[]
  for k in keys:
   if k.startswith('prism'):bounds.append((max(-.6,p[k]-.2),min(.6,p[k]+.2)));continue
   a,b=A.parameter_bounds(k);step=.08 if k.startswith('c') else .1;bounds.append((max(a,p[k]-step),min(b,p[k]+step)))
  best=[A.fit(p)[0],p,co];calls=0;proposals=[tuple(best)];t=time.time()
  def evaluate(v):
   global calls
   calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,c=A.fit(q)
   if loss<best[0]:best[:]=[loss,q,c]
   if calls%200==0:proposals.append((loss,q,c))
   return float(loss)
  minimize(evaluate,[p[k] for k in keys],method='Powell',bounds=bounds,options=dict(maxfev=3500,xtol=.00005,ftol=1e-9));proposals.append(tuple(best));viable=[]
  for _,q,c in sorted(proposals,key=lambda r:r[0])[:5]:
   sc=A.scores(A.render(q,c));valid=supported(A,coverage_report(A,q))
   if valid and sc['loss']<=native['loss']+1e-8 and sc['glass']['rmse']<=native['glass']['rmse']+1e-8:viable.append((sc,q,c))
  if viable:native,p,co=min(viable,key=lambda r:r[0]['loss'])
  scoreB=B.scores(B.render(p,co));row=dict(seed=name,stage=stage,parameters=p,material=co.tolist(),scores=[native,scoreB],beats_published_A=native['loss']<=old['scores']['loss'] and native['glass']['rmse']<=old['scores']['glass']['rmse'],evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{name}-{stage}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(seed=name,stage=stage,loss=[native['loss'],scoreB['loss']],glass=[native['glass']['rmse'],scoreB['glass']['rmse']],prism=[p['prism_x'],p['prism_y']],beats_published=row['beats_published_A'],calls=calls)),flush=True)
  if stage in [1,3,6]:A.comparison(A.render(p,co),out/f'{name}-{stage}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(rows=rows,baseline=old,limits='Sharp prism/tilt hypothesis with unchanged frozen inputs. No accepted mutation. A constant phase gradient is integrable; this does not make the other empirical map physical or identify Apple internals. Native score gates still required.'),indent=2)+'\n')
