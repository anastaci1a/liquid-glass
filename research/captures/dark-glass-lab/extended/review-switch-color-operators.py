"""Frozen-coefficient operator-isolation proposal, not a new fit or score pass.
Ordinary source blur, ordinary output blur and directional RGB mixing are
separate operators. Actual index dispersion remains the same in all variants.
"""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_cauchy_surface import CauchySurfaceStudy
from material_context import effective
from grazing_reflection import layers
from render import shade
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';seed=json.loads((out/'cauchy-native-settlement.json').read_text());co=np.array(seed['material']);p0=seed['parameters'];rows=[]
variants=[('current',False,False,False),('no-source-Gaussian',True,False,False),('no-output-Gaussian',False,True,False),('no-ordinary-Gaussian',True,True,False),('no-directional-mixture',False,False,True),('spectral-only-transmission',True,True,True)]
for name in ['a','b']:
 s=CauchySurfaceStudy(root/'paired'/name);idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];target=s.target_crop.reshape(-1,3)[idx];rim=s.rim.ravel()[idx];w,env=layers(s,p0);w=w.ravel()[idx,None];env=env.reshape(-1,3)[idx];vals=[]
 for label,no_source,no_output,no_directional in variants:
  p=copy.deepcopy(p0)
  if no_source:p['sigma']=0.
  if no_output:p['post_sigma']=0.
  if no_directional:p['directional_transmission']['strength']=0.
  h=np.sqrt(2)*s.kernel_sigma(p,'post_sigma')/s.L
  taps=[-h,0,0,h] if h else [0.];dx,dy=np.meshgrid(taps,taps);C,J=s.field(x[:,None]+dx.ravel(),y[:,None]+dy.ravel(),p)
  im=shade(C,J,effective(s,p,co)).mean(1);im=im*(1-w)+env*w;e=(im-target)*255;glass=float(np.mean(e**2));edge=float(np.mean(e[rim]**2));vals.append(dict(variant=label,proposal_E=float(np.sqrt(.7*glass+.3*edge)),glass_rmse=float(np.sqrt(glass)),rim_rmse=float(np.sqrt(edge))))
 rows.append(dict(observation=name,proposals=vals))
result=dict(rows=rows,seed=seed['parameters'],method=__doc__,limits='5000fixedpoints with16Gaussian quadrature taps, or one central tap without output blur. Not native filtering/supersampling or a final acceptance comparison. Material/source/shape unchanged, no new calibration/pass.')
with (out/'color-operator-review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(rows),flush=True)
