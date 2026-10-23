"""Joint stretch-band/blur refinement; fixed normal profile and source geometry."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.optimize import differential_evolution,minimize
from reproduce import CASES,training_samples,optical_inputs,render,scores
from render import case_geometry,fit_material,shade,spline_basis

root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['regular'];source=cv2.imread(str(folder/'regular-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'regular-target.png'))[:,:,::-1].astype(np.float32)/255
base=json.loads((folder/'regular-tensor.json').read_text());xs,ys,x,y,idx,weights=training_samples(case)
px=x.ravel()[idx,None]+np.array([-.25,.25,-.25,.25]);py=y.ravel()[idx,None]+np.array([-.25,-.25,.25,.25])
boundary=case_geometry(case,px,py);basis=spline_basis(-boundary[0],case['radius']);expected=target[ys.flat[idx].astype(int),xs.flat[idx].astype(int)]
blurs={}
def evaluate(v,ret=False):
 f=copy.deepcopy(base);f['parameters'].update(tangent=v[0],tangent_band=v[1]);f['parameters']['_basis']=basis
 f['sigma']=round(v[2]*4)/4
 if f['sigma']not in blurs:blurs[f['sigma']]=cv2.GaussianBlur(source,(0,0),f['sigma'])
 a,L,_=optical_inputs(source,blurs[f['sigma']],case,f,px,py,boundary)
 co,_=fit_material(a,L,expected,weights);loss=float(np.mean(((shade(a,L,co).mean(1)-expected)*weights[:,None])**2))
 if ret:
  del f['parameters']['_basis'];f['material']=co.tolist();f['fit_loss']=loss;return f
 return loss
bounds=[(.1,.4),(.3,1.),(8,12)]
record=[]
for seed in [3301,3302]:
 result=differential_evolution(evaluate,bounds,seed=seed,popsize=7,maxiter=45,polish=False,x0=[base['parameters']['tangent'],base['parameters']['tangent_band'],base['sigma']])
 polished=minimize(evaluate,result.x,method='Powell',bounds=bounds,options={'maxiter':30,'ftol':1e-8,'xtol':.0005})
 v=polished.x if polished.fun<result.fun else result.x
 f=evaluate(v,True);f.update(seed=seed,role='Tensor map refinement, not a recovered 3D body')
 output=render(source,case,f).astype(np.float32);x0,y0,x1,y1=case['crop'];f['scores']=scores(output,target[y0:y1,x0:x1],case)
 np.save(out/f'regular-profile-{seed}.npy',output);cv2.imwrite(str(out/f'regular-profile-{seed}.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/f'regular-profile-{seed}.json').write_text(json.dumps(f,indent=2)+'\n')
 record.append(f);print(seed,f['parameters']['tangent'],f['parameters']['tangent_band'],f['sigma'],f['scores']['selection_loss'],flush=True)
(out/'regular-profile-search.json').write_text(json.dumps(record,indent=2)+'\n')
