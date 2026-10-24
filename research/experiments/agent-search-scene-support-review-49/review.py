from pathlib import Path
import json,datetime,hashlib,zipfile
import numpy as np
O=Path(__file__).parent;ROOT=O.parents[2];D=ROOT/'research/experiments/agent-search-oval-paths-25';ledger={'numeric_payload_bytes':0,'machine_record_text_bytes':0,'endpoint_records':0,'scalar_entries':0,'NPY_header_bytes':0};headers=[];detail=[]
def readjson(p):
 b=p.read_bytes();ledger['machine_record_text_bytes']+=len(b);assert ledger['machine_record_text_bytes']<=16777216;return json.loads(b)
P=readjson(O/'protocol.json')
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Deadline'
def save(n,v):gate();(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
first=readjson(O/'first-hashes.json')
for f,h in first.items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h['sha256'],f
meta=readjson(D/'decode-reservation.json');shape=[x['shape'] for x in meta['headers'] if x['member']=='known'];assert len(shape)==2 and all(x==[1080,1920] for x in shape);H,W=shape[0];surface=readjson(ROOT/'research/experiments/agent-search-closed-oval-24/protocol.json')['surface'];L=surface['L'];center=np.array(surface['center']);assert L==89 and surface['D']==2
categories=['supported_raw','center_outside','border_crossing','unknown_in_frame'];coarse=['down_supported','down_unsupported','environment_unknown','unresolved','tail'];specs={D/'launches.npz':['flat_indices'],D/'partitions.npz':['flat_indices','tail_sp']+[f'{ref}_{role}_{cat}_sp' for ref in ['a','b'] for role in ['raw','incident_compatible'] for cat in coarse]}
for e in [1]+list(range(3,17)):
 specs[D/f'event-{e:02d}.npz']=['scene_role','source_native','background_endpoint','availability','reflected_power_sp' if e==1 else 'transmitted_power_sp']+([] if e==1 else ['transmission_blocked'])
for path,names in specs.items():
 with zipfile.ZipFile(path) as z:
  for name in names:
   with z.open(name+'.npy') as f:
    version=np.lib.format.read_magic(f);shape,fortran,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f);size=int(np.prod(shape))*dtype.itemsize;assert not dtype.hasobject and shape[0]==549;ledger['NPY_header_bytes']+=f.tell();headers.append({'file':str(path.relative_to(ROOT)),'member':name,'shape':shape,'dtype':str(dtype),'payload_bytes':size})
reservation={'numeric_payload_bytes':sum(x['payload_bytes'] for x in headers),'endpoint_records':15*549,'scalar_entries':15*549*256+549*32*24,'machine_record_text_bytes':16777216};assert all(v<=P['caps'][k] for k,v in reservation.items());save('headers-and-reservation.json',{'headers':headers,'reservation':reservation,'frame':[W,H],'coordinate_units':'Saved source_native is original integer-centered native source-index pixels. background_endpoint is originalL normalized; unit conversion only.','L':L,'center':center.tolist()});gate(True);save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_hashes_exact':True,'all_required_headers_available':True,'frame_and_units_established_before_classification':True,'reservation':reservation,'decoded_payload_so_far':0});print('CHECKPOINT_PASS',flush=True)
def load(path):
 out={}
 with np.load(path,allow_pickle=False) as z:
  for name in specs[path]:
   h=next(x for x in headers if x['file']==str(path.relative_to(ROOT)) and x['member']==name);charge('numeric_payload_bytes',h['payload_bytes']);out[name]=z[name]
 return out
status='STARTING';result={}
try:
 launches=load(D/'launches.npz');part=load(D/'partitions.npz');ids=launches['flat_indices'];assert np.array_equal(ids,part['flat_indices']) and len(np.unique(ids))==549
 accum={ref:{cat:np.zeros((549,2)) for cat in categories} for ref in ['a','b']};incident={ref:{'supported':np.zeros((549,2)),'additional_failure':np.zeros((549,2)),'unsupported_total':np.zeros((549,2))} for ref in ['a','b']};environment=np.zeros((549,2));counts={ref:{cat:0 for cat in categories} for ref in ['a','b']};all_available=0;downcount=0;upcount=0;latcount=0
 for e in [1]+list(range(3,17)):
  gate();q=load(D/f'event-{e:02d}.npz');charge('endpoint_records',549);charge('scalar_entries',549*256);roles=q['scene_role'];native=q['source_native'];flags=q['availability'];power=q['reflected_power_sp' if e==1 else 'transmitted_power_sp'];assert roles.shape==(549,) and native.shape==(549,2) and flags.shape==(549,2,2) and power.shape==(549,2);assert (power>=0).all() and np.isfinite(power).all() and np.isin(roles,[0,1,2,3]).all()
  if e!=1:assert np.array_equal(roles==0,q['transmission_blocked'])
  down=roles==1;env=(roles==2)|(roles==3);assert np.isfinite(native[down]).all() and np.isnan(native[~down]).all();np.testing.assert_allclose(native[down],q['background_endpoint'][down,:2]*L+center,atol=1e-9,rtol=0);environment[env]+=power[env];all_available+=int((roles!=0).sum());downcount+=int(down.sum());upcount+=int((roles==2).sum());latcount+=int((roles==3).sum());xy=native[down];idx=np.flatnonzero(down);inside=(xy[:,0]>=0)&(xy[:,0]<W)&(xy[:,1]>=0)&(xy[:,1]<H);flo=np.floor(xy);corners=(flo[:,0]>=0)&(flo[:,1]>=0)&(flo[:,0]+1<W)&(flo[:,1]+1<H);assert np.all(~corners|inside)
  for ri,ref in enumerate(['a','b']):
   raw=flags[down,ri,0];inc=flags[down,ri,1];assert np.all(~raw|corners) and np.all(~inc|raw);masks={'supported_raw':raw,'center_outside':~inside,'border_crossing':inside&~corners,'unknown_in_frame':corners&~raw};assert np.all(sum(x.astype(int) for x in masks.values())==1)
   for cat,m in masks.items():accum[ref][cat][idx[m]]+=power[idx[m]];counts[ref][cat]+=int(m.sum())
   incident[ref]['supported'][idx[inc]]+=power[idx[inc]];incident[ref]['additional_failure'][idx[raw&~inc]]+=power[idx[raw&~inc]];incident[ref]['unsupported_total'][idx[~inc]]+=power[idx[~inc]]
   detail.append({'event':e,'reference':ref,'downward_records':len(idx),'counts':{k:int(m.sum()) for k,m in masks.items()},'launch_ids':{k:ids[idx[m]].tolist() for k,m in masks.items()}})
 charge('scalar_entries',549*32*24)
 def summarize(a):return {'sum_s':float(a[:,0].sum()),'sum_p':float(a[:,1].sum()),'sum_unpolarized':float(a.sum()),'mean_per_549_launch':float(a.sum()/549)}
 errors=[];out={}
 for ref in ['a','b']:
  supported=accum[ref]['supported_raw'];unsupported=sum(accum[ref][k] for k in categories if k!='supported_raw');roleerrors={}
  for role in ['raw','incident_compatible']:
   supp=supported if role=='raw' else incident[ref]['supported'];unsupp=unsupported if role=='raw' else incident[ref]['unsupported_total'];expected={cat:part[f'{ref}_{role}_{cat}_sp'] for cat in coarse};total=supp+unsupp+environment+expected['unresolved']+part['tail_sp'];err=max(float(np.max(abs(supp-expected['down_supported']))),float(np.max(abs(unsupp-expected['down_unsupported']))),float(np.max(abs(environment-expected['environment_unknown']))),float(np.max(abs(part['tail_sp']-expected['tail']))),float(np.max(abs(total-.5))));assert err<=P['closure_guard'],(ref,role,err);roleerrors[role]=err;errors.append(err)
  out[ref]={'raw_categories':{k:dict(summarize(v),endpoint_records=counts[ref][k]) for k,v in accum[ref].items()},'incident_compatible':{k:summarize(v) for k,v in incident[ref].items()},'unknown_environment':summarize(environment),'geometric_unresolved':summarize(part[f'{ref}_raw_unresolved_sp']),'event16_tail':summarize(part['tail_sp']),'aggregate_crosscheck_max_errors':roleerrors}
 result={'references':out,'launch_denominator':549,'all_available_air_exits':all_available,'downward_records':downcount,'upward_records':upcount,'lateral_records':latcount,'max_category_closure_error':max(errors),'no_renormalization':True};save('classification-details.json',detail);save('summary.json',result);status='COMPLETE_SAVED_ENDPOINT_SUPPORT_INVENTORY'
except Exception as e:status='STOPPED_FIRST_RETENTION_OR_INVARIANT_GAP';failure=repr(e)
finally:save('result.json',{'status':status,'failure':locals().get('failure'),'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'summary':result,'ledger':ledger,'new_optical_mask_RGB_source_operations':0});print(status,locals().get('failure'),flush=True)
