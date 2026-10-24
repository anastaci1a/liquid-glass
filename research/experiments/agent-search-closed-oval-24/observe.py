"""One shared closed ellipsoid primary-path discriminator; no tracing fork."""
from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np
O=Path(__file__).resolve().parent;ROOT=O.parents[2];B=O.parent/'agent-music-search-baseline-01';WORK=ROOT/'.evidence-working/music-search-baseline-01'
P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clock(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if checkpoint else 'deadline'].replace('Z','+00:00')),'Original deadline'
def save(f,v):clock();(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):clock();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
assert not (O/'started.json').exists(),'Single setting, no retry'
assert json.loads((O/'input-identity-FIRST.json').read_text())['all_frozen_bytes_match']
save('started.json',{'at':now()});result={'status':'STARTING','ledger':ledger}
try:
 sys.path.insert(0,str(ROOT/'reconstruction'))
 import geometric_optics as go
 R=P['surface']['R'];depth=P['surface']['depth'];center=np.array(P['surface']['center']);L=P['surface']['L']
 class RadiusOval:
  def __init__(self):self.base=go.ClosedCircularOval(depth=depth,kappa=0.)
  @property
  def half_extents(self):return (R,R,depth)
  @property
  def center(self):return self.base.center
  def level_gradient(self,points):
   points=np.asarray(points,float);charge('level_points',points.size//3)
   scaled=points.copy();scaled[...,:2]/=R;F,g=self.base.level_gradient(scaled);g[...,:2]/=R;return F,g
  def front_height(self,x,y):return self.base.front_height(np.asarray(x)/R,np.asarray(y)/R)
  def boundary_mask(self,x,y):return self.base.boundary_mask(np.asarray(x)/R,np.asarray(y)/R)
 surface=RadiusOval()
 def trace(x,y,index,native=False):
  N=np.broadcast_arrays(x,y)[0].size;charge('native_rays' if native else 'fixture_rays',N);assert ledger['level_points']+70*N<=P['caps']['level_points'],'Pre-reserved level budget'
  return go.trace_closed_orthographic(surface,x,y,index,2.,tolerance=1e-11,max_iterations=64)
 # Unit-index straight paths, mirrored physical normals/paths, exact projected poles.
 x=np.array([-.8,-.2,.3,.8]*4)*R;y=np.repeat([-.3,0.,.2,.5],4)*R
 u=trace(x,y,1.);assert u['complete'].all();np.testing.assert_allclose(u['X'],x,atol=1e-9,rtol=0);np.testing.assert_allclose(u['Y'],y,atol=1e-9,rtol=0)
 a=trace(x,y,1.5);b=trace(-x,-y,1.5);assert np.array_equal(a['complete'],b['complete']);assert np.array_equal(a['blocked'],b['blocked'])
 for key in ['X','Y']:np.testing.assert_allclose(b[key],-a[key],atol=1e-9,rtol=0,equal_nan=True)
 np.testing.assert_allclose(b['entry'][...,:2],-a['entry'][...,:2],atol=1e-12,rtol=0)
 poles=trace(np.array([R,-R,0,0,R*1.1,-R*1.1,0,0]),np.array([0,0,R,-R,0,0,R*1.1,-R*1.1]),1.5)
 assert poles['boundary_unresolved'][:4].all() and np.isnan(poles['X'][:4]).all() and not poles['complete'][:4].any();assert poles['complete'][4:].all()
 assert max(abs(a['exit_level_residual']).max(),abs(u['exit_level_residual']).max())<1e-8
 np.savez_compressed(O/'fixture-paths.npz',x=x,y=y,**a)
 clock(True);save('checkpoint.json',{'at':now(),'status':'PASS_ELLIPSOID_RADIUS_UNIT_INDEX_MIRROR_AND_PROJECTED_TANGENCY','fixture_rays':ledger['fixture_rays'],'central_thickness':2*depth,'input_bytes_verified_before_controls':True,'convexity':'Positive definite diagonal Hessian of one shared radius-scaled kappa0 quadratic. Boundary gradient never zero. No concavity/height-front shortcut.','ledger':ledger.copy()});print('CHECKPOINT_PASS',now(),flush=True)
 crop=json.loads((WORK/'a/case.json').read_text())['crop'];x0,y0,x1,y1=crop;H,W=y1-y0,x1-x0;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-center[0])/L;y=(yy-.25-center[1])/L
 save('native-reservation.json',{'at':now(),'rays':int(x.size),'level_points_reserved':70*int(x.size),'previous_level_points':ledger['level_points']})
 q=trace(x,y,1.5,True);np.savez_compressed(O/'native-paths.npz',**q)
 inside=q['inside'];regular=q['regular_entry'];tir=q['blocked'];incomplete=regular&~q['complete'];nondown=incomplete&~tir;required_rows=[]
 for k in ['a','b']:
  m=np.load(B/f'{k}-masks.npz',allow_pickle=False);required=inside|np.repeat(np.repeat(m['required'],2,0),2,1)
  required_rows.append({'reference':k,'required_subrays':int(required.sum()),'incomplete_required_primary':int((required&~q['complete']).sum()),'blocked_required':int((required&tir).sum()),'original_partial_glass_pixels_preserved':38,'scoring_masks_unchanged':True})
 save('primary-path-gate.json',{'status':'INCOMPLETE_NO_RGB' if incomplete.any() else 'PRIMARY_COMPLETE_SOURCE_GATE_PENDING','records':required_rows,'native_regular':int(regular.sum()),'TIR_or_critical':int(tir.sum()),'other_incomplete_regular':int(nondown.sum()),'unresolved_projection':int(q['boundary_unresolved'].sum()),'complete_regular':int((regular&q['complete']).sum()),'scope':'Blocked is shared Snell discriminant<=0. It means a real continued-reflection branch, not invalid ellipsoid geometry. Transmitted-first tracer does not follow it.'})
 # Optional actual direct-front directions only, under aggregate100k entry cap.
 # No Fresnel or emitter call; no radiance is assigned to any direction.
 N=int(regular.sum());charge('direct_front_entries',N);normal=q['entry_normal'][regular];incident=np.zeros_like(normal);incident[:,2]=-1
 reflected=go.reflect_direction(incident,normal);front=q['entry'][regular];down=reflected[:,2]<0;up=reflected[:,2]>0;lateral=~(down|up)
 endpoint=np.full_like(reflected,np.nan);t=np.full(N,np.nan);t[down]=(-2-front[down,2])/reflected[down,2];assert (t[down]>0).all();endpoint[down]=front[down]+t[down,None]*reflected[down]
 np.savez_compressed(O/'direct-front-directions.npz',entry=front,outward_normal=normal,reflected_direction=reflected,downward=down,upward=up,lateral=lateral,background_endpoint=endpoint)
 # Only known-mask corner lookups, never background RGB or environment assignment.
 from PIL import Image
 roles=[]
 for k in ['a','b']:
  known=np.asarray(Image.open(WORK/k/'known.png'))>0;X=endpoint[down,0]*L+center[0];Y=endpoint[down,1]*L+center[1];aa=np.floor(X).astype(np.int64);bb=np.floor(Y).astype(np.int64)
  bounds=np.isfinite(X)&np.isfinite(Y)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);idx=np.flatnonzero(bounds);support=np.zeros(len(X),bool);charge('known_corner_lookups',4*len(idx))
  support[idx]=known[bb[idx],aa[idx]]&known[bb[idx]+1,aa[idx]]&known[bb[idx],aa[idx]+1]&known[bb[idx]+1,aa[idx]+1]
  roles.append({'reference':k,'downward_plane_endpoints':len(X),'out_of_bounds':int((~bounds).sum()),'raw_four_corner_supported':int(support.sum()),'unsupported':int((~support).sum()),'RGB_queries':0,'infinite_environment_not_used_for_downward':True})
 save('direct-front-role-review.json',{'actual_direct_front_entries':N,'upward':int(up.sum()),'downward':int(down.sum()),'lateral':int(lateral.sum()),'records':roles,'Fresnel_entries':0,'emitter_evaluations':0,'radiance_assigned':False,'scope':'Downward directions encounter the existing modeled background plane before any infinite environment; raw known-mask support only is audited. Upward environment remains unobserved.'})
 if incomplete.any():
  result['status']='INCOMPLETE_PRIMARY_TRANSPORT_ZERO_IMAGES';result['reason']='TIR/critical or other incomplete regular transmitted-first paths. Complete primary source gate cannot pass. No fields, RGB or comparisons executed.'
 else:
  result['status']='PRIMARY_COMPLETE_RADIANCE_PROTOCOL_INCOMPLETE_ZERO_IMAGES';result['reason']='Primary complete but full finite-source/radiance role integration remains unexecuted. No comparison or source support claimed.'
 result['path_counts']={'regular':int(regular.sum()),'blocked':int(tir.sum()),'other_incomplete':int(nondown.sum()),'complete':int((regular&q['complete']).sum())};result['selected_changed']=False
except Exception as exc:result['status']='STOPPED_FIRST_UNEXPECTED_INVARIANT';result['failure']=repr(exc)
finally:
 result['finished']=now();(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(O/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FINAL',result['status'],result.get('failure'),flush=True)
