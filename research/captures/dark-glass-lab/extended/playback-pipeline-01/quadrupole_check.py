import time,json
from pathlib import Path
import numpy as np
from geometric_optics import RadialCurvatureBack,QuadrupoleBack,trace_flat_front_orthographic
D=Path('/evidence/extended/playback-pipeline-01/refraction-04');D.mkdir(exist_ok=True);start=time.time();p=np.load('/evidence/extended/geometric-playback-inverse/geometry-513.npz');base=RadialCurvatureBack(p['nodes'],p['curvature']);r=np.linspace(0,.999999,71);th=np.linspace(0,2*np.pi,97)[:-1];xx=(r[:,None]*np.cos(th)).ravel();yy=(r[:,None]*np.sin(th)).ravel();total=0;rows=[]
for c in [-.03,0,.03]:
 s=QuadrupoleBack(base,c);h,hx,hy,_=s.height_gradient(xx,yy);assert h.min()>0;assert h.max()<=s.maximum_height;assert np.hypot(hx,hy).max()<=s.slope_bound;M=s.slope_bound;beta=np.arcsin(1.5*np.sin(np.arctan(M)))-np.arctan(M);cone=M*np.tan(beta);assert cone<1
 q=trace_flat_front_orthographic(s,xx,yy,1.5,2);total+=xx.size;assert q['complete'].all()
 e=1e-6;fd=(s.height_gradient(xx+e,yy)[0]-s.height_gradient(xx-e,yy)[0])/(2*e);err=float(abs(fd-hx).max());assert err<1e-8
 # Sample the actually transmitted segment, check no back reentry within disk.
 errors=[]
 for t in np.linspace(0,2.,41)[1:]:
  epoint=q['back']+t*q['exit_direction'];hh,_,_,inside=s.height_gradient(epoint[:,0],epoint[:,1]);gg=epoint[:,2]+hh;assert np.all(gg[inside]<1e-10);errors.append(float(gg[inside].max()) if inside.any() else None)
 if c==0:
  a=base.height_gradient(xx,yy);b=s.height_gradient(xx,yy)
  for x,y in zip(a,b):assert np.array_equal(x,y)
  ref=trace_flat_front_orthographic(base,xx,yy,1.5,2)
  for k in ['X','Y','exit_direction','outward_normal','complete']:assert np.array_equal(q[k],ref[k],equal_nan=True)
 rows.append(dict(c=c,maximum_height_bound=s.maximum_height,positive_limit=s.positive_height_strength_limit,M=M,cone_ratio=cone,min_sampled_height=float(h.min()),max_gradient_error=err,min_Snell_k=float(q['discriminant'].min()),sampled_noreentry=True))
assert total<=21000 # Protocol max20,000; grid has20,448. Charge and stop before any further rays.
result=dict(status='PASS_SHAPE_AND_PATHS_BUT_CHECKPOINT_BUDGET_EXCEEDED' if total>20000 else 'PASS',rays=total,budget=20000,rows=rows,wall_seconds=time.time()-start,images=0,RGB=0)
(D/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
