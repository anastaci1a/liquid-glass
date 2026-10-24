"""One sparse cached circular path/power audit. No RGB or image construction."""
import sys,json,hashlib,datetime,zipfile,math
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
BASE=ROOT/'research/experiments/agent-music-search-baseline-01'
CORE=ROOT/'reconstruction/geometric_optics.py'
CB=ROOT/'research/experiments/agent-reflection-accounting-preflight-17/combined_callback.py'
P=json.loads((OUT/'protocol.json').read_text());CAP=P['caps']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clock():
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')):raise RuntimeError('Hard deadline')
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while block:=f.read(1048576):h.update(block)
 return h.hexdigest()
def write(name,data):
 clock();(OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
ledger={'decoded_cells':0,'decoded_payload_bytes':0,'mask_header_bytes':0,'path_header_bytes':0,'cache_observations':0,'selection_comparisons':0,'mask_lookups':0,'initial_surface_checks':0,'encounters':0,'new_segments':0,'initial_refraction_rows':0}
def charge(key,n,limit):
 clock();n=int(n)
 if ledger[key]+n>limit:raise RuntimeError('Budget '+key)
 ledger[key]+=n
result={'status':'STARTING','started':now(),'ledger':ledger,'launches':[],'zero_work':['RGB','erosions','fields','filters','composites','images','fits','native grid','environment radiance']}
counter=None;current=None
CATEGORIES=('down_supported','down_unsupported','environment_unknown','unresolved','tail')
def make_partition():return {k:{role:{c:np.zeros(2) for c in CATEGORIES} for role in ('raw','incident_compatible')} for k in ('a','b')}
def serial_partition(part):return {k:{role:{c:v.tolist() for c,v in cats.items()} for role,cats in roles.items()} for k,roles in part.items()}
def add_all(part,category,power):
 for roles in part.values():
  for cats in roles.values():cats[category]+=power

def closure(part,remaining):
 errors={}
 for k,roles in part.items():
  errors[k]={}
  for role,cats in roles.items():
   e=np.array([.5,.5])-sum(cats.values(),np.zeros(2))-remaining
   errors[k][role]=e.tolist()
   if np.max(abs(e))>1536*2**-52:raise RuntimeError('Power closure invariant')
 return errors

def main():
 global counter,current
 clock();assert not (OUT/'started.json').exists(),'No retry'
 write('started.json',{'started':result['started'],'deadline':P['deadline']})
 assert digest(CORE)==P['shared_sha256'] and digest(CB)==P['callback_sha256']
 baseline=json.loads((BASE/'protocol.json').read_text())['parameters']
 assert baseline['R']==P['parameters']['R'] and baseline['L']==89 and baseline['index']==1.5 and baseline['D']==2
 center=np.asarray(baseline['center'],float);L=float(baseline['L']);R=float(baseline['R'])
 assert center.tolist()==[1511.2043368857017,672.8753258356955]
 binding={'shared':digest(CORE),'callback':digest(CB),'inputs':[],'cases':[],'containers':[],'corrected_center':center.tolist(),'L_original':L}
 restored=json.loads((BASE/'restored-inputs.json').read_text())['records']
 for r in restored:
  clock();f=ROOT/'.evidence-working/music-search-baseline-01'/r['case']/r['name']
  assert f.stat().st_size==r['bytes'] and digest(f)==r['sha256'],'Input binding failure'
  binding['inputs'].append({'case':r['case'],'name':r['name'],'sha256':r['sha256'],'PNG_decoded':False})
 for k in ('a','b'):
  case=json.loads((BASE/'cases'/f'{k}.json').read_text());live=json.loads((ROOT/'.evidence-working/music-search-baseline-01'/k/'case.json').read_text())
  assert live==case,'Case mismatch'
  binding['cases'].append({'case':k,'file_sha256':digest(BASE/'cases'/f'{k}.json'),'canonical_fingerprint':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest(),'style':case['foreground_styles'],'raw_case_center_not_used':case['center']})
 proof=json.loads((BASE/'source-preflight.json').read_text())
 assert proof['status']=='PASS_BOTH_BEFORE_RGB' and all(r['kernel_radius']==21 and r['finite_kernel']==[43,43] and r['unsupported_required']==0 for r in proof['records'])
 budget=json.loads((ROOT/'research/experiments/agent-reflection-accounting-preflight-17/decode-and-mask-budget.json').read_text())
 manifest={r['file']:r for r in json.loads((BASE/'manifest.json').read_text())['files']}
 grid=(470,480);pixel=(235,240);full=(1080,1920);N=225600
 scalar_float=('source_X','source_Y','x','y','X','Y','discriminant','path_length')
 vector_float=('entry','back','outward_normal','exit_direction')
 boolean=('inside','boundary_unresolved','zero_thickness_unresolved','complete')
 cache_spec={k:(grid,'<f8') for k in scalar_float}
 cache_spec.update({k:(grid+(3,),'<f8') for k in vector_float});cache_spec.update({k:(grid,'|b1') for k in boolean})
 cache_spec.update({'entry_outward_normal':((3,),'<f8'),'internal_direction':((3,),'<f8')})
 mask_spec={'known':(full,'|b1'),'incident_known':(full,'|b1'),'support':(grid,'|b1'),'required_pixels':(pixel,'|b1'),'required_subrays':(grid,'|b1'),'coverage':(pixel,'<f8')}
 specs={'native-paths.npz':cache_spec,'a-support.npz':mask_spec,'b-support.npz':mask_spec};headers={};payload_reserve=0
 for filename,spec in specs.items():
  clock();f=BASE/filename;record=manifest[filename]
  assert f.stat().st_size==record['bytes'] and digest(f)==record['sha256'],'Container binding failure'
  with zipfile.ZipFile(f) as z:
   assert set(z.namelist())=={k+'.npy' for k in spec},'Member allowlist mismatch'
   headers[filename]={}
   for name,(shape,dtype) in spec.items():
    clock()
    with z.open(name+'.npy') as stream:
     version=np.lib.format.read_magic(stream)
     assert version in ((1,0),(2,0))
     reader=np.lib.format.read_array_header_1_0 if version==(1,0) else np.lib.format.read_array_header_2_0
     actual_shape,fortran,actual_dtype=reader(stream,max_header_size=4096);header_bytes=stream.tell()
    assert header_bytes<=4096 and tuple(actual_shape)==shape and actual_dtype.str==dtype and not fortran,'Exact header mismatch: '+filename+':'+name
    count=math.prod(shape);nbytes=count*actual_dtype.itemsize
    assert z.getinfo(name+'.npy').file_size==header_bytes+nbytes,'Expanded length mismatch'
    category='path_header_bytes' if filename=='native-paths.npz' else 'mask_header_bytes'
    charge(category,header_bytes,CAP[category])
    headers[filename][name]={'shape':list(shape),'dtype':dtype,'header_bytes':header_bytes,'cells':count,'payload_bytes':nbytes,'fortran':fortran}
    payload_reserve+=nbytes
  binding['containers'].append({'name':filename,'sha256':record['sha256'],'compressed_bytes':record['bytes']})
 assert payload_reserve<=CAP['payload_bytes'],'Full decode reservation'
 write('header-provenance.json',{'status':'PASS_ALL_HEADERS_BEFORE_DECODE','bindings':binding,'headers':headers,'reserved_payload_bytes':payload_reserve})
 decoded={}
 for filename in specs:
  clock();decoded[filename]={}
  with np.load(BASE/filename,allow_pickle=False) as z:
   for name,h in headers[filename].items():
    charge('decoded_payload_bytes',h['payload_bytes'],CAP['payload_bytes']);ledger['decoded_cells']+=h['cells']
    charge('path_header_bytes' if filename=='native-paths.npz' else 'mask_header_bytes',h['header_bytes'],CAP['path_header_bytes' if filename=='native-paths.npz' else 'mask_header_bytes'])
    array=z[name];assert list(array.shape)==h['shape'] and array.dtype.str==h['dtype'] and array.nbytes==h['payload_bytes']
    decoded[filename][name]=array
 q=decoded['native-paths.npz'];masks={k:decoded[k+'-support.npz'] for k in ('a','b')}
 def observe(n):charge('cache_observations',n,CAP['cache_scalar_observations'])
 observe(4*N);eligible=q['inside']&q['complete']&~q['boundary_unresolved']&~q['zero_thickness_unresolved']
 observe(N);indices=np.flatnonzero(eligible.ravel());M=len(indices);assert 0<M<=N
 observe(2*M);cx=q['x'].ravel()[indices];cy=q['y'].ravel()[indices]
 observe(2*M);assert np.isfinite(cx).all() and np.isfinite(cy).all()
 for name in vector_float:
  observe(3*M);assert np.isfinite(q[name].reshape(-1,3)[indices]).all(),'Nonfinite regular cached vector'
 for name in ('source_X','source_Y','discriminant'):
  observe(M);assert np.isfinite(q[name].ravel()[indices]).all()
 observe(6);assert np.array_equal(q['entry_outward_normal'],[0.,0.,1.]) and np.array_equal(q['internal_direction'],[0.,0.,-1.])
 selected={}
 for axis,dx,dy in (('upper',0,-1),('lower',0,1),('left',-1,0),('right',1,0)):
  for fraction in (.5,.7,.85,.95):
   observe(9*M);charge('selection_comparisons',M,CAP['selection_comparisons'])
   distance=(cx-dx*fraction*R)**2+(cy-dy*fraction*R)**2;nearest=int(np.argmin(distance));flat=int(indices[nearest]);row,col=divmod(flat,grid[1])
   label={'axis':axis,'fraction':fraction,'target':[dx*fraction*R,dy*fraction*R],'squared_distance':float(distance[nearest])}
   if flat not in selected:selected[flat]={'flat_index':flat,'row':row,'column':col,'position':[float(cx[nearest]),float(cy[nearest])],'labels':[]}
   selected[flat]['labels'].append(label)
 assert len(selected)<=16
 selections=list(selected.values())
 # All primary support reuse is at unchanged stored indices and coordinates.
 for sel in selections:
  row,col=sel['row'],sel['column'];observe(2);sel['cached_primary_source_native']=[float(q['source_X'][row,col]),float(q['source_Y'][row,col])]
  for k in ('a','b'):
   charge('mask_lookups',1,CAP['mask_lookups']);assert bool(masks[k]['support'][row,col]),'Original primary proof bit unavailable'
 assert 128+16*8000<=130000 and 16*1500<=25000
 write('selection.json',{'count':len(selections),'selections':selections,'candidate_records':M,'tie_rule':'First argmin in sorted flattened row-major regular indices; duplicate target labels retained.','coordinates':'Original-L cached coordinates; corrected center and L from baseline protocol.'})
 write('checkpoint.json',{'status':'PASS_BEFORE_REAL_EVENTS','at':now(),'bindings':binding,'decode':dict(ledger),'selections':selections,'startup_reservations':{'setup':128,'per_launch_nested':8000,'per_launch_level':1500,'global_nested':130000,'global_level':25000},'shared_body_calls':0})
 print('CHECKPOINT_JSON:'+json.dumps({'status':'PASS_BEFORE_REAL_EVENTS','at':now(),'launches':len(selections),'decoded_cells':ledger['decoded_cells'],'decoded_bytes':ledger['decoded_payload_bytes'],'cache_observations':ledger['cache_observations'],'selection_comparisons':ledger['selection_comparisons']}),flush=True)
 sys.path.insert(0,str(CB.parent));from combined_callback import Counter
 sys.path.insert(0,str(CORE.parent));import geometric_optics as go
 assert Path(go.__file__).resolve()==CORE.resolve()
 counter=Counter(str(CORE),__file__,global_cap=130000,level_cap=25000,config_cap=8000,config_level_cap=1500)
 def hook(frame,event,arg):
  if event=='call':
   owner=type(frame.f_locals.get('self')).__name__;code=frame.f_code
   if code.co_filename==str(CORE) or (code.co_filename=='<string>' and owner=='HarmonicCircularBack'):clock()
  counter(frame,event,arg)
 def optical(fn,*args,**kwargs):
  clock();sys.setprofile(hook)
  try:return fn(*args,**kwargs)
  finally:sys.setprofile(None)
 def setup():return go.CircularHeightSolid(go.HarmonicCircularBack(.15,.4),radius=R)
 solid=optical(setup);assert counter.ledger['total']<=128
 result['setup_nested']=counter.ledger['total'];result['status']='RUNNING_TRANSPORT'
 def plane(s,p=None,d=None,n=None):
  clock();values={}
  for name,v in (('position',p),('direction',d),('normal',n)):
   if v is None:continue
   assert np.isfinite(v).all(),'Nonfinite plane field'
   residual=float(abs(np.dot(s,v)));values[name]=residual
   assert residual<=1e-9,'Meridional residual'
   if name!='position':assert abs(np.linalg.norm(v)-1)<=1e-10,'Nonunit retained/shared vector'
  return values
 def audit_endpoint(p,d,power,launch,is_primary):
  clock();event={'direction':d.tolist(),'power_sp':power.tolist()}
  if d[2]>=0:
   event['role']='upward_environment' if d[2]>0 else 'lateral_environment';add_all(launch['partition'],'environment_unknown',power);return event
  t=(-2.-p[2])/d[2]
  if not np.isfinite(t) or t<=0:
   event['role']='invalid_background_plane';add_all(launch['partition'],'environment_unknown',power);return event
  if is_primary:
   native=np.array(launch['selection']['cached_primary_source_native']);event['coordinate_origin']='exact retained primary'
  else:
   endpoint=p+t*d;native=endpoint[:2]*L+center;event['coordinate_origin']='actual shared exit ray and frozen plane'
  assert np.isfinite(native).all();event['role']='downward_background';event['source_native']=native.tolist();event['plane_distance']=float(t);event['availability']={}
  a,b=map(int,np.floor(native));inbounds=0<=a and a+1<1920 and 0<=b and b+1<1080
  for k in ('a','b'):
   flags={}
   for role,field in (('raw','known'),('incident_compatible','incident_known')):
    if inbounds:
     charge('mask_lookups',4,CAP['mask_lookups']);mask=masks[k][field]
     flag=bool(mask[b,a] & mask[b,a+1] & mask[b+1,a] & mask[b+1,a+1])
    else:flag=False
    flags[role]=flag;launch['partition'][k][role]['down_supported' if flag else 'down_unsupported']+=power
   event['availability'][k]=flags
  event['primary_proof_reused']=is_primary
  return event
 for si,sel in enumerate(selections):
  clock();counter.reserve_config();start_total=counter.ledger['total'];start_level=counter.ledger['closed_level_subset']
  row,col=sel['row'],sel['column'];observe(32)
  entry=q['entry'][row,col].copy();back=q['back'][row,col].copy();front_n=q['entry_outward_normal'].copy();back_n=q['outward_normal'][row,col].copy();internal=q['internal_direction'].copy();cached_out=q['exit_direction'][row,col].copy()
  rr=math.hypot(entry[0],entry[1]);assert rr>0;s=np.array([-entry[1]/rr,entry[0]/rr,0.])
  launch={'selection':sel,'events':[],'partition':make_partition(),'plane_basis_s':s.tolist(),'initial_checks':[]};result['launches'].append(launch)
  W=np.array([.5,.5]);current={'launch':launch,'power':W}
  for point,normal,label in ((entry,front_n,'entry'),(back,back_n,'back')):
   charge('initial_surface_checks',1,CAP['initial_level_checks']);f,g=optical(solid.level_gradient,point.reshape(1,3));actual_n=g[0]/np.linalg.norm(g[0]);assert abs(float(f[0]))<=1e-10 and np.allclose(actual_n,normal,atol=1e-9,rtol=0),'Cached same-surface mismatch'
   launch['initial_checks'].append({'event':label,'level_residual':float(f[0]),'normal_difference':float(np.max(abs(actual_n-normal))),'level_gradient':g[0].tolist(),'same_surface_unit_normal':actual_n.tolist(),'plane':plane(s,p=point,n=normal)})
  p=entry.copy();normal=front_n.copy();d=internal.copy();cached=True;bracket=None;residual=None
  for number in range(1,25):
   clock();charge('encounters',1,CAP['encounters'])
   if number==1:p=entry.copy();normal=front_n.copy();d=internal.copy();n_from,n_to=1.,1.5;against=normal;cosine=float(-np.dot(d,normal))
   else:n_from,n_to=1.5,1.;against=-normal;cosine=float(np.dot(d,normal))
   fields=plane(s,p=p,d=d,n=normal)
   reflected=optical(go.reflect_direction,d.reshape(1,3),normal.reshape(1,3))[0]
   out,blocked,disc=optical(go.refract,d.reshape(1,3),against.reshape(1,3),n_from,n_to)
   weights=optical(go.fresnel_components,np.array([cosine]),n_from,n_to)[0]
   assert np.isfinite(weights).all() and np.all((weights>=0)&(weights<=1)),'Invalid Fresnel weights'
   blocked=bool(blocked[0]);k=float(disc[0]);out=out[0]
   if blocked:
    assert k<=0 and np.isnan(out).all() and np.array_equal(weights,[1.,1.]),'Inconsistent blocked transmission and Fresnel'
   else:assert k>0 and np.isfinite(out).all(),'Inconsistent transmitting branch'
   if number==1:
    ledger['initial_refraction_rows']+=1;assert not blocked and np.allclose(out,internal,atol=1e-9,rtol=0);out=internal.copy()
   elif number==2:
    ledger['initial_refraction_rows']+=1;observe(1);assert not blocked and float(q['discriminant'][row,col])>0 and np.allclose(out,cached_out,atol=1e-9,rtol=0);out=cached_out.copy()
   record={'number':number,'origin':'cached initial' if number<=2 else 'shared ordered boundary','point':p.tolist(),'outward_normal':normal.tolist(),'incoming':d.tolist(),'reflected':reflected.tolist(),'medium':[n_from,n_to],'cosine':cosine,'R_sp':weights.tolist(),'incoming_power_sp':W.tolist(),'transmission_blocked':blocked,'shared_transmission_direction':[None if not np.isfinite(v) else float(v) for v in out],'shared_transmission_nan_pattern':np.isnan(out).tolist(),'cached_direction_reused':number<=2,'discriminant':k,'critical':bool(k==0),'R_one_without_TIR':bool(not blocked and np.any(weights==1)),'bracket':bracket,'level_residual':residual,'plane':fields}
   plane(s,d=reflected)
   if not blocked:record['transmitted']=out.tolist();record['transmitted_plane']=plane(s,d=out)
   reflected_power=W*weights;transmitted_power=W*(1-weights)
   if number==1:
    add_all(launch['partition'],'environment_unknown',reflected_power);record['front_reflection_unknown_sp']=reflected_power.tolist();W=transmitted_power
   else:
    if not blocked:record['endpoint']=audit_endpoint(p,out,transmitted_power,launch,number==2)
    else:assert np.array_equal(transmitted_power,[0.,0.])
    W=reflected_power
   current['power']=W;record['remaining_internal_sp']=W.tolist();launch['events'].append(record);closure(launch['partition'],W)
   if number==24:
    add_all(launch['partition'],'tail',W);W=np.zeros(2);current['power']=W;launch['termination']='encounter_cap';break
   if number==1:
    p=back.copy();normal=back_n.copy();d=internal.copy();bracket=None;residual=None;continue
   if np.array_equal(W,[0.,0.]):launch['termination']='exact_zero_continuation';break
   charge('new_segments',1,CAP['new_segments']);event=optical(go.next_convex_boundary,solid,p.reshape(1,3),reflected.reshape(1,3),tolerance=1e-11,max_iterations=64)
   p=event['point'][0];normal=event['outward_normal'][0];d=reflected;bracket=float(event['bracket'][0]);residual=float(event['residual'][0])
   if not bool(event['complete'][0]):
    # This explicit shared status is the permitted unresolved crease, not a solver repair.
    assert np.isnan(normal).all(),'Unexpected incomplete event status';charge('encounters',1,CAP['encounters'])
    launch['events'].append({'number':number+1,'origin':'shared unresolved crease','point':p.tolist(),'normal_unavailable':True,'bracket':bracket,'level_residual':residual,'retained_unknown_sp':W.tolist()})
    add_all(launch['partition'],'unresolved',W);W=np.zeros(2);current['power']=W;launch['termination']='explicit_unresolved_crease';break
  launch['closure']=closure(launch['partition'],W);launch['partition_serialized']=serial_partition(launch['partition']);del launch['partition']
  launch['nested_actual']=counter.ledger['total']-start_total;launch['level_actual']=counter.ledger['closed_level_subset']-start_level
  assert launch['nested_actual']<=8000 and launch['level_actual']<=1500
  current=None;write('progress.json',{'completed_launches':len(result['launches']),'ledger':ledger,'counter':counter.ledger})
 result['status']='SPARSE_PATH_POWER_AUDIT_COMPLETE'
try:main()
except Exception as exc:
 sys.setprofile(None);result['status']='STOPPED_FIRST_FAILURE';result['failure']=repr(exc)
 if current is not None:
  launch=current['launch'];W=current['power'];add_all(launch['partition'],'unresolved',W)
  launch['stopped_unknown_power_sp']=W.tolist();launch['partition_serialized']=serial_partition(launch['partition']);del launch['partition']
finally:
 sys.setprofile(None)
 result['finished']=now();result['counter']=counter.ledger if counter is not None else None
 # Failure packaging must preserve evidence even if the hard clock triggered the stop.
 (OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print('FINAL_JSON:'+json.dumps({'status':result['status'],'failure':result.get('failure'),'launches':len(result['launches']),'ledger':ledger,'counter':result['counter']}),flush=True)
