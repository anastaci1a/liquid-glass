"""No-reversal optical control, not a recovered physical lens body.

Positive radial increments + monotone cubic interpolation preserve orientation.
This tests whether the observed playback rim can fit without reversed detail.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.interpolate import PchipInterpolator
from scipy.optimize import differential_evolution,minimize
from reproduce import CASES,training_samples,scores
from render import case_geometry,illumination,fit_material,shade

root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['media'];source=cv2.imread(str(folder/'media-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'media-target.png'))[:,:,::-1].astype(np.float32)/255
knots=np.array([0,.25,.5,.7,.85,.93,.97,1]);floor=.001
def mapping(x,y,rates):
 rho=np.hypot(x,y)/case['radius'];m=PchipInterpolator(knots,np.r_[0,np.cumsum(np.diff(knots)*rates)])
 values=m(np.clip(rho,0,1));F=floor*rho+(1-floor)*values
 ratio=np.divide(F,rho,out=np.full_like(rho,floor+(1-floor)*m.derivative()(0)),where=rho>1e-12)
 return x*ratio,y*ratio

xs,ys,x,y,idx,weights=training_samples(case)
px=x.ravel()[idx,None]+np.array([-.25,.25,-.25,.25]);py=y.ravel()[idx,None]+np.array([-.25,-.25,.25,.25]);boundary=case_geometry(case,px,py)
expected=target[ys.flat[idx].astype(int),xs.flat[idx].astype(int)];blurs={}
def sample(x,y,v):
 sigma=round(v[-2]*4)/4
 if sigma not in blurs:blurs[sigma]=cv2.GaussianBlur(source,(0,0),sigma)if sigma else source
 lx,ly=mapping(x,y,np.array(v[:7]));return cv2.remap(blurs[sigma],(lx+960).astype(np.float32),(ly+542).astype(np.float32),cv2.INTER_LINEAR).reshape((*x.shape,3))
def evaluate(v,ret=False):
 a=sample(px,py,v);L=illumination(px,py,case['half'],case['radius'],v[-1],boundary);co,_=fit_material(a,L,expected,weights)
 loss=float(np.mean(((shade(a,L,co).mean(1)-expected)*weights[:,None])**2))
 return (loss,co)if ret else loss
bounds=[(.7,1.3),(.7,1.3),(.3,1.5)]+[(.01,3)]*4+[(0,.5),(1,12)]
for seed in [3401,3402]:
 result=differential_evolution(evaluate,bounds,seed=seed,popsize=7,maxiter=65,polish=False,x0=[1]*7+[.25,4])
 polished=minimize(evaluate,result.x,method='Powell',bounds=bounds,options={'maxiter':45,'ftol':1e-8,'xtol':.0005})
 v=polished.x if polished.fun<result.fun else result.x;loss,co=evaluate(v,True)
 x0,y0,x1,y1=case['crop'];output=np.zeros((y1-y0,x1-x0,3))
 for top in range(y0,y1,24):
  bottom=min(top+24,y1);yy,xx=np.mgrid[top:bottom:.25,x0:x1:.25];xx=xx-.375-960;yy=yy-.375-542
  L=illumination(xx,yy,case['half'],case['radius'],v[-1],case_geometry(case,xx,yy));color=shade(sample(xx,yy,v),L,co)
  output[top-y0:bottom-y0]=color.reshape(bottom-top,4,x1-x0,4,3).mean((1,3))
 stats=scores(output.astype(np.float32),target[y0:y1,x0:x1],case)
 m=PchipInterpolator(knots,np.r_[0,np.cumsum(np.diff(knots)*v[:7])]);rr=np.linspace(0,1,10001)
 f=dict(model='positive-radial-control',rates=v[:7].tolist(),knots=knots.tolist(),sigma=round(v[-2]*4)/4,rim_width=float(v[-1]),material=co.tolist(),fit_loss=loss,scores=stats,seed=seed,min_sampled_radial_derivative=float(np.min(floor+(1-floor)*m.derivative()(rr))),limits='Designed image mapping with positive radial/tangential derivatives; not verified thick-lens geometry. Monotone cubic control has C1 continuity, not globally C2. Same source and material freedom as other fits.')
 cv2.imwrite(str(out/f'media-monotone-{seed}.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/f'media-monotone-{seed}.json').write_text(json.dumps(f,indent=2)+'\n')
 print(seed,stats['all_glass']['rmse'],stats['rim']['rmse'],stats['selection_loss'],f['min_sampled_radial_derivative'],flush=True)
