"""Exact-native settlement of the bounded Euclidean back-surface family.
Tests proposal-approximation error after fixed quadrature calibration. No new
surface/source/masks/material freedom. Six trust steps, original publication
gates unchanged. Infeasible starts may only improve their current glass/shadow
error until they meet incumbent guards. Crop measurements stay advisory.
"""
import sys,json,copy,time,gc
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from switch_euclidean_surface import EuclideanSurfaceStudy
from paired_fit import Cached
from joint_visible_statistics import statistics,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface'
final=out/'native-settlement.json'
if final.exists():raise FileExistsError(final)
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text())
initial=json.loads((out/'coupling-settlement.json').read_text())
S=[EuclideanSurfaceStudy(root/'paired'/n) for n in ['a','b']]
base=[]
for s in [Study(root/'paired'/n) for n in ['a','b']]:
 im=s.render(old['parameters'],np.array(old['material']));base.append({**s.scores(im,False),**measures(s,old['parameters'],im)})
q=initial['parameters']['euclidean_surface'];point=np.r_[[q['bx'],q['by']],q['profile'],[q['longitudinal']],initial['material']]
scales=np.r_[np.full(9,.005),[.03],np.full(23,.08)]
def unpack(v):
 p=copy.deepcopy(initial['parameters']);q=p['euclidean_surface'];q['bx'],q['by']=map(float,v[:2]);q['profile']=v[2:9].tolist();q['longitudinal']=float(v[9]);return p,v[10:]
def images(v):
 p,c=unpack(v);return [s.render(p,c) for s in S]
def metrics(ims,p):return [{**s.scores(im,False),**measures(s,p,im)} for s,im in zip(S,ims)]
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
def bound(k):
 if k<2:return(-.08,.08)
 if k<9:return(-.5,.5)
 if k==9:return(-.25,.25)
 j=k-10;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
ims=images(point);met=metrics(ims,unpack(point)[0]);initial_scores=copy.deepcopy(met);history=[];trust=1.
for iteration in range(6):
 start=time.time();p,c=unpack(point);forms=[]
 for si,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);cache_error=float(np.max(abs(cache.render(c)-im)));assert cache_error<2e-6,cache_error
  derivatives=[]
  for k in range(10):
   eps=.001 if k==9 else .0002;v=point.copy();v[k]+=eps;pa,ca=unpack(v);v[k]-=2*eps;pb,cb=unpack(v)
   derivatives.append((s.render(pa,ca)-s.render(pb,cb))/(2*eps))
  forms.append(statistics(cache,c,derivatives,scales,im));del cache,derivatives;s.distance_cache.clear();gc.collect()
  print('JAC',iteration+1,si+1,round(time.time()-start,2),flush=True)
 def value(i,v,kind):
  Hg,gg=forms[i]['glass'];Hr,gr=forms[i]['rim'];H,g=(.7*Hg+.3*Hr,.7*gg+.3*gr) if kind=='loss' else forms[i][kind]
  start=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return start+2*g@d+d@H@d
 def constraints(v):
  vals=[a for i,b in enumerate(base) for a in [v[-1]-value(i,v,'loss')/b['loss'],*[max(1.,(met[i][k]['rmse']/b[k]['rmse'])**2)-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]]
  trial=point+scales*v[:-1];bx,by=trial[:2];a=max(abs(trial[2:9]));k=abs(trial[9])
  for s in S:
   _,_,half,r,_=s.shape(np.array([0.]),np.array([0.]),p);M=2*np.hypot(bx*half[0]/r,by*half[1]/r)+a*(1+k*(1+1.5*r/max(half)));low=.8+min(bx,0)*(half[0]/r)**2+min(by,0)*(half[1]/r)**2-.75*a*(1+k);vals.extend([.87-M,low-.02])
  return np.array(vals)
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(33),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best=point.copy();bm=met;bi=ims;trials=[]
 for alpha in [1,.5,.25,.125]:
  v=point+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs,unpack(v)[0]);allowed=all(a[k]['rmse']<=max(b[k]['rmse'],pr[k]['rmse'])+1e-7 for a,b,pr in zip(m,base,met) for k in ['glass','shadow'])
  trials.append(dict(alpha=alpha,allowed=allowed,scores=m))
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi;history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 p,c=unpack(point);ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)];record=dict(parameters=p,material=c.tolist(),scores=met,baseline=base,initial_scores=initial_scores,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios) and all(a[k]['rmse']<=b[k]['rmse'] for a,b in zip(met,base) for k in ['glass','shadow']),accepted=False,history=history,method=__doc__)
 (out/'native-progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,flush=True)
