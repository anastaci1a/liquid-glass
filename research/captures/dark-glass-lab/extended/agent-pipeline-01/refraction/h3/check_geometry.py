"""Two preregistered powers; same actual shared-profile law, no fit."""
from pathlib import Path
import sys,json,time,numpy as np
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h3';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
from geometric_optics import trace_flat_front_orthographic
assert 1792654200.<=time.time()<1792657200.,'Declared07:30–08:20 window'
total=0
for p in [4,5]:
 F=O/f'p{p}';g=json.loads((F/'geometry-checkpoint.json').read_text());scene=g['scene'];s=ExpandedHarmonicBack(tuple(scene['surface_half']),scene['surface_radius'],power=p)
 rng=np.random.default_rng(222);x=rng.uniform(-s.half[0]+.1,s.half[0]-.1,240);y=rng.uniform(-.8,.8,240);h,hx,hy,m=s.height_gradient(x,y);e=5e-6
 dx=(s.height_gradient(x+e,y)[0]-s.height_gradient(x-e,y)[0])/(2*e);dy=(s.height_gradient(x,y+e)[0]-s.height_gradient(x,y-e)[0])/(2*e);error=float(max(abs(dx-hx).max(),abs(dy-hy).max()));assert error<2e-8
 assert s.slope_bound<1/np.sqrt(1.5**2-1) and s.maximum_height<2
 x,y=np.meshgrid(np.linspace(-s.half[0],s.half[0],101),np.linspace(-s.half[1],s.half[1],41));q=trace_flat_front_orthographic(s,x,y,1.5,2.);total+=x.size;assert total<=10000;m=q['inside']&~q['boundary_unresolved'];assert q['complete'][m].all()
 np.savez(F/'checkpoint-paths.npz',x=x,y=y,**q);g.update(status='PASS_GEOMETRY_CHECKPOINT',power=p,gradient_FD_error=error,checkpoint_rays=int(x.size),min_discriminant=float(q['discriminant'][m].min()),global_slope_bound=s.slope_bound,maximum_height=s.maximum_height,certificate='For both p>=3 the distance-to-convex-box composition remains concave; increasing concave shared H plus longitudinal concave quadratic, same argument as H1. C1 regular interior, boundary unresolved. No new circle equality claimed: inherited shared p3 circle fixture remains separate.',finished_unix=time.time());(F/'geometry-checkpoint.json').write_text(json.dumps(g,indent=2));print(p,error,s.slope_bound)
(O/'checkpoint-ledger.json').write_text(json.dumps({'total_checkpoint_rays':total,'full_images':0,'settings':[4,5]},indent=2))
