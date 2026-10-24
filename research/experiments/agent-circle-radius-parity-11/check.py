"""One-shot shared-tracer parity; no source, color, or reflection operations."""
import sys,json,hashlib,datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
import geometric_optics as go
P=json.loads((OUT/'protocol.json').read_text())
assert hashlib.sha256(Path(go.__file__).read_bytes()).hexdigest()==P['shared_sha256']
assert not (OUT/'result.json').exists(), 'No rerun permitted'
ledger={'attempted_rays':0,'closed_level_points':0,'height_boundary_points':0,'per_function':{}}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def charge(key,n,cap):
    if ledger[key]+n>cap: raise RuntimeError('Budget stop: '+key)
    ledger[key]+=n

def profile(frame,event,arg):
    if event!='call': return
    name=frame.f_code.co_name
    if frame.f_code.co_filename not in (go.__file__,__file__): return
    local=frame.f_locals
    if name=='level_gradient':
        n=np.asarray(local['p']).shape[0]
        charge('closed_level_points',n,50000)
    elif name in ('height_gradient','_height_gradient','boundary_mask','front_height','nonsmooth_mask'):
        v=local.get('x',local.get('p'))
        n=np.asarray(v).size if 'x' in local else np.asarray(v).shape[0]
        charge('height_boundary_points',n,100000)
    else:return
    key=type(local.get('self')).__name__+'.'+name
    ledger['per_function'][key]=ledger['per_function'].get(key,0)+n
class ScaledFlatBack:
    """Previously approved radius chain rule, delegating all height arithmetic."""
    def __init__(self,back,R):self.back=back;self.R=R
    @property
    def maximum_height(self):return self.back.maximum_height
    @property
    def slope_bound(self):return self.back.slope_bound/self.R
    def height_gradient(self,x,y):
        h,hx,hy,inside=self.back.height_gradient(np.asarray(x)/self.R,np.asarray(y)/self.R)
        return h,hx/self.R,hy/self.R,inside
    def boundary_mask(self,x,y):return self.back.boundary_mask(np.asarray(x)/self.R,np.asarray(y)/self.R)
result={'started':now(),'merge_commit':'12e9d931dc8d5c26d3ec562392808980bc85be31','merge_remote_verified_before_tests':True,'configs':[],'status':'RUNNING'}
try:
 for R in P['radii']:
  for index in P['indices']:
   if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')):raise RuntimeError('Deadline stop')
   # Reserve the exact pair before either tracer; nested counters increment at entry.
   charge('attempted_rays',66,396)
   pts=np.array([(x*R,y*R) for x in P['grid_offsets'] for y in P['grid_offsets']]+[(s*R*x,s*R*y) for s in (1.1,1.) for x,y in ((1,0),(-1,0),(0,1),(0,-1))])
   base=go.HarmonicCircularBack(.15,.4)
   flat=ScaledFlatBack(base,R);closed=go.CircularHeightSolid(base,radius=R)
   closed.maximum_level_points=50000-ledger['closed_level_points']
   sys.setprofile(profile)
   a=go.trace_flat_front_orthographic(flat,pts[:,0],pts[:,1],index,2.)
   b=go.trace_closed_orthographic(closed,pts[:,0],pts[:,1],index,2.,tolerance=1e-11,max_iterations=64)
   sys.setprofile(None)
   name=f'config-{len(result["configs"]):02d}'
   np.savez_compressed(OUT/(name+'.npz'),points=pts,**{'flat_'+k:v for k,v in a.items()},**{'closed_'+k:v for k,v in b.items()})
   rec={'R':R,'index':index,'points':33,'array_file':name+'.npz','status_comparisons':{}}
   result['configs'].append(rec)
   for k in ('inside','boundary_unresolved','complete'):
    mismatch=np.flatnonzero(a[k]!=b[k]).tolist()
    rec['status_comparisons'][k]={'equal':not mismatch,'mismatch_indices':mismatch}
    if mismatch:raise AssertionError(f'{k} status mismatch at {mismatch}; first invariant failure, no retry')
   for k in ('X','Y'):
    assert np.array_equal(np.isnan(a[k]),np.isnan(b[k])),k+' NaN mismatch'
   regular=a['inside']&~a['boundary_unresolved']
   assert a['complete'][regular].all() and b['complete'][regular].all()
   errors={}
   for ka,kb in (('X','X'),('Y','Y'),('back','exit'),('outward_normal','exit_normal'),('exit_direction','exit_direction')):
    assert np.array_equal(np.isnan(a[ka][regular]),np.isnan(b[kb][regular]))
    errors[ka]=float(np.max(np.abs(a[ka][regular]-b[kb][regular])))
    assert np.allclose(a[ka][regular],b[kb][regular],atol=1e-9,rtol=0),ka+' value mismatch'
   rec['regular_max_errors']=errors
   if index==1:
    for v in (a,b):
     assert np.allclose(v['X'][regular],pts[regular,0],atol=1e-9,rtol=0)
     assert np.allclose(v['Y'][regular],pts[regular,1],atol=1e-9,rtol=0)
   if len(result['configs'])==1:
    (OUT/'checkpoint.json').write_text(json.dumps({'status':'PASS','time':now(),'ledger':ledger},indent=2)+'\n')
    # A separate execution would be a forbidden retry; continuation requires notification first.
    raise RuntimeError('CHECKPOINT_REACHED: remaining configurations not executed pending delivery boundary')
 result['status']='PASS'
except Exception as e:
 sys.setprofile(None)
 result['status']='STOPPED_FIRST_FAILURE';result['failure']=str(e)
finally:
 result['finished']=now();result['ledger']=ledger
 result['zero_work']=['source queries','RGB','filters','Fresnel','composites','images','fits']
 (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
