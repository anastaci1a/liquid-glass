from pathlib import Path
import copy,json,time,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted,scores
from material_local import statistics
root=Path('/evidence/extended/music-home-vector');out=root/'bridge-probe';out.mkdir(exist_ok=True)
a=json.loads((root/'accepted.json').read_text());b=json.loads((root/'paired/accepted.json').read_text());studies=[Study(root/'paired'/n) for n in ['a','b']]
target=[a['scores'],b['scores'][1]];scale=np.mean([r['loss'] for r in target]);results=[]
def bound(k):return (.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else (-4,4)
def violation(metric):return sum(max(0,(r['loss']-t['loss'])/scale)**2+max(0,(r['glass']['rmse']**2-t['glass']['rmse']**2)/scale)**2 for r,t in zip(metric,target))
for blend in [0.,.25,.5,.75,1.]:
 p=copy.deepcopy(a['parameters'])
 for key,v in p.items():
  if isinstance(v,(int,float)) and not isinstance(v,bool) and key in b['parameters']:p[key]=(1-blend)*v+blend*b['parameters'][key]
 caches=[Cached(s,p) for s in studies];point=(1-blend)*np.array(a['material'])+blend*np.array(b['material']);actual=scores(caches,point)
 for iteration in range(12):
  forms=[statistics(c,point) for c in caches]
  def value(i,v,kind):
   delta=v-point;Q,g=forms[i]['glass'];R,h=forms[i]['rim'];H,e=(.7*Q+.3*R,.7*g+.3*h) if kind=='loss' else (Q,g)
   base=actual[i]['loss'] if kind=='loss' else actual[i]['glass']['rmse']**2
   return base+2*e@delta+delta@H@delta
  def constraints(v):return np.array([x for i,t in enumerate(target) for x in [(t['loss']-value(i,v,'loss'))/scale,(t['glass']['rmse']**2-value(i,v,'glass'))/scale]])
  bounds=[(max(bound(k)[0],point[k]-.15),min(bound(k)[1],point[k]+.15)) for k in range(23)]
  fit=minimize(lambda v:np.mean([value(i,v,'loss') for i in range(2)])/scale,point,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=150,ftol=1e-11))
  best=point;metric=actual;merit=violation(actual)
  for step in [1,.5,.25,.125,.0625,.03125]:
   q=point+step*(fit.x-point);trial=scores(caches,q);m=violation(trial)
   if m<merit-1e-14 or (m<=1e-14 and merit<=1e-14 and sum(r['loss'] for r in trial)<sum(r['loss'] for r in metric)):best=q;metric=trial;merit=m
  changed=np.max(abs(best-point));point,actual=best,metric
  if changed<1e-8:break
 full=[s.scores(s.render(p,point)) for s in studies];row=dict(blend=blend,parameters=p,material=point.tolist(),scores=full,violation=violation(full),permitted=permitted(full,target),iterations=iteration+1);results.append(row)
 (out/'report.json').write_text(json.dumps(dict(scope='Private feasibility experiment; actual current metrics and desired acceptance thresholds remain separate. Never changes accepted state or historical receipts.',targets=target,results=results),indent=2)+'\n')
 print(json.dumps(dict(blend=blend,loss=[r['loss'] for r in full],glass=[r['glass']['rmse'] for r in full],violation=row['violation'],permitted=row['permitted'])),flush=True)
