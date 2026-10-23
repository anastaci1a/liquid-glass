"""Convex closed rotational body: quiet center, variable rim, two interfaces."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.optimize import differential_evolution,minimize
from reproduce import CASES,training_samples,optical_inputs,render,scores
from render import case_geometry,fit_material,shade

ap=argparse.ArgumentParser();ap.add_argument('--broad',action='store_true');args=ap.parse_args()
root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['media'];source=cv2.imread(str(folder/'media-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'media-target.png'))[:,:,::-1].astype(np.float32)/255
xs,ys,x,y,idx,weights=training_samples(case);px=x.flat[idx];py=y.flat[idx];boundary=case_geometry(case,px,py);expected=target[ys.flat[idx].astype(int),xs.flat[idx].astype(int)]
blur=cv2.GaussianBlur(source,(0,0),.5)
def decode(v,bounces=12):return dict(model='solid',parameters=dict(height=v[0],gap=v[1],shoulder=v[2],ior=v[3],rear=1,beta=.5,crown_x=0,crown_y=0,cross_curvature=0),sigma=.5,rim_width=4.,ray_bounces=bounces,intersection_steps=26)
def evaluate(v,ret=False):
 f=decode(v);sample,L,diag=optical_inputs(source,blur,case,f,px,py,boundary);co,_=fit_material(sample,L,expected,weights)
 loss=float(np.mean(((shade(sample,L,co)-expected)*weights[:,None])**2))+.25*(diag['untraced_energy_mean']+diag['unknown_background_energy_mean'])
 if ret:f.update(material=co.tolist(),fit_loss=loss,ray_diagnostics=diag);return f
 return loss
bounds=[(.2,3),(0,1),(1,60),(1.001,1.45)]if args.broad else [(.5,2),(0,1),(1,12),(1.02,1.4)]
seed=3561 if args.broad else 3501
start=[.7,.07,12,1.0345]if args.broad else [1,.1,2,1.33]
result=differential_evolution(evaluate,bounds,seed=seed,popsize=7 if args.broad else 6,maxiter=65 if args.broad else 25,tol=.001,polish=False,x0=start)
print('DE',result.fun,result.x.tolist(),flush=True)
polished=minimize(evaluate,result.x,method='Powell',bounds=bounds,options={'maxiter':15,'ftol':1e-7,'xtol':.001})
v=polished.x if polished.fun<result.fun else result.x;f=evaluate(v,True);f.update(seed=seed,role='Convex closed-body comparator; no recovered Apple geometry')
# Refit material with 2x2 integration and a longer path series for the final.
fx=px[:,None]+np.array([-.25,.25,-.25,.25]);fy=py[:,None]+np.array([-.25,-.25,.25,.25]);f['ray_bounces']=24;f['intersection_steps']=30
a,L,diag=optical_inputs(source,blur,case,f,fx,fy,case_geometry(case,fx,fy));co,_=fit_material(a,L,expected,weights);f.update(material=co.tolist(),ray_diagnostics=diag)
output=render(source,case,f).astype(np.float32);x0,y0,x1,y1=case['crop'];f['scores']=scores(output,target[y0:y1,x0:x1],case)
cv2.imwrite(str(out/f'media-solid-{seed}.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/f'media-solid-{seed}.json').write_text(json.dumps(f,indent=2)+'\n');print(json.dumps(f,indent=2),flush=True)
