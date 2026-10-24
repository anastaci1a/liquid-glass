from pathlib import Path
import sys,json,datetime,hashlib,functools
import numpy as np,cv2
O=Path(__file__).resolve().parent;ROOT=O.parents[2];B=O.parent/'agent-music-search-baseline-01';T=O.parent/'agent-music-search-neutral-05';WORK=ROOT/'.evidence-working/music-search-baseline-01';P=json.loads((O/'protocol.json').read_text());ledger=json.loads((O/'ledger.json').read_text()) if (O/'ledger.json').exists() else {k:0 for k in P['caps']}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Original clock'
def save(f,v):gate();(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert sha(ROOT/f)==h,'Frozen input/code'
sys.path.insert(0,str(ROOT/'reconstruction'))
import raised_front_optics as ro,geometric_optics as go
from spline_height_back import SplineFootprintBack
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from hermite_height_back import HermiteFootprintBack
from extended_fit import Study
from geometric_render import neutral_color_response,incident_source_filter
from environment_radiance import annular_environment,decode_srgb,encode_srgb
cv2.setNumThreads(1)
def instrument(cls,name,nargs=2):
 old=getattr(cls,name)
 @functools.wraps(old)
 def counted(self,*args,**kw):
  a=np.broadcast_arrays(*[np.asarray(x) for x in args[:nargs]])[0];charge('nested_units',a.size);return old(self,*args,**kw)
 setattr(cls,name,counted)
for cls in [SplineFootprintBack,HermiteFootprintBack,ro.VerticalScaleBack]:
 for method in ['height_gradient','boundary_mask']:instrument(cls,method)
instrument(HermiteFootprintBack,'profile',1);instrument(RoundedRectangleHarmonicBack,'footprint')
for name in ['refract','reflect_direction','fresnel_components','escape_clearance']:
 old=getattr(ro,name)
 def primitive(*args,_fn=old,_name=name,**kw):
  n=np.asarray(args[0]).size if _name=='fresnel_components' else np.asarray(args[0]).size//3;charge('nested_units',n);return _fn(*args,**kw)
 setattr(ro,name,primitive)
F=json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text());g=F['geometry'];Rf=g['corner_radius'];R=.9972124917582454;s=R/Rf;D=2.0850423023221105;center=np.array([1511.2043368857017,672.8753258356955]);L=89;model=json.loads((ROOT/'research/experiments/miniplayer-inverse-geometry-17/back-profile.json').read_text())
def build(half,radius,scale):
 charge('nested_units',4096);base=SplineFootprintBack(half,radius,g['breaks'],np.array(g['height_controls'])*scale,cap_join_width=0);m={**model,'radius_nodes':(np.array(model['radius_nodes'])/Rf*radius).tolist(),'heights':(np.array(model['heights'])*scale).tolist()};back=HermiteFootprintBack(base,m);front=ro.VerticalScaleBack(base,.5);return base,back,front
base,back,front=build((R,R),R,s)
def trace(b,f,x,y,D,n=1.5,native=False):
 N=np.broadcast_arrays(x,y)[0].size;charge('native_rays' if native else 'fixture_parity_records',N);charge('nested_units',N);return ro.trace_raised_front_orthographic(b,x,y,1.,n,D,front_surface=f)
def studies():
 data={}
 for k in ['a','b']:
  st=Study(WORK/k);m=dict(np.load(B/f'{k}-masks.npz',allow_pickle=False));old=np.load(T/f'full-{k}-candidate.npz',allow_pickle=False);assert np.array_equal(st.valid,m['glass']) and np.array_equal(st.rim,m['rim']) and np.array_equal(st.held,m['held']);data[k]={'s':st,'m':m,'old':old}
 return data
if __name__=='__main__':
 assert not (O/'checkpoint.json').exists(),'No fixture retry';status={'status':'STARTING'}
 try:
  data=studies()
  for k,d in data.items():
   charge('selected_foreground_identities',1);C=d['s'].apply_foreground(d['old']['pre_foreground'].copy());assert np.array_equal(C,d['old']['complete'],equal_nan=True)
  cb,bb,ff=build((F['members']['expanded']['major_half'],g['minor_half']),Rf,1.)
  corner=np.array([cb.half[0]-Rf,cb.half[1]-Rf]);rho=np.repeat([.45,.6,.8,.95],4);theta=np.tile([.2,.5,.8,1.2],4);v=Rf*rho[:,None]*np.stack([np.cos(theta),np.sin(theta)],1);records=[]
  for n in [1.,1.5]:
   old=trace(bb,ff,v[:,0]+corner[0],v[:,1]+corner[1],2.1,n);new=trace(back,front,v[:,0]*s,v[:,1]*s,D,n)
   assert old['complete'].all() and new['complete'].all()
   for key in ['X','Y']:j=0 if key=='X' else 1;np.testing.assert_allclose(new[key],s*(old[key]-corner[j]),atol=1e-9,rtol=0)
   for key in ['front_normal','outward_normal','interior_direction','exit_direction']:np.testing.assert_allclose(new[key],old[key],atol=1e-9,rtol=0)
   for key in ['front','back']:
    mapped=old[key].copy();mapped[:,:2]-=corner;mapped*=s;np.testing.assert_allclose(new[key],mapped,atol=1e-9,rtol=0)
   records.append({'index':n,'canonical_corner_scale_positions_normals_exact_within_1e9':True})
  gate(True);status={'status':'PASS_FROZEN_INPUTS_TWO_FOREGROUND_IDENTITIES_AND_CORNER_SCALE','at':now(),'fixtures':records,'ledger':ledger.copy()};save('checkpoint.json',status);print('CHECKPOINT_PASS',now(),flush=True)
 except Exception as e:status={'status':'STOPPED_FIRST_IDENTITY_OR_FIXTURE','failure':repr(e),'at':now()};save('checkpoint-failure.json',status);print('STOP',repr(e),flush=True)
 finally:save('ledger.json',ledger)
