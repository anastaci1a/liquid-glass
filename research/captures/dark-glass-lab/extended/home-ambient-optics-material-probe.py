from pathlib import Path
import copy,json,time,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,scores,permitted
from material_local import statistics
from source_support import coverage_report,supported
root=Path('/evidence/extended/music-home-vector');out=root/'ambient-optics-material-probe';out.mkdir(exist_ok=True)
a=json.loads((root/'accepted.json').read_text());b=json.loads((root/'paired/accepted.json').read_text());targets=[a['scores'],b['scores'][1]];studies=[Study(root/'paired'/n) for n in ['a','b']];norm=np.mean([r['loss'] for r in targets]);results=[]
def bound(k):return (.05,1.5) if k<3 or 20<=k<23 else (-.8,.8) if k<6 else (-4,4)
def violation(metric):return sum(max(0,(r['loss']-t['loss'])/norm)**2+max(0,(r['glass']['rmse']**2-t['glass']['rmse']**2)/norm)**2 for r,t in zip(metric,targets))
chosen=json.loads((root/'ambient-optics-normalized-probe/running.json').read_text())['best']
for label,seed in [('joint-optics',chosen)]:
 start=time.time();p=seed['parameters'];caches=[Cached(s,p) for s in studies];transforms=[];means=[]
 for s in studies:
  x0,y0,x1,y1=s.crop;*_,(sd,_,_)=s.shape(s.x,s.y,p);mean=s.source[y0:y1,x0:x1][sd<0].mean(0,dtype=np.float64);luma=float(mean@np.array([.2126,.7152,.0722]));means.append(luma)
  T=np.c_[np.eye(23),np.zeros((23,3))];T[[6,9,12],np.arange(23,26)]=luma-.5;transforms.append(T)
 def metric(v):return [s.scores(c.render(T@v),include_ssim=False) for s,c,T in zip(studies,caches,transforms)]
 point=np.r_[seed['material'],seed['ambient_rim_response']];actual=metric(point)
 for iteration in range(40):
  forms=[]
  for c,T in zip(caches,transforms):
   raw=statistics(c,T@point);forms.append({name:(T.T@H@T,T.T@g) for name,(H,g) in raw.items()})
  def value(i,v,kind):
   delta=v-point;Q,g=forms[i]['glass'];R,h=forms[i]['rim'];H,e=(.7*Q+.3*R,.7*g+.3*h) if kind=='loss' else (Q,g);base=actual[i]['loss'] if kind=='loss' else actual[i]['glass']['rmse']**2
   return base+2*e@delta+delta@H@delta
  def constraints(v):return np.array([x for i,t in enumerate(targets) for x in [(t['loss']-value(i,v,'loss'))/norm,(t['glass']['rmse']**2-value(i,v,'glass'))/norm]])
  radius=np.r_[np.full(23,.15),np.full(3,.8)];bounds=[(max(bound(k)[0],point[k]-radius[k]),min(bound(k)[1],point[k]+radius[k])) for k in range(26)]
  fit=minimize(lambda v:np.mean([value(i,v,'loss') for i in range(2)])/norm,point,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=150,ftol=1e-11))
  best=point;best_metric=actual;merit=violation(actual)
  for step in [1,.5,.25,.125,.0625,.03125]:
   q=point+step*(fit.x-point);m=metric(q);v=violation(m)
   if v<merit-1e-14 or (v<=1e-14 and merit<=1e-14 and sum(r['loss'] for r in m)<sum(r['loss'] for r in best_metric)):best=q;best_metric=m;merit=v
  changed=np.max(abs(best-point));point,actual=best,best_metric
  if changed<1e-8:break
 full=[s.scores(s.render(p,T@point)) for s,T in zip(studies,transforms)];footprints=[coverage_report(s,p) for s in studies];row=dict(seed=label,parameters=p,material=point[:23].tolist(),ambient_rim_response=point[23:].tolist(),source_luma=means,scores=full,permitted=permitted(full,targets) and all(supported(s,r) for s,r in zip(studies,footprints)),source_support=footprints,iterations=iteration+1,seconds=time.time()-start);results.append(row)
 (out/'report.json').write_text(json.dumps(dict(scope='Private common source-luma response in three neutral rim-light basis coefficients, not unrelated per-scene materials or an identified Apple law. No accepted-state writes/counts.',model='effective thin/e/f coefficients=shared base+(mean unrefracted source encoded luma−.5)*three shared response values; all source/scoring masks fixed.',targets=targets,results=results),indent=2)+'\n')
 for name,s,T in zip(['a','b'],studies,transforms):s.comparison(s.render(p,T@point),out/(label+'-'+name+'.png'),p)
 print(json.dumps(dict(seed=label,loss=[r['loss'] for r in full],permitted=row['permitted'],response=row['ambient_rim_response'])),flush=True)
