"""Check an actually integrated curvature profile and its circle/scale limits."""
from pathlib import Path
import datetime,json
import numpy as np
from footprint_curvature_back import FootprintCurvatureBack
from geometric_optics import RadialCurvatureBack,trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);fit=json.loads((OUT/'inference.json').read_text());scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']
assert not (OUT/'checkpoint.json').exists();knots=fit['knots'];curvature=np.array(fit['best']['curvature']);half=tuple(scene['surface_half']);radius=scene['surface_radius'];surface=FootprintCurvatureBack(half,radius,knots,curvature);rays=0
assert (curvature>=0).all() and surface.slope_bound<1/np.sqrt(1.5**2-1) and surface.maximum_height<2.1
rng=np.random.default_rng(53);x=rng.uniform(-.95*half[0],.95*half[0],96);y=rng.uniform(-.7*half[1],.7*half[1],96);eps=1e-5;h,hx,hy,inside=surface.height_gradient(x,y);dx=(surface.height_gradient(x+eps,y)[0]-surface.height_gradient(x-eps,y)[0])/(2*eps);dy=(surface.height_gradient(x,y+eps)[0]-surface.height_gradient(x,y-eps)[0])/(2*eps);error=max(float(abs(dx-hx).max()),float(abs(dy-hy).max()));assert inside.all() and error<1e-7
xx,yy=np.meshgrid(np.linspace(-.999*half[0],.999*half[0],17),np.linspace(-.999*half[1],.999*half[1],17));q=trace_flat_front_orthographic(surface,xx,yy,1.5,2.1);rays+=xx.size;assert q['complete'].all();np.testing.assert_allclose(q['X'],-q['X'][:,::-1],atol=1e-12,rtol=0);np.testing.assert_allclose(q['Y'],-q['Y'][::-1],atol=1e-12,rtol=0)
np.savez_compressed(OUT/'checkpoint-paths.npz',x=xx,y=yy,**q)
cx,cy=np.meshgrid(np.linspace(-.98*radius,.98*radius,9),np.linspace(-.98*radius,.98*radius,9));circle=FootprintCurvatureBack((radius,radius),radius,knots,curvature);a=trace_flat_front_orthographic(circle,cx,cy,1.5,2.1);b=trace_flat_front_orthographic(RadialCurvatureBack(knots,curvature/radius),cx/radius,cy/radius,1.5,2.1/radius);rays+=2*cx.size
np.testing.assert_array_equal(a['complete'],b['complete']);np.testing.assert_allclose(a['X'],b['X']*radius,atol=1e-12,rtol=0);np.testing.assert_allclose(a['Y'],b['Y']*radius,atol=1e-12,rtol=0)
scaled=FootprintCurvatureBack(tuple(2*np.array(half)),2*radius,knots,2*curvature);a=trace_flat_front_orthographic(scaled,2*xx[::2,::2],2*yy[::2,::2],1.5,4.2);rays+=a['X'].size;np.testing.assert_allclose(a['X'],2*q['X'][::2,::2],atol=1e-12,rtol=0);np.testing.assert_allclose(a['Y'],2*q['Y'][::2,::2],atol=1e-12,rtol=0)
ux,uy=np.meshgrid(np.linspace(-.8*half[0],.8*half[0],7),np.linspace(-.8*half[1],.8*half[1],7));u=trace_flat_front_orthographic(surface,ux,uy,1.,2.1);rays+=ux.size;np.testing.assert_array_equal(u['X'],ux);np.testing.assert_array_equal(u['Y'],uy)
assert rays<=p['budgets']['fixture_rays'] and datetime.datetime.now(datetime.timezone.utc)<deadline
out=dict(status='PASS',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixture_rays=rays,gradient_max_error=error,slope_bound=surface.slope_bound,maximum_height=surface.maximum_height,circle_scale_covariance=True,RGB_queries=0,native_images=0,regularity='C2 radial height; rounded-coordinate joins may be C1. Exact projected crease remains unresolved.')
(OUT/'checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
