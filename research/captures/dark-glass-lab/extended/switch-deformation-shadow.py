"""One shared generated-shadow opacity fit, keeping optical proposal immutable."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize_scalar
from switch_deformation_model import DeformationStudy
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'deformation-review';candidate=json.loads((out/'minimax.json').read_text());old=json.loads((root/'rim-width-review/minimax.json').read_text());p=candidate['parameters'];co=np.asarray(candidate['material']);baseline=json.loads((root/'rim-width-review/hq/verification.json').read_text())['candidate']['observations'];rows=[];products=[]
for name in ['a','b']:
    s=DeformationStudy(root/'paired'/name);im=s.render(p,co);mask=(s.sd>0)&(s.sd<.35)
    q=copy.deepcopy(p);q['shadow']['opacity']=0.;A=clean_composite(s,q,im)
    q['shadow']['opacity']=1.;B=clean_composite(s,q,im);K=(A-B)[mask].astype(float)*255;E=(A-s.target_crop)[mask].astype(float)*255
    aa=float(np.mean(K*K));bb=float(np.mean(K*E));cc=float(np.mean(E*E));limit=baseline[name.upper()]['shadow']['rmse']**2
    disc=bb*bb-aa*(cc-limit);interval=None if disc<0 else [(bb-np.sqrt(disc))/aa,(bb+np.sqrt(disc))/aa]
    rows.append(dict(observation=name,quadratic=[aa,bb,cc],baseline_limit_squared=limit,nonregression_opacity_interval=interval));products.append((s,im,mask))
def objective(op):return max((r['quadratic'][0]*op*op-2*r['quadratic'][1]*op+r['quadratic'][2])/r['baseline_limit_squared'] for r in rows)
fit=minimize_scalar(objective,bounds=(0,.2),method='bounded',options=dict(xatol=1e-10));q=copy.deepcopy(p);q['shadow']['opacity']=float(fit.x);observed=[]
for (s,im,mask),row in zip(products,rows):
    full=clean_composite(s,q,im);value=float(np.sqrt(np.mean(((full-s.target_crop)[mask]*255)**2)));observed.append(value)
result=dict(analytic_diagnostics=rows,new_opacity=float(fit.x),old_opacity=p['shadow']['opacity'],actual_shadow_rmse=observed,passed=all(v<=np.sqrt(r['baseline_limit_squared']) for v,r in zip(observed,rows)),parameters=q,material=candidate['material'],scores=candidate['scores'],accepted=False,limits='Same generated footprint-shadow model, one shared neutral opacity fitted on frozen exterior. No target residual copied. Optical score is unchanged; this is part of the pending optical revision, not another pass.')
(out/'shadow-refit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
