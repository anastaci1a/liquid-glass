"""Uncounted feasibility probe: bounded reflection mixed in display-linear light."""
from pathlib import Path
import json,numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted
r=Path('/evidence/extended/music-navigation/paired');old=json.loads((r/'accepted.json').read_text());p=old['parameters'];studies=[Study(r/n) for n in ['a','b']];caches=[Cached(s,p) for s in studies];baseline=old['scores'];results=[]
for s in studies:s.case['foreground_styles']=old.get('foreground_styles',{})
def decode(v):
 v=np.asarray(v,float);return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def encode(v):
 v=np.maximum(v,0);return np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055)
def ddecode(v):
 return np.where(v<=.04045,1/12.92,2.4/1.055*((v+.055)/1.055)**1.4)
def dencode(v):
 return np.where(v<=.0031308,12.92,1.055/2.4*np.maximum(v,1e-12)**(1/2.4-1))
for width in [.02,.05,.08,.12,.2]:
 weights=[]
 for s in studies:
  H,W=s.target_crop.shape[:2];mask=np.empty((H,W),np.float32)
  for row,bottom,ww,x,y in s.raster_tiles(1):
   *_,(sd,_,_)=s.shape(x,y,p);mask[row:bottom]=np.exp(-(np.maximum(-sd,0)/width)**2).reshape(bottom-row,2,ww,2).mean((1,3))
  weights.append(mask)
 point=np.array([*old['material'],0,0,0,0],float)
 def images(v):
  bases=[c.render(v[:23]) for c in caches]
  if v[23]==0 and np.all(v[24:]==0):return bases
  return [encode(decode(G)*(1-w[...,None]*v[23])+w[...,None]*v[24:27]).astype(np.float32) for G,w in zip(bases,weights)]
 def scores(v):return [s.scores(pred,include_ssim=False) for s,pred in zip(studies,images(v))]
 metric=scores(point)
 def bound(k):return ((.05,1.5) if k<3 or 20<=k<23 else (-.8,.8) if k<6 else (-4,4)) if k<23 else (0,1)
 for iteration in range(16):
  forms=[];predictions=images(point)
  for c,w,pred in zip(caches,weights,predictions):
   H,W=c.H,c.W;C,J=c.C,c.J;core=J[...,-1];gain=(1-core[...,None])*point[:3]+core[...,None]*point[20:23];z=C*gain+point[3:6]+(J[...,:-1]@point[6:20])[...,None];base=c.render(point[:23]);residual=pred.astype(float)-c.study.target_crop
   scene={name:[np.zeros((27,27)),np.zeros(27)] for name in ['glass','rim']}
   for channel in range(3):
    active=(z[...,channel]>0)&(z[...,channel]<1);average=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3));F=np.zeros((H,W,27))
    F[...,channel]=average(active*C[...,channel]*(1-core));F[...,channel+3]=average(active);F[...,6:20]=average(active[...,None]*J[...,:-1]);F[...,channel+20]=average(active*C[...,channel]*core)
    if p['post_sigma']>.001:F[...,:23]=cv2.GaussianBlur(F[...,:23],(0,0),p['post_sigma'])
    linear=decode(base[...,channel]);mixed=linear*(1-w*point[23])+w*point[24+channel];slope=dencode(mixed)
    F[...,:23]*=(ddecode(base[...,channel])*(1-w*point[23])*slope)[...,None];F[...,23]=-w*linear*slope;F[...,24+channel]=w*slope
    for name,mask in [('glass',c.study.valid),('rim',c.study.rim)]:
     X=F[mask];e=residual[...,channel][mask];factor=255**2/(3*mask.sum());scene[name][0]+=(X.T@X)*factor;scene[name][1]+=(X.T@e)*factor
   forms.append(scene)
  scale=max(1,np.mean([v['loss'] for v in metric]));scales=np.array([.05]*23+[.25]*4)
  def value(i,v,kind):
   d=v-point;Q,g=forms[i]['glass'];R,h=forms[i]['rim'];A,b=(.7*Q+.3*R,.7*g+.3*h) if kind=='loss' else (Q,g);base=metric[i]['loss'] if kind=='loss' else metric[i]['glass']['rmse']**2;return base+2*b@d+d@A@d
  def constraints(u):
   v=point+u*scales;return np.array([*list(v[23]-v[24:]),*[x for i,b in enumerate(baseline) for x in [(b['loss']-value(i,v,'loss'))/scale,(b['glass']['rmse']**2-value(i,v,'glass'))/scale]]])
  bounds=[((max(bound(k)[0],point[k]-scales[k])-point[k])/scales[k],(min(bound(k)[1],point[k]+scales[k])-point[k])/scales[k]) for k in range(27)]
  fit=minimize(lambda u:np.mean([value(i,point+u*scales,'loss') for i in range(2)])/scale,np.zeros(27),method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=160,ftol=1e-12))
  best=point.copy();best_metric=metric
  for t in [1,.5,.25,.125,.0625,.03125,.015625]:
   v=point+t*fit.x*scales;trial=scores(v)
   if min(v[23]-v[24:])>=-1e-8 and permitted(trial,baseline) and sum(x['loss'] for x in trial)<sum(x['loss'] for x in best_metric):best=v;best_metric=trial
  improvement=sum(x['loss'] for x in metric)-sum(x['loss'] for x in best_metric);point,metric=best,best_metric;print(width,iteration+1,[x['loss'] for x in metric],point[23:].tolist(),flush=True)
  if improvement<1e-6:break
 fg=[]
 for s,G in zip(studies,images(point)):
  composite=s.apply_foreground(G.copy());x0,y0,_,_=s.crop
  for layer in s.case['foreground_layers']:
   if layer.get('fit_style',True):
    a,b,c,d=layer['box'];fg.append(float(np.mean((composite[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2)
 row=dict(width=width,parameters=point.tolist(),scores=metric,foreground_mse=fg);results.append(row)
 for i,(s,G) in enumerate(zip(studies,images(point))):s.comparison(G,r/f'probe-joint-linear-reflection-{width}-{i}.png',p)
(r/'joint-linear-reflection-probe.json').write_text(json.dumps(dict(scope='Exploratory, not a counted pass or adopted renderer. Full native loss/glass gates protect both references.',baseline=baseline,rows=results),indent=2)+'\n')
