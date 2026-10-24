"""Budgeted radius contract controls; no RGB, source or fitted geometry."""
from pathlib import Path
import datetime,hashlib,json,subprocess,types,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
import geometric_optics as new
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline_utc'].replace('Z','+00:00'))
assert not (P/'result.json').exists(),'No repeat'
source=subprocess.check_output(['git','show',p['base_commit']+':reconstruction/geometric_optics.py'],cwd=ROOT).decode()
old=types.ModuleType('preserved_geometric_optics');sys.modules[old.__name__]=old;exec(compile(source,'preserved_geometric_optics.py','exec'),old.__dict__)
count={'fixture_configurations':0,'ordered_segment_rays':0,'height_control_points':0};solids=[]
def gate():assert datetime.datetime.now(datetime.timezone.utc)<end

def counted(cls):
 class Counted(cls):
  def height_gradient(self,x,y):
   n=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size
   assert count['height_control_points']+n<=p['caps']['height_control_points']
   count['height_control_points']+=int(n)
   return super().height_gradient(x,y)
 return Counted

def back(module,name):
 cls=counted(getattr(module,name))
 return cls([0.,.5,1.],[0.,.2,.4]) if name=='RadialCurvatureBack' else cls()

rows=[];fdmax=0.;maxres=0.;maxbracket=0.
for name in ['HarmonicCircularBack','CircularBevel','RadialCurvatureBack']:
 for R in [1.,.9972124917582454,.5,2.]:
  gate();count['fixture_configurations']+=1;f=back(new,name);solid=new.CircularHeightSolid(f,radius=R);solids.append(solid)
  solid.maximum_level_points=p['caps']['level_point_evaluations']-sum(s.level_point_evaluations for s in solids[:-1])
  xy=R*np.array([[0,0],[.2,0],[-.2,0],[0,.4],[0,-.4],[.3,.4],[-.3,.4],[.45,-.2],[-.45,-.2]])
  h,hx,hy,inside=solid._height_gradient(xy[:,0],xy[:,1]);assert inside.all() and (h>0).all()
  bh,bx,by,_=f.height_gradient(xy[:,0]/R,xy[:,1]/R)
  assert np.array_equal(h,bh) and np.array_equal(hx,bx/R) and np.array_equal(hy,by/R)
  pts=np.column_stack([xy,-h]);level,grad=solid.level_gradient(pts)
  assert np.max(abs(level))<1e-15
  assert np.array_equal(grad,np.column_stack([-hx,-hy,-np.ones(len(h))]))
  for axis in range(3):
   offset=np.zeros(3);offset[axis]=1e-6
   fp,_=solid.level_gradient(pts+offset);fm,_=solid.level_gradient(pts-offset)
   err=float(np.max(abs((fp-fm)/(2e-6)-grad[:,axis])));fdmax=max(fdmax,err);assert err<2e-8
  mid=np.column_stack([xy,-h/2]);assert (solid.level_gradient(mid)[0]<0).all()
  above=np.column_stack([xy,np.full(len(xy),.1)]);below=np.column_stack([xy,-h-.1])
  assert (solid.level_gradient(above)[0]>0).all() and (solid.level_gradient(below)[0]>0).all()
  assert np.array_equal(solid.half_extents,[R,R,f.maximum_height/2])
  assert np.array_equal(solid.center,[0,0,-f.maximum_height/2])
  assert solid.front_height(np.array([0.,R,1.1*R]),np.zeros(3))[1].tolist()==[True,False,False]
  assert solid.boundary_mask(np.array([R,-R,0.,0.]),np.array([0.,0.,R,-R])).all()
  crease=np.array([[R,0.,0.],[-R,0.,0.],[0.,R,0.],[0.,-R,0.]])
  assert solid.nonsmooth_mask(crease,1e-11).all()
  assert not solid.nonsmooth_mask(pts[:1],1e-11).any()
  if R==1.:
   preserved=old.CircularHeightSolid(back(old,name));solids.append(preserved)
   controls=np.vstack([pts,mid,above,below,crease]);a=solid.level_gradient(controls);b=preserved.level_gradient(controls)
   assert all(np.array_equal(x,y) for x,y in zip(a,b))
   assert all(np.array_equal(x,y) for x,y in zip(solid.front_height(xy[:,0],xy[:,1]),preserved.front_height(xy[:,0],xy[:,1])))
   assert np.array_equal(solid.nonsmooth_mask(controls,1e-11),preserved.nonsmooth_mask(controls,1e-11))
  start=np.column_stack([xy[:4],np.zeros(4)]);direction=np.tile([0.,0.,-1.],(4,1))
  launch=pts[4:8];normal=grad[4:8]/np.linalg.norm(grad[4:8],axis=-1)[:,None]
  reflected=new.reflect_direction(np.tile([0.,0.,-1.],(4,1)),normal)
  origins=np.vstack([start,launch]);directions=np.vstack([direction,reflected])
  assert count['ordered_segment_rays']+8<=p['caps']['ordered_segment_rays'];count['ordered_segment_rays']+=8
  event=new.next_convex_boundary(solid,origins,directions,tolerance=1e-11,max_iterations=64)
  assert event['complete'].all() and np.isfinite(event['point']).all() and np.isfinite(event['outward_normal']).all()
  assert (np.sum(directions*event['outward_normal'],axis=-1)>0).all()
  maxres=max(maxres,float(np.max(abs(event['residual']))));maxbracket=max(maxbracket,float(event['bracket'].max()))
  assert maxbracket<=1e-11
  assert sum(s.level_point_evaluations for s in solids)<=p['caps']['level_point_evaluations']
  rows.append(dict(back=name,radius=R,ordered_segments=8,regular_complete=True,unit_old_exact=R==1.,level_points=solid.level_point_evaluations))
for bad in [0.,-1.,float('nan'),float('inf')]:
 count['fixture_configurations']+=1
 try:new.CircularHeightSolid(back(new,'HarmonicCircularBack'),radius=bad)
 except ValueError:pass
 else:raise AssertionError('Invalid radius accepted')
count['level_point_evaluations']=sum(s.level_point_evaluations for s in solids)
assert count['fixture_configurations']==16 and count['ordered_segment_rays']==96
gate();out=dict(status='PASS_RADIUS_CONTRACT_NO_IMAGE',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=count,gradient_FD_max=fdmax,ordered_exit_residual_max=maxres,ordered_bracket_max=maxbracket,configurations=rows,shared_sha256=hashlib.sha256((ROOT/'reconstruction/geometric_optics.py').read_bytes()).hexdigest(),old_source_sha256=hashlib.sha256(source.encode()).hexdigest(),limits='Geometry and segment controls only. No source endpoints, RGB, full radiance or fidelity acceptance.')
(P/'result.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps(out),flush=True)
