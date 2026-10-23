"""First checkpoint; count every actual height and traced fixture evaluation."""
from pathlib import Path
import datetime,json,time
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from geometric_optics import HarmonicCircularBack,trace_flat_front_orthographic
from curvature import capsule_offset
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
protocol=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['stages'][0]['first_checkpoint_deadline']).timestamp()
if (OUT/'geometry-check.json').exists():raise RuntimeError('Completed checkpoint cannot repeat')
counts={'height':0,'rays':0}
original=RoundedRectangleHarmonicBack.height_gradient;original_circle=HarmonicCircularBack.height_gradient
def gate():
 if time.time()>deadline:raise RuntimeError('First checkpoint deadline reached')
def counted(self,x,y):
 gate();counts['height']+=np.broadcast_arrays(x,y)[0].size;assert counts['height']<=12000
 return original(self,x,y)
def counted_circle(self,x,y):
 gate();counts['height']+=np.broadcast_arrays(x,y)[0].size;assert counts['height']<=12000
 return original_circle(self,x,y)
RoundedRectangleHarmonicBack.height_gradient=counted;HarmonicCircularBack.height_gradient=counted_circle
def trace(surface,x,y,index=1.5):
 counts['rays']+=np.broadcast_arrays(x,y)[0].size;assert counts['rays']<=512
 return trace_flat_front_orthographic(surface,x,y,index,2.)
p=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters']
half=(434/88.5+p['half_x_delta'],1+p['half_y_delta']);radius=min(1+p['radius_delta'],*half)
s=RoundedRectangleHarmonicBack(half,radius,cap_join_width=p['cap_join_width'])
rng=np.random.default_rng(222);x=rng.uniform(-half[0]*.95,half[0]*.95,600);y=rng.uniform(-radius*.6,radius*.6,600)
inside=s.footprint(x,y)[0]<.9;x=x[inside];y=y[inside];h,hx,hy,_=s.height_gradient(x,y);eps=1e-5
dx=(s.height_gradient(x+eps,y)[0]-s.height_gradient(x-eps,y)[0])/(2*eps);dy=(s.height_gradient(x,y+eps)[0]-s.height_gradient(x,y-eps)[0])/(2*eps)
error=max(float(abs(dx-hx).max()),float(abs(dy-hy).max()));assert error<2e-7
xx,yy=np.meshgrid(np.linspace(-half[0]*1.05,half[0]*1.05,11),np.linspace(-radius*1.05,radius*1.05,11))
q=trace(s,xx,yy);normal=trace(s,xx,yy,1.);regular=normal['complete'];np.testing.assert_array_equal(normal['X'][regular],xx[regular]);np.testing.assert_array_equal(normal['Y'][regular],yy[regular])
assert q['complete'].all()  # This sparse grid excludes the exact rim.
assert np.isfinite(q['X']).all() and np.all(q['exit_direction'][...,2]<0)
np.testing.assert_allclose(s.height_gradient(-x,y)[0],h,atol=0,rtol=0)
np.testing.assert_allclose(s.height_gradient(-x,y)[1],-hx,atol=0,rtol=0)
# The same accepted footprint coordinate, independently expressed.
a=half[0]-radius;offset,_=capsule_offset(abs(xx)-a,p['cap_join_width']);sd=np.hypot(offset,yy)-radius
np.testing.assert_array_equal(q['inside'],sd<=0)
circle=RoundedRectangleHarmonicBack((1.,1.),1.,isotropic_fixture=True);standard=HarmonicCircularBack()
cy,cx=np.meshgrid(np.linspace(-1.1,1.1,11),np.linspace(-1.1,1.1,11))
for v,w in zip(circle.height_gradient(cx,cy),standard.height_gradient(cx,cy)):np.testing.assert_allclose(v,w,atol=2e-16,rtol=0)
one=trace(circle,cx,cy);two=trace(standard,cx,cy)
for key in one:
 if one[key].dtype==bool:np.testing.assert_array_equal(one[key],two[key])
 else:np.testing.assert_allclose(one[key],two[key],atol=3e-15,rtol=0,equal_nan=True)
pole=trace(s,np.array([-half[0],half[0]]),np.zeros(2));assert (~pole['complete']).all() and np.isnan(pole['X']).all()
u=np.linspace(0,1,401);assert (u*u*(3-2*u)>=0).all() and (u*u*(3-2*u)<=1).all();assert (3*u*(1-u)/p['cap_join_width']>=0).all()
result={'status':'PASS','finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'height_evaluations':counts['height'],'fixture_rays':counts['rays'],'derivative_max_error':error,'surface':{'half':half,'radius':radius,'cap_join_width':p['cap_join_width'],'depth':.15,'crown_depth':.4,'power':3},'slope_bound':s.slope_bound,'maximum_height':s.maximum_height,'circle_equality':True,'accepted_smoothed_footprint_equal':True,'zero_height_poles_unresolved':True,'rgb_samples':0,'certificate':'Convex nondecreasing smoothed positive part, derivative in [0,1] and nonnegative second derivative; convex rho, concave heights and nondecreasing concave harmonic composition. No independent normal.'}
(OUT/'geometry-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
