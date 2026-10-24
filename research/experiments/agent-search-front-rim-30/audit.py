"""All saved closed24 first-front events; no tracing or RGB data."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile,math,bisect
import numpy as np
O=Path(__file__).parent;ROOT=O.parents[2];C=O.parent/'agent-search-closed-oval-24';B=O.parent/'agent-music-search-baseline-01';P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Original deadline'
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def save(f,v):gate();(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'started.json').exists(),'No retry or substitute subset';save('started.json',{'at':now()});result={'status':'STARTING','ledger':ledger}
try:
 for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert sha(ROOT/f)==h,'Frozen bytes'
 cp=json.loads((C/'protocol.json').read_text())['surface'];R=cp['R'];L=cp['L'];center=np.array(cp['center']);assert cp['index']==1.5 and cp['D']==2 and L==89
 proof=json.loads((B/'source-preflight.json').read_text());assert all(r['kernel_radius']==21 and r['finite_kernel']==[43,43] for r in proof['records'])
 specs={C/'native-paths.npz':{'regular_entry':((470,480),'|b1'),'entry':((470,480,3),'<f8'),'entry_normal':((470,480,3),'<f8')}}
 for ref in ['a','b']:specs[B/f'{ref}-support.npz']={k:((1080,1920),'|b1') for k in ['known','incident_known']}
 headers=[];total=0
 for f,spec in specs.items():
  with zipfile.ZipFile(f) as z:
   for name,(shape,dtype) in spec.items():
    with z.open(name+'.npy') as stream:
     v=np.lib.format.read_magic(stream);assert v in [(1,0),(2,0)];reader=np.lib.format.read_array_header_1_0 if v==(1,0) else np.lib.format.read_array_header_2_0;sh,fortran,dt=reader(stream,max_header_size=4096);hb=stream.tell()
    nb=math.prod(shape)*np.dtype(dtype).itemsize;assert tuple(sh)==shape and dt.str==dtype and not fortran and hb<=4096 and z.getinfo(name+'.npy').file_size==nb+hb;total+=nb;headers.append({'file':str(f.relative_to(ROOT)),'member':name,'shape':list(shape),'dtype':dtype,'header_bytes':hb,'payload_bytes':nb})
 assert total<=P['caps']['decoded_bytes'];save('headers-FIRST.json',{'at':now(),'selected_payload_bytes':total,'members':headers,'no_RGB_members':True})
 loaded={}
 for f,spec in specs.items():
  loaded[f]={}
  with np.load(f,allow_pickle=False) as z:
   for name,(shape,dtype) in spec.items():charge('decoded_bytes',math.prod(shape)*np.dtype(dtype).itemsize);a=z[name];assert a.shape==shape and a.dtype.str==dtype;loaded[f][name]=a
 q=loaded[C/'native-paths.npz'];charge('saved_reduction_elements',225600);ids=np.flatnonzero(q['regular_entry'].ravel());N=len(ids);assert N==98989
 entry=q['entry'].reshape(-1,3)[ids];normal=q['entry_normal'].reshape(-1,3)[ids];masks={ref:loaded[B/f'{ref}-support.npz'] for ref in ['a','b']}
 gate(True);save('checkpoint.json',{'at':now(),'status':'PASS_EXACT_HASH_HEADERS_ALL98989_NATIVE_FRONT_EVENTS','selected':N,'includes_all549_TIR_launches':True,'primitive_inputs_so_far':0,'ledger':ledger.copy()});print('CHECKPOINT_PASS',now(),flush=True)
 sys.path.insert(0,str(ROOT/'reconstruction'));from geometric_optics import reflect_direction,fresnel_components
 charge('retained_normals',N);charge('primitive_input_points',N);i=np.zeros_like(normal);i[:,2]=-1;reflected=reflect_direction(i,normal)
 charge('primitive_input_points',N);Rsp=fresnel_components(normal[:,2],1.,1.5)
 # Actual downward air reaches modeled plane before any infinite environment.
 down=reflected[:,2]<0;up=reflected[:,2]>0;lateral=~(down|up);di=np.flatnonzero(down);charge('source_plane_endpoint_checks',len(di))
 endpoint=np.full_like(entry,np.nan);t=(-2-entry[di,2])/reflected[di,2];assert np.isfinite(t).all() and (t>0).all();endpoint[di]=entry[di]+t[:,None]*reflected[di];native=np.full((N,2),np.nan);native[di]=endpoint[di,:2]*L+center
 aa=np.floor(native[di,0]).astype(np.int64);bb=np.floor(native[di,1]).astype(np.int64);bounds=(aa>=0)&(bb>=0)&(aa+1<1920)&(bb+1<1080);bi=np.flatnonzero(bounds);flags=np.zeros((N,2,2),bool)
 for ri,ref in enumerate(['a','b']):
  charge('source_plane_endpoint_checks',len(di))
  for mi,(role,name) in enumerate([('raw','known'),('incident','incident_known')]):
   charge('raw_corner_lookups' if mi==0 else 'incident_corner_lookups',4*len(bi));mask=masks[ref][name];ok=mask[bb[bi],aa[bi]]&mask[bb[bi]+1,aa[bi]]&mask[bb[bi],aa[bi]+1]&mask[bb[bi]+1,aa[bi]+1];flags[di[bi],ri,mi]=ok
 # One joint pass over selected record fields for all fixed statistics and AA.
 charge('saved_reduction_elements',N*7+56400)
 bands=[{'min':a,'max':b,'count':0,'sum_R':0.,'max_R':0.,'min_radius':None} for a,b in zip([0,20,38,60,80],[20,38,60,80,90])]
 hist=[{'degree':k,'count':0,'sum_Rs':0.,'sum_Rp':0.,'sum_R':0.} for k in range(90)]
 power={ref:{role:{c:0. for c in ['down_supported','down_unsupported','environment_unknown']} for role in ['raw','incident_compatible']} for ref in ['a','b']}
 minangle=90.;maxangle=0.;mins=[1.,1.,1.];maxs=[0.,0.,0.];sumR=0.;unit=np.zeros(N);angle=np.zeros(N);rad=np.zeros(N);pixel=np.zeros((235,240));coverage=np.zeros((235,240));thresholds={str(t):{'count':0,'sum_power':0.,'min_radius':None} for t in [.1,.25,.5]};grazing={str(t):{'count':0,'sum_power':0.,'min_radius':None} for t in [60,80]}
 roles=np.where(down,1,np.where(up,2,3)).astype(np.int8)
 for j,flat in enumerate(ids):
  theta=math.degrees(math.acos(min(1.,max(0.,float(normal[j,2])))));rs=float(Rsp[j,0]);rp=float(Rsp[j,1]);rf=.5*(rs+rp);radius=math.hypot(float(entry[j,0]),float(entry[j,1]));unit[j]=rf;angle[j]=theta;rad[j]=radius;minangle=min(minangle,theta);maxangle=max(maxangle,theta);sumR+=rf
  for k,val in enumerate([rs,rp,rf]):mins[k]=min(mins[k],val);maxs[k]=max(maxs[k],val)
  bucket=bands[min(4,bisect.bisect_right([20,38,60,80],theta))];bucket['count']+=1;bucket['sum_R']+=rf;bucket['max_R']=max(bucket['max_R'],rf);bucket['min_radius']=radius if bucket['min_radius'] is None else min(bucket['min_radius'],radius)
  h=hist[min(89,int(theta))];h['count']+=1;h['sum_Rs']+=rs;h['sum_Rp']+=rp;h['sum_R']+=rf
  for threshold,group in [(float(k),v) for k,v in thresholds.items()]:
   if rf>=threshold:group['count']+=1;group['sum_power']+=rf;group['min_radius']=radius if group['min_radius'] is None else min(group['min_radius'],radius)
  for threshold,group in [(float(k),v) for k,v in grazing.items()]:
   if theta>=threshold:group['count']+=1;group['sum_power']+=rf;group['min_radius']=radius if group['min_radius'] is None else min(group['min_radius'],radius)
  rr,cc=divmod(int(flat),480);pixel[rr//2,cc//2]+=.25*rf;coverage[rr//2,cc//2]+=.25
  for ri,ref in enumerate(['a','b']):
   for mi,role in enumerate(['raw','incident_compatible']):power[ref][role]['environment_unknown' if roles[j]!=1 else ('down_supported' if flags[j,ri,mi] else 'down_unsupported')]+=rf
 conditional=np.zeros_like(pixel);pixelmax=0.;pixsum=0.;coveredpixels=0;pixcounts={str(t):0 for t in [.1,.25,.5]}
 for rr in range(235):
  for cc in range(240):
   val=float(pixel[rr,cc]);pixsum+=val;pixelmax=max(pixelmax,val)
   if coverage[rr,cc]>0:coveredpixels+=1;conditional[rr,cc]=val/coverage[rr,cc]
   for key in pixcounts:pixcounts[key]+=int(val>=float(key))
 for group in list(grazing.values())+list(thresholds.values()):
  group['fraction_of_all_first_front_power']=group['sum_power']/sumR;group['maximum_sampled_inward_distance_native_pixels']=None if group['min_radius'] is None else (R-group['min_radius'])*L
 for group in bands:
  group['mean_R']=group['sum_R']/group['count'] if group['count'] else None;group['fraction_of_all_first_front_power']=group['sum_R']/sumR
 for h in hist:
  for name in ['Rs','Rp','R']:h['mean_'+name]=h['sum_'+name]/h['count'] if h['count'] else None
 np.savez_compressed(O/'first-front.npz',flat_indices=ids,incidence_degrees=angle,Rs_Rp=Rsp,unpolarized_Rf=unit,reflected_direction=reflected,scene_role=roles,background_endpoint=endpoint,source_native=native,raw_incident_support=flags)
 np.savez_compressed(O/'AA2-unit-reflectance.npz',pixel_averaged_unit_Rf=pixel,coverage=coverage,covered_mean_Rf=conditional)
 save('angle-histogram.json',{'bins':hist,'fixed_bin_width_degrees':1,'derived_scalar_plot_only':True})
 result.update(status='ALL_NATIVE_FIRST_FRONT_POWER_ROLES_COMPLETE_NO_RGB',regular_front_records=N,incidence_degrees=[minangle,maxangle],reflectance_ranges={'Rs':[mins[0],maxs[0]],'Rp':[mins[1],maxs[1]],'unpolarized':[mins[2],maxs[2]]},mean_Rf=sumR/N,total_Rf_sum=sumR,power_support=power,incidence_bands=bands,grazing=grazing,reflectance_thresholds=thresholds,pixel_field={'shape':[235,240],'AA':'Sum4native first-front Rf/4; misses have no interface contribution, not assigned scene black.','maximum':pixelmax,'sum':pixsum,'covered_pixels':coveredpixels,'threshold_counts':pixcounts,'conditional_mean_field_separate':True},scene_counts={'downward':len(di),'upward':int(up.sum()),'lateral':int(lateral.sum()),'downward_out_of_bounds':int((~bounds).sum())},no_radiance_assigned=True,selected_state_changed=False)
 save('result.json',result);print('RESULT',minangle,maxangle,mins[2],maxs[2],grazing,flush=True)
except Exception as exc:result['status']='STOPPED_FIRST_PREREQUISITE_OR_INVARIANT';result['failure']=repr(exc)
finally:
 result['finished']=now();(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(O/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FINAL',result['status'],result.get('failure'),ledger,flush=True)
