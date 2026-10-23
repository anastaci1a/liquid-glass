"""One bounded recentered proposal from saved derivatives; no repeated probes."""
import os,sys,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/expanded-mini-short-round');sys.path.insert(0,str(ROOT));from preflight import Study,guards,emitted
from composition_helpers import composition,good
from preview_size import dimensions
import cv2
os.umask(0o002);stage=int(sys.argv[1]);assert stage in [2,3]
OLD=ROOT/f'pass-{stage-1:02}';OUT=ROOT/f'local-step-{stage:02}';OUT.mkdir(exist_ok=True)
assert not (OUT/'started.json').exists(),'Inspect saved attempts before recovery'
(OUT/'started.json').write_text(json.dumps(dict(stage=stage,budget='ONE recentered saved26parameter quadratic; max4newnativepairs, no repeated baseline/map/material probes',normalized_step_bound=.5,snapshot_derivatives='profile-material/forms.json',limits='Recentered old local model is proposal only; original actualnativegates determine acceptability.'),indent=2)+'\n')
base=json.loads((OLD/f'pass-{stage-1:02}.json').read_text());p=base['parameters'];co=np.array(base['material']);origin=json.loads((ROOT/'baseline-native-recipe.json').read_text());raw=json.loads((ROOT/'profile-material/forms.json').read_text());forms=[{k:[np.array(v['H']),np.array(v['g'])] for k,v in scene.items()} for scene in raw]
point=np.r_[[(p[f'c{k}']-origin['parameters'][f'c{k}'])/.002 for k in range(3)],(co-np.array(origin['material']))/.005]
for f in forms:
 for k,(H,g) in f.items():f[k]=[H,g+H@point]
ss=[Study(ROOT/n) for n in ['a','b']];keys=['loss','glass',*base['scores'][0]['foreground_mse']]
def norm(i,k):
 b=base['scores'][i];return max(1.,b['loss'] if k=='loss' else b['glass']['rmse']**2 if k=='glass' else b['foreground_mse'][k])
def value(i,k,v):
 H,g=forms[i][k];return (2*g@v+v@H@v)/norm(i,k)
def jac(i,k,v):
 H,g=forms[i][k];return 2*(g+H@v)/norm(i,k)
fun=lambda v:sum(value(i,'loss',v) for i in range(2))/2
fj=lambda v:sum(jac(i,'loss',v) for i in range(2))/2
cons=lambda v:np.array([-value(i,k,v) for i in range(2) for k in keys]);cj=lambda v:np.array([-jac(i,k,v) for i in range(2) for k in keys])
opt=minimize(fun,np.zeros(26),jac=fj,method='SLSQP',bounds=[(-.5,.5)]*26,constraints=[dict(type='ineq',fun=cons,jac=cj)],options=dict(maxiter=100,ftol=1e-12))
(OUT/'proposal.json').write_text(json.dumps(dict(direction=opt.x.tolist(),origin_position=point.tolist(),predicted=float(opt.fun),success=bool(opt.success),message=opt.message),indent=2)+'\n')
rows=[]
for j,t in enumerate([1.,.5,.25,.125] if opt.fun < -1e-12 else []):
 q={**p,**{f'c{k}':float(p[f'c{k}']+.002*t*opt.x[k]) for k in range(3)}};new=co+.005*t*opt.x[3:]
 imgs=[s.render(q,new) for s in ss];sc=[guards(s,q,a)[0] for s,a in zip(ss,imgs)]
 row=dict(factor=t,scores=sc,all_guards=good(sc,base['scores']));rows.append(row)
 for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
 (OUT/'trials.json').write_text(json.dumps(rows,indent=2)+'\n');print('STEP',stage,t,[v['E'] for v in sc],row['all_guards'],flush=True)
 if not row['all_guards'] or not any(v['E']<b['E'] for v,b in zip(sc,base['scores'])):continue
 proof=[emitted(s,q,i) for i,s in enumerate(ss)];assert all(v['passed'] for v in proof)
 record={**base,'parameters':q,'material':new.tolist(),'scores':sc,'source_proof':proof};(OUT/'candidate-native.json').write_text(json.dumps(record,indent=2)+'\n')
 for i,(s,a) in enumerate(zip(ss,imgs)):
  full=composition(s,q,a,True);cv2.imwrite(str(OUT/f'ref{i}-candidate.png'),np.rint(np.clip(full,0,1)*255).astype(np.uint8)[...,::-1]);np.save(OUT/f'ref{i}-complete.npy',composition(s,q,a))
 break
(OUT/'result.json').write_text(json.dumps(dict(trials=rows,accepted=False,count=0,limits='All original actual native gates; new changed-map finite source proof; primary replay and visual review required. No repeat derivative evaluations.'),indent=2)+'\n')
