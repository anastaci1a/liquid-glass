"""Photometric proposal for one shared integrable map; full renderer decides."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize
from extended_fit import Study
from switch_potential_model import PotentialStudy
from material_context import effective
from render import shade
from grazing_reflection import layers
root=Path('/evidence/extended/active-switch');out=root/'potential-review';old=json.loads((root/'rim-width-review/minimax.json').read_text())
trial=json.loads((out/'review.json').read_text())['trials'][0];p0=trial['parameters'];co=np.array(old['material']);S=[Study(root/'paired'/n) for n in ['a','b']];P=[PotentialStudy(s.folder) for s in S];probes=[]
for s in S:
    idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];h=np.sqrt(2)*s.kernel_sigma(p0,'post_sigma')/s.L;dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);w,env=layers(s,p0)
    probes.append(dict(x=x[:,None]+dx.ravel(),y=y[:,None]+dy.ravel(),target=s.target_crop.reshape(-1,3)[idx],rim=s.rim.ravel()[idx],co=effective(s,p0,co),w=w.ravel()[idx,None],env=env.reshape(-1,3)[idx]))
def measure(studies,p):
    loss=[]
    for s,q in zip(studies,probes):
        C,J=s.field(q['x'],q['y'],p);rgb=shade(C,J,q['co']).mean(1);rgb=rgb*(1-q['w'])+q['env']*q['w'];e=(rgb-q['target'])*255
        loss.append(.7*np.mean(e**2)+.3*np.mean(e[q['rim']]**2))
    return np.array(loss)
base=measure(S,old['parameters']);q=p0['potential_profile'];start=np.r_[q['coefficients'],q['core'],q['longitudinal_weight']];delta=np.r_[np.full(7,.15),.08,.08,.15];lower=start-delta;upper=start+delta;lower[-1]=max(-.95,lower[-1]);calls=0;best=(np.inf,start.copy())
def params(v):
    p=copy.deepcopy(p0);p['potential_profile']=dict(coefficients=v[:7].tolist(),core=v[7:9].tolist(),longitudinal_weight=float(v[-1]));return p
def objective(v):
    global calls,best
    calls+=1;value=float(np.max(measure(P,params(v))/base))
    if value<best[0]:best=(value,v.copy())
    if calls%20==0:print('PROPOSAL',calls,value,best[0],flush=True)
    return value
fit=minimize(objective,start,method='Powell',bounds=list(zip(lower,upper)),options=dict(maxfev=320,xtol=.0005,ftol=1e-6))
p=params(best[1]);native=[s.scores(s.render(p,co)) for s in P];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(native,old['scores'])]
report=dict(parameters=p,material=co.tolist(),scores=native,ratios=ratios,proposal_evaluations=calls,solver_success=bool(fit.success),solver_message=str(fit.message),best_proposal_loss=best[0],bounds=list(zip(lower.tolist(),upper.tolist())),numeric_pass=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,native,old['scores'])),accepted=False,limits='Approximate quadrature only proposes parameters; frozen full native comparisons decide. Integrable paraxial optical-path family, no thick-surface identification.')
(out/'fit.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE',ratios,report['numeric_pass'],flush=True)
