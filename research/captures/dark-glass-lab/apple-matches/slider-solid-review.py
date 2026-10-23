"""Test the provisionally preferred third shape against the real slider input."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,argparse
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.optimize import differential_evolution,minimize
from reproduce import CASES,training_samples,optical_inputs,render,scores
from render import case_geometry,fit_material,shade

ap=argparse.ArgumentParser();ap.add_argument('--transverse',action='store_true');ap.add_argument('--corrected',action='store_true');args=ap.parse_args()
root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['slider'];source=cv2.imread(str(out/'slider-corrected-source.png'if args.corrected else folder/'slider-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'slider-target.png'))[:,:,::-1].astype(np.float32)/255
xs,ys,x,y,idx,weights=training_samples(case);px=x.flat[idx];py=y.flat[idx];boundary=case_geometry(case,px,py);expected=target[ys.flat[idx].astype(int),xs.flat[idx].astype(int)]
def decode(v):return dict(model='solid',parameters=dict(height=v[0],gap=v[1],shoulder=1,ior=v[2],rear=1,beta=.5,crown_x=.6,crown_y=0,cross_curvature=1,cross_section_power=v[3]if args.transverse else 1),sigma=0.,rim_width=4.,ray_bounces=16,intersection_steps=26)
def evaluate(v,ret=False):
 f=decode(v);sample,L,diag=optical_inputs(source,source,case,f,px,py,boundary);co,_=fit_material(sample,L,expected,weights)
 loss=float(np.mean(((shade(sample,L,co)-expected)*weights[:,None])**2))+.25*(diag['untraced_energy_mean']+diag['unknown_background_energy_mean'])
 if ret:f.update(material=co.tolist(),fit_loss=loss,ray_diagnostics=diag);return f
 return loss
bounds=[(.15,2.),(0,2),(1.01,1.4)]+([(1,8)]if args.transverse else [])
seed=(3662 if args.transverse else 3602)if args.corrected else (3661 if args.transverse else 3601);start=[1.2,.2,1.33]+([3.]if args.transverse else [])
result=differential_evolution(evaluate,bounds,seed=seed,popsize=6,maxiter=35,tol=.001,polish=False,x0=start);print('DE',result.fun,result.x.tolist(),flush=True)
polished=minimize(evaluate,result.x,method='Powell',bounds=bounds,options={'maxiter':20,'ftol':1e-7,'xtol':.001});v=polished.x if polished.fun<result.fun else result.x
f=evaluate(v,True);f.update(seed=seed,role='Preferred crown-0.6 shape held fixed; effective height/gap/index fitted. Shape preference is provisional.')
fx=px[:,None]+np.array([-.25,.25,-.25,.25]);fy=py[:,None]+np.array([-.25,-.25,.25,.25]);f['ray_bounces']=32;f['intersection_steps']=30
a,L,diag=optical_inputs(source,source,case,f,fx,fy,case_geometry(case,fx,fy));co,_=fit_material(a,L,expected,weights);f.update(material=co.tolist(),ray_diagnostics=diag)
output=render(source,case,f).astype(np.float32);x0,y0,x1,y1=case['crop'];f['scores']=scores(output,target[y0:y1,x0:x1],case)
stem=(f'slider-transverse-{seed}'if args.transverse else f'slider-solid-{seed}')+('-corrected'if args.corrected else '')
cv2.imwrite(str(out/f'{stem}.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/f'{stem}.json').write_text(json.dumps(f,indent=2)+'\n');print(json.dumps(f,indent=2),flush=True)
