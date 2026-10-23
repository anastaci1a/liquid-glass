"""Cap-depth normal profile and shared material settlement; one family following the branch screen.

Same renderer, inputs and masks. Analytic clipped-affine material derivatives and native optical finite differences propose a step;
nonlinear native rendering accepts it. No pixel corrections or new model terms.
"""
import sys,json,copy,time,gc
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize
sys.path.insert(0,'/evidence/extended')
from switch_cap_edge_model import CachedCapEdge
class Study(CachedCapEdge):
 def geometry_field(self,x,y,p):
  q={k:v for k,v in p.items() if k not in ['edge0','edge1','edge2']};q['cap_edge_profile']=[p.get('edge'+str(i),0.) for i in range(3)];return super().geometry_field(x,y,q)
from paired_fit import Cached
from joint_material_jacobian import statistics as joint_statistics
root=Path('/evidence/extended/active-switch');out=root/'rev3-cap-edge-review';out.mkdir(exist_ok=True)
old=json.loads((root/'joint-native-review/candidate.json').read_text());verification=json.loads((root/'joint-native-review/hq/verification.json').read_text());old['scores']=[verification['candidate']['observations'][n] for n in ['A','B']]
S=[Study(root/'paired'/n,old['parameters']) for n in ['a','b']]
old['parameters'].update(edge0=0.,edge1=0.,edge2=0.)
keys=['edge0','edge1','edge2']
scales=np.array([.25,.25,.15]+[.08]*23)
resume=json.loads((out/'batch-01.json').read_text());assert json.loads((root/'joint-jacobian-check/verification.json').read_text())['passed']
start=np.r_[[resume['parameters'][k] for k in keys],resume['material']];point=start.copy();history=resume['history'].copy()
N=len(keys)
def unpack(v):
 p=copy.deepcopy(old['parameters']);p.update(zip(keys,map(float,v[:N])));return p,v[N:]
def images(v):
 p,c=unpack(v);return [s.render(p,c) for s in S]
def metrics(ims):return [s.scores(im,include_ssim=False) for s,im in zip(S,ims)]
def merit(m):return max(a['loss']/b['loss'] for a,b in zip(m,old['scores']))
def bounds(i):
 if i<N:
  if keys[i].startswith('edge'):return (-3.,6.)
  if keys[i].startswith('core'):return (-.8,.18)
  if keys[i]=='cap_normal_gain':return (-.95,1.8)
  return (-2.5,2.5)
 k=i-N;return (.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4)
ims=images(point);met=metrics(ims);trust=1.5
for iteration in range(8,16):
 t0=time.time();p,c=unpack(point);forms=[]
 for index,(s,im) in enumerate(zip(S,ims)):
  cache=Cached(s,p);assert np.max(abs(cache.render(c)-im))<2e-6
  derivatives=[]
  for k in range(N):
   eps=.0006;pa=copy.deepcopy(p);pb=copy.deepcopy(p);pa[keys[k]]+=eps;pb[keys[k]]-=eps
   derivatives.append((s.render(pa,c)-s.render(pb,c))/(2*eps))
  forms.append(joint_statistics(cache,c,derivatives,scales,im));del cache,derivatives;gc.collect();print('ANALYTIC_JAC',iteration+1,index+1,round(time.time()-t0,2),flush=True)
 def value(i,v,kind):
  Hg,gg=forms[i]['glass'];Hr,gr=forms[i]['rim'];H,g=(.7*Hg+.3*Hr,.7*gg+.3*gr) if kind=='loss' else forms[i][kind]
  base=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2
  d=v[:-1];return base+2*g@d+d@H@d
 def constraints(v):return np.array([z for i,b in enumerate(old['scores']) for z in [v[-1]-value(i,v,'loss')/b['loss'],1-value(i,v,'glass')/b['glass']['rmse']**2,1-value(i,v,'rim')/b['rim']['rmse']**2]])
 ranges=[(max(-trust,(bounds(i)[0]-v)/scales[i]),min(trust,(bounds(i)[1]-v)/scales[i])) for i,v in enumerate(point)]+[(0,10)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(len(point)),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 best=point.copy();bestims=ims;bestmet=met;trials=[]
 for alpha in [1,.5,.25,.125]:
  v=point+alpha*scales*fit.x[:-1];candidate=images(v);m=metrics(candidate)
  allowed=all(a['glass']['rmse']<=b['glass']['rmse']+1e-7 and a['rim']['rmse']<=b['rim']['rmse']+1e-7 for a,b in zip(m,old['scores']))
  trials.append(dict(alpha=alpha,merit=merit(m),allowed=allowed,scores=m))
  if allowed and merit(m)<merit(bestmet):best,bestims,bestmet=v,candidate,m
 gain=merit(met)-merit(bestmet);point,ims,met=best,bestims,bestmet
 row=dict(iteration=iteration+1,seconds=time.time()-t0,trust=trust,solver_success=bool(fit.success),solver_message=str(fit.message),scores=met,gain=gain,trials=trials);history.append(row)
 p,c=unpack(point);ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(met,old['scores'])]
 record=dict(parameters=p,material=c.tolist(),scores=met,ratios=ratios,numeric_pass=bool(max(ratios)<=.995),accepted=False,history=history,keys=keys,scales=scales.tolist(),method=__doc__)
 (out/'continued-settlement.json').write_text(json.dumps(record,indent=2)+'\n');print('ITER',iteration+1,ratios,gain,flush=True)
 if gain<1e-6:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
print('FINAL',ratios,flush=True)
