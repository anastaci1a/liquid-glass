"""One existing signed thin-light attenuation family, both frozen observations."""
import os,json,copy,hashlib
from pathlib import Path
import cv2,numpy as np
from extended_fit import Study
os.umask(2);cv2.setNumThreads(1)
R=Path('/evidence/extended');D=R/'home-thin-rim-review';P=R/'home-short-round/boundary-epoch/pass-03';r=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/music-home-vector/boundary-round/pass-03.json').read_text());prior=json.loads((P/'accepted-verification.json').read_text())['candidate']['observations'];states=[]
for i,n in enumerate(['a','b']):
 s=Study(R/'home-short-round/input-boundary-replay-proposal'/n);assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==r['case_sha256'][n]
 for f,sha in r['vector_sha256'][n].items():assert hashlib.sha256((s.folder/f).read_bytes()).hexdigest()==sha
 s.case={**s.case,'foreground_response':r['foreground_response']};M=np.load(P/f'joint-candidate-{i}.npy');states.append((n,s,M))
# Freeze BEFORE proposals. Only neutral thin and its two directional terms,
# including source-conditioned isotropic thin offset, receive one common gain.
(D/'protocol-FIRST.json').write_text(json.dumps(dict(family='Existing thin lighting times eta; material[6:9] and ambient_rim_response[0] scaled together',eta=[.99,.995],baseline=prior,ray_source_shape_filter_foreground_shadow_unchanged=True,source_proof='Original 401451 per observation emitted queries unchanged; estimated boundary .44%/.30% persists; no new physical-source claim',accepted=False),indent=2)+'\n')
rows=[]
for eta in [.99,.995]:
 trial=[]
 for n,s,baseM in states:
  p=copy.deepcopy(r['parameters']);p['ambient_rim_response'][0]*=eta;co=np.array(r['material']);co[6:9]*=eta;M=s.render(p,co);score=s.scores(M,False);score['E']=float(np.sqrt(score['loss']));l,t,rr,b=s.case['foreground_layers'][0]['box'];x,y,_,_=s.crop;F=s.apply_foreground(M.copy());score['foreground']={'rmse':float(np.sqrt(float(np.mean((F[t-y:b-y,l-x:rr-x]-s.target[t:b,l:rr])**2))*255**2))};before=prior[n.upper()];checks={k:score[k]['rmse']<=before[k]['rmse'] for k in ['glass','rim','held','interior','foreground']};checks.update(E=score['E']<=before['E'],shadow_unchanged=True);np.save(D/f'eta-{eta}-{n}.npy',M);trial.append(dict(observation=n,scores=score,checks=checks));print(json.dumps(dict(eta=eta,observation=n,E=score['E'],checks=checks)),flush=True)
  (D/'partial.json').write_text(json.dumps(rows+[dict(eta=eta,observations=trial)],indent=2)+'\n')
 row=dict(eta=eta,observations=trial,qualifies=all(all(v['checks'].values()) for v in trial));rows.append(row)
 if row['qualifies']:break
(D/'result.json').write_text(json.dumps(dict(family='One common attenuation of existing signed thin-rim lighting',rows=rows,accepted=False,body_renders=2*len(rows)),indent=2)+'\n')
