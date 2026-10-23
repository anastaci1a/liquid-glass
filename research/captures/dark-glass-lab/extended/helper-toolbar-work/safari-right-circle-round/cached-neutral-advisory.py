"""Analytic continuous g/b basis from saved native baseline ONLY, not a fit/test."""
import os,json,sys
from pathlib import Path
import numpy as np
os.umask(0o002)
R=Path('/evidence/extended/helper-toolbar-work/safari-right-circle-round');D=R/'neutral-baseline';a=np.load(D/'baseline-native-arrays.npz');sys.path.insert(0,str(D/'code'))
from extended_fit import Study
s=Study(D/'inputs/a');M=a['material'];C=a['complete'];alpha=a['alpha'];fg=np.zeros(alpha.shape,np.float32)
for box,coverage,color in s.foreground_layers:
 l,t,r,b=box;x0,y0,_,_=s.crop;fg[t-y0:b-y0,l-x0:r-x0]=coverage
k=alpha*(1-fg);dm_b=np.ones_like(M);dm_g=M.copy();dc_b=np.repeat(k[...,None],3,2);dc_g=M*k[...,None]
rows={}
for name,maskkey,full in [('glass','glass_mask',False),('rim','rim_mask',False),('held','held_mask',False),('interior','interior_mask',False),('glyph','glyph_mask',True),('exterior','exterior_mask',True),('full_visible_exterior','full_visible_exterior_mask',True)]:
 mask=a[maskkey];base=C if full else M;err=(base.astype(float)-s.target_crop.astype(float))*255;basis=[dc_g,dc_b] if full else [dm_g,dm_b];der=np.stack([x.astype(float)[mask].ravel()*255 for x in basis],1);e=err[mask].ravel();rows[name]=dict(pixels=int(mask.sum()),signed_rgb=err[mask].mean(0).tolist(),continuous_mse_gradient_g_b=(2*der.T@e/len(e)).tolist(),continuous_mse_hessian_g_b=(2*der.T@der/len(e)).tolist())
rows['weighted_E_squared']=dict(continuous_gradient_g_b=(.7*np.array(rows['glass']['continuous_mse_gradient_g_b'])+.3*np.array(rows['rim']['continuous_mse_gradient_g_b'])).tolist(),continuous_hessian_g_b=(.7*np.array(rows['glass']['continuous_mse_hessian_g_b'])+.3*np.array(rows['rim']['continuous_mse_hessian_g_b'])).tolist())
q=dict(status='ADVISORY_CACHED_LINEAR_NEUTRAL_BASIS_ONLY_NOT_FIT',directions=['common g','common b'],parameters_at_baseline=dict(g=1,b=0),metrics=rows,scope='Continuous unclipped encoded-RGB C=clip(g*S+b). At neutralbaseline defined samples inside0..1, derivative dM/dg=M, dM/db=1; complete derivative carries original alpha and fixed black SVG. Post blur linear in ideal arithmetic.',limits='NOT exact floating-point finite-native derivative, no candidate or optimum predicted/scored. SSIM nonlinear/rounding and native strict guards still require actual authorized native trial. No material calibration, map/source/glyph/protocol change or scoreepoch.',extra_body_renders=0,material_fits=0,accepted_count=0)
(D/'cached-neutral-advisory.json').write_text(json.dumps(q,indent=2)+'\n');np.savez_compressed(D/'cached-neutral-directions.npz',d_material_g=dm_g,d_material_b=dm_b,d_complete_g=dc_g,d_complete_b=dc_b);print(json.dumps(q))
