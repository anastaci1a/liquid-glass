"""Exploratory source-dependent reflection mixture; not a counted pass."""
from pathlib import Path
import copy,json,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
r=Path('/evidence/extended/music-navigation/paired');state=json.loads((r/'accepted.json').read_text());p=state['parameters'];co=np.asarray(state['material']);studies=[Study(r/n) for n in ['a','b']]
for s in studies:
 if 'foreground_styles' in state:s.case['foreground_styles']=state['foreground_styles']
base=[s.render(p,co) for s in studies];baseline=[s.scores(v) for s,v in zip(studies,base)];scale=max(1,np.mean([x['loss'] for x in baseline]));rows=[]
for width in [.006,.01,.015,.02,.03,.05,.08]:
 masks=[];forms=[]
 for s,G in zip(studies,base):
  opacity=np.empty(G.shape[:2],np.float32)
  for row,bottom,W,x,y in s.raster_tiles(1):
   *_,(sd,_,_)=s.shape(x,y,p);d=np.maximum(-sd,0);opacity[row:bottom]=np.exp(-(d/width)**2).reshape(bottom-row,2,W,2).mean((1,3))
  masks.append(opacity);scene={}
  for name,mask in [('glass',s.valid),('rim',s.rim)]:
   F=np.zeros((mask.sum(),3,4));F[:,:,0]=-opacity[mask,None]*G[mask]
   for c in range(3):F[:,c,c+1]=opacity[mask]
   X=F.reshape(-1,4);e=(G-s.target_crop)[mask].reshape(-1);factor=255**2/e.size;scene[name]=(X.T@X*factor,X.T@e*factor,float(np.mean(e**2))*255**2)
  forms.append(scene)
 def value(i,v,kind):
  def f(name):Q,g,b=forms[i][name];return b+2*g@v+v@Q@v
  return .7*f('glass')+.3*f('rim') if kind=='loss' else f('glass')
 def objective(v):return np.mean([value(i,v,'loss') for i in range(2)])/scale
 def constraints(v):return np.array([*list(v[0]-v[1:]),*[x for i,b in enumerate(baseline) for x in [(b['loss']-value(i,v,'loss'))/scale,(b['glass']['rmse']**2-value(i,v,'glass'))/scale]]])
 result=minimize(objective,np.zeros(4),method='SLSQP',bounds=[(0,1)]*4,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-12))
 v=result.x;pred=[(G*(1-W[...,None]*v[0])+W[...,None]*v[1:]).astype(np.float32) for G,W in zip(base,masks)];score=[s.scores(G) for s,G in zip(studies,pred)];row=dict(width=width,coefficients=v.tolist(),scores=score,solver_success=bool(result.success),constraint_min=float(min(constraints(v))))
 rows.append(row);print(width,v.tolist(),[x['loss'] for x in score],row['constraint_min'],flush=True)
 for i,s in enumerate(studies):s.comparison(pred[i],r/f'probe-reflection-{width}-{i}.png',p)
(r/'rim-reflection-probe.json').write_text(json.dumps(dict(scope='Uncounted model-feasibility probe; source-dependent convex reflection mixture after output filtering, not a painted additive outline.',baseline=baseline,state_parameters=p,rows=rows),indent=2)+'\n')
