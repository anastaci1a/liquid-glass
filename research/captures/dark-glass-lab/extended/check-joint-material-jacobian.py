import sys,json,time,gc
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from paired_fit import Cached
from material_local import statistics as original_statistics
from joint_material_jacobian import material_channels,statistics
root=Path('/evidence/extended/active-switch');out=root/'joint-jacobian-check';out.mkdir(exist_ok=True)
r=json.loads((root/'joint-native-review/candidate.json').read_text());co=np.array(r['material']);rng=np.random.default_rng(312221);directions=rng.normal(size=(3,23));directions/=np.linalg.norm(directions,axis=1)[:,None];records=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);cache=Cached(s,r['parameters']);t=time.time();derivatives=np.empty((3,cache.H,cache.W,3),np.float32)
 for channel,F in material_channels(cache,co):derivatives[...,channel]=np.moveaxis(F@directions.T,-1,0)
 analytic_seconds=time.time()-t;comparisons=[]
 for k,d in enumerate(directions):
  eps=2e-4;t=time.time();fd=(cache.render(co+eps*d)-cache.render(co-eps*d))/(2*eps)
  diff=(derivatives[k]-fd)[s.valid].astype(float);den=fd[s.valid].astype(float)
  relative=float(np.linalg.norm(diff)/np.linalg.norm(den));comparisons.append(dict(direction=k,relative_l2=relative,max_abs=float(abs(diff).max()),finite_seconds=time.time()-t));assert relative<.005,(name,k,relative)
 t=time.time();a=statistics(cache,co,[],np.ones(23));analytic_form_seconds=time.time()-t;t=time.time();b=original_statistics(cache,co);original_seconds=time.time()-t
 err=max(float(np.max(abs(aa-bb))) for key in a for aa,bb in zip(a[key],b[key]));assert err<1e-8,err
 row=dict(observation=name.upper(),directional_checks=comparisons,analytic_three_direction_seconds=analytic_seconds,forms_max_abs_difference=err,analytic_form_seconds=analytic_form_seconds,original_form_seconds=original_seconds);records.append(row);print(json.dumps(row),flush=True);del cache,s,derivatives;gc.collect()
(out/'verification.json').write_text(json.dumps(dict(passed=True,method='Reuse exact public clipped-affine material derivatives in a joint Jacobian. Optical columns retain native finite differences. Full nonlinear output still decides acceptance.',observations=records),indent=2)+'\n')
