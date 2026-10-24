"""One sparse same-geometry return audit; no source or scene radiance is read."""
from pathlib import Path
from types import SimpleNamespace
import json,datetime,hashlib,zipfile,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from bevel_footprint_back import BevelFootprintBack
from hermite_height_back import HermiteFootprintBack
from first_front_return import trace_first_front_return
from polarization_transport import polarized_interface
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};tags={}
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def gate(changes):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline'
 assert all(0<=v and ledger[k]+v<=P['caps'][k] for k,v in changes.items()),changes
 for k,v in changes.items():ledger[k]+=int(v)
 save('ledger.json',dict(ledger,surface_tags=dict(tags)))
def count(label,n):
 gate(dict(surface_point_callbacks=n,conservative_surface_units=20*n));tags[label]=tags.get(label,0)+n
def interface(*args):
 n=len(args[0]);gate(dict(polarized_interface_points=n,reserved_nested_Snell_points=n,reserved_nested_Fresnel_points=n,reserved_nested_reflection_points=n));return polarized_interface(*args)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 family=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());g=family['geometry'];model_path=ROOT/'research/experiments/miniplayer-perimeter-inverse-77/back-profile.json';model=json.loads(model_path.read_text());design=json.loads((model_path.parent/'result.json').read_text());fields=['regular_entry','front','front_normal','back','outward_normal','interior_direction','primary_power']
 inputs=['reconstruction/first_front_return.py','reconstruction/raised_front_optics.py','reconstruction/rounded_rectangle_back.py','reconstruction/bevel_footprint_back.py','reconstruction/hermite_height_back.py','reconstruction/geometric_optics.py','reconstruction/polarization_transport.py','reconstruction/families/music-mini-player-working.json',str(model_path.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]+[f'research/experiments/miniplayer-codesigned-native-78/{m}-paths.npz' for m in ['expanded','compact']]
 first={name:sha(ROOT/name) for name in inputs};save('first-hashes.json',first);assert first[str(model_path.relative_to(ROOT))]=='567e39c8170e99be8a0b114c99c9dc82ec72bda4537c27dd7df00f629dbe9bdc'
 records=[];bounds=None
 for member in ['expanded','compact']:
  a=family['members'][member]['major_half'];b=g['minor_half'];coordinate=RoundedRectangleHarmonicBack((a,b),g['corner_radius'],cap_join_width=0.);front=BevelFootprintBack(coordinate,design['front_height'],8.)
  gate(dict(profile_bound_segments=len(model['radius_nodes'])-1));back=HermiteFootprintBack(SimpleNamespace(coordinate=coordinate,half=(a,b),radius=g['corner_radius']),model)
  if bounds is None:
   gate(dict(scalar_bound_calculations=1));mf,mb=front.slope_bound,back.slope_bound;n=family['optics']['index'];alpha=np.arctan(mf);delta=alpha-np.arcsin(np.sin(alpha)/n);beta=delta+2*np.arctan(mb);critical=np.arcsin(1/n);cmf=np.cos(beta)-mf*np.sin(beta);cmb=np.cos(beta)-mb*np.sin(beta);lower=n*np.cos(beta)-np.sqrt(n*n-1)
   assert cmf>0 and cmb>0 and lower>0
   bounds=dict(front_slope=mf,back_slope=mb,maximum_internal_tilt=float(delta),maximum_return_tilt=float(beta),critical_angle=float(critical),front_clearance_lower=float(cmf),back_clearance_lower=float(cmb),conditional_transmitted_z_lower=float(lower),incidence_note="Vertical tilt does not guarantee transmission against a tilted normal");save('global-bounds.json',bounds)
  path=ROOT/f'research/experiments/miniplayer-codesigned-native-78/{member}-paths.npz';headers={}
  with zipfile.ZipFile(path) as z:
   for key in fields:
    with z.open(key+'.npy') as f:
     version=np.lib.format.read_magic(f);shape,fortran,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f);size=int(np.prod(shape));assert not dtype.hasobject and not fortran;headers[key]=dict(shape=list(shape),dtype=str(dtype),payload_bytes=size*dtype.itemsize,scalars=size)
  save(member+'-headers.json',headers)
  gate(dict(cache_payload_decoded_bytes=sum(h['payload_bytes'] for h in headers.values()),cache_scalar_observations=sum(h['scalars'] for h in headers.values())))
  with np.load(path,allow_pickle=False) as z:data={k:z[k] for k in fields}
  shape=data['regular_entry'].shape;indices=np.flatnonzero(data['regular_entry']);entry=data['front'].reshape(-1,3)[indices];selected=[];targets=[]
  for y in [-.9,-.3,.3,.9]:
   for x in [-.98,-.7,-.4,-.1,.1,.4,.7,.98]:
    gate(dict(selection_distance_comparisons=len(indices)));target=np.array([a*x,b*y]);j=int(np.argmin(np.sum((entry[:,:2]-target)**2,axis=-1)));selected.append(int(indices[j]));targets.append(target.tolist())
  assert len(set(selected))==32;selected=np.array(selected);gate(dict(cached_launches=len(selected)))
  q={k:v.reshape((-1,)+v.shape[2:])[selected] for k,v in data.items()};del data,entry
  camera=np.zeros((32,3));camera[:,2]=-1;basis=np.broadcast_to(np.array([[1.,0,0],[0,1.,0]]),(32,2,3)).copy();density=np.broadcast_to(.5*np.eye(2,dtype=complex),(32,2,2)).copy();i0=interface(camera,q['front_normal'],1.,n,basis,density)
  assert not i0['blocked'].any() and np.max(abs(i0['transmitted_direction']-q['interior_direction']))<1e-12
  i1=interface(q['interior_direction'],-q['outward_normal'],n,1.,i0['transmitted_basis'],i0['transmitted_density'])
  assert not i1['blocked'].any();primary_error=float(np.max(abs(i1['transmitted_power']-q['primary_power'])));assert primary_error<P['tolerances']['primary_power_parity']
  gate(dict(return_segments=32));r=trace_first_front_return(front,back,q['back'],i1['reflected_direction'],charge=count)
  i2=interface(i1['reflected_direction'],-r['outward_normal'],n,1.,i1['reflected_basis'],i1['reflected_density'])
  transmitting=~i2['blocked'];closure=i0['reflected_power']+i1['transmitted_power']+i2['transmitted_power']+i2['reflected_power']-1
  # Save all raw paths and branches before interpretation assertions.
  saved={'selected_flat_indices':selected,'selection_targets':np.array(targets),'cache_grid_shape':np.array(shape)}
  saved.update({'cached_'+k:v for k,v in q.items()});saved.update({'return_'+k:v for k,v in r.items()})
  for label,values in [('initial_front',i0),('initial_back',i1),('return_interface',i2)]:saved.update({label+'_'+k:v for k,v in values.items()})
  np.savez_compressed(OUT/(member+'-returns.npz'),**saved)
  assert np.max(abs(closure))<P['tolerances']['closure'] and np.max(abs(r['residual']))<P['tolerances']['root_residual']
  assert (i2['transmitted_direction'][transmitting,2]>0).all()
  assert np.isnan(i2['transmitted_direction'][~transmitting]).all() and (i2['transmitted_power'][~transmitting]==0).all()
  record=dict(member=member,launches=32,primary_power_error=primary_error,maximum_root_residual=float(np.max(abs(r['residual']))),maximum_bracket_width=float(np.max(r['bracket_high']-r['bracket_low'])),minimum_front_clearance=float(r['front_clearance'].min()),minimum_back_clearance=float(r['back_clearance'].min()),all_existing_emissions_upward=True,minimum_emitted_z=float(i2['transmitted_direction'][transmitting,2].min()) if transmitting.any() else None,emitted_power_min=float(i2['transmitted_power'].min()),emitted_power_max=float(i2['transmitted_power'].max()),emitted_power_mean=float(i2['transmitted_power'].mean()),retained_power_max=float(i2['reflected_power'].max()),retained_power_mean=float(i2['reflected_power'].mean()),maximum_power_closure_error=float(np.max(abs(closure))),maximum_interface_closure_error=float(max(np.max(v['closure_error']) for v in [i0,i1,i2])),blocked_transmissions=int(i2['blocked'].sum()),transmitted_branches=int(transmitting.sum()))
  records.append(record);save('partial-results.json',{'records':records})
  if member=='expanded':
   now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=now.isoformat(),expanded=record,global_bounds=bounds,ledger=ledger));print('CHECKPOINT '+now.isoformat()+' expanded32 actual front returns and all branch powers retained; continuing compact',flush=True)
 last={name:sha(ROOT/name) for name in first};assert last==first;save('last-hashes.json',last);save('result.json',dict(status='SPARSE_FIRST_RETURN_PASS',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,global_bounds=bounds,ledger=dict(ledger),surface_tags=dict(tags),scene_radiance_evaluated=False,new_images=0,selected_model_changed=False,unassigned_later_power_retained=True,scope='Sparse actual-path/polarization checks plus intended global first-return certificate; not a full native/source/radiance/fidelity result.'));print(json.dumps({'status':'PASS','records':records,'ledger':ledger}),flush=True)
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(e).__name__,message=str(e),ledger=ledger,surface_tags=tags));raise
