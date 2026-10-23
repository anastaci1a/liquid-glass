"""Uncounted coupled native profile/material probe; no extra material layer."""
from pathlib import Path
import json,copy,numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted
r=Path('/evidence/extended/music-navigation/paired');old=json.loads((r/'accepted.json').read_text());p=old['parameters'];studies=[Study(r/n) for n in ['a','b']];baseline=old['scores'];point=np.array([*old['material'],*[p[f'c{i}'] for i in range(7)]],float);history=[]
for s in studies:s.case['foreground_styles']=old.get('foreground_styles',{})
def params(v):return {**p,**{f'c{i}':float(v[23+i]) for i in range(7)}}
def images(v):return [s.render(params(v),v[:23]) for s in studies]
def scores(v):return [s.scores(G,include_ssim=False) for s,G in zip(studies,images(v))]
def bound(k):return ((.05,1.5) if k<3 or 20<=k<23 else (-.8,.8) if k<6 else (-4,4)) if k<23 else (0,2.5)
metric=scores(point)
for iteration in range(12):
 predicted=images(point);caches=[Cached(s,params(point)) for s in studies];derivatives=[]
 for k in range(7):
  plus=point.copy();minus=point.copy();plus[23+k]+=.01;minus[23+k]-=.01;A=images(plus);B=images(minus);derivatives.append([(a-b)/.02 for a,b in zip(A,B)])
 forms=[]
 for scene,(c,pred) in enumerate(zip(caches,predicted)):
  H,W=c.H,c.W;C,J=c.C,c.J;core=J[...,-1];gain=(1-core[...,None])*point[:3]+core[...,None]*point[20:23];z=C*gain+point[3:6]+(J[...,:-1]@point[6:20])[...,None];residual=pred.astype(float)-c.study.target_crop
  data={name:[np.zeros((30,30)),np.zeros(30)] for name in ['glass','rim']}
  for channel in range(3):
   active=(z[...,channel]>0)&(z[...,channel]<1);average=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3));F=np.zeros((H,W,30))
   F[...,channel]=average(active*C[...,channel]*(1-core));F[...,channel+3]=average(active);F[...,6:20]=average(active[...,None]*J[...,:-1]);F[...,channel+20]=average(active*C[...,channel]*core)
   if p['post_sigma']>.001:F[...,:23]=cv2.GaussianBlur(F[...,:23],(0,0),p['post_sigma'])
   for k in range(7):F[...,23+k]=derivatives[k][scene][...,channel]
   for name,mask in [('glass',c.study.valid),('rim',c.study.rim)]:
    X=F[mask];e=residual[...,channel][mask];factor=255**2/(3*mask.sum());data[name][0]+=(X.T@X)*factor;data[name][1]+=(X.T@e)*factor
  forms.append(data)
 scale=max(1,np.mean([v['loss'] for v in metric]));scales=np.array([.05]*23+[.04]*7)
 def value(i,v,kind):
  d=v-point;Q,g=forms[i]['glass'];R,h=forms[i]['rim'];A,b=(.7*Q+.3*R,.7*g+.3*h) if kind=='loss' else (Q,g);base=metric[i]['loss'] if kind=='loss' else metric[i]['glass']['rmse']**2;return base+2*b@d+d@A@d
 def constraints(u):
  v=point+u*scales;return np.array([x for i,b in enumerate(baseline) for x in [(b['loss']-value(i,v,'loss'))/scale,(b['glass']['rmse']**2-value(i,v,'glass'))/scale]])
 bounds=[((max(bound(k)[0],point[k]-scales[k])-point[k])/scales[k],(min(bound(k)[1],point[k]+scales[k])-point[k])/scales[k]) for k in range(30)]
 fit=minimize(lambda u:np.mean([value(i,point+u*scales,'loss') for i in range(2)])/scale,np.zeros(30),method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=160,ftol=1e-12))
 best=point.copy();best_metric=metric
 for t in [1,.5,.25,.125,.0625,.03125,.015625]:
  v=point+t*fit.x*scales;trial=scores(v)
  if permitted(trial,baseline) and sum(x['loss'] for x in trial)<sum(x['loss'] for x in best_metric):best=v;best_metric=trial
 improvement=sum(x['loss'] for x in metric)-sum(x['loss'] for x in best_metric);point,metric=best,best_metric;history.append(dict(iteration=iteration+1,scores=metric,parameters=point.tolist()));print(iteration+1,[x['loss'] for x in metric],flush=True)
 if improvement<1e-6:break
fg=[]
for i,(s,G) in enumerate(zip(studies,images(point))):
 composite=s.apply_foreground(G.copy());x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  if layer.get('fit_style',True):
   a,b,c,d=layer['box'];fg.append(float(np.mean((composite[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2)
 s.comparison(G,r/f'probe-joint-profile-{i}.png',params(point))
(r/'joint-profile-probe.json').write_text(json.dumps(dict(scope='Uncounted coupled profile/material feasibility probe. Native renderer owns both per-scene loss/glass gates; no extra rendering operator.',baseline=baseline,parameters=point.tolist(),scores=metric,foreground_mse=fg,history=history),indent=2)+'\n')
