"""Final fixed-fixture parity through shared tracers and reviewed accounting."""
import sys,json,hashlib,datetime
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
P=json.loads((OUT/'protocol.json').read_text())
SHARED=ROOT/'reconstruction/geometric_optics.py'
CALLBACK=ROOT/'research/experiments/agent-parity-accounting-preflight-14/callback.py'
OLD=ROOT/'research/experiments/agent-membership-parity-13/check.py'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clock():
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')):raise RuntimeError('Deadline stop')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
clock();assert not (OUT/'started.json').exists(),'No retry permitted'
assert sha(SHARED)==P['shared_sha256']
assert sha(CALLBACK)==P['callback_sha256']
assert sha(OLD)==P['old_driver_sha256']
sys.path.insert(0,str(CALLBACK.parent));from callback import Counter
sys.path.insert(0,str(SHARED.parent));import geometric_optics as go
assert Path(go.__file__).resolve()==SHARED.resolve()
class ScaledFlatBack:
 """The approved radius chain rule; shared base computes actual height."""
 def __init__(self,back,R):self.back=back;self.R=R
 @property
 def maximum_height(self):return self.back.maximum_height
 @property
 def slope_bound(self):return self.back.slope_bound/self.R
 def height_gradient(self,x,y):
  h,hx,hy,inside=self.back.height_gradient(np.asarray(x)/self.R,np.asarray(y)/self.R)
  return h,hx/self.R,hy/self.R,inside
 def boundary_mask(self,x,y):return self.back.boundary_mask(np.asarray(x)/self.R,np.asarray(y)/self.R)
counter=Counter(str(SHARED),__file__)
def wall_hook(frame,event,arg):
 if event=='call':
  code=frame.f_code;owner=type(frame.f_locals.get('self')).__name__
  selected=(code.co_filename==str(SHARED) or (code.co_filename==__file__ and owner=='ScaledFlatBack') or (code.co_filename=='<string>' and owner=='HarmonicCircularBack'))
  if selected:clock()
 counter(frame,event,arg)
fixtures=[]
for R in P['radii']:
 for index in P['indices']:
  clock()
  xy=np.array([(x*R,y*R) for x in P['offsets'] for y in P['offsets']]+[(s*R*x,s*R*y) for s in (1.1,1.) for x,y in ((1,0),(-1,0),(0,1),(0,-1))])
  assert xy.shape==(33,2) and np.isfinite(xy).all()
  assert xy[:,0].shape==xy[:,1].shape==(33,)
  fixtures.append((R,index,xy))
assert len(fixtures)==6 and 6*66==P['launch_cap']
assert 6*15000<=P['nested_cap'] and 6*2000<=P['level_cap']
result={'started':now(),'status':'RUNNING','configurations':[],'reserved_launches':0,'entered_flat_launches':0,'entered_closed_launches':0,'startup_hashes_exact':True,'all_fixture_shapes_validated':True,'counter_scope':'Total includes closed-level subset; do not add the subset again.'}
(OUT/'started.json').write_text(json.dumps({'started':result['started'],'startup_validated':True,'hashes':{'shared':sha(SHARED),'callback':sha(CALLBACK),'old_driver':sha(OLD)},'fixtures':6,'optical_setup_probes':0},indent=2)+'\n')
def assert_equal(a,b,label):
 clock();assert np.array_equal(a,b),label
try:
 for ci,(R,index,xy) in enumerate(fixtures):
  clock();counter.reserve_config()
  assert result['reserved_launches']+66<=396
  result['reserved_launches']+=66
  reservation={'nested_start':counter.ledger['total'],'level_start':counter.ledger['closed_level_subset'],'nested_reserved':15000,'level_reserved':2000,'launches_reserved':66}
  rec={'R':R,'index':index,'started':now(),'reservation':reservation,'status':'STARTED'}
  result['configurations'].append(rec);a=b=None
  try:
   sys.setprofile(wall_hook)
   base=go.HarmonicCircularBack(.15,.4);flat=ScaledFlatBack(base,R);solid=go.CircularHeightSolid(base,radius=R)
   solid.maximum_level_points=2000
   result['entered_flat_launches']+=33
   a=go.trace_flat_front_orthographic(flat,xy[:,0],xy[:,1],index,2.)
   result['entered_closed_launches']+=33
   b=go.trace_closed_orthographic(solid,xy[:,0],xy[:,1],index,2.,tolerance=1e-11,max_iterations=64)
  finally:
   sys.setprofile(None);clock()
   raw={'points':xy}
   if a is not None:raw.update({'flat_'+k:v for k,v in a.items()})
   if b is not None:raw.update({'closed_'+k:v for k,v in b.items()})
   if len(raw)>1:
    filename=f'config-{ci:02d}.npz';np.savez_compressed(OUT/filename,**raw);rec['raw_arrays']=filename
   rec['flat_returned']=a is not None;rec['closed_returned']=b is not None
   rec['nested_actual']=counter.ledger['total']-reservation['nested_start']
   rec['level_actual']=counter.ledger['closed_level_subset']-reservation['level_start']
  clock();rec['status_fields']={}
  for key in ('projected_inside','regular_entry','boundary_unresolved','complete'):
   assert_equal(a[key],b[key],key+' mismatch');rec['status_fields'][key]='EXACT'
  ids=np.arange(33);regular=ids<25;clear=(ids>=25)&(ids<29);poles=ids>=29
  for q in (a,b):
   assert_equal(q['projected_inside'],regular|poles,'Unexpected inclusive membership')
   assert_equal(q['regular_entry'],regular,'Unexpected regular membership')
   assert_equal(q['boundary_unresolved'],poles,'Unexpected unresolved cohort')
   assert_equal(q['complete'],~poles,'Unexpected incomplete regular path or clear miss')
  clock();legacy=np.flatnonzero(a['inside']!=b['inside']).tolist()
  assert legacy==[29,30,31,32]
  assert a['inside'][poles].all() and not b['inside'][poles].any()
  rec['legacy_inside_differences']=legacy
  valid=a['regular_entry']&b['regular_entry']&a['complete']&b['complete']
  errors={}
  for key,col in (('X',0),('Y',1)):
   assert_equal(np.isnan(a[key]),np.isnan(b[key]),key+' global NaN pattern')
   for q in (a,b):
    assert_equal(q[key][clear],xy[clear,col],key+' clear miss identity')
    clock();assert np.isnan(q[key][poles]).all()
   clock();errors[key]=float(np.max(np.abs(a[key][valid]-b[key][valid])))
   assert np.allclose(a[key][valid],b[key][valid],atol=1e-9,rtol=0),key+' tolerance'
  for ka,kb in (('back','exit'),('outward_normal','exit_normal'),('exit_direction','exit_direction')):
   clock();aa=a[ka][valid];bb=b[kb][valid]
   assert_equal(np.isnan(aa),np.isnan(bb),ka+' regular NaN pattern')
   assert np.isfinite(aa).all() and np.isfinite(bb).all()
   errors[ka]=float(np.max(np.abs(aa-bb)))
   assert np.allclose(aa,bb,atol=1e-9,rtol=0),ka+' tolerance'
  clock();entry=np.column_stack((xy[valid],np.zeros(valid.sum())))
  assert np.allclose(b['entry'][valid],entry,atol=1e-9,rtol=0)
  clock();assert np.allclose(b['entry_normal'][valid],np.array([0.,0.,1.]),atol=1e-9,rtol=0)
  rec['max_absolute_errors']=errors
  if index==1:
   for q in (a,b):
    for key,col in (('X',0),('Y',1)):
     clock();assert np.allclose(q[key][valid],xy[valid,col],atol=1e-9,rtol=0)
    clock();assert np.allclose(q['exit_direction'][valid],np.array([0.,0.,-1.]),atol=1e-9,rtol=0)
   rec['index_one_straight']='PASS'
  clock();rec['status']='PASS';rec['finished']=now()
  if ci==0:
   checkpoint={'status':'PASS','at':now(),'configuration':rec,'reserved_launches':result['reserved_launches'],'entered_launches':result['entered_flat_launches']+result['entered_closed_launches'],'counter':counter.ledger}
   (OUT/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
   print('CHECKPOINT_JSON:'+json.dumps({'status':'PASS','at':checkpoint['at'],'rays':66,'nested':counter.ledger['total'],'levels':counter.ledger['closed_level_subset'],'errors':errors}),flush=True)
  (OUT/'progress.json').write_text(json.dumps(result,indent=2)+'\n')
 result['status']='PASS_SHARED_PRIMARY_GEOMETRY_CONTRACT_ONLY'
except Exception as exc:
 sys.setprofile(None);result['status']='STOPPED_FIRST_FAILURE';result['failure']=repr(exc)
finally:
 sys.setprofile(None)
 result['finished']=now();result['counter']=counter.ledger
 result['zero_work']=['source queries','RGB','filters','Fresnel','composites','images','fits','reflected branches','environment']
 (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print('FINAL_JSON:'+json.dumps({'status':result['status'],'failure':result.get('failure'),'configurations':len(result['configurations']),'reserved_launches':result['reserved_launches'],'entered_flat_launches':result['entered_flat_launches'],'entered_closed_launches':result['entered_closed_launches'],'counter':counter.ledger}),flush=True)
