"""Geometry-only diagnostic: no source fitting or image score changes."""
import sys,json,copy,hashlib
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np
from extended_fit import Study
from switch_curvature_cap import cap_mode,CurvatureCapStudy
from switch_crown_geometry import CrownGeometry
root=Path('/evidence/extended/active-switch');out=root/'rev6-curvature-cap';model=json.loads((root/'rev5-joint-existing/candidate.json').read_text());p=model['parameters'];rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);half=s.half+np.array([p['half_x_delta'],p['half_y_delta']]);cx,cy=p['shape_dx'],p['shape_dy'];g=CrownGeometry(half,p['crown_softness']);theta=np.arange(8192)*2*np.pi/8192;bx,by=g.radial_boundary(theta);k=g.curvature(bx,by)
 x,y=np.meshgrid(np.linspace(-half[0],half[0],201)+cx,np.linspace(-half[1],half[1],141)+cy)
 dx,dy=cap_mode(s,x,y,p);mode=np.stack([dx,dy],-1);active=np.hypot(dx,dy)>1e-10
 derivatives=[]
 for key in [*[f'c{i}' for i in range(7)],'core_x','core_y']:
  a=copy.deepcopy(p);b=copy.deepcopy(p);a[key]+=.001;b[key]-=.001
  A=s.geometry_field(x,y,a);B=s.geometry_field(x,y,b);derivatives.append(np.stack([(A[0]-B[0])/.002,(A[1]-B[1])/.002],-1)[active].ravel())
 for index in range(3):
  a=copy.deepcopy(p);b=copy.deepcopy(p);a['cap_edge_profile'][index]+=.001;b['cap_edge_profile'][index]-=.001
  A=s.geometry_field(x,y,a);B=s.geometry_field(x,y,b);derivatives.append(np.stack([(A[0]-B[0])/.002,(A[1]-B[1])/.002],-1)[active].ravel())
 A=np.array(derivatives).T;inside=s.shape(x,y,p)[-1][0][active]<-1e-6;inner_A=A.reshape(-1,2,len(derivatives))[inside].reshape(-1,len(derivatives));inner_target=mode[active][inside].ravel();inner_fit=np.linalg.lstsq(inner_A,inner_target,rcond=1e-10)[0];interior_remaining=float(np.linalg.norm(inner_target-inner_A@inner_fit)/np.linalg.norm(inner_target));norm=np.linalg.norm(A,axis=0);A=A/np.maximum(norm,1e-30);target=mode[active].ravel();co=np.linalg.lstsq(A,target,rcond=1e-10)[0];remaining=float(np.linalg.norm(target-A@co)/np.linalg.norm(target))
 # Reflection/90degree rotation/scaling and explicit radial-circle invariance.
 ma=cap_mode(s,2*cx-x,y,p);mirror=float(max(abs(ma[0]+dx).max(),abs(ma[1]-dy).max()));print("MIRROR_DIAG",mirror,"maxpoint",np.unravel_index(np.argmax(abs(ma[0]+dx)),dx.shape),flush=True);assert mirror<1e-10
 class Rotated:
  case=s.case
  def shape(self,xx,yy,pp):
   a,b,h,r,(sd,nx,ny)=s.shape(yy,-xx,pp);return -b,a,h[::-1],r,(sd,-ny,nx)
 rx,ry=cap_mode(Rotated(),-y,x,p);rotation=float(max(abs(rx+dy).max(),abs(ry-dx).max()));assert rotation<1e-10
 scale=3.1
 class Scaled:
  case=s.case
  def shape(self,xx,yy,pp):
   a,b,h,r,(sd,nx,ny)=s.shape(xx/scale,yy/scale,pp);return a*scale,b*scale,h*scale,r*scale,(sd*scale,nx,ny)
 sp=copy.deepcopy(p);sp['cap_edge_profile']=(np.asarray(p['cap_edge_profile'])*scale).tolist();sx,sy=cap_mode(Scaled(),x*scale,y*scale,sp);scaling=float(max(abs(sx-dx*scale).max(),abs(sy-dy*scale).max()));assert scaling<1e-9
 class Radial:
  case={'radial':True}
  def shape(self,xx,yy,pp):return s.shape(xx,yy,pp)
 radial=cap_mode(Radial(),x,y,p);assert not np.any(radial)
 q=CurvatureCapStudy(s.folder);A=s.geometry_field(x,y,p);B=q.geometry_field(x,y,p);zero=all(np.array_equal(a,b) for a,b in zip(A,B));assert zero
 row=dict(observation=name.upper(),active_nodes=int(active.sum()),boundary_curvature_over_L_range=[float(k.min()*min(half)),float(k.max()*min(half))],independent_mode_norm_fraction=remaining,inside_footprint_independent_fraction=interior_remaining,sample_max_added_displacement_per_unit_lambda=float(np.hypot(dx,dy).max()),mirror_error=mirror,rotation_error=rotation,scale_error=scaling,circle_zero=True,zero_map_exact=zero,projection_scope='Existing7normal+2center+3cap map derivatives on declared active grid; no image/source/target residual involved')
 rows.append(row);print(json.dumps(row),flush=True)
report=dict(method=__doc__,observations=rows,provenance={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),Path('/evidence/extended/switch_curvature_cap.py'),Path('/evidence/extended/switch_crown_geometry.py')]},limits='Discrete geometry diagnostics, not a full source-domain proof or independent physical-surface identification; no optical score/pass.')
with (out/'geometry-audit-interior.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
