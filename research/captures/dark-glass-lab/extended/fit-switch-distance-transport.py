"""Bounded native profile/material settlement of true-distance transport.

Three inner normal and three cap coefficients, same shared material. Original
geometry/source/shape/masks/shadow unchanged. Trials are not verified passes.
"""
import sys,json,copy,time,gc,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from switch_distance_transport import DistanceTransportStudy
from paired_fit import Cached
from joint_visible_statistics import statistics,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-distance-transport'
old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());base=json.loads((root/'rev5-filter-space/material-run-inputs.json').read_text())['baseline']
p0=copy.deepcopy(old['parameters']);p0['distance_transport']=True;S=[DistanceTransportStudy(root/'paired'/n) for n in ['a','b']]
point=np.r_[[p0[f'c{i}'] for i in [4,5,6]],p0['cap_edge_profile'],old['material']];initial_point=point.copy();scales=np.r_[np.full(6,.03),np.full(23,.05)]
final=out/'native-settlement.json'
if final.exists():raise FileExistsError(final)
def unpack(v):
 p=copy.deepcopy(p0)
 for j,i in enumerate([4,5,6]):p[f'c{i}']=float(v[j])
 p['cap_edge_profile']=v[3:6].tolist();return p,v[6:]
def cache_render(s,v):
 p,c=unpack(v);cache=Cached(s,p);return cache.render(c)
def images(v):return [cache_render(s,v) for s in S]
def metrics(ims,p):return [{**s.scores(im,False),**measures(s,p,im)} for s,im in zip(S,ims)]
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,base))
def guards(m):return all(a[k]['rmse']<=b[k]['rmse']+1e-7 for a,b in zip(m,base) for k in ['glass','shadow'])
def bound(k):
 if k<6:
  width=.2 if k<3 else .1 if k==3 else .3
  return(max(-4,initial_point[k]-width),min(4,initial_point[k]+width))
 j=k-6;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
ims=images(point);met=metrics(ims,p0)
native=json.loads((out/'native-initializations.json').read_text())['rows'];expected=[r for r in native if r['variant']=='unchanged-coefficients']
cache_score_errors=[abs(a['loss']-b['scores']['loss']) for a,b in zip(met,expected)];assert max(cache_score_errors)<1e-6,cache_score_errors
run=dict(initial_scores=met,baseline=base,initial_point=point.tolist(),scales=scales.tolist(),bounds=[bound(k) for k in range(29)],native_direct_cache_loss_difference=cache_score_errors,files={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),Path('/evidence/extended/switch_distance_transport.py')]})
with (out/'native-run-inputs.json').open('x') as f:json.dump(run,f,indent=2)
trust=1.;history=[]
for iteration in range(4):
 start=time.time();p,co=unpack(point);forms=[]
 for i,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);derivatives=[]
  for k in range(6):
   eps=.00015;u=point.copy();v=point.copy();u[k]+=eps;v[k]-=eps
   derivatives.append((cache_render(s,u)-cache_render(s,v))/(2*eps))
  forms.append(statistics(cache,co,derivatives,scales,im));del cache,derivatives;gc.collect();print('FORM',iteration+1,i+1,round(time.time()-start,2),flush=True)
 np.savez_compressed(out/f'native-form-{iteration+1:02d}.npz',point=point,scales=scales,**{f'{i}_{name}_{kind}':value[j] for i,f in enumerate(forms) for name,value in f.items() for j,kind in enumerate(['H','g'])})
 def value(i,v,kind):
  H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if kind=='loss' else forms[i][kind]
  b=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return b+2*g@d+d@H@d
 ceilings=[{k:max(a[k]['rmse'],b[k]['rmse'])**2 for k in ['glass','shadow']} for a,b in zip(met,base)]
 def constraints(v):return np.array([q for i,b in enumerate(base) for q in [v[-1]-value(i,v,'loss')/b['loss'],*[1-value(i,v,k)/ceilings[i][k] for k in ['glass','shadow']]]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(29),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best,bm,bi=point.copy(),met,ims;trials=[]
 for alpha in [1,.5,.25,.125]:
  v=point+alpha*scales*fit.x[:-1];imgs=images(v);m=metrics(imgs,unpack(v)[0]);allowed=all(a[k]['rmse']**2<=ceilings[i][k]+1e-6 for i,a in enumerate(m) for k in ['glass','shadow'])
  trial=dict(iteration=iteration+1,alpha=alpha,point=v.tolist(),restoration_permitted=allowed,original_guards=guards(m),scores=m);trials.append(trial)
  with (out/'native-trials.ndjson').open('a') as f:f.write(json.dumps(trial)+'\n')
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,imgs
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi
 history.append(dict(iteration=iteration+1,seconds=time.time()-start,gain=gain,solver_success=bool(fit.success),solver_message=str(fit.message),trials=trials))
 p,co=unpack(point);ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(met,base)]
 record=dict(parameters=p,material=co.tolist(),scores=met,baseline=base,ratios=ratios,numeric_pass=all(r<=.995 for r in ratios) and guards(met),accepted=False,history=history,method=__doc__)
 (out/'native-progress.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,'gain',gain,'guards',guards(met),flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
with final.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print('FINAL',ratios,flush=True)
