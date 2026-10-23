"""Cheap deterministic optical proposal; full native renderer decides acceptance."""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize
from extended_fit import Study
from render import shade
from material_context import effective
from grazing_reflection import layers
root=Path('/evidence/extended/active-switch');out=root/'optical-profile-review';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text());S=[Study(root/'paired'/n) for n in ['a','b']];p0=old['parameters'];co=np.asarray(old['material']);probes=[]
for s in S:
 idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];h=np.sqrt(2)*s.kernel_sigma(p0,'post_sigma')/s.L
 dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);w,env=layers(s,p0)
 probes.append(dict(x=x[:,None]+dx.ravel(),y=y[:,None]+dy.ravel(),target=s.target_crop.reshape(-1,3)[idx],rim=s.rim.ravel()[idx],co=effective(s,p0,co),w=w.ravel()[idx,None],env=env.reshape(-1,3)[idx]))
keys=['core_x','core_y','c2','c3','c4','cap_normal_gain'];start=np.array([p0[k] for k in keys]);delta=np.array([.04,.04,.08,.08,.08,.10]);count=0
def proposal_scores(v):
 p=copy.deepcopy(p0);p.update(zip(keys,map(float,v)));loss=[]
 for s,q in zip(S,probes):
  C,J=s.field(q['x'],q['y'],p);rgb=shade(C,J,q['co']).mean(1);rgb=rgb*(1-q['w'])+q['env']*q['w'];e=(rgb-q['target'])*255;loss.append(.7*np.mean(e**2)+.3*np.mean(e[q['rim']]**2))
 return np.array(loss)
baseline=proposal_scores(start)
def objective(v):
 global count
 count+=1;loss=proposal_scores(v);m=float(np.max(loss/baseline))
 if count%20==0:print('PROPOSAL',count,m,flush=True)
 return m
fit=minimize(objective,start,method='Powell',bounds=list(zip(start-delta,start+delta)),options=dict(maxfev=260,xtol=.0005,ftol=1e-6))
records=[];best=None
for alpha in [1,.5,.25]:
 p=copy.deepcopy(p0);p.update(zip(keys,map(float,start+alpha*(fit.x-start))));sc=[s.scores(s.render(p,co)) for s in S];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,old['scores'])];ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,sc,old['scores']));row=dict(alpha=alpha,parameters=p,material=co.tolist(),scores=sc,ratios=ratios,numeric_pass=ok);records.append(row)
 if ok and (best is None or max(ratios)<max(best['ratios'])):best=row
 print('NATIVE',alpha,ratios,ok,flush=True)
(out/'review.json').write_text(json.dumps(dict(keys=keys,bounds=list(zip((start-delta).tolist(),(start+delta).tolist())),proposal_evaluations=count,proposal_baseline=baseline.tolist(),proposal_solution=fit.x.tolist(),native_trials=records,candidate=best,accepted=False,limits='Deterministic subsampled Gaussian quadrature is a proposal only; frozen full native RGB/rim and glass guards decide. Coefficients remain one shared empirical map, not recovered Apple geometry.'),indent=2)+'\n')
