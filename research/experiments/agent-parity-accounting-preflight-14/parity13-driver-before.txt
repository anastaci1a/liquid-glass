"""One-shot new-contract parity, preserving both raw shared-driver outputs."""
import sys,json,hashlib,datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
import geometric_optics as go
P=json.loads((OUT/'protocol.json').read_text())
assert hashlib.sha256(Path(go.__file__).read_bytes()).hexdigest()==P['shared_sha256']
assert not (OUT/'started.json').exists(), 'No retry permitted'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def deadline():
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')):raise RuntimeError('Deadline stop')
ledger={'attempted_rays':0,'closed_level_points':0,'nested_interface_points':0,'per_function':{},'reservations':[]}
active=None
def profile(frame,event,arg):
 if event!='call' or frame.f_code.co_filename not in (go.__file__,__file__):return
 name=frame.f_code.co_name;v=frame.f_locals
 if name in ('height_gradient','_height_gradient','boundary_mask','front_height','trace_flat_front_orthographic','trace_closed_orthographic'):n=np.asarray(v['x']).size
 elif name in ('level_gradient','nonsmooth_mask'):n=np.asarray(v['p']).shape[0]
 elif name=='next_convex_boundary':n=np.asarray(v['points']).shape[0]
 elif name=='harmonic_cap':n=np.asarray(v['first']).size
 elif name=='refract':n=np.asarray(v['incident']).reshape(-1,3).shape[0]
 elif name=='<lambda>' and 'v' in v:n=np.asarray(v['v']).shape[0]
 elif name in ('maximum_height','slope_bound','__post_init__','__init__'):n=1
 elif frame.f_code.co_filename==go.__file__:raise RuntimeError('Unaccounted shared call '+name)
 else:return
 deadline()
 if ledger['nested_interface_points']+n>P['nested_interface_cap']:raise RuntimeError('Nested cap')
 if active is not None and ledger['nested_interface_points']+n-active['nested_start']>15000:raise RuntimeError('Nested reservation exceeded')
 if name=='level_gradient':
  if ledger['closed_level_points']+n>P['closed_level_cap'] or ledger['closed_level_points']+n-active['level_start']>2000:raise RuntimeError('Level reservation exceeded')
  ledger['closed_level_points']+=n
 ledger['nested_interface_points']+=n
 key=type(v.get('self')).__name__+'.'+name
 ledger['per_function'][key]=ledger['per_function'].get(key,0)+n
class ScaledFlatBack:
 """Approved exact radius chain rule; all base height arithmetic is shared."""
 def __init__(self,back,R):self.back=back;self.R=R
 @property
 def maximum_height(self):return self.back.maximum_height
 @property
 def slope_bound(self):return self.back.slope_bound/self.R
 def height_gradient(self,x,y):
  h,hx,hy,inside=self.back.height_gradient(np.asarray(x)/self.R,np.asarray(y)/self.R)
  return h,hx/self.R,hy/self.R,inside
 def boundary_mask(self,x,y):return self.back.boundary_mask(np.asarray(x)/self.R,np.asarray(y)/self.R)
result={'started':now(),'status':'RUNNING','configs':[],'counter_scope':'Closed levels are a subset of total nested interface points; never add them twice.'}
(OUT/'started.json').write_text(json.dumps({'started':result['started'],'merge_remote_verified':json.loads((OUT/'merge-verification.json').read_text())},indent=2)+'\n')
try:
 for R in P['radii']:
  for index in P['indices']:
   deadline()
   if ledger['attempted_rays']+66>P['ray_cap'] or ledger['nested_interface_points']+15000>P['nested_interface_cap'] or ledger['closed_level_points']+2000>P['closed_level_cap']:raise RuntimeError('Cannot reserve configuration')
   active={'R':R,'index':index,'reserved_at':now(),'rays':66,'nested':15000,'level':2000,'nested_start':ledger['nested_interface_points'],'level_start':ledger['closed_level_points']}
   ledger['reservations'].append(active)
   ledger['attempted_rays']+=66
   pts=np.array([(x*R,y*R) for x in P['offsets'] for y in P['offsets']]+[(s*R*x,s*R*y) for s in (1.1,1.) for x,y in ((1,0),(-1,0),(0,1),(0,-1))])
   sys.setprofile(profile)
   base=go.HarmonicCircularBack(.15,.4);flat=ScaledFlatBack(base,R);closed=go.CircularHeightSolid(base,radius=R)
   closed.maximum_level_points=2000
   a=go.trace_flat_front_orthographic(flat,pts[:,0],pts[:,1],index,2.)
   b=go.trace_closed_orthographic(closed,pts[:,0],pts[:,1],index,2.,tolerance=1e-11,max_iterations=64)
   sys.setprofile(None)
   active['actual_nested']=ledger['nested_interface_points']-active['nested_start'];active['actual_level']=ledger['closed_level_points']-active['level_start']
   name=f'config-{len(result["configs"]):02d}'
   np.savez_compressed(OUT/(name+'.npz'),points=pts,**{'flat_'+k:v for k,v in a.items()},**{'closed_'+k:v for k,v in b.items()})
   rec={'R':R,'index':index,'arrays':name+'.npz','status':'CHECKING','status_comparisons':{}};result['configs'].append(rec)
   for k in P['status_fields_exact']:
    mismatch=np.flatnonzero(a[k]!=b[k]).tolist();rec['status_comparisons'][k]={'equal':not mismatch,'mismatches':mismatch}
    assert not mismatch,k+' mismatch'
   expected_regular=np.arange(33)<25;expected_boundary=np.arange(33)>=29;clear=(np.arange(33)>=25)&(np.arange(33)<29)
   for q in (a,b):
    assert np.array_equal(q['regular_entry'],expected_regular),'Unexpected regular cohort'
    assert np.array_equal(q['projected_inside'],expected_regular|expected_boundary),'Unexpected footprint'
    assert np.array_equal(q['boundary_unresolved'],expected_boundary),'Unexpected boundary'
    assert q['complete'][expected_regular].all(),'Incomplete regular path'
    assert q['complete'][clear].all() and not q['complete'][expected_boundary].any()
   legacy=np.flatnonzero(a['inside']!=b['inside']).tolist();rec['legacy_inside_differences']=legacy
   assert legacy==[29,30,31,32],'Legacy differences spread or changed'
   assert a['inside'][expected_boundary].all() and not b['inside'][expected_boundary].any()
   valid=a['regular_entry']&b['regular_entry']&a['complete']&b['complete'];errors={}
   for key,axis in (('X',0),('Y',1)):
    assert np.array_equal(np.isnan(a[key]),np.isnan(b[key])),key+' NaN pattern'
    for q in (a,b):
     assert np.array_equal(q[key][clear],pts[clear,axis]),'Clear miss not exact identity'
     assert np.isnan(q[key][expected_boundary]).all(),'Tangent source not NaN'
    errors[key]=float(np.max(np.abs(a[key][valid]-b[key][valid])))
    assert np.allclose(a[key][valid],b[key][valid],atol=1e-9,rtol=0)
   for ka,kb in (('back','exit'),('outward_normal','exit_normal'),('exit_direction','exit_direction')):
    assert np.array_equal(np.isnan(a[ka][valid]),np.isnan(b[kb][valid]))
    assert np.isfinite(a[ka][valid]).all() and np.isfinite(b[kb][valid]).all()
    errors[ka]=float(np.max(np.abs(a[ka][valid]-b[kb][valid])))
    assert np.allclose(a[ka][valid],b[kb][valid],atol=1e-9,rtol=0),ka+' mismatch'
   # Flat front has exact analytic entry coordinates and outward normal, no extra trace.
   expected_entry=np.column_stack((pts[valid],np.zeros(valid.sum())))
   assert np.allclose(b['entry'][valid],expected_entry,atol=1e-9,rtol=0)
   assert np.allclose(b['entry_normal'][valid],np.array([0.,0.,1.]),atol=1e-9,rtol=0)
   rec['regular_max_absolute_errors']=errors
   if index==1:
    for q in (a,b):
     assert np.allclose(q['X'][valid],pts[valid,0],atol=1e-9,rtol=0)
     assert np.allclose(q['Y'][valid],pts[valid,1],atol=1e-9,rtol=0)
     assert np.allclose(q['exit_direction'][valid],np.array([0.,0.,-1.]),atol=1e-9,rtol=0)
    rec['index_one_straight']='PASS'
   rec['status']='PASS';rec['finished']=now()
   (OUT/'progress.json').write_text(json.dumps({'configs':result['configs'],'ledger':ledger},indent=2)+'\n')
   if len(result['configs'])==1:
    (OUT/'checkpoint.json').write_text(json.dumps({'status':'PASS','at':now(),'configuration':rec,'ledger':ledger},indent=2)+'\n')
    print('CHECKPOINT_PASS: first nonunit index1; same process awaits notification boundary',flush=True)
    if input().strip()!='continue-same-task':raise RuntimeError('Checkpoint continuation not received')
    deadline()
 result['status']='PASS_SHARED_PRIMARY_GEOMETRY_ONLY'
except Exception as e:
 sys.setprofile(None);result['status']='STOPPED_FIRST_FAILURE';result['failure']=repr(e)
finally:
 sys.setprofile(None);result['finished']=now();result['ledger']=ledger
 result['zero_work']=['source queries','RGB','filters','Fresnel','composites','images','fits','other fixtures']
 (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'configs':len(result['configs']),'failure':result.get('failure'),'ledger':ledger},indent=2),flush=True)
