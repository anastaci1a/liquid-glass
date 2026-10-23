"""Four bounded native joint steps for the constant-thickness two-interface crown.
Front f and back h0-f share the same complete height derivatives. Same accepted
source, material family, kernels and native publication guards. Solver steps
are not passes; intermediate infeasible progress cannot be published.
"""
import sys,json,copy,time,gc
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from switch_two_surface import TwoSurfaceStudy
from paired_fit import Cached
from joint_visible_statistics import statistics,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'physical-two-surface'
initial=json.loads((root/'physical-euclidean-surface/native-settlement.json').read_text());old=json.loads((root/'rev4-ambient-review/candidate.json').read_text())
final=out/'coupled-native-settlement.json'
if final.exists():raise FileExistsError(final)
S=[TwoSurfaceStudy(root/'paired'/n) for n in ['a','b']]
base=[]
for s in [Study(root/'paired'/n) for n in ['a','b']]:
 im=s.render(old['parameters'],np.array(old['material']));base.append({**s.scores(im,False),**measures(s,old['parameters'],im)})
point=np.r_[0.,initial['material']];scales=np.r_[.01,np.full(23,.08)]
def unpack(v):
 p=copy.deepcopy(initial['parameters']);p.update(front_crown=float(v[0]),front_profile='ellipse',front_back_coupling=-1.);return p,v[1:]
def images(v):
 p,c=unpack(v);return [s.render(p,c) for s in S]
def metrics(ims,p):return [{**s.scores(im,False),**measures(s,p,im)} for s,im in zip(S,ims)]
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
p,c=unpack(point)
def bound(k):
 if k==0:return(-.08,.08)
 j=k-1;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
ims=images(point);met=metrics(ims,p);initial_scores=copy.deepcopy(met)
assert max(abs(a['loss']-b['loss']) for a,b in zip(met,initial['scores']))<1e-6
history=[];trust=1.
for iteration in range(4):
 start=time.time();p,c=unpack(point);forms=[]
 for si,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);assert np.max(abs(cache.render(c)-im))<2e-6
  eps=.0001;pa=copy.deepcopy(p);pb=copy.deepcopy(p)
  pa['front_crown']+=eps;pb['front_crown']-=eps
  D=(s.render(pa,c)-s.render(pb,c))/(2*eps)
  forms.append(statistics(cache,c,[D],scales,im));del cache,D;s.distance_cache.clear();gc.collect()
 np.savez_compressed(out/f'coupled-native-form-{iteration+1:02d}.npz',point=point,scales=scales,**{f'{i}_{name}_{kind}':value[j] for i,f in enumerate(forms) for name,value in f.items() for j,kind in enumerate(['H','g'])})
 def value(i,v,kind):
  Hg,gg=forms[i]['glass'];Hr,gr=forms[i]['rim'];H,g=(.7*Hg+.3*Hr,.7*gg+.3*gr) if kind=='loss' else forms[i][kind]
  start=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return start+2*g@d+d@H@d
 def constraints(v):return np.array([a for i,b in enumerate(base) for a in [v[-1]-value(i,v,'loss')/b['loss'],*[max(1.,(met[i][k]['rmse']/b[k]['rmse'])**2)-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(24),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best=point.copy();bm=met;bi=ims;trials=[]
 for alpha in [1,.5,.25,.125,.0625]:
  v=point+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs,unpack(v)[0]);allowed=all(a[k]['rmse']<=max(b[k]['rmse'],pr[k]['rmse'])+1e-7 for a,b,pr in zip(m,base,met) for k in ['glass','shadow'])
  trials.append(dict(alpha=alpha,allowed=allowed,scores=m))
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi;history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 p,c=unpack(point);ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)];record=dict(parameters=p,material=c.tolist(),scores=met,baseline=base,initial_scores=initial_scores,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios) and all(a[k]['rmse']<=b[k]['rmse'] for a,b in zip(met,base) for k in ['glass','shadow']),accepted=False,history=history,method=__doc__)
 (out/'coupled-native-progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,'front',point[0],'gain',gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,flush=True)
