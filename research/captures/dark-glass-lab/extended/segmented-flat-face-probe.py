"""Clear projected labels, flat inner face and smooth refracting outer band."""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.optimize import minimize
from segmented_layered_fixture import Layered
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'flat-face-probe';out.mkdir(exist_ok=True);state=json.loads((folder/'accepted.json').read_text());rows=[]
for style in [1.,1.0625,1.125,1.1875]:
 studies=[Layered(folder,style),Layered(root/'segmented-matched-state-preparation/second-observation',style),Layered(folder/'second-observation',style)];s=studies[0]
 for seed_name in ['retained','broad-rim']:
  p=copy.deepcopy(state['parameters']);p.update(sigma=2.,post_sigma=0.,gamma=1.,core_x=0.,core_y=0.,tangent=0.,coupling=0.,cap_normal_gain=0.,cap_join_width=0.,c5=0.,c6=0.,spline=True)
  if seed_name=='broad-rim':p.update(c0=.9,c1=1.2,c2=.9,c3=.5,c4=.1)
  best=[float('inf'),None,None];calls=0;t=time.time();keys=[f'c{i}' for i in range(5)]
  def evaluate(v):
   global calls
   calls+=1;q=copy.deepcopy(p);q.update(zip(keys,map(float,v)));loss,co=s.fit(q)
   if loss<best[0]:best[:]=[float(loss),q,co]
   return float(loss)
  fit=minimize(evaluate,[p[k] for k in keys],method='Powell',bounds=[(0,2.5)]*5,options=dict(maxfev=2600,xtol=.0005,ftol=1e-9));p=best[1];co=best[2];scores=[a.scores(a.render(p,co)) for a in studies];row=dict(style=style,seed=seed_name,parameters=p,material=co.tolist(),scores=scores,training_loss=best[0],evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{style}-{seed_name}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(style=style,seed=seed_name,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],calls=calls)),flush=True)
  for j,a in enumerate(studies):a.comparison(a.render(p,co),out/f'{style}-{seed_name}-{j}.png',p,context_completed=True)
 del studies,s
(out/'report.json').write_text(json.dumps(dict(baseline=state,rows=rows,limits='Compositing/flat-face hypothesis; projected content remains clear while material scattering affects only the background. Fixed native masks and files. No accepted-state mutation or proprietary-shader identification.'),indent=2)+'\n')
