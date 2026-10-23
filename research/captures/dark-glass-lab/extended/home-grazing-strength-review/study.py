"""Bounded existing white incident-field mixture, distinct from signed material."""
import os,json,copy,hashlib
from pathlib import Path
import cv2,numpy as np
from extended_fit import Study
from grazing_reflection import layers
os.umask(2);cv2.setNumThreads(1)
R=Path('/evidence/extended');D=R/'home-grazing-strength-review';P=R/'home-short-round/boundary-epoch/pass-03';r=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/music-home-vector/boundary-round/pass-03.json').read_text());base=json.loads((P/'accepted-verification.json').read_text())['candidate']['observations'];states=[]
for i,n in enumerate(['a','b']):
 s=Study(R/'home-short-round/input-boundary-replay-proposal'/n);assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==r['case_sha256'][n];s.case={**s.case,'foreground_response':r['foreground_response']};M=np.load(P/f'joint-candidate-{i}.npy');f,E=layers(s,r['parameters']);assert np.max(f)<=.5;body=(M.astype(float)-E*f[...,None])/(1-f[...,None]);states.append((n,s,M,f,E,body))
(D/'protocol-FIRST.json').write_text(json.dumps(dict(model='Existing grazing_reflection mixture (1-f)M+f*white; only declared strength .5->.55 or.525, width.00675/white environment unchanged',strengths=[.55,.525],baseline=base,other_parameters_frozen=True,source_query_set_unchanged=True,scalar_reflection_not_Apple_Fresnel=True),indent=2)+'\n')
def measure(s,M,b):
 score=s.scores(M,False);score['E']=float(np.sqrt(score['loss']));l,t,rr,bb=s.case['foreground_layers'][0]['box'];x,y,_,_=s.crop;F=s.apply_foreground(M.copy());score['foreground']={'rmse':float(np.sqrt(float(np.mean((F[t-y:bb-y,l-x:rr-x]-s.target[t:bb,l:rr])**2))*255**2))};checks={k:score[k]['rmse']<=b[k]['rmse'] for k in ['glass','rim','held','interior','foreground']};checks.update(E=score['E']<b['E'],shadow_unchanged=True);return score,checks
rows=[];actual=[]
for strength in [.55,.525]:
 pred=[]
 for n,s,M,f,E,body in states:
  ff=f*(strength/.5);v=(body*(1-ff[...,None])+E*ff[...,None]).astype(np.float32);score,checks=measure(s,v,base[n.upper()]);pred.append(dict(observation=n,scores=score,checks=checks));print(json.dumps(dict(stage='prediction',strength=strength,observation=n,E=score['E'],checks=checks)),flush=True)
 row=dict(strength=strength,predictions=pred,predicted_qualifier=all(all(a['checks'].values()) for a in pred));rows.append(row)
 if row['predicted_qualifier']:
  for n,s,M,f,E,body in states:
   p=copy.deepcopy(r['parameters']);p['grazing_reflection']['strength']=strength;v=s.render(p,np.array(r['material']));score,checks=measure(s,v,base[n.upper()]);np.save(D/(n+'-candidate.npy'),v);actual.append(dict(observation=n,scores=score,checks=checks));print(json.dumps(dict(stage='native',strength=strength,observation=n,E=score['E'],checks=checks)),flush=True)
  break
(D/'result.json').write_text(json.dumps(dict(rows=rows,native=actual,qualifies=bool(actual) and all(all(a['checks'].values()) for a in actual),accepted=False,native_body_renders=len(actual),sourceproof='Original computationally defined query support transfers; no transmission or reflectionsource queries added, declared white environment unchanged; estimated boundary .44/.30percent remains'),indent=2)+'\n')
