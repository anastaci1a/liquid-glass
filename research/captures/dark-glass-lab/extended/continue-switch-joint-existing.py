"""One bounded joint settlement of existing shared optical/material parameters."""
import sys,json,copy,time,gc,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached
from joint_visible_statistics import statistics,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-joint-existing/continuation'
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p0=old['parameters'];S=[Study(root/'paired'/n) for n in ['a','b']]
base=json.loads((root/'rev5-filter-space/material-run-inputs.json').read_text())['baseline']
point=np.r_[[p0[f'c{i}'] for i in range(7)],p0['cap_edge_profile'],p0['core_x'],p0['core_y'],p0['gamma'],old['material']]
initial=point.copy();previous=root/'rev5-joint-existing/native-settlement.json';start_record=json.loads(previous.read_text());point=np.asarray(start_record['point']);N=13;scales=np.r_[np.full(10,.02),.01,.01,.1,np.full(23,.05)]
final=out/'native-settlement.json'
if final.exists():raise FileExistsError(final)
def unpack(v):
 p=copy.deepcopy(p0)
 for i in range(7):p[f'c{i}']=float(v[i])
 p.update(cap_edge_profile=v[7:10].tolist(),core_x=float(v[10]),core_y=float(v[11]),gamma=float(v[12]))
 return p,v[N:]
def images(v):
 p,c=unpack(v);return [s.render(p,c) for s in S]
def metrics(ims,v):return [{**s.scores(im,False),**measures(s,unpack(v)[0],im)} for s,im in zip(S,ims)]
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
def bound(k):
 if k<7:return(-2.5,2.5)
 if k<10:return(max(-4,initial[k]-.5),min(4,initial[k]+.5))
 if k<12:return(-.8,.18)
 if k==12:return(.65,2.5)
 j=k-N;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
ims=images(point);met=metrics(ims,point);assert max(abs(a['loss']-b['loss']) for a,b in zip(met,start_record['scores']))<1e-6
run=dict(initial_point=point.tolist(),scales=scales.tolist(),bounds=[bound(k) for k in range(len(point))],baseline=base,continuation_of=str(previous),continuation_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),Path('/workspace/docs/liquid-glass/experiments/reconstruction/extended_fit.py'),Path('/evidence/extended/joint_visible_statistics.py')]})
with (out/'native-run-inputs.json').open('x') as f:json.dump(run,f,indent=2)
history=[];trust=1.;small_steps=0
for iteration in range(8):
 start=time.time();p,co=unpack(point);forms=[]
 for i,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);assert np.max(abs(cache.render(co)-im))<2e-6
  derivatives=[]
  for k in range(N):
   eps=.00015 if k<12 else .0003;a=point.copy();b=point.copy();a[k]=min(bound(k)[1],a[k]+eps);b[k]=max(bound(k)[0],b[k]-eps)
   pa,ca=unpack(a);pb,cb=unpack(b);derivatives.append((s.render(pa,ca)-s.render(pb,cb))/(a[k]-b[k]))
  forms.append(statistics(cache,co,derivatives,scales,im));del cache,derivatives;gc.collect();print('FORM',iteration+1,i+1,round(time.time()-start,2),flush=True)
 np.savez_compressed(out/f'native-form-{iteration+1:02d}.npz',point=point,scales=scales,**{f'{i}_{name}_{kind}':value[j] for i,f in enumerate(forms) for name,value in f.items() for j,kind in enumerate(['H','g'])})
 def value(i,v,kind):
  H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if kind=='loss' else forms[i][kind]
  z=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return z+2*g@d+d@H@d
 def constraints(v):return np.array([q for i,b in enumerate(base) for q in [v[-1]-value(i,v,'loss')/b['loss'],*[1-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(len(point)),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best,bm,bi=point.copy(),met,ims;trials=[]
 for alpha in [1,.5,.25,.125]:
  v=point+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs,v);allowed=all(a[k]['rmse']<=b[k]['rmse']+1e-7 for a,b in zip(m,base) for k in ['glass','shadow'])
  trial=dict(iteration=iteration+1,alpha=alpha,point=v.tolist(),allowed=allowed,scores=m);trials.append(trial)
  with (out/'native-trials.ndjson').open('a') as f:f.write(json.dumps(trial)+'\n')
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi
 history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 p,co=unpack(point);ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)]
 record=dict(parameters=p,material=co.tolist(),scores=met,baseline=base,point=point.tolist(),ratios=ratios,numeric_pass=all(r<=.995 for r in ratios),accepted=False,history=history,method=__doc__)
 (out/'native-progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,'gain',gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 small_steps=small_steps+1 if gain<1e-5 else 0
 if trust<.1 or small_steps>=2:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,flush=True)
