"""Geometry invariants only; no score/pass from these tests."""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_two_surface import TwoSurfaceStudy
from switch_euclidean_surface import EuclideanSurfaceStudy
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'physical-two-surface';out.mkdir(exist_ok=True)
p=json.loads((root/'physical-euclidean-surface/native-settlement.json').read_text())['parameters'];rows=[]
for name in ['a','b']:
 s=TwoSurfaceStudy(root/'paired'/name);base=EuclideanSurfaceStudy(root/'paired'/name)
 x=s.x.ravel()[s.indices];y=s.y.ravel()[s.indices]
 old=base.geometry_field(x,y,p);zero=s.geometry_field(x,y,p)
 assert all(np.array_equal(a,b) for a,b in zip(old,zero))
 xx,yy,half,r,*_=s.surface(x,y,p);f,fx,fy=s.front(xx,yy,half,r,.08);eps=1e-6
 ex=np.max(abs((s.front(xx+eps,yy,half,r,.08)[0]-s.front(xx-eps,yy,half,r,.08)[0])/(2*eps)-fx))
 ey=np.max(abs((s.front(xx,yy+eps,half,r,.08)[0]-s.front(xx,yy-eps,half,r,.08)[0])/(2*eps)-fy))
 assert max(ex,ey)<1e-8
 variants=[]
 for amplitude in [-.08,-.04,.04,.08]:
  q=copy.deepcopy(p);q['front_crown']=amplitude
  try:
   X,Y,d,J=s.geometry_field(x,y,q);assert np.isfinite(X).all() and np.isfinite(Y).all()
   # Symmetry around declared shape center; material not part of this check.
   sx=p.get('shape_dx',0.);sy=p.get('shape_dy',0.)
   U,V,*_=s.geometry_field(2*sx-x,2*sy-y,q)
   error=max(np.max(abs(U-(2*sx-X))),np.max(abs(V-(2*sy-Y))))
   assert error<1e-8,error
   variants.append(dict(amplitude=amplitude,valid=True,mirror_error=float(error)))
  except ValueError as e:variants.append(dict(amplitude=amplitude,valid=False,reason=str(e)))
 rows.append(dict(observation=name,zero_exact=True,gradient_error=[float(ex),float(ey)],trials=variants))
with (out/'invariants.json').open('x') as f:json.dump(dict(rows=rows,limits='5000fixed points, not all raster rays or source support. Symmetric double-surface geometry; retained material is empirical.'),f,indent=2)
print(json.dumps(rows),flush=True)
