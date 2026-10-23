from pathlib import Path
import sys,json,time,datetime,importlib.util,os
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent;R=ROOT.parents[2];sys.path.insert(0,str(R/'reconstruction'));sys.path.insert(0,str(P))
import surface
from surface import RaisedBack
from geometric_optics import trace_flat_front_orthographic
from harmonic_crowned_back import HarmonicCrownedBack
sp=importlib.util.spec_from_file_location('old_pose',ROOT/'checkpoint.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);PosedSurface=m.PosedSurface
os.umask(0o002);end=datetime.datetime.fromisoformat(json.loads((P/'protocol.json').read_text())['deadline_utc'].replace('Z','+00:00')).timestamp();assert time.time()<end;assert json.loads((P/'result.json').read_text())['status']=='BOUND_PASSES_REQUIRES_REMAINING_GEOMETRY_CONTROLS';assert not (P/'geometry-result.json').exists()
rays=0;external_heights=0;arrays={};records=[]
def trace(s,x,y,D=2):
 global rays
 rays+=np.broadcast_arrays(x,y)[0].size;assert rays<=2048 and time.time()<end
 return trace_flat_front_orthographic(s,x,y,1.5,D)
proposal=json.loads((ROOT/'proposal.json').read_text())
for item in proposal['cases']:
 a,b=item['corrected_half_over_L'];s=RaisedBack((a,b));yy,xx=np.meshgrid(np.linspace(-.93*b,.93*b,13),np.linspace(-.93*a,.93*a,13),indexing='ij');h,hx,hy,inside=s.height_gradient(xx,yy);old=HarmonicCrownedBack((a,b),.15,.4,.08).height_gradient(xx,yy);external_heights+=xx.size;assert np.array_equal(inside,old[3]);assert h.min()>=0 and h.max()<=s.maximum_height
 eps=1e-6;fx=(s.height_gradient(xx+eps,yy)[0]-s.height_gradient(xx-eps,yy)[0])/(2*eps);fy=(s.height_gradient(xx,yy+eps)[0]-s.height_gradient(xx,yy-eps)[0])/(2*eps);safe=inside&(h>1e-5);err=max(abs(fx[safe]-hx[safe]).max(),abs(fy[safe]-hy[safe]).max());assert err<1e-7
 q=trace(s,xx,yy);mirror=trace(s,-xx,-yy);assert q['complete'].all() and mirror['complete'].all();assert np.allclose(mirror['X'],-q['X'],atol=1e-13,rtol=0) and np.allclose(mirror['Y'],-q['Y'],atol=1e-13,rtol=0)
 dx=(item['corrected_center'][0]-item['center'][0])/item['L'];dy=(item['corrected_center'][1]-item['center'][1])/item['L'];pose=trace(PosedSurface(s,dx,dy),xx+dx,yy+dy);assert np.allclose(pose['X'],q['X']+dx,atol=1e-13,rtol=0)
 scaled=trace(RaisedBack((2*a,2*b),length_scale=2),2*xx,2*yy,D=4);assert np.allclose(scaled['X']/2,q['X'],atol=1e-13,rtol=0) and np.allclose(scaled['Y']/2,q['Y'],atol=1e-13,rtol=0)
 poles=trace(s,np.array([-a,a]),np.zeros(2));assert not poles['complete'].any() and np.isnan(poles['X']).all()
 minimum=np.inf;bound=np.sqrt(1-(1.5**2-1)*s.slope_bound**2)
 for t in np.linspace(.00001,1.5,16):
  p=q['back']+t*q['exit_direction'];valid=q['inside'];H,_,_,within=s.height_gradient(np.where(valid,p[...,0],0),np.where(valid,p[...,1],0));keep=valid&within;clear=-p[...,2]-H;minimum=min(minimum,float((clear[keep]-t*bound).min()) if keep.any() else np.inf)
 assert minimum>=-1e-12
 center=s.height_gradient(np.array([0.]),np.array([0.]));assert center[1][0]==0 and center[2][0]==0
 # A fixed central transverse section records the actual gradient sign change.
 v=np.linspace(-.95*b,.95*b,65);sec=s.section(v,'y');positive=v>0;inner=positive&(v<.4*b);outer=v>.8*b;assert (sec['gradient'][inner,1]>0).all() and (sec['gradient'][outer,1]<0).all()
 for axis in ['x','y']:
  v=np.linspace(-(a if axis=='x' else b),(a if axis=='x' else b),65);sect=s.section(v,axis)
  for k,val in sect.items():arrays[item['key']+'_'+axis+'_'+k]=val
 for k in ['X','Y','inside','back','outward_normal','exit_direction','complete']:arrays[item['key']+'_'+k]=q[k]
 records.append(dict(case=item['key'],global_M=s.slope_bound,maximum_height=s.maximum_height,certified_clearance_rate=bound,gradient_error=float(err),sampled_clearance_excess_min=minimum,inside_rule_exact=True,mirror_pose_scale_pass=True,exact_poles_unresolved=True,inner_outward_height_gradient_and_outer_inward_gradient=True))
# Independent direct radial algebra, with the exact hypot/r*r domain convention.
class RadialDirect:
 maximum_height=.121*.4/(.121+.4);slope_bound=.88
 def boundary_mask(self,x,y):return np.hypot(x,y)==1
 def height_gradient(self,x,y):
  global external_heights
  x,y=np.broadcast_arrays(x,y);external_heights+=x.size;r=np.hypot(x,y);T=r*r;inside=r<=1;u=np.where(inside,.4*(1-T)*(.1+T),0.);v=.4*np.maximum(1-T,0.);total=u+v;h=np.divide(u*v,total,out=np.zeros_like(u),where=total>0);du=.4*(.9-2*T);dv=-.4;dh=np.divide(v*v*du+u*u*dv,total*total,out=np.zeros_like(u),where=total>0);return h,dh*2*x,dh*2*y,inside
ry,rx=np.mgrid[-.91:.92:9j,-.93:.94:9j];circle=trace(RaisedBack((1.,1.),radial_fixture=True),rx,ry);direct=trace(RadialDirect(),rx,ry);ce=max(float(abs(circle[k]-direct[k]).max()) for k in ['X','Y']);assert ce<1e-12
poles=trace(RaisedBack((1.,1.),radial_fixture=True),np.array([1.,-1.,0.,0.]),np.array([0.,0.,1.,-1.]));assert not poles['complete'].any()
assert surface.height_evaluations+external_heights<=100000 and time.time()<end
np.savez_compressed(P/'geometry-arrays.npz',**arrays)
result=dict(status='RAISED_BACK_PRIMARY_GEOMETRY_CHECKPOINT_PASS',records=records,circle_fixture_max_error=ce,new_fixture_comparator_rays=rays,new_height_evaluations=surface.height_evaluations+external_heights,new_native_rays=0,RGB_queries=0,images=0,fits=0,cumulative_fixture_comparator_rays=8182+rays,cumulative_native_rays=7473600,cumulative_images=4,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),limitations='Primary flat-front certificate only. Nonconvex solid not supplied to next_convex_boundary. No source sampling, image fidelity or full-native mask rerender.')
(P/'geometry-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
