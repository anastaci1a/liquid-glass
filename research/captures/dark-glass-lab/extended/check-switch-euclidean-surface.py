import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_euclidean_surface import EuclideanSurfaceStudy
from crowned_footprint import field
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';out.mkdir(exist_ok=True)
p=json.loads((root/'rev4-ambient-review/candidate.json').read_text())['parameters'];p['euclidean_surface']=dict(t0=.5,bx=.05,by=.065,profile=[p['c'+str(i)]/4.75 for i in range(7)],width=.75,n=1.5,gap=10.5);rows=[]
for name in ['a','b']:
 s=EuclideanSurfaceStudy(root/'paired'/name);x=np.linspace(-1.5,1.5,79);y=np.linspace(-.98,.98,73);x,y=np.meshgrid(x,y);x+=p['shape_dx'];y+=p['shape_dy'];xx,yy,half,r,_=s.shape(x,y,p);mask=field(xx,yy,half,p['crown_softness'])[0]<.98;x=x[mask];y=y[mask];e=2e-6*r
 *_,inside,h,hx,hy=s.surface(x,y,p)
 hp=s.surface(x+e,y,p)[-3];hm=s.surface(x-e,y,p)[-3];vp=s.surface(x,y+e,p)[-3];vm=s.surface(x,y-e,p)[-3];error=float(np.max(np.hypot((hp-hm)/(2*e)-hx,(vp-vm)/(2*e)-hy)));assert error<1e-7,error
 # No arbitrary unit-normal substitution: differentiate the implemented height.
 cache=s.distance_cache;g=s.euclidean_geometry;tab=g.arc_table(8192);reach_estimate=float(1/np.max(tab['curvature']));assert .75*r<reach_estimate
 *_,hhx,hhy=s.surface(x+e,y,p);*_,hlx,hly=s.surface(x-e,y,p);*_,hux,huy=s.surface(x,y+e,p);*_,hdx,hdy=s.surface(x,y-e,p);curl=float(np.max(abs((hhy-hly-hux+hdx)/(2*e))));assert curl<1e-6,curl
 X,Y,_,_=s.geometry_field(x,y,p);assert np.isfinite(X).all() and np.isfinite(Y).all()
 rows.append(dict(observation=name,gradient_error=error,curl=curl,minimum_sampled_radius_of_curvature=reach_estimate,width=.75*r,cache_entries=len(cache)))
(out/'invariants.json').write_text(json.dumps(dict(passed=True,rows=rows,parameters=p,limits='Curvature radius estimate sampled; actual projections additionally enforce stationarity and distance no worse than global16384point seed. Native emitted-ray/height/source bounds required for acceptance.'),indent=2)+'\n');print(json.dumps(rows),flush=True)
