"""Fixed fixtures for one additive geometric escape certificate."""
from pathlib import Path
import datetime,json,sys,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from music_miniplayer_family import surface_for_member
from spline_height_back import SplineFootprintBack
from hermite_height_back import HermiteFootprintBack
from raised_front_optics import VerticalScaleBack,trace_raised_front_orthographic,monotone_front_reflection_escape
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
def count(label,n):charge('surface_point_queries',n);charge('conservative_adapter_units',20*n)
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
legacy={};exec(compile((ROOT/'research/experiments/monotone-front-escape-34/baseline-tracer.py').read_text(),'immutable8a6d-comparator','exec'),legacy)
oldmodel=json.loads((ROOT/'research/experiments/miniplayer-inverse-geometry-17/back-profile.json').read_text());newmodel=json.loads((ROOT/'research/experiments/miniplayer-steeper-front-32/back-profile.json').read_text());rows=[]
for member in ['expanded','compact']:
 base=surface_for_member(member);a=base.half[0];fx,fy=np.meshgrid(np.array([-a+.2,-1.,0.,1.,a-.2]),np.array([-.5,0.,.5]));N=fx.size
 charge('profile_bound_segments',2048);oldback=HermiteFootprintBack(base,oldmodel);newback=HermiteFootprintBack(base,newmodel);half=VerticalScaleBack(base,.5);full=VerticalScaleBack(base,1.)
 legacyhalf=legacy['VerticalScaleBack'](base,.5)
 charge('fixture_comparator_rays',2*N);old=legacy['trace_raised_front_orthographic'](oldback,fx,fy,1.,1.5,2.1,count,front_surface=legacyhalf);new=trace_raised_front_orthographic(oldback,fx,fy,1.,1.5,2.1,count,front_surface=half)
 for key,value in old.items():assert np.array_equal(value,new[key],equal_nan=True),key
 rows.append({'member':member,'legacy_fields_exact':True,'legacy_fields':len(old)})
 for index in [1.,1.5]:
  charge('fixture_comparator_rays',N);actual=trace_raised_front_orthographic(newback,fx,fy,1.,index,2.1,count,front_surface=full);assert actual['complete'].all();assert np.max(abs(actual['X']+actual['X'][:,::-1]))<1e-9
  if index==1.:assert np.max(abs(actual['X']-fx))<1e-9 and np.max(abs(actual['Y']-fy))<1e-9
  rows.append({'member':member,'index':index,'full_front_complete':True,'certificate':str(actual['front_reflection_escape_certificate']),'retained_Lipschitz_min':float(np.nanmin(actual['reflection_front_clearance']))})
 if member=='expanded':save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'ledger':ledger})
base=surface_for_member('expanded');up=np.array([[0.,0.,1.]]);zero=np.zeros((1,2));charge('synthetic_certificate_cases',4)
assert monotone_front_reflection_escape(base,up,zero).all()
c=base.height_controls.copy();c[5]=c[4]*1.1;bad=SplineFootprintBack(base.half,base.radius,base.breaks,c);assert not monotone_front_reflection_escape(bad,up,zero).any()
smooth=SplineFootprintBack((3.,1.),1.,base.breaks,base.height_controls,cap_join_width=.1);assert not monotone_front_reflection_escape(smooth,up,zero).any()
assert not monotone_front_reflection_escape(base,-up,zero).any()
save('result.json',{'status':'ADDITIVE_CERTIFICATE_FIXED_FIXTURES_PASS','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'legacy_fields_unchanged':True,'ledger':ledger,'source_queries':0,'images':0,'native_rays':0})
print(json.dumps({'status':'PASS','ledger':ledger}),flush=True)
