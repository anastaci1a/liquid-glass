"""Saved native quadratic diagnostic; relaxing a constraint here is NOT an acceptance change."""
import sys,json
from pathlib import Path
sys.path[:0]=['/tmp/optics-deps','/tmp/optics-fit-deps']
import numpy as np
from scipy.optimize import minimize
out=Path('/evidence/extended/active-switch/physical-euclidean-surface');D=np.load(out/'cauchy-native-form-01.npz');seed=json.loads((out/'native-settlement.json').read_text());met=seed['scores'];base=seed['baseline'];point=D['point'];scales=D['scales'];forms=[]
for i in range(2):
 f={k:(D[f'{i}_{k}_H'],D[f'{i}_{k}_g']) for k in ['glass','rim','shadow']};f['loss']=(.7*f['glass'][0]+.3*f['rim'][0],.7*f['glass'][1]+.3*f['rim'][1]);forms.append(f)
def value(i,v,k):
 H,g=forms[i][k];b=met[i]['loss'] if k=='loss' else met[i][k]['rmse']**2;d=v[:-1];return b+2*g@d+d@H@d
def bound(k):
 if k==0:return(0,.03)
 j=k-1;return(.05,1.5) if j<3 or j>=20 else(-.8,.8) if j<6 else(-4,4)
ranges=[(max(-1.,(bound(k)[0]-v)/scales[k]),min(1.,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,10)];rows=[]
for shadow in [True,False]:
 keys=['glass','shadow'] if shadow else ['glass']
 def constraints(v):return np.array([a for i,b in enumerate(base) for a in [v[-1]-value(i,v,'loss')/b['loss'],*[max(1.,(met[i][k]['rmse']/b[k]['rmse'])**2)-value(i,v,k)/b[k]['rmse']**2 for k in keys]]])
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(24),max(a['loss']/b['loss'] for a,b in zip(met,base))],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=250,ftol=1e-11))
 rows.append(dict(shadow_guard_used=shadow,success=bool(fit.success),predicted_worst_E_ratio=float(np.sqrt(fit.x[-1])),predicted_shadow_rmse=[float(np.sqrt(value(i,fit.x,'shadow'))) for i in range(2)],proposed_delta=float(scales[0]*fit.x[0])))
result=dict(rows=rows,limits='Diagnostic local model only; original exterior nonregression remains mandatory. No native candidate, fit adoption or pass.')
with (out/'shadow-bottleneck-review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result),flush=True)
