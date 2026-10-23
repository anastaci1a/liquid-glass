"""Bounded closed-front checkpoint, with all comparator launches charged."""
from pathlib import Path
import datetime,hashlib,json
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from parabolic_front_solid import ParabolicFrontHeightSolid
from geometric_optics import trace_closed_orthographic,trace_flat_front_orthographic,CircularHeightSolid,HarmonicCircularBack
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline'])
assert not (OUT/'checkpoint.json').exists()
for f,h in p['code_hashes'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];back=RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius'])
counts=dict(launches=0,level_points=0);native=ParabolicFrontHeightSolid.level_gradient;circle=CircularHeightSolid.level_gradient
# Charge level queries from nonsmooth masks too, which call _fields directly.
fields=ParabolicFrontHeightSolid._fields
def charge(n):
 assert counts['level_points']+n<=p['budgets']['checkpoint_level_points'];counts['level_points']+=n
try:
 def counted_fields(self,points):charge(np.asarray(points)[...,0].size);return fields(self,points)
 def counted_circle(self,points):charge(np.asarray(points)[...,0].size);return circle(self,points)
 ParabolicFrontHeightSolid._fields=counted_fields;CircularHeightSolid.level_gradient=counted_circle
 def trace(surface,x,y,index=1.5,closed=True):
  assert datetime.datetime.now(datetime.timezone.utc)<deadline
  counts['launches']+=np.broadcast_arrays(x,y)[0].size;assert counts['launches']<=p['budgets']['checkpoint_launches']
  return trace_closed_orthographic(surface,x,y,index,2,tolerance=1e-11,max_iterations=64) if closed else trace_flat_front_orthographic(surface,x,y,index,2)
 solid=ParabolicFrontHeightSolid(back,.4);rng=np.random.default_rng(31);x=rng.uniform(-.9*back.half[0],.9*back.half[0],96);y=rng.uniform(-.6*back.half[1],.6*back.half[1],96)
 eps=1e-5;maximum_gradient_error=0.
 for z in [solid._front(x,y)[0],-back.height_gradient(x,y)[0]]:
  points=np.stack([x,y,z],-1);F,G=solid.level_gradient(points);assert abs(F).max()<1e-12
  for axis in range(3):
   d=np.eye(3)[axis]*eps;fd=(solid.level_gradient(points+d)[0]-solid.level_gradient(points-d)[0])/(2*eps);maximum_gradient_error=max(maximum_gradient_error,float(abs(fd-G[:,axis]).max()))
 assert maximum_gradient_error<p['control_tolerances']['gradient_absolute']
 xx,yy=np.meshgrid(np.linspace(-.999*back.half[0],.999*back.half[0],31),np.linspace(-.999*back.half[1],.999*back.half[1],17));q=trace(solid,xx,yy);assert q['complete'].all() and not q['blocked'].any()
 np.testing.assert_allclose(q['X'],-q['X'][:,::-1],atol=1e-9,rtol=0);np.testing.assert_allclose(q['Y'],-q['Y'][::-1],atol=1e-9,rtol=0)
 valid=q['inside'];F,G=solid.level_gradient(q['entry'][valid]);np.testing.assert_allclose(F,0,atol=1e-10,rtol=0);np.testing.assert_allclose(G/np.linalg.norm(G,axis=-1)[:,None],q['entry_normal'][valid],atol=1e-12,rtol=0)
 F,G=solid.level_gradient(q['exit'][valid]);assert abs(F).max()<1e-9;np.testing.assert_allclose(G/np.linalg.norm(G,axis=-1)[:,None],q['exit_normal'][valid],atol=1e-12,rtol=0)
 np.savez_compressed(OUT/'checkpoint-paths.npz',x=xx,y=yy,**q)
 ux,uy=np.meshgrid(np.linspace(-.9*back.half[0],.9*back.half[0],13),np.linspace(-.9*back.half[1],.9*back.half[1],7));zero=trace(ParabolicFrontHeightSolid(back,0),ux,uy);prior=trace(back,ux,uy,closed=False)
 np.testing.assert_array_equal(zero['complete'],prior['complete']);delta=max(float(np.nanmax(abs(zero['X']-prior['X']))),float(np.nanmax(abs(zero['Y']-prior['Y']))));assert delta<p['control_tolerances']['zero_front_source_over_L']
 cx,cy=np.meshgrid(np.linspace(-1,1,9),np.linspace(-1,1,9));iso=RoundedRectangleHarmonicBack((1.,1.),1.,isotropic_fixture=True);c1=trace(ParabolicFrontHeightSolid(iso,0),cx,cy);c2=trace(CircularHeightSolid(HarmonicCircularBack()),cx,cy)
 for k in ['inside','complete','boundary_unresolved','blocked']:np.testing.assert_array_equal(c1[k],c2[k])
 for k in ['X','Y','entry','exit','entry_normal','exit_normal']:np.testing.assert_allclose(c1[k],c2[k],atol=1e-9,rtol=0,equal_nan=True)
 ix,iy=np.meshgrid(np.linspace(-.8*back.half[0],.8*back.half[0],7),np.linspace(-.8*back.half[1],.8*back.half[1],7));u=trace(solid,ix,iy,index=1.);assert u['complete'].all();np.testing.assert_allclose(u['X'],ix,atol=1e-12,rtol=0);np.testing.assert_allclose(u['Y'],iy,atol=1e-12,rtol=0)
 r=dict(status='PASS',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=counts,maximum_gradient_error=maximum_gradient_error,zero_front_source_difference_over_L=delta,maximum_exit_level_residual=float(abs(q['exit_level_residual'][valid]).max()),maximum_intersection_bracket=float(q['intersection_bracket'][valid].max()),RGB_queries=0,native_images=0,limits='Primary transmission only. No reflected scene or radiance identification.')
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 (OUT/'checkpoint.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
except Exception as exc:
 (OUT/'checkpoint-failure.json').write_text(json.dumps(dict(status='STOP_FIRST_INVARIANT_FAILURE',counts=counts,error=str(exc)),indent=2)+'\n');raise
finally:ParabolicFrontHeightSolid._fields=fields;CircularHeightSolid.level_gradient=circle
