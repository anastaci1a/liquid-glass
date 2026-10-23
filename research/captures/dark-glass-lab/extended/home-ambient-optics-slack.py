from pathlib import Path
import json,time,numpy as np
from paired_fit import Cached,permitted
from extended_fit import Study
from material_local import statistics
from source_support import coverage_report,supported
root=Path('/evidence/extended/music-home-vector');out=root/'ambient-optics-slack';out.mkdir(exist_ok=True);r=json.loads((root/'ambient-optics-material-probe/report.json').read_text());seed=r['results'][0];targets=r['targets'];p=seed['parameters'];studies=[Study(root/'paired'/n) for n in ['a','b']];caches=[Cached(s,p) for s in studies];v=np.r_[seed['material'],seed['ambient_rim_response']];transforms=[]
for mu in seed['source_luma']:
 T=np.c_[np.eye(23),np.zeros((23,3))];T[[6,9,12],np.arange(23,26)]=mu-.5;transforms.append(T)
forms=statistics(caches[0],transforms[0]@v);Q,g=forms['glass'];R,h=forms['rim'];gradient=transforms[0].T@(.7*g+.3*h);gradient/=np.linalg.norm(gradient);trials=[];best=None
for step in [1e-6,2e-6,5e-6,1e-5,2e-5,5e-5,1e-4,2e-4,5e-4,.001,.002,.005]:
 q=v-step*gradient
 for k in range(26):q[k]=np.clip(q[k],*( (.05,1.5) if k<3 or 20<=k<23 else (-.8,.8) if k<6 else (-4,4)))
 scores=[s.scores(c.render(T@q)) for s,c,T in zip(studies,caches,transforms)];allowed=permitted(scores,targets);trials.append(dict(step=step,scores=scores,permitted=allowed))
 if allowed and (best is None or sum(x['loss'] for x in scores)<sum(x['loss'] for x in best['scores'])):best=dict(parameters=p,material=q[:23].tolist(),ambient_rim_response=q[23:].tolist(),source_luma=seed['source_luma'],scores=scores)
if best:
 best['source_support']=[coverage_report(s,p) for s in studies];assert all(supported(s,q) for s,q in zip(studies,best['source_support']))
 for name,s,T in zip(['a','b'],studies,transforms):s.comparison(s.render(p,T@np.r_[best['material'],best['ambient_rim_response']]),out/(name+'.png'),p)
(out/'report.json').write_text(json.dumps(dict(model=r['model'],targets=targets,seed=seed,trials=trials,best=best,limits='Private bridge candidate. Requires public implementation/parity/HQ/native replay before use. Historical invalid paired chain remains untouched.'),indent=2)+'\n');print(json.dumps(dict(best=best)),flush=True)
