"""Declared surface fixture budget; no RGB or source queries."""
import json,datetime
from pathlib import Path
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from geometric_optics import HarmonicCircularBack,trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
p=json.loads((ROOT/'reconstruction/studies/music-navigation/review-round/pass-03.json').read_text())['parameters']
half=(511.5/113.5+p['half_x_delta'],1+p['half_y_delta']);radius=min(1+p['radius_delta'],*half)
s=RoundedRectangleHarmonicBack(half,radius)
count=0
def field(obj,x,y):
 global count
 count+=np.broadcast_arrays(x,y)[0].size
 assert count<=12000
 return obj.height_gradient(x,y)
rng=np.random.default_rng(222);x=rng.uniform(-half[0]*.95,half[0]*.95,600);y=rng.uniform(-half[1]*.7,half[1]*.7,600)
h,hx,hy,inside=field(s,x,y);eps=1e-5
dx=(field(s,x+eps,y)[0]-field(s,x-eps,y)[0])/(2*eps)
dy=(field(s,x,y+eps)[0]-field(s,x,y-eps)[0])/(2*eps)
error=max(float(abs(dx-hx).max()),float(abs(dy-hy).max()));assert error<2e-7
assert np.all(h[inside]>=0) and h.max()<=s.maximum_height and np.hypot(hx,hy).max()<=s.slope_bound
circle=RoundedRectangleHarmonicBack((1.,1.),1.,isotropic_fixture=True);other=HarmonicCircularBack()
yy,xx=np.meshgrid(np.linspace(-1.1,1.1,21),np.linspace(-1.1,1.1,21))
for a,b in zip(field(circle,xx,yy),field(other,xx,yy)):np.testing.assert_allclose(a,b,atol=2e-16,rtol=0)
q=trace_flat_front_orthographic(s,np.array([-half[0],half[0]]),np.zeros(2),1.5,2.)
assert (~q['complete']).all() and np.isnan(q['X']).all()
# Convex footprint and concave height: rho is a convex norm of positive-part
# distances; 1-rho^p is concave on rho<=1. Positive harmonic composition is
# concave/nondecreasing in both concave nonnegative heights.
result={'status':'PASS','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixture_height_points':count,'fixture_primary_rays':2,'derivative_max_error':error,'half':half,'radius':radius,'maximum_height':s.maximum_height,'slope_bound':s.slope_bound,'exact_zero_height_poles_incomplete':True,'circle_field_equality_tolerance':2e-16,'continuity':'C1 with second-derivative joins; front/back rim crease unresolved, not globally smooth.','rgb_queries':0}
(OUT/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
