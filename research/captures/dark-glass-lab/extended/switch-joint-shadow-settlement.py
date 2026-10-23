"""Bounded shared shadow profile; analytical RGB opacity quadratics."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize,minimize_scalar
from extended_fit import Study as DeformationStudy
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'joint-native-review';old=json.loads((out/'settled-optical.json').read_text());p=old['parameters'];co=np.asarray(old['material']);base=json.loads((root/'rim-width-review/hq/verification.json').read_text())['candidate']['observations'];states=[]
for name in ['a','b']:
 s=DeformationStudy(root/'paired'/name);im=s.render(p,co);mask=(s.sd>0)&(s.sd<.35);q=copy.deepcopy(p);q['shadow']['opacity']=0.;full=clean_composite(s,q,im);alpha=s.shape_coverage(p);a,b,c,d=s.crop
 states.append(dict(s=s,im=im,mask=mask,x=s.x[mask],y=s.y[mask],K=((1-alpha)[...,None]*s.source[b:d,a:c])[mask]*255,E=(full-s.target_crop)[mask]*255,base=base[name.upper()]['shadow']['rmse']**2))
calls=0;best=None
def evaluate(v):
 global calls,best
 sigma,dx,dy=v;forms=[]
 for r in states:
  *_,(sd,_,_)=r['s'].shape(r['x']-dx,r['y']-dy,p);f=np.exp(-.5*(np.maximum(sd,0)/sigma)**2);K=r['K']*f[:,None];E=r['E']
  forms.append((float(np.mean(K*K)),float(np.mean(K*E)),float(np.mean(E*E)),r['base']))
 def op_loss(op):return max((a*op*op-2*b*op+c)/base for a,b,c,base in forms)
 fit=minimize_scalar(op_loss,bounds=(.04,.10),method='bounded',options=dict(xatol=1e-10));calls+=1
 if best is None or fit.fun<best['loss']:best=dict(loss=float(fit.fun),profile=list(map(float,v)),opacity=float(fit.x))
 if calls%20==0:print('SHADOW',calls,best,flush=True)
 return float(fit.fun)
start=[p['shadow']['sigma'],*p['shadow']['offset']]
fit=minimize(evaluate,start,method='Powell',bounds=[(.07,.105),(-.012,.018),(.085,.115)],options=dict(maxfev=240,xtol=1e-5,ftol=1e-9))
q=copy.deepcopy(p);sigma,dx,dy=best['profile'];q['shadow']=dict(opacity=best['opacity'],sigma=sigma,offset=[dx,dy]);values=[]
for r in states:
 full=clean_composite(r['s'],q,r['im']);values.append(float(np.sqrt(np.mean(((full-r['s'].target_crop)[r['mask']]*255)**2))))
report=dict(parameters=q,material=old['material'],scores=old['scores'],shadow_scores=values,shadow_pass=all(a<=np.sqrt(r['base']) for a,r in zip(values,states)),evaluations=calls,solver_success=bool(fit.success),solver_message=str(fit.message),best=best,bounds=[(.05,.13),(-.025,.025),(.05,.15)],accepted=False,limits='Shared original shadow family, normalized bounds, fixed exterior masks, no target residual copied. Optical metrics unchanged; part of pending geometry revision, not an extra optical pass.')
(out/'shared-shadow-settlement.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT',report['shadow_pass'],values,flush=True)
