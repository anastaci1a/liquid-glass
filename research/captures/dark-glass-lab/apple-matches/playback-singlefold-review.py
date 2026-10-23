"""Single-turn radial phase-map control; no outer return/mirroring strip.

An integrable radial image map, not a verified thick-lens body. It preserves
the quiet center and tests the unwanted OUTER return separately from inversion.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import differential_evolution,minimize
from reproduce import CASES,training_samples,scores
from render import case_geometry,illumination,fit_material,shade
root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['media'];source=cv2.imread(str(folder/'media-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'media-target.png'))[:,:,::-1].astype(np.float32)/255
def mapping(x,y,v):
 r=np.hypot(x,y);d=245-r;A=v[0]*245;b=v[1]*245;u=np.clip(1-d/b,0,1);a=A*u**v[2]
 ratio=np.divide(r-a,r,out=np.ones_like(r),where=r>1e-12);return x*ratio,y*ratio
xs,ys,x,y,idx,weights=training_samples(case);px=x.ravel()[idx,None]+np.array([-.25,.25,-.25,.25]);py=y.ravel()[idx,None]+np.array([-.25,-.25,.25,.25]);boundary=case_geometry(case,px,py);expected=target[ys.flat[idx].astype(int),xs.flat[idx].astype(int)];blurs={}
def sample(x,y,v):
 sigma=round(v[3]*4)/4
 if sigma not in blurs:blurs[sigma]=cv2.GaussianBlur(source,(0,0),sigma)if sigma else source
 lx,ly=mapping(x,y,v);return cv2.remap(blurs[sigma],(lx+960).astype(np.float32),(ly+542).astype(np.float32),cv2.INTER_LINEAR).reshape((*x.shape,3))
def evaluate(v,ret=False):
 a=sample(px,py,v);L=illumination(px,py,case['half'],245,v[4],boundary);co,_=fit_material(a,L,expected,weights);loss=float(np.mean(((shade(a,L,co).mean(1)-expected)*weights[:,None])**2))
 return (loss,co)if ret else loss
bounds=[(.05,.9),(.02,.4),(2.1,8),(0,.5),(1,12)]
for seed in [3461,3462]:
 result=differential_evolution(evaluate,bounds,seed=seed,popsize=7,maxiter=80,tol=.0005,polish=False,x0=[.6,.12,3,.25,4]);polish=minimize(evaluate,result.x,method='Powell',bounds=bounds,options={'maxiter':35,'ftol':1e-8,'xtol':.0005});v=polish.x if polish.fun<result.fun else result.x;loss,co=evaluate(v,True)
 x0,y0,x1,y1=case['crop'];output=np.zeros((y1-y0,x1-x0,3))
 for top in range(y0,y1,24):
  bottom=min(top+24,y1);yy,xx=np.mgrid[top:bottom:.25,x0:x1:.25];xx=xx-.375-960;yy=yy-.375-542;L=illumination(xx,yy,case['half'],245,v[4],case_geometry(case,xx,yy));C=shade(sample(xx,yy,v),L,co);output[top-y0:bottom-y0]=C.reshape(bottom-top,4,x1-x0,4,3).mean((1,3))
 stats=scores(output.astype(np.float32),target[y0:y1,x0:x1],case);d=np.linspace(0,245,20001);u=np.clip(1-d/(v[1]*245),0,1);derivative=1-v[0]*v[2]/v[1]*u**(v[2]-1)
 f=dict(model='single-turn-phase-control',parameters=dict(amplitude=float(v[0]),band=float(v[1]),power=float(v[2])),sigma=round(v[3]*4)/4,rim_width=float(v[4]),material=co.tolist(),fit_loss=loss,scores=stats,seed=seed,outer_source_derivative=float(derivative[0]),sampled_derivative_sign_changes=int(np.count_nonzero(np.diff(np.sign(derivative)))),limits='Radial phase-map approximation with one or zero derivative sign changes, no outer return. It can retain an inverted rim; this distinguishes removal of the outer mirrored strip from global noninversion. No recovered solid claim.')
 cv2.imwrite(str(out/f'media-singlefold-{seed}.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/f'media-singlefold-{seed}.json').write_text(json.dumps(f,indent=2)+'\n');print(seed,stats['all_glass']['rmse'],stats['rim']['rmse'],stats['selection_loss'],f['parameters'],flush=True)
