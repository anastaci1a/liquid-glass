"""Conservative glass-error intervals for unknown RGB in a fixed input canvas.

Conditions: source-independent geometry, positive gamma, fixed source-context
material, nonnegative sampled-color gain, positive filtering/subpixel weights.
Known pixels stay exact; every undefined pixel may vary independently in[0,1].
This does NOT bound errors in known recovery/registration/geometry or Apple.
"""
from pathlib import Path
import json,copy
from collections import OrderedDict
import cv2,numpy as np
from extended_fit import Study
from material_context import affine,footprint,effective
root=Path('/evidence/extended/music-home-vector-corrected/paired');out=root.parent/'source-input-interval';out.mkdir(exist_ok=True);state=json.loads((root/'accepted.json').read_text());p=state['parameters'];co=np.array(state['material']);rows=[]
for n in ['a','b']:
 s=Study(root/n);source=s.source.copy();known=cv2.imread(str(s.folder/'known.png'),0)>254;prediction=s.render(p,co);base_co=effective(s,p,co)
 if 'material_chroma_sensitivity' in p or 'ambient_rim_response' in p:
  X,Y,inside=footprint(s,p);context_known=cv2.remap(known.astype(np.float32),X,Y,cv2.INTER_LINEAR)
  assert np.min(context_known[inside])==1.,'Cannot certify color-dependent material from an unknown context'
 minimum=float('inf');maximum=-float('inf')
 for row,bottom,W,x,y in s.raster_tiles():
  *_,J=s.geometry_field(x,y,p);c=J[...,-1];gain=(1-c[...,None])*base_co[:3]+c[...,None]*base_co[-3:];minimum=min(minimum,float(gain.min()));maximum=max(maximum,float(gain.max()))
 assert minimum>=0 and p['gamma']>0
 bounds=[]
 for value in [0.,1.]:
  s.source=np.where(known[...,None],source,value).astype(np.float32);s.cache=OrderedDict();assert np.array_equal(effective(s,p,co),base_co),'Source-context material changed under missing-input variation';bounds.append(s.render(p,co).astype(np.float64))
 low,high=bounds;assert np.all(low<=high+2e-6);assert np.all(prediction>=low-2e-6) and np.all(prediction<=high+2e-6)
 width=(high-low)*255;T=s.target_crop.astype(np.float64);distance_min=np.where((T>=low)&(T<=high),0,np.minimum((T-low)**2,(T-high)**2));distance_max=np.maximum((T-low)**2,(T-high)**2);metrics={}
 for label,mask in [('glass',s.valid),('rim',s.rim)]:
  lower=float(distance_min[mask].mean())*255**2;upper=float(distance_max[mask].mean())*255**2
  metrics[label]=dict(mse_lower=lower,mse_upper=upper,uncertain_pixel_fraction=float(np.any(width[mask]>1e-4,axis=-1).mean()),pixel_fraction_with_interval_over_1rgb=float(np.any(width[mask]>1,axis=-1).mean()),maximum_interval_rgb=float(width[mask].max()))
 loss=[.7*metrics['glass'][k]+.3*metrics['rim'][k] for k in ['mse_lower','mse_upper']];native=s.scores(prediction)
 assert loss[0]-1e-4<=native['loss']<=loss[1]+1e-4
 rows.append(dict(sample=n,native=native,material_gain_range=[minimum,maximum],metrics=metrics,weighted_loss_interval=loss))
report=dict(frozen_state=state,definition='All RGB assignments of undefined pixels in the fixed input canvas, known RGB exact. Monotone source transport permits componentwise lower/upper renders. Per-pixel squared-error extrema give conservative aggregate bounds; simultaneous attainability is not claimed.',assumptions='Geometry/gamma/lighting/foreground exclusions fixed; source context wholly defined and unchanged; nonnegative color gain; positive kernels/subpixel weights; encoded RGB[0,1]. Canvas border policy fixed. Float32 tolerance1e-4MSE.',samples=rows,limits='Not a confidence interval/statistical probability, Apple fidelity bound, or bound on recovery/registration/known-pixel error. It isolates missing-input uncertainty within this renderer. No score/input/mask changes.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows),flush=True)
