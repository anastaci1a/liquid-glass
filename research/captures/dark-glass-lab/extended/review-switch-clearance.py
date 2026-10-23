"""Finite-clearance sensitivity with preserved first-order optical power.
Proposal only: same5000fixed points/16Gaussian taps as earlier calibration.
G grows, all nonconstant height terms scale by (G0-t0)/(G-t0); one same physical
surface across references. Tests nonlinear finite-gap effect, no source/shape
changes and no arbitrary coordinate stretch. No new fit/pass.
"""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_euclidean_surface import EuclideanSurfaceStudy
from material_context import effective
from grazing_reflection import layers
from render import shade
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';seed=json.loads((out/'native-settlement.json').read_text());p0=seed['parameters'];co=np.array(seed['material']);rows=[]
for name in ['a','b']:
 s=EuclideanSurfaceStudy(root/'paired'/name);idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];h=np.sqrt(2)*s.kernel_sigma(p0,'post_sigma')/s.L;dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);xx=x[:,None]+dx.ravel();yy=y[:,None]+dy.ravel();target=s.target_crop.reshape(-1,3)[idx];rim=s.rim.ravel()[idx];w,env=layers(s,p0);w=w.ravel()[idx,None];env=env.reshape(-1,3)[idx];vals=[]
 for gap in [p0['euclidean_surface']['gap'],20.,40.,80.]:
  p=copy.deepcopy(p0);q=p['euclidean_surface'];ratio=(q['gap']-q['t0'])/(gap-q['t0']);q['gap']=gap;q['bx']*=ratio;q['by']*=ratio;q['profile']=[a*ratio for a in q['profile']]
  C,J=s.field(xx,yy,p);im=shade(C,J,effective(s,p,co)).mean(1);im=im*(1-w)+env*w;e=(im-target)*255;glass=float(np.mean(e**2));edge=float(np.mean(e[rim]**2));vals.append(dict(gap=gap,height_coefficient_scale=ratio,proposal_E=float(np.sqrt(.7*glass+.3*edge)),glass_rmse=float(np.sqrt(glass)),rim_rmse=float(np.sqrt(edge)),surface=q))
 rows.append(dict(observation=name,proposals=vals))
result=dict(rows=rows,method=__doc__,limits='Fixed-material local sensitivity, not calibrated native scores. Clearance/thickness/IOR are not identified by reference images; arbitrarily large clearance is not an Apple measurement.')
with (out/'clearance-proposal-review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps([{ 'observation':r['observation'],'E':[(v['gap'],v['proposal_E']) for v in r['proposals']]} for r in rows]),flush=True)
