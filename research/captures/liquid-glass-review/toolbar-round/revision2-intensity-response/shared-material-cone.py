"""One shared-contrast/bias local feasibility audit, not a native material fit."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from scipy.optimize import linprog
from PIL import Image
import toolbar_candidate as m
r=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-intensity-response');pkg=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((pkg/'recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];T=np.asarray(Image.open(pkg/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=np.asarray(Image.open(pkg/'inputs/source.png'),float)[y0:y1,x0:x1]/255;C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');A=np.load(r/'affine-design.npy',mmap_mode='r');g=np.load(r/'gamma-derivative.npy');D=np.stack([g*np.log(1.25),np.asarray(A[...,:3]).sum(-1)*.03,np.asarray(A[...,3:6]).sum(-1)*.015,np.asarray(A[...,20:23]).sum(-1)*.03],axis=-1);mask=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fg=np.load(pkg/'derived-foreground.npz');shadow=m.gaussian_coverage_shadow(case,p);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);df=D*a[...,None,None];rows=[]
def metric(R,F):return np.mean(2*R[...,None]*F,axis=tuple(range(R.ndim)))*255**2
for name in ['glass','rim']:rows.append(metric((C-T)[mask[name]],D[mask[name]]))
rows.append(metric((full-T)[mask['exterior']],df[mask['exterior']]))
for layer in p['foreground_layers']:
 aa=fg[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa;df=df*(1-aa[...,None])
for layer in p['foreground_layers']:
 b,c,d,e=layer['box'];sl=(slice(c-y0,e-y0),slice(b-x0,d-x0));rows.append(metric((full-T)[sl],df[sl]))
J=np.array(rows);scales=np.maximum(np.linalg.norm(J,axis=1),1e-20);objective=.7*J[0]+.3*J[1];fit=linprog(objective,A_ub=J/scales[:,None],b_ub=np.zeros(5),bounds=[(-.2,.2)]*4,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9});out={'parameters':['loggamma/log1.25','shared_rim_gain_delta/.03','shared_bias_delta/.015','shared_core_gain_delta/.03'],'local_trust_box':[-.2,.2],'MSE_Jacobian':J.tolist(),'objective_gradient':objective.tolist(),'LP_success':bool(fit.success),'message':fit.message,'normalized_step':fit.x.tolist() if fit.success else None,'predicted_objective_change':float(fit.fun) if fit.success else None,'predicted_guard_changes':(J@fit.x).tolist() if fit.success else None,'native_fit_or_gain':False,'limits':'Local analytical cone under ONE shared curve+three existing common material offsets. No global infeasibility/optimality claim; actual nonlinear controls/native scores required. Wider23coefficient fits not searched.'};(r/'shared-material-cone.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
