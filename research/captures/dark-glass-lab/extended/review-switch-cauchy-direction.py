"""Reuse saved native local statistics; no new renders or acceptance claims."""
import sys,json
from pathlib import Path
sys.path[:0]=['/tmp/optics-deps','/tmp/optics-fit-deps']
import numpy as np
from scipy.optimize import minimize
out=Path('/evidence/extended/active-switch/physical-euclidean-surface');data=np.load(out/'cauchy-native-form-01.npz');seed=json.loads((out/'native-settlement.json').read_text());met=seed['scores'];base=seed['baseline'];point=data['point'];scales=data['scales'];forms=[]
for i in range(2):
 f={name:(data[f'{i}_{name}_H'],data[f'{i}_{name}_g']) for name in ['glass','rim','shadow']};f['loss']=(.7*f['glass'][0]+.3*f['rim'][0],.7*f['glass'][1]+.3*f['rim'][1]);forms.append(f)
def value(i,v,kind):
 H,g=forms[i][kind];b=met[i]['loss'] if kind=='loss' else met[i][kind]['rmse']**2;d=v[:-1];return b+2*g@d+d@H@d
def constraints(v):return np.array([a for i,b in enumerate(base) for a in [v[-1]-value(i,v,'loss')/b['loss'],*[max(1.,(met[i][k]['rmse']/b[k]['rmse'])**2)-value(i,v,k)/b[k]['rmse']**2 for k in ['glass','shadow']]]])
def bound(k):
 if k==0:return (0.,.03)
 j=k-1;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
ranges=[(max(-1.,(bound(k)[0]-v)/scales[k]),min(1.,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)];rows=[]
for free in [False,True]:
 b=ranges.copy()
 if not free:b[0]=(0,0)
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(24),max(a['loss']/b['loss'] for a,b in zip(met,base))],method='SLSQP',bounds=b,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 rows.append(dict(dispersion_free=free,success=bool(fit.success),predicted_worst_E_ratio=float(np.sqrt(fit.x[-1])),proposed_delta=float(scales[0]*fit.x[0]),minimum_constraint=float(constraints(fit.x).min())))
H=sum(f['loss'][0]/b['loss'] for f,b in zip(forms,base));rank=[]
for cutoff in [1e-6,1e-8,1e-10,1e-12]:
 rem=H[0,0]-H[0,1:]@np.linalg.pinv(H[1:,1:],rcond=cutoff)@H[1:,0];rank.append(dict(pseudoinverse_cutoff=cutoff,dispersion_derivative_energy_outside_material_span_fraction=float(rem/H[0,0])))
result=dict(local_models=rows,derivative_independence=rank,fixed_material_loss_slopes=[float(2*f['loss'][1][0]) for f in forms],limits='Saved local clipped-affine/quadratic approximation only. Not native trial scores, a proof of attainable gain or a new pass. Whole-image nonlinear/source checks still required.')
with (out/'cauchy-direction-review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result),flush=True)
