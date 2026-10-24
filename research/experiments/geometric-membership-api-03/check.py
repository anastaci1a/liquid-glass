"""Small old/new output contract test; existing geometry outputs stay exact."""
from pathlib import Path
import datetime,json,types,subprocess,sys,hashlib
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'reconstruction'))
import geometric_optics as new
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
assert not (P/'result.json').exists()
old=types.ModuleType('old_membership_core');sys.modules[old.__name__]=old
src=subprocess.check_output(['git','show',p['base_commit']+':reconstruction/geometric_optics.py'],cwd=ROOT).decode();exec(compile(src,'old_membership_core.py','exec'),old.__dict__)
ledger={'fixture_configurations':0,'attempted_comparator_rays':0,'height_boundary_points':0,'level_points':0};solids=[]
def gate():assert datetime.datetime.now(datetime.timezone.utc)<end

def make_back(module):
 class Counted(module.HarmonicCircularBack):
  def height_gradient(self,x,y):
   n=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size
   assert ledger['height_boundary_points']+n<=p['caps']['height_boundary_points'];ledger['height_boundary_points']+=int(n)
   return super().height_gradient(x,y)
 return Counted()
class Scaled:
 def __init__(self,base,R):self.base,self.R=base,R
 @property
 def maximum_height(self):return self.base.maximum_height
 @property
 def slope_bound(self):return self.base.slope_bound/self.R
 def height_gradient(self,x,y):
  h,hx,hy,i=self.base.height_gradient(x/self.R,y/self.R);return h,hx/self.R,hy/self.R,i
 def boundary_mask(self,x,y):
  n=np.broadcast_arrays(x,y)[0].size;assert ledger['height_boundary_points']+n<=p['caps']['height_boundary_points'];ledger['height_boundary_points']+=int(n)
  return self.base.boundary_mask(x/self.R,y/self.R)

def charge(n):assert ledger['attempted_comparator_rays']+n<=p['caps']['attempted_comparator_rays'];ledger['attempted_comparator_rays']+=n

def equal_legacy(a,b):
 assert set(b)==set(a)|{'projected_inside','regular_entry'}
 assert all(np.array_equal(a[k],b[k],equal_nan=True) for k in a)

rows=[]
for R,index in [(.9972124917582454,1.),(.9972124917582454,1.5),(1.,1.5)]:
 gate();ledger['fixture_configurations']+=1;x=R*np.array([0.,.4,1.1,1.]);y=R*np.array([0.,.2,0.,0.]);both=[]
 for module in [old,new]:
  base=make_back(module);flat=Scaled(base,R);solid=module.CircularHeightSolid(base,radius=R);solids.append(solid)
  solid.maximum_level_points=p['caps']['level_points']-sum(s.level_point_evaluations for s in solids[:-1])
  charge(4);a=module.trace_flat_front_orthographic(flat,x,y,index,2.)
  charge(4);b=module.trace_closed_orthographic(solid,x,y,index,2.)
  assert sum(s.level_point_evaluations for s in solids)<=p['caps']['level_points']
  both.append((a,b))
 for k in [0,1]:equal_legacy(both[0][k],both[1][k])
 for result in both[1]:
  assert result['projected_inside'].tolist()==[True,True,False,True]
  assert result['regular_entry'].tolist()==[True,True,False,False]
  assert result['complete'].tolist()==[True,True,True,False]
 assert both[1][0]['inside'][-1] and not both[1][1]['inside'][-1]
 assert np.isfinite(both[1][0]['exit_direction'][2:]).all()
 assert np.isnan(both[1][1]['exit_direction'][2:]).all()
 rows.append(dict(radius=R,index=index,all_legacy_fields_exact=True,new_membership_exact=True,off_event_legacy_directions_preserved=True))
class ZeroHeight:
 maximum_height=0.;slope_bound=0.
 def height_gradient(self,x,y):
  ledger['height_boundary_points']+=np.asarray(x).size;z=np.zeros_like(x);return z,z,z,np.hypot(x,y)<=1
 def boundary_mask(self,x,y):
  ledger['height_boundary_points']+=np.asarray(x).size;return np.hypot(x,y)==1
zero=ZeroHeight();values=[];ledger['fixture_configurations']+=1
for module in [old,new]:charge(1);values.append(module.trace_flat_front_orthographic(zero,np.array([0.]),np.array([0.]),1.5,2.))
equal_legacy(*values);r=values[1]
assert r['inside'][0] and r['projected_inside'][0] and not r['regular_entry'][0] and r['boundary_unresolved'][0] and not r['complete'][0]
ledger['level_points']=sum(s.level_point_evaluations for s in solids)
assert ledger['fixture_configurations']<=4 and ledger['height_boundary_points']<=p['caps']['height_boundary_points'];gate()
result=dict(status='PASS_ADDITIVE_MEMBERSHIP_LEGACY_BYTES_PRESERVED',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),ledger=ledger,regular_configurations=rows,interior_zero_thickness_unresolved=True,shared_sha256=hashlib.sha256((ROOT/'reconstruction/geometric_optics.py').read_bytes()).hexdigest(),old_source_sha256=hashlib.sha256(src.encode()).hexdigest(),new_source_queries=0,new_images=0,limits='Metadata and small fixture controls only; no full parity cycle, reflected source or fidelity acceptance.')
(P/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result))
