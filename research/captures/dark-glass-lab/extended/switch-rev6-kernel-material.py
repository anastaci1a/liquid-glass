"""One predeclared four-step ordinary-kernel/material comparator after gamma changed."""
import sys,copy,json,gc,time,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study as PublicStudy
from extended_fit import Study
from paired_fit import Cached
from joint_visible_statistics import statistics,measures
from chromatic_transmission import weight
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev6-kernel-material';final=out/'settlement.json'
if final.exists():raise FileExistsError(final)
old=json.loads((root/'rev5-joint-existing/candidate.json').read_text());p0=old['parameters'];S=[Study(root/'paired'/n) for n in ['a','b']];N=2
scales=np.r_[.6,.3,np.full(23,.05)];point=np.r_[p0['sigma'],p0['post_sigma'],old['material']]
def bound(k):
 if k<N:return(0.,16.)
 j=k-N;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
def unpack(v):
 p=copy.deepcopy(p0);p['sigma']=float(v[0]);p['post_sigma']=float(v[1]);return p,v[N:]
def images(v):
 p,c=unpack(v);return [s.render(p,c) for s in S]
def metrics(ims,v):return [{**s.scores(im,False),**measures(s,unpack(v)[0],im)} for s,im in zip(S,ims)]
ims=images(point);base=metrics(ims,point);met=base;control=[]
saved=json.loads((root/'rev5-joint-existing/independent-resumed/verification.json').read_text())['candidate']['observations']
for s,m in zip(S,base):
 difference=abs(m['loss']-saved[s.folder.name.upper()]['loss']);assert difference<1e-9
 control.append(dict(observation=s.folder.name,baseline_loss_difference=difference))
record=dict(method=__doc__,baseline_commit='f8061edd3125b090eb5d203b67bb15fd51df8d28',bounds=[bound(i) for i in range(len(point))],baseline=base,controls=control,source_support='Existing maps, changed Gaussian widths; fresh support proof required for any qualifying candidate',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(out/'run-inputs.json').write_text(json.dumps(record,indent=2)+'\n');print('CONTROLS',control,flush=True)
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
history=[];trust=1.
for iteration in range(4):
 start=time.time();p,c=unpack(point);forms=[]
 for i,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);assert abs(cache.render(c)-im).max()<2e-6;derivatives=[]
  for k in range(N):
   a=point.copy();b=point.copy();a[k]=min(bound(k)[1],a[k]+.05);b[k]=max(bound(k)[0],b[k]-.05);pa,ca=unpack(a);pb,cb=unpack(b);derivatives.append((s.render(pa,ca)-s.render(pb,cb))/(a[k]-b[k]))
  forms.append(statistics(cache,c,derivatives,scales,im));del cache,derivatives;gc.collect();print('FORM',iteration+1,i+1,round(time.time()-start,2),flush=True)
 def value(i,v,kind):
  H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if kind=='loss' else forms[i][kind]
  z=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return z+2*g@d+d@H@d
 def constraints(v):return np.array([q for i,b in enumerate(base) for q in [v[-1]-value(i,v,'loss')/b['loss'],*[1-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(len(point)),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best,bm,bi=point.copy(),met,ims;trials=[]
 for alpha in [1,.5,.25,.125]:
  v=point+alpha*scales*fit.x[:-1]
  if np.array_equal(v,point):continue
  imgs=images(v);m=metrics(imgs,v);allowed=all(a[k]['rmse']<=b[k]['rmse']+1e-7 for a,b in zip(m,base) for k in ['glass','shadow'])
  row=dict(iteration=iteration+1,alpha=alpha,point=v.tolist(),scores=m,allowed=allowed);trials.append(row)
  with (out/'trials.ndjson').open('a') as f:f.write(json.dumps(row)+'\n')
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi
 history.append(dict(iteration=iteration+1,gain=gain,seconds=time.time()-start,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 p,c=unpack(point);ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)];result=dict(parameters=p,material=c.tolist(),scores=met,baseline=base,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios),accepted=False,history=history,termination='Predeclared4updatebudget; notglobalconvergence')
 (out/'progress.json').write_text(json.dumps(result,indent=2)+'\n');print('ITER',iteration+1,ratios,point[:2].tolist(),gain,flush=True)
 trust=trust*.4 if gain<1e-6 else min(1.5,trust*1.2)
with final.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
