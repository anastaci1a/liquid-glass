"""H1 bounded physical surface checkpoint; no source RGB or image formation."""
from pathlib import Path
import sys,json,time
import numpy as np
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h1';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
from geometric_optics import trace_flat_front_orthographic,HarmonicCircularBack
from render import geometry
proto=json.loads((O/'protocol.json').read_text());deadline=1792654355.
rec=json.loads((P/'historical-pass03.json').read_text());case=json.loads((P/'inputs/a/case.json').read_text());p=rec['parameters'];L=min(case['half']);half=np.array(case['half'])/L+[p['half_x_delta'],p['half_y_delta']];radius=min(case['radius']/L+p['radius_delta'],min(half));center=np.array(case['center'])+L*np.array([p['shape_dx'],p['shape_dy']]);s=ExpandedHarmonicBack(tuple(half),radius)
R={'status':'RUNNING','rays':0,'RGB_samples':0,'images':0,'checks':{},'scene':{'center':center.tolist(),'original_reference_L':L,'surface_half':half.tolist(),'surface_radius':radius,'depth':s.depth,'crown_depth':s.crown_depth,'index':1.5,'D':2}}
def save():(O/'geometry-checkpoint.json').write_text(json.dumps(R,indent=2,allow_nan=False))
def check(name,ok,data):
 R['checks'][name]={'pass':bool(ok),'details':data};save()
 if not ok:raise AssertionError(name)
 if time.time()>deadline:raise TimeoutError('H1 declared deadline')
def trace(s,x,y):
 R['rays']+=np.broadcast_arrays(x,y)[0].size
 if R['rays']>20000:raise RuntimeError('Checkpoint ray cap')
 return trace_flat_front_orthographic(s,x,y,1.5,2.)
try:
 rng=np.random.default_rng(222);x=rng.uniform(-half[0]+.1,half[0]-.1,240);y=rng.uniform(-.8,.8,240)
 h,hx,hy,inside=s.height_gradient(x,y);errors=[]
 for step in [1e-5,5e-6]:
  dx=(s.height_gradient(x+step,y)[0]-s.height_gradient(x-step,y)[0])/(2*step);dy=(s.height_gradient(x,y+step)[0]-s.height_gradient(x,y-step)[0])/(2*step)
  errors.append(float(max(abs(dx-hx).max(),abs(dy-hy).max())))
 check('same_height_gradient',max(errors)<2e-8,{'FD_steps':[1e-5,5e-6],'errors':errors})
 xx,yy=np.meshgrid(np.linspace(-half[0],half[0],101),np.linspace(-half[1],half[1],41));sd,*_=geometry(xx,yy,half,radius);rho,*_=s.footprint(xx,yy)
 check('frozen_rounded_outline',np.array_equal(sd<=0,rho<=1),{'different_grid_classifications':int(((sd<=0)!=(rho<=1)).sum()),'analytic':'rho=distance to frozen core rectangle / radius. rho<=1 is exactly the same rounded rectangle; no fitted silhouette change.'})
 check('concavity_global_certificate',s.slope_bound<1/np.sqrt(1.5**2-1) and s.maximum_height<2,{'proof':'Distance to convex core box is convex; rho^power convex for power>=3; h1 concave. h2 longitudinal quadratic concave. Shared harmonic_cap increasing concave, nonnegative weights summing<=1. Height bound at center; gradient bound max(power*depth/radius,2*crown_depth/majorhalf).','global_slope_bound':s.slope_bound,'maximum_height':s.maximum_height,'regularity':'Actual height/gradient C1; second derivatives can jump at the frozen capsule/core-box joins. No false global C2 claim or independent normals.'})
 o=trace(s,xx,yy);valid=o['inside']&~o['boundary_unresolved'];check('regular_primary_paths',np.all(o['complete'][valid]) and np.all(o['discriminant'][valid]>0),{'regular_count':int(valid.sum()),'boundary_unresolved':int(o['boundary_unresolved'].sum()),'min_discriminant':float(o['discriminant'][valid].min())})
 np.savez(O/'checkpoint-paths.npz',x=xx,y=yy,**o)
 cx,cy=np.meshgrid(np.linspace(-.98,.98,21),np.linspace(-.98,.98,21));own=ExpandedHarmonicBack((1.,1.),1.,isotropic_fixture=True);root=HarmonicCircularBack();a=trace(own,cx,cy);b=trace(root,cx,cy);diff=0.
 for k in a:
  if a[k].dtype==bool:assert np.array_equal(a[k],b[k]);continue
  assert np.array_equal(np.isnan(a[k]),np.isnan(b[k]));m=np.isfinite(a[k]);diff=max(diff,float(abs(a[k][m]-b[k][m]).max()) if m.any() else 0.)
 check('meaningful_circle_limit',diff<1e-12,{'max_difference':diff,'scope':'Same harmonic law and physical depths, true circle plus isotropic quadratic. Longitudinal pill profile is intentionally not falsely called rotationally symmetric.'})
 h0,hx0,hy0,_=s.height_gradient(0.,0.);e=1e-4;hxx=float((s.height_gradient(e,0)[1]-s.height_gradient(-e,0)[1])/(2*e));R['central_hxx']=hxx
 v=np.linspace(-half[0],half[0],301);sec=s.section(v);np.savez(O/'actual-section.npz',**sec)
 R['status']='PASS_GEOMETRY_CHECKPOINT';R['finished_unix']=time.time();save();print(json.dumps(R))
except Exception as e:
 R['status']='STOP_FIRST_INVARIANT_FAILURE';R['error']=repr(e);save();raise
