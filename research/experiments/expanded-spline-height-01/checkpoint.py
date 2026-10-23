"""Continue the same explicit runtime budgets; no image or RGB operation."""
from pathlib import Path
import datetime,json
import numpy as np
from spline_height_back import SplineFootprintBack
from geometric_optics import trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());old=json.loads((OUT/'inference.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'checkpoint.json').exists();scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];counter=old['height_adapter_calls'];rays=0;comparator=0
class Counted(SplineFootprintBack):
 def height_gradient(self,x,y):
  global counter
  n=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size
  assert counter+n<=p['budgets']['total_height_adapter_calls'],'Reserve adapter graph calls before evaluation'
  counter+=n;return super().height_gradient(x,y)
def trace(s,x,y,index=1.5,D=2.1):
 global rays
 n=np.asarray(x).size;assert rays+comparator+n<=p['budgets']['fixture_comparator_rays'];rays+=n
 return trace_flat_front_orthographic(s,x,y,index,D)
c=np.asarray(old['best']['heights']);s=Counted(scene['surface_half'],scene['surface_radius'],old['breaks'],c);rng=np.random.default_rng(225);x=rng.uniform(-s.half[0],s.half[0],128);y=rng.uniform(-s.half[1],s.half[1],128);inside=s.coordinate.footprint(x,y)[0]<.99;x=x[inside][:64];y=y[inside][:64];assert len(x)==64
h,hx,hy,_=s.height_gradient(x,y);e=1e-6;dx=(s.height_gradient(x+e,y)[0]-s.height_gradient(x-e,y)[0])/(2*e);dy=(s.height_gradient(x,y+e)[0]-s.height_gradient(x,y-e)[0])/(2*e);error=max(abs(dx-hx).max(),abs(dy-hy).max());assert error<1e-8;assert h.min()>0 and h.max()<=s.maximum_height;assert np.hypot(hx,hy).max()<=s.slope_bound
q=trace(s,x,y);qm=trace(s,-x,y);assert q['complete'].all() and qm['complete'].all();np.testing.assert_allclose(qm['X'],-q['X'],atol=1e-14,rtol=0);np.testing.assert_allclose(qm['Y'],q['Y'],atol=1e-14,rtol=0)
scale=3.;ss=Counted(tuple(scale*np.asarray(s.half)),scale*s.radius,old['breaks'],scale*c);qs=trace(ss,scale*x,scale*y,D=scale*2.1);np.testing.assert_allclose(qs['X']/scale,q['X'],atol=1e-14,rtol=0);np.testing.assert_allclose(qs['Y']/scale,q['Y'],atol=1e-14,rtol=0)
circle=Counted((1.,1.),1.,old['breaks'],c);r=np.linspace(0,.995,64);theta=np.arange(64)*np.pi*(3-np.sqrt(5));cx=r*np.cos(theta);cy=r*np.sin(theta);cq=trace(circle,cx,cy);n1=trace(circle,cx,cy,index=1.);np.testing.assert_allclose(n1['X'],cx,atol=2e-15,rtol=0);np.testing.assert_allclose(n1['Y'],cy,atol=2e-15,rtol=0)
r=np.hypot(cx,cy);h=circle.profile(r);hr=circle.radial_derivative(r);angle=np.arctan(abs(hr));phi=np.arcsin(1.5*np.sin(angle))-angle;factor=np.divide((2.1-h)*np.tan(phi)*np.sign(hr),r,out=np.zeros_like(r),where=r>0);comparator+=64;assert rays+comparator<=p['budgets']['fixture_comparator_rays'];np.testing.assert_allclose(cq['X'],cx+factor*cx,atol=2e-15,rtol=0);np.testing.assert_allclose(cq['Y'],cy+factor*cy,atol=2e-15,rtol=0)
bound=trace(circle,np.array([1.,-1.,0.,0.]),np.array([0.,0.,1.,-1.]));assert not bound['complete'].any() and np.isnan(bound['X']).all();miss=trace(circle,np.array([1.1,-1.1]),np.zeros(2));np.testing.assert_array_equal(miss['X'],[1.1,-1.1]);assert miss['complete'].all();assert datetime.datetime.now(datetime.timezone.utc)<deadline
np.savez_compressed(OUT/'checkpoint-paths.npz',back=q['back'],normal=q['outward_normal'],exit_direction=q['exit_direction'],X=q['X'],Y=q['Y']);result=dict(status='GEOMETRY_CHECKPOINT_PASS_NO_IMAGE',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),gradient_max_error=float(error),fixture_physical_rays=rays,independent_comparator_rays=comparator,charged_fixture_comparator_rays=rays+comparator,cumulative_height_adapter_calls=counter,maximum_height=s.maximum_height,global_slope_bound=s.slope_bound,RGB_queries=0,images=0,new_fits=0,scope='Primary normal flat-front paths only; no numerical source/fidelity/dispersion/scene validation.');(OUT/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
