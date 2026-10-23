"""One bounded shared-material update, frozen two-reference selector inputs."""
import sys,copy,json,time,hashlib,gc
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached
from joint_visible_statistics import statistics,measures
from revision_replay import clean_composite
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-segmented-selector');out=Path('/evidence/extended/selector-short-round/pass-01');out.mkdir(parents=True,exist_ok=True)
assert not (out/'candidate.json').exists(),'Completed proposal must not be repeated'
old=json.loads((root/'accepted.json').read_text());p=old['parameters'];co=np.array(old['material']);studies=[Study(root),Study(root/'second-observation')]
scales=np.full(23,.025);forms=[];base=[];images=[]
for i,s in enumerate(studies):
 cache=Cached(s,p);pred=cache.render(co);direct=s.render(p,co);assert np.max(np.abs(pred-direct))<2e-6
 score={**s.scores(pred,False),**measures(s,p,pred)};base.append(score);images.append(pred)
 if i==0:assert abs(score['glass']['rmse']-old['scores']['glass']['rmse'])<1e-6
 forms.append(statistics(cache,co,[],scales,pred));np.save(out/f'baseline-{i}.npy',pred);del cache;gc.collect()
 print('BASE',i,score,flush=True)
def val(i,z,key):
 H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if key=='loss' else forms[i][key]
 b=base[i]['loss'] if key=='loss' else base[i][key]['rmse']**2
 return b+2*g@z+z@H@z
def con(v):
 return np.array([c for i,b in enumerate(base) for c in [v[-1]-val(i,v[:-1],'loss')/b['loss'],*[1-val(i,v[:-1],k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
bounds=[]
for k,c in enumerate(co):
 lo,hi=(.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4)
 bounds.append((max(-1.,(lo-c)/scales[k]),min(1.,(hi-c)/scales[k])))
fit=minimize(lambda v:v[-1],np.r_[np.zeros(23),1.],method='SLSQP',bounds=bounds+[(0,2)],constraints=[dict(type='ineq',fun=con)],options=dict(maxiter=100,ftol=1e-11))
trials=[];best=None
for alpha in [1.,.5,.25]:
 c=co+alpha*scales*fit.x[:-1];scores=[];preds=[]
 for s in studies:
  im=s.render(p,c);preds.append(im);scores.append({**s.scores(im,False),**measures(s,p,im)})
 allowed=all(a['loss']<=b['loss'] and all(a[k]['rmse']<=b[k]['rmse'] for k in ['glass','shadow']) for a,b in zip(scores,base))
 ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(scores,base)]
 row=dict(alpha=alpha,material=c.tolist(),scores=scores,ratios=ratios,allowed=allowed);trials.append(row);print('TRIAL',alpha,ratios,allowed,flush=True)
 if allowed and any(r<1-1e-8 for r in ratios):
  best=row
  for i,(s,im) in enumerate(zip(studies,preds)):
   np.save(out/f'candidate-{i}.npy',im);from PIL import Image
   Image.fromarray(np.uint8(np.rint(np.clip(clean_composite(s,p,im),0,1)*255))).save(out/f'preview-{i}.png')
  break
record=dict(baseline=base,trials=trials,solver_success=bool(fit.success),solver_message=str(fit.message),bounds=bounds,parameters=p,material=best['material'] if best else co.tolist(),scores=best['scores'] if best else base,ratios=best['ratios'] if best else [1,1],numeric_candidate=best is not None,accepted=False,method=__doc__,limits='Frozen input estimates remain uncertain; material calibration does not correct known footprint/refraction/ordinary-blur defects. One bounded update, no convergence claim.')
(out/'candidate.json').write_text(json.dumps(record,indent=2)+'\n');print('DONE',record['ratios'],flush=True)
