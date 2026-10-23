"""Existing lighting widths re-calibrated after accepted geometry/ambient changes.

The earlier width study preceded cap-profile and ambient revisions. Fixed crops
still show excessive dark-rim width. This reuses the exact accepted transmission;
only two existing lighting widths and the same shared material can change.
"""
import sys,json,copy,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from switch_rim_width_cache import RimWidthCache
from joint_visible_statistics import statistics,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-light-width'
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p0=old['parameters'];S=[Study(root/'paired'/n) for n in ['a','b']]
caches=[RimWidthCache(s,p0) for s in S];final=out/'settlement.json'
if final.exists():raise FileExistsError(final)
point=np.r_[p0['rim_width'],p0['thin_width'],old['material']];scales=np.r_[.003,.001,np.full(23,.05)]
def unpack(v):
 p=copy.deepcopy(p0);p.update(rim_width=float(v[0]),thin_width=float(v[1]));return p,v[2:]
def images(v):return [c.widths(*v[:2]).render(v[2:]) for c in caches]
def metrics(ims,p):return [{**s.scores(im,False),**measures(s,p,im)} for s,im in zip(S,ims)]
p,co=unpack(point);ims=images(point);met=metrics(ims,p);base=copy.deepcopy(met)
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
def bound(k):
 if k==0:return(.005,.12)
 if k==1:return(.001,.05)
 j=k-2;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
history=[];trust=1.
for iteration in range(8):
 start=time.time();p,co=unpack(point);forms=[]
 for si,(cache,im) in enumerate(zip(caches,ims)):
  ds=[]
  for k in range(2):
   eps=1e-5;va=point[:2].copy();vb=point[:2].copy();va[k]+=eps;vb[k]-=eps
   da=cache.widths(*va).render(co);db=cache.widths(*vb).render(co);ds.append((da-db)/(2*eps))
  cache.widths(*point[:2]);forms.append(statistics(cache,co,ds,scales,im))
 np.savez_compressed(out/f'form-{iteration+1:02d}.npz',point=point,scales=scales,**{f'{i}_{name}_{kind}':value[j] for i,f in enumerate(forms) for name,value in f.items() for j,kind in enumerate(['H','g'])})
 def value(i,v,kind):
  H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if kind=='loss' else forms[i][kind]
  b=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return b+2*g@d+d@H@d
 def constraints(v):return np.array([a for i,b in enumerate(base) for a in [v[-1]-value(i,v,'loss')/b['loss'],*[1.-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(25),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best=point.copy();bm=met;bi=ims;trials=[]
 for alpha in [1,.5,.25,.125,.0625]:
  v=point+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs,unpack(v)[0]);allowed=all(a[k]['rmse']<=b[k]['rmse']+1e-7 for a,b in zip(m,base) for k in ['glass','shadow'])
  trial=dict(iteration=iteration+1,alpha=alpha,point=v.tolist(),allowed=allowed,scores=m);trials.append(trial)
  with (out/'trials.ndjson').open('a') as f:f.write(json.dumps(trial)+'\n')
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi
 history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 p,co=unpack(point);ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)]
 record=dict(parameters=p,material=co.tolist(),scores=met,baseline=base,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios) and all(a[k]['rmse']<=b[k]['rmse'] for a,b in zip(met,base) for k in ['glass','shadow']),accepted=False,history=history,method=__doc__)
 (out/'progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,'widths',point[:2].tolist(),'gain',gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,flush=True)
