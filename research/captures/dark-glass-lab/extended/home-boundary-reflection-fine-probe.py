"""Supplementary geometric rim study. No accepted-state writes/pass counts.

Uniform neutral incident field replaces transmission at grazing edge, bounded
by normalized distance. Empirical, not measured Fresnel/Apple environment.
"""
from pathlib import Path
import json,time,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import permitted
root=Path('/evidence/extended/music-home-vector-corrected/paired');out=root.parent/'boundary-reflection-fine-probe';out.mkdir(exist_ok=True);state=json.loads((root/'accepted.json').read_text());p=state['parameters'];co=np.array(state['material']);studies=[Study(root/n) for n in ['a','b']];start=time.time();parts=[]
for s in studies:
 *_,(sd,_,_)=s.shape(s.x,s.y,p);inside=-sd;mask=(sd<=0)&(sd>-.025);pred=s.render(p,co);parts.append((inside,mask,pred))
cache={};calls=0;best=None

def evaluate(v):
 global calls,best
 key=np.array(v).tobytes()
 if key not in cache:
  a,width=v;metrics=[];contours=[]
  for s,(d,mask,pred) in zip(studies,parts):
   u=np.clip(np.maximum(d,0)/width,0,1);F=a*(1-u**3*(u*(6*u-15)+10));image=(pred*(1-F[...,None])+F[...,None]).astype(np.float32);metrics.append(s.scores(image,include_ssim=False));contours.append(float(np.mean(((image-s.target_crop)[mask]*255)**2)))
  calls+=1;cache.clear();cache[key]=(metrics,contours);oldcontour=[float(np.mean(((pred-s.target_crop)[mask]*255)**2)) for s,(_,mask,pred) in zip(studies,parts)];allowed=permitted(metrics,state['scores']) and all(a<=b for a,b in zip(contours,oldcontour))
  if allowed and (best is None or sum(contours)<sum(best['contour_mse'])):best=dict(strength=float(a),width=float(width),scores=metrics,contour_mse=contours)
 return cache[key]
for w in np.linspace(.004,.008,81):
 for a in np.linspace(.3,1,15):evaluate([a,w])
if best:
 scale=np.mean([m['loss'] for m in state['scores']])
 # Native body and the independently reported unscored contour both protect
 # each background; do not select only by a combined average.
 oldcontour=[float(np.mean(((pred-s.target_crop)[mask]*255)**2)) for s,(_,mask,pred) in zip(studies,parts)]
 def cons(v):
  metrics,contours=evaluate(v);return np.array([z for m,t,c,oldc in zip(metrics,state['scores'],contours,oldcontour) for z in [(t['loss']-m['loss'])/scale,(t['glass']['rmse']**2-m['glass']['rmse']**2)/scale,(oldc-c)/max(1,oldc)]])
 fit=minimize(lambda v:sum(evaluate(v)[1])/sum(oldcontour),[best['strength'],best['width']],method='SLSQP',bounds=[(0,1),(.0001,.05)],constraints=[dict(type='ineq',fun=cons)],options=dict(maxiter=100,ftol=1e-11,eps=1e-5))
 evaluate(fit.x)
report=dict(model='F=a*(1−S(clamp(d/w))), C=(1−F)*C_transmission_after_output_blur+F*[1,1,1]. Shared a/w, distances normalized byL; empirical uniform neutral incident field, not measured Fresnel response.',baseline=state,baseline_contour_mse=[float(np.mean(((pred-s.target_crop)[mask]*255)**2)) for s,(_,mask,pred) in zip(studies,parts)],best=best,calls=calls,seconds=time.time()-start,limits='Private trial against frozen checkpoint. Must recheck any evolving incumbent, source/HQ/material/cache paths before adoption. Contour supplements, never replaces native gates.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(best=best,calls=calls)),flush=True)
