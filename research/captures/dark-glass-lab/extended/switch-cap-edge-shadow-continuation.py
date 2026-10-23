"""Existing shadow opacity settlement; only widen profile search if needed."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from scipy.optimize import minimize_scalar,minimize
from switch_cap_edge_model import CapEdgeStudy
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'rev3-cap-edge-review';old=json.loads((out/'settled-optical.json').read_text());p=old['parameters'];co=np.array(old['material']);base=json.loads((root/'joint-native-review/hq/verification.json').read_text())['candidate']['observations'];states=[]
for name in ['a','b']:
 s=CapEdgeStudy(root/'paired'/name);im=s.render(p,co);mask=(s.sd>0)&(s.sd<.35);q=copy.deepcopy(p);q['shadow']['opacity']=0.;full=clean_composite(s,q,im);alpha=s.shape_coverage(p);a,b,c,d=s.crop
 states.append(dict(s=s,im=im,mask=mask,x=s.x[mask],y=s.y[mask],K=((1-alpha)[...,None]*s.source[b:d,a:c])[mask]*255,E=(full-s.target_crop)[mask]*255,base=base[name.upper()]['shadow']['rmse']**2))
calls=0;best=None
bounds=[(.09,.18),(-.008,.012),(.10,.20)]
def evaluate(v):
 global calls,best
 sigma,dx,dy=v;forms=[]
 for r in states:
  *_,(sd,_,_)=r['s'].shape(r['x']-dx,r['y']-dy,p);f=np.exp(-.5*(np.maximum(sd,0)/sigma)**2);K=r['K']*f[:,None];E=r['E']
  forms.append((float(np.mean(K*K)),float(np.mean(K*E)),float(np.mean(E*E)),r['base']))
 def loss(op):return max((a*op*op-2*b*op+c)/base for a,b,c,base in forms)
 fit=minimize_scalar(loss,bounds=(.04,.10),method='bounded',options=dict(xatol=1e-10));calls+=1
 if best is None or fit.fun<best['loss']:best=dict(loss=float(fit.fun),profile=list(map(float,v)),opacity=float(fit.x))
 return float(fit.fun)
previous=json.loads((out/'shadow-initial-summary.json').read_text());start=[previous['shadow']['sigma'],*previous['shadow']['offset']];initial=evaluate(start);shape_search=True;fit=None
if shape_search:fit=minimize(evaluate,start,method='Powell',bounds=bounds,options=dict(maxfev=700,xtol=1e-5,ftol=1e-9))
q=copy.deepcopy(p);sigma,dx,dy=best['profile'];q['shadow']=dict(opacity=best['opacity'],sigma=sigma,offset=[dx,dy]);values=[]
for r in states:
 full=clean_composite(r['s'],q,r['im']);values.append(float(np.sqrt(np.mean(((full-r['s'].target_crop)[r['mask']]*255)**2))))
report=dict(parameters=q,material=old['material'],scores=old['scores'],shadow_scores=values,shadow_pass=all(a<=np.sqrt(r['base']) for a,r in zip(values,states)),evaluations=calls,shape_search=shape_search,best=best,shape_bounds=bounds if shape_search else None,opacity_bounds=[.04,.10],solver_success=bool(fit.success) if fit is not None else True,accepted=False,limits='Same shared generated shadow family. Optical metrics unchanged; this is part of the pending optical revision, not a separate pass.')
(out/'shadow-continuation.json').write_text(json.dumps(report,indent=2)+'\n');(out/'candidate.json').write_text(json.dumps(dict(parameters=q,material=old['material'],parameter_length_reference=216.5,units=old['units']),indent=2)+'\n');print(json.dumps(dict(pass_shadow=report['shadow_pass'],values=values,shape_search=shape_search,profile=q['shadow'],calls=calls)),flush=True)
