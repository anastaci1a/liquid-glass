"""Test an isotropic component of the existing source-derived reflected field.

R(d)*[A(n)+rho*(1-A(n))], rho in[0,1], interpolates directional and
isotropic angular reflection using the SAME radial profile/environment.
C=(1-weight)*transmission+weight*environment; no target-colored outlines.
Shared scalar on both references. Existing geometry/material/sources fixed.
This is an empirical environment proxy, not measured Fresnel reflection.
Exact quadratic native residuals constrain proposals before rendering checks.
"""
import sys,copy,json,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import numpy as np,cv2
from scipy.optimize import minimize_scalar
from extended_fit import Study
from grazing_reflection import layers
from revision_replay import clean_composite
from joint_visible_statistics import visible_masks,measures
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-reflection-floor';out.mkdir(exist_ok=True)
base=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=base['parameters'];co=np.array(base['material']);studies=[Study(root/'paired'/name) for name in ['a','b']];rows=[];fields=[]
previous=json.loads((root/'rev4-ambient-review/hq/verification.json').read_text())['candidate']['observations']
cropbase=json.loads((root/'rev4-ambient-review/crops/visible-crops.json').read_text())['observations']
for i,s in enumerate(studies):
 q=copy.deepcopy(p);q.pop('grazing_reflection');raw=s.render(q,co);w,environment=layers(s,p);iso=copy.deepcopy(p);iso['grazing_reflection']['angular_power']=0.;wi,_=layers(s,iso)
 C=s.render(p,co);assert np.max(abs(C-(raw*(1-w[...,None])+environment*w[...,None])))<1e-7
 delta=(wi-w)[...,None]*(environment-raw);alpha=s.shape_coverage(p);V=clean_composite(s,p,C);masks={'glass':s.valid,'rim':s.rim,**visible_masks(s)};forms={}
 for name,mask in masks.items():
  visible=name not in ['glass','rim'];r=((V if visible else C)-s.target_crop)[mask]*255;d=(delta*alpha[...,None] if visible else delta)[mask]*255
  forms[name]=dict(a=float(np.mean(d*d)),b=float(2*np.mean(r*d)),c=float(np.mean(r*r)))
 forms['loss']={k:.7*forms['glass'][k]+.3*forms['rim'][k] for k in ['a','b','c']}
 assert abs(forms['loss']['c']-previous['AB'[i]]['loss'])<1e-4
 # Every allowed proposal must preserve native full regions. Crop protection
 # stays relative to revision4, preventing accumulated local drift.
 for name,v in forms.items():
  v['limit']=float(cropbase[i]['states'][0][name[5:]]['rgb_rmse_255']**2*1.02**2) if name.startswith('crop_') else v['c']
 rows.append(forms);fields.append((s,C,delta));print('DERIVATIVE','AB'[i],forms['loss']['b'],flush=True)
feasible_hi=1.;bounds=[]
for i,forms in enumerate(rows):
 for name,v in forms.items():
  if name=='loss':continue
  # Convex quadratic and feasible rho=0 give one upper feasible root.
  a,b,c=v['a'],v['b'],v['c']-v['limit']
  if c>1e-4:raise ValueError(('Baseline crop protection violated',i,name,c))
  if a>1e-14:hi=max(0.,(-b+np.sqrt(max(0,b*b-4*a*min(c,0))))/(2*a))
  else:hi=1. if b<=0 else max(0,-c/b)
  feasible_hi=min(feasible_hi,hi);bounds.append(dict(observation='AB'[i],region=name,upper=hi))
def ratio(rho):return max((v['loss']['a']*rho*rho+v['loss']['b']*rho+v['loss']['c'])/v['loss']['c'] for v in rows)
fit=minimize_scalar(ratio,bounds=(0,feasible_hi),method='bounded',options=dict(xatol=1e-12)) if feasible_hi>1e-12 else None
rho=float(fit.x) if fit and fit.fun<ratio(0) else 0.;trials=[]
for t in sorted(set([0.,rho,.1,.25,.5,1.])):
 scores=[]
 for s,C,D in fields:
  im=C+t*D;scores.append({**s.scores(im,include_ssim=False),**measures(s,p,im)})
 ratios=[float(np.sqrt(m['loss']/v['loss']['c'])) for m,v in zip(scores,rows)];allowed=t<=feasible_hi+1e-10
 trials.append(dict(rho=t,ratios=ratios,scores=scores,allowed=allowed,numeric_pass=allowed and max(ratios)<=.995))
report=dict(method=__doc__,baseline='64b970e switch revision5',quadratics=rows,feasible_upper=feasible_hi,limiting_bounds=sorted(bounds,key=lambda r:r['upper'])[:5],best_rho=rho,trials=trials,accepted=False)
(out/'screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['feasible_upper','limiting_bounds','best_rho']}),flush=True)
