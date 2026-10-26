"""Bounded geometry controls; durable protocol and results before native work."""
from pathlib import Path
import json,datetime,traceback
import numpy as np
from shoulder_core_coordinate import ShoulderCoreCoordinate,ShoulderCoreSplineBack
from ellipse_core_coordinate import EllipseCoreCoordinate
from raised_front_optics import VerticalScaleBack,trace_raised_front_orthographic
from hermite_height_back import HermiteFootprintBack
OUT=Path(__file__).parent;ROOT=OUT.parents[2];records=[]
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
save('geometry-controls-start.json',{'start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'maximum_points':100000,'maximum_fixture_rays':256,'deadline':'2026-10-26T06:02:24+00:00'})
try:
 F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels'];g=F['geometry'];R=g['corner_radius']-1.25/L
 for member in ['expanded','compact']:
  half=(F['members'][member]['major_half']+1.5/L,g['minor_half']);c=ShoulderCoreCoordinate(half,R,1./L)
  t=np.linspace(0,np.pi/2,257);h,hp,hpp=c.support(t);n=np.stack([np.cos(t),np.sin(t)],-1);tan=np.stack([-np.sin(t),np.cos(t)],-1);p=h[:,None]*n+hp[:,None]*tan
  assert np.min(h+hpp)>0
  worst=0.
  for shift in [.001,.1,c.radius,c.radius+.2]:
   q=p+shift*n;d,nx,ny=c.distance_gradient(q[:,0],q[:,1]);err=max(np.max(abs(d-shift)),np.max(abs(nx-n[:,0])),np.max(abs(ny-n[:,1])));worst=max(worst,float(err));assert err<1e-9
  grid=np.linspace(-1.1,1.1,121);xx,yy=np.meshgrid(grid*half[0],grid*half[1]);d,nx,ny=c.distance_gradient(xx,yy)
  assert np.max(abs(d-d[::-1]))<1e-10 and np.max(abs(d-d[:,::-1]))<1e-10
  eps=1e-6;good=(d>.01)&(np.abs(xx)>.01)&(np.abs(yy)>.01)
  dx=(c.distance_gradient(xx+eps,yy)[0]-c.distance_gradient(xx-eps,yy)[0])/(2*eps);dy=(c.distance_gradient(xx,yy+eps)[0]-c.distance_gradient(xx,yy-eps)[0])/(2*eps)
  graderr=max(float(np.max(abs(dx[good]-nx[good]))),float(np.max(abs(dy[good]-ny[good]))));assert graderr<1e-7
  base=ShoulderCoreSplineBack(half,R,1/L,g['breaks'],g['height_controls']);prof=json.loads((ROOT/g['back_profile']).read_text());scale=base.radius/prof['radius_nodes'][-1];prof['radius_nodes']=(np.array(prof['radius_nodes'])*scale).tolist();prof['radius_nodes'][-1]=base.radius;prof['derivatives']=(np.array(prof['derivatives'])/scale).tolist();back=HermiteFootprintBack(base,prof);front=VerticalScaleBack(base,g['front_scale'])
  q=p+(.7*c.radius)*n;ids=np.arange(1,257,8);q=q[ids]
  out=trace_raised_front_orthographic(back,q[:,0],q[:,1],1,1,F['optics']['background_distance'],front_surface=front)
  assert out['complete'].all();identity=max(float(np.max(abs(out['X']-q[:,0]))),float(np.max(abs(out['Y']-q[:,1]))));assert identity<1e-9
  records.append(dict(member=member,projection_error=worst,gradient_error=graderr,unit_index_error=identity,fixture_rays=len(ids),core_minimum_curvature=float(np.min(h+hpp)),rolling_radius=c.radius))
 save('geometry-controls-result.json',{'passed':True,'records':records,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 print(json.dumps(records),flush=True)
except Exception as e:
 save('geometry-controls-failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'records':records,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});raise
