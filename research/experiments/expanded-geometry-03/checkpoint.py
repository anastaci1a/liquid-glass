"""Fixed-height surface checkpoint; count all actual height/trace evaluations."""
from pathlib import Path
import datetime,json
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from geometric_optics import trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline'])
assert not (OUT/'checkpoint.json').exists()
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']
original=RoundedRectangleHarmonicBack.height_gradient;counts=dict(height=0,rays=0);last=None
try:
 def counted(self,x,y):
  global last
  counts['height']+=np.broadcast_arrays(x,y)[0].size
  assert counts['height']<=p['budgets']['checkpoint_height_evaluations']
  last=original(self,x,y);return last
 RoundedRectangleHarmonicBack.height_gradient=counted
 old=RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius'])
 new=RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius'],depth=.24,crown_depth=.2)
 rng=np.random.default_rng(17);x=rng.uniform(-.98*new.half[0],.98*new.half[0],256);y=rng.uniform(-.8*new.half[1],.8*new.half[1],256);keep=new.footprint(x,y)[0]<.9;x=x[keep][:96];y=y[keep][:96];assert len(x)==96
 h,hx,hy,inside=new.height_gradient(x,y);eps=1e-5
 dx=(new.height_gradient(x+eps,y)[0]-new.height_gradient(x-eps,y)[0])/(2*eps);dy=(new.height_gradient(x,y+eps)[0]-new.height_gradient(x,y-eps)[0])/(2*eps)
 error=max(float(np.max(abs(dx-hx))),float(np.max(abs(dy-hy))));assert error<1e-7 and inside.all()
 second=[]
 for surface in [old,new]:
  e=.001;v=np.array([-e,0,e]);hh=surface.height_gradient(v,np.zeros(3))[0];fd=(hh[0]-2*hh[1]+hh[2])/e**2;analytic=-2*surface.crown_depth/surface.half[0]**2*(surface.depth/(surface.depth+surface.crown_depth))**2
  assert abs(fd-analytic)<1e-9;second.append(float(analytic))
 assert abs(new.maximum_height-old.maximum_height)<1e-15 and abs(second[1]/second[0]-2)<1e-14
 xx,yy=np.meshgrid(np.linspace(-.999*new.half[0],.999*new.half[0],31),np.linspace(-.999*new.half[1],.999*new.half[1],17));q=trace_flat_front_orthographic(new,xx,yy,1.5,2);counts['rays']+=xx.size
 assert q['complete'].all() and np.isfinite(q['X']).all() and np.isfinite(q['Y']).all()
 np.testing.assert_allclose(q['X'],-q['X'][:,::-1],atol=1e-12,rtol=0);np.testing.assert_allclose(q['Y'],-q['Y'][::-1],atol=1e-12,rtol=0)
 hh,gx,gy,_=last;valid=q['inside'];norm=np.stack([gx,gy,np.ones_like(gx)],-1);norm=-norm/np.linalg.norm(norm,axis=-1)[...,None];np.testing.assert_allclose(q['outward_normal'][valid],norm[valid],atol=1e-14,rtol=0)
 np.testing.assert_allclose(q['back'][valid,2],-hh[valid],atol=0,rtol=0)
 np.savez_compressed(OUT/'checkpoint-paths.npz',x=xx,y=yy,**q)
 ux,uy=np.meshgrid(np.linspace(-.9*new.half[0],.9*new.half[0],13),np.linspace(-.9*new.half[1],.9*new.half[1],7));u=trace_flat_front_orthographic(new,ux,uy,1.,2);counts['rays']+=ux.size
 np.testing.assert_array_equal(u['X'],ux);np.testing.assert_array_equal(u['Y'],uy);assert u['complete'].all();assert counts['rays']<=p['budgets']['checkpoint_rays']
 result=dict(status='PASS',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=counts,gradient_max_error=error,central_hxx=second,curvature_ratio=second[1]/second[0],maximum_height=new.maximum_height,slope_bound=new.slope_bound,critical_slope=1/np.sqrt(1.5**2-1),RGB_queries=0,native_images=0,certificates=['Same increasing concave harmonic composition and frozen convex footprint.','Actual surface supplies all normals and heights.','Global slope below critical; background2 exceeds maximum height.','Exact projected crease remains unresolved; no boundary fixture claimed transmitting.'])
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 (OUT/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
except Exception as exc:
 (OUT/'checkpoint-failure.json').write_text(json.dumps(dict(status='STOP_FIRST_INVARIANT_FAILURE',counts=counts,error=str(exc)),indent=2)+'\n');raise
finally:RoundedRectangleHarmonicBack.height_gradient=original
