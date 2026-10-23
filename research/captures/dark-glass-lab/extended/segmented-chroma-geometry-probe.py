"""Sharp ray-map calibration from red-text boundaries, not RGB blur fitting.

Gaussian pyramids are registration objectives only. Every displayed/scored
render keeps both renderer blur parameters atZERO, including intermediate rows.
"""
from pathlib import Path
import sys,json,copy,time,hashlib
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import least_squares
from extended_fit import Study
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'chroma-geometry-probe';out.mkdir(exist_ok=True)
class Prism(Study):
 def geometry_field(self,x,y,p):
  X,Y,d,J=super().geometry_field(x,y,p);return X+p.get('prism_x',0.),Y+p.get('prism_y',0.),d,J
A=Prism(folder);B=Prism(folder/'second-observation');old=json.loads((folder/'accepted.json').read_text());rows=[]
source=np.clip((A.source[:,:,0]-A.source[:,:,1])/.65,0,1).astype(np.float32);target=np.clip((A.target[:,:,0]-A.target[:,:,1])/.65,0,1).astype(np.float32)
# A fixed mixture of general and text-neighborhood samples. This changes only
# optimization sampling; native scoring remains exactly the frozen protocol.
rng=np.random.default_rng(222);near=cv2.dilate((target>.05).astype(np.uint8),np.ones((21,21),np.uint8));a,b,c,d=A.crop;general=np.flatnonzero(A.valid);special=np.flatnonzero(A.valid&(near[b:d,a:c]>0));rng.shuffle(general);rng.shuffle(special);idx=np.unique(np.r_[general[:2500],special[:3500]]);x=A.x.ravel()[idx];y=A.y.ravel()[idx]
keys=[*[f'c{i}' for i in range(7)],'core_x','core_y','prism_x','prism_y','tangent','tangent_band','coupling','cap_normal_gain','cap_tangent_fade','cap_join_width'];calls=0
for seed,file in [('retained',folder/'clear-local-probe/retained-sharp-8.json'),('measured',folder/'clear-local-probe/measured-outline-1.json')]:
 p=copy.deepcopy(json.loads(file.read_text())['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.,prism_x=0.,prism_y=0.)
 for level,sigma in enumerate([6.,3.,1.5,.5,0.],1):
  S=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;T=cv2.GaussianBlur(target,(0,0),sigma) if sigma else target;expected=T[b:d,a:c].ravel()[idx];start=time.time();calls=0
  bounds=[(-.5,.5) if k.startswith('prism') else A.parameter_bounds(k) for k in keys];lo,hi=np.array(bounds).T
  def residual(v):
   global calls
   calls+=1;q={**p,**dict(zip(keys,map(float,v)))};X,Y,*_=A.geometry_field(x,y,q);alpha=cv2.remap(S,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel();return (alpha-expected).astype(np.float64)
  def jac(v):
   # Absolute0.1-native-pixel map-scale perturbation clears lookup quantization.
   h=.0007;J=np.empty((len(idx),len(keys)))
   for i in range(len(keys)):
    upper=v.copy();lower=v.copy();upper[i]=min(hi[i],v[i]+h);lower[i]=max(lo[i],v[i]-h);J[:,i]=(residual(upper)-residual(lower))/(upper[i]-lower[i])
   return J
  fit=least_squares(residual,np.clip([p[k] for k in keys],lo+1e-9,hi-1e-9),jac=jac,bounds=(lo,hi),x_scale='jac',max_nfev=100,ftol=1e-9,xtol=1e-8,gtol=1e-8);p.update(zip(keys,map(float,fit.x)));_,co=A.fit(p);scores=[q.scores(q.render(p,co)) for q in [A,B]];valid=[supported(q,coverage_report(q,p)) for q in [A,B]];row=dict(seed=seed,level=level,registration_objective_sigma=sigma,renderer_sigma=0.,renderer_post_sigma=0.,parameters=p.copy(),material=co.tolist(),scores=scores,supported=valid,beats_published_A=scores[0]['loss']<=old['scores']['loss'] and scores[0]['glass']['rmse']<=old['scores']['glass']['rmse'],evaluations=calls,registration_loss=float(np.mean(fit.fun**2)),seconds=time.time()-start);rows.append(row);(out/f'{seed}-{level}.json').write_text(json.dumps(row,indent=2)+'\n');A.comparison(A.render(p,co),out/f'{seed}-{level}.png',p,context_completed=True);print(json.dumps(dict(seed=seed,level=level,objective_sigma=sigma,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],prism=[p['prism_x'],p['prism_y']],beats_published=row['beats_published_A'],supported=valid,calls=calls)),flush=True)
(out/'report.json').write_text(json.dumps(dict(rows=rows,baseline=old,limits='No accepted/source mutation. Registration pyramids do not add blur to any rendered output. Red-boundary geometry objective is separate from final frozen RGB/native gates. Prismatic term is an empirical global phase-gradient hypothesis; not an identified Apple geometry.'),indent=2)+'\n')
