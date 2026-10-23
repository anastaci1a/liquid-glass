"""Preferred longitudinal shape with independent transverse profile, flat exit."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import differential_evolution,minimize
from reproduce import CASES,training_samples,optical_inputs,render,scores
from render import case_geometry,fit_material,shade
root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['slider'];source=cv2.imread(str(folder/'slider-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'slider-target.png'))[:,:,::-1].astype(np.float32)/255
xs,ys,x,y,idx,weights=training_samples(case);px=x.ravel()[idx,None]+np.array([-.25,.25,-.25,.25]);py=y.ravel()[idx,None]+np.array([-.25,-.25,.25,.25]);expected=target[ys.flat[idx].astype(int),xs.flat[idx].astype(int)];boundary=case_geometry(case,px,py)
def decode(v):return dict(model='surface',parameters=dict(height=v[0],gap=v[1],cross_section_power=v[2],ior=1.33,beta=.5,crown_x=.6,crown_y=0,cross_curvature=1,shoulder=1),sigma=0.,rim_width=v[3])
def evaluate(v,ret=False):
 f=decode(v);sample,L,_=optical_inputs(source,source,case,f,px,py,boundary);co,_=fit_material(sample,L,expected,weights);loss=float(np.mean(((shade(sample,L,co).mean(1)-expected)*weights[:,None])**2))
 if ret:f.update(material=co.tolist(),fit_loss=loss);return f
 return loss
bounds=[(.01,1.8),(0,1.5),(1,10),(1,12)]
for seed in [3701,3702]:
 result=differential_evolution(evaluate,bounds,seed=seed,popsize=7,maxiter=65,tol=.0005,polish=False,x0=[.5,.2,3,4])
 polish=minimize(evaluate,result.x,method='Powell',bounds=bounds,options={'maxiter':35,'ftol':1e-8,'xtol':.0005});v=polish.x if polish.fun<result.fun else result.x;f=evaluate(v,True);f.update(seed=seed,role='Preferred longitudinal crown, variable transverse curvature, smooth front with flat exit; no glass blur')
 output=render(source,case,f).astype(np.float32);x0,y0,x1,y1=case['crop'];f['scores']=scores(output,target[y0:y1,x0:x1],case)
 cv2.imwrite(str(out/f'slider-front-{seed}.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/f'slider-front-{seed}.json').write_text(json.dumps(f,indent=2)+'\n');print(seed,f['parameters'],f['scores']['all_glass'],f['scores']['rim'],flush=True)
