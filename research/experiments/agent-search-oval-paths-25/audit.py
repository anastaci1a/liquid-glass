"""All cached ellipsoid TIR continuations through unchanged shared primitives."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile,math
import numpy as np
O=Path(__file__).resolve().parent;ROOT=O.parents[2];B=O.parent/'agent-music-search-baseline-01';C=O.parent/'agent-search-closed-oval-24'
P=json.loads((O/'protocol.json').read_text());caps=P['caps'];ledger={k:0 for k in caps};ledger.update(decoded_cells=0,mask_header_bytes=0,initial_cached_events=0,front_root_points=0)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clock():assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')),'Original deadline'
def reserve(delta,mutate=True):
 clock()
 for k,n in delta.items():assert n>=0 and ledger[k]+n<=caps[k],k
 if mutate:
  for k,n in delta.items():ledger[k]+=int(n)
def save(name,value):clock();(O/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert not (O/'started.json').exists(),'One execution only'
save('started.json',{'at':now()});result={'status':'STARTED','ledger':ledger};part=None;W=None
try:
 first=json.loads((O/'first-hashes.json').read_text())
 for file,digest in first.items():assert sha(ROOT/file)==digest,'Frozen identity: '+file
 proof=json.loads((B/'source-preflight.json').read_text());assert proof['status']=='PASS_BOTH_BEFORE_RGB' and all(r['kernel_radius']==21 and r['finite_kernel']==[43,43] for r in proof['records'])
 cp=json.loads((C/'protocol.json').read_text())['surface'];R=cp['R'];depth=cp['depth'];L=cp['L'];center=np.array(cp['center']);assert cp['kappa']==0 and cp['index']==1.5 and cp['D']==2
 specs={C/'native-paths.npz':{'blocked':((470,480),'|b1'),'regular_entry':((470,480),'|b1'),'entry':((470,480,3),'<f8'),'exit':((470,480,3),'<f8'),'entry_normal':((470,480,3),'<f8'),'exit_normal':((470,480,3),'<f8'),'internal_direction':((470,480,3),'<f8'),'exit_direction':((470,480,3),'<f8'),'discriminant':((470,480),'<f8')},C/'direct-front-directions.npz':{k:((98989,3),'<f8') for k in ['entry','outward_normal','reflected_direction','background_endpoint']}}
 for ref in ['a','b']:specs[B/f'{ref}-support.npz']={k:((1080,1920),'|b1') for k in ['known','incident_known']}
 headers=[];total=0
 for file,spec in specs.items():
  with zipfile.ZipFile(file) as z:
   for key,(shape,dtype) in spec.items():
    with z.open(key+'.npy') as stream:
     ver=np.lib.format.read_magic(stream);assert ver in [(1,0),(2,0)];reader=np.lib.format.read_array_header_1_0 if ver==(1,0) else np.lib.format.read_array_header_2_0;sh,fortran,dt=reader(stream,max_header_size=4096);hb=stream.tell()
    assert tuple(sh)==shape and dt.str==dtype and not fortran and hb<=4096
    nb=math.prod(shape)*dt.itemsize;assert z.getinfo(key+'.npy').file_size==hb+nb;total+=nb;headers.append({'file':str(file.relative_to(ROOT)),'member':key,'shape':list(shape),'dtype':dtype,'decoded_bytes':nb,'header_bytes':hb})
 assert total<=caps['decoded_bytes'];save('decode-reservation.json',{'at':now(),'selected_payload_bytes':total,'headers':headers,'no_RGB_members_selected':True})
 loaded={}
 for file,spec in specs.items():
  loaded[file]={}
  with np.load(file,allow_pickle=False) as z:
   for key,(shape,dtype) in spec.items():
    n=math.prod(shape);reserve({'decoded_bytes':n*np.dtype(dtype).itemsize});ledger['decoded_cells']+=n;a=z[key];assert a.shape==shape and a.dtype.str==dtype;loaded[file][key]=a
 q=loaded[C/'native-paths.npz'];direct=loaded[C/'direct-front-directions.npz'];masks={ref:loaded[B/f'{ref}-support.npz'] for ref in ['a','b']}
 selected=np.flatnonzero(q['blocked'].ravel());assert len(selected)==549 and np.all(q['regular_entry'].ravel()[selected]);reserve({'launch_records':549})
 regular_indices=np.flatnonzero(q['regular_entry'].ravel());regpos=np.searchsorted(regular_indices,selected);assert np.array_equal(regular_indices[regpos],selected)
 def rows(name):return q[name].reshape((-1,)+q[name].shape[2:])[selected].copy()
 entry=rows('entry');back=rows('exit');nf=rows('entry_normal');nb=rows('exit_normal');internal=rows('internal_direction');disc=rows('discriminant');assert (disc<0).all() and np.isnan(rows('exit_direction')).all()
 front_direction=direct['reflected_direction'][regpos].copy();front_endpoint=direct['background_endpoint'][regpos].copy();assert np.array_equal(entry,direct['entry'][regpos]) and np.array_equal(nf,direct['outward_normal'][regpos])
 N=549;r=np.linalg.norm(entry[:,:2],axis=1);assert (r>0).all();s=np.stack([-entry[:,1]/r,entry[:,0]/r,np.zeros(N)],-1)
 np.savez_compressed(O/'launches.npz',flat_indices=selected,regular_cache_indices=regpos,entry=entry,cached_back=back,entry_normal=nf,back_normal=nb,internal_direction=internal,meridional_s=s)
 save('checkpoint.json',{'status':'PASS_HASHES_HEADERS_ALL549_EXACT_CACHED_SELECTION','at':now(),'launches':N,'decoded_bytes':ledger['decoded_bytes'],'no_new_grid':True,'reservations':P['reservation']});print('CHECKPOINT_PASS',now(),flush=True)
 sys.path.insert(0,str(ROOT/'reconstruction'));import geometric_optics as go
 assert sha(Path(go.__file__))==first['reconstruction/geometric_optics.py']
 reserve({'delegate_units':64})
 class RadiusOval:
  def __init__(self):self.base=go.ClosedCircularOval(depth=depth,kappa=0.)
  @property
  def half_extents(self):return (R,R,depth)
  @property
  def center(self):return (0.,0.,-depth)
  def level_gradient(self,points):
   n=np.asarray(points).size//3;reserve({'level_points':n,'delegate_units':6*n});a=np.asarray(points).copy();a[...,:2]/=R;f,g=self.base.level_gradient(a);g[...,:2]/=R;return f,g
 solid=RadiusOval()
 def optical(fn,n,units,*args,**kwargs):reserve({'delegate_units':units*n});return fn(*args,**kwargs)
 def plane(point=None,direction=None,normal=None):
  maxima={}
  for key,a in [('position',point),('direction',direction),('normal',normal)]:
   if a is None:continue
   assert np.isfinite(a).all();value=np.max(abs(np.sum(a*s,axis=1)));assert value<=1e-9,'Meridional plane';maxima[key]=float(value)
   if key!='position':assert np.max(abs(np.linalg.norm(a,axis=1)-1))<=1e-10,'Unit vector'
  return maxima
 categories=['down_supported','down_unsupported','environment_unknown','unresolved','tail'];part={ref:{role:{cat:np.zeros((N,2)) for cat in categories} for role in ['raw','incident_compatible']} for ref in ['a','b']}
 def closure(remaining):
  maxerr=0.
  for roles in part.values():
   for cats in roles.values():
    err=np.array([.5,.5])-sum(cats.values(),np.zeros((N,2)))-remaining;maxerr=max(maxerr,float(abs(err).max()))
  assert maxerr<=P['tolerances']['power_closure'],'Power partition closure';return maxerr
 def endpoints(point,direction,power,available,cached=None):
  clock();ids=np.flatnonzero(available);roles=np.zeros(N,np.int8);xyz=np.full((N,3),np.nan);native=np.full((N,2),np.nan);flags=np.zeros((N,2,2),bool)
  down=available&(direction[:,2]<0);up=available&(direction[:,2]>0);lateral=available&~(down|up);roles[down]=1;roles[up]=2;roles[lateral]=3
  for rr in part.values():
   for cats in rr.values():cats['environment_unknown'][up|lateral]+=power[up|lateral]
  di=np.flatnonzero(down);t=(-2.-point[di,2])/direction[di,2];assert np.isfinite(t).all() and (t>0).all(),'Background plane'
  xyz[di]=point[di]+t[:,None]*direction[di]
  if cached is not None:np.testing.assert_allclose(xyz[di],cached[di],atol=1e-9,rtol=0)
  native[di]=xyz[di,:2]*L+center;aa=np.floor(native[di,0]).astype(np.int64);bb=np.floor(native[di,1]).astype(np.int64);bounds=(aa>=0)&(bb>=0)&(aa+1<1920)&(bb+1<1080);bi=np.flatnonzero(bounds)
  for ri,ref in enumerate(['a','b']):
   for mi,(role,name) in enumerate([('raw','known'),('incident_compatible','incident_known')]):
    reserve({'mask_lookups':4*len(bi)});mask=masks[ref][name];ok=np.zeros(len(di),bool);ok[bi]=mask[bb[bi],aa[bi]]&mask[bb[bi]+1,aa[bi]]&mask[bb[bi],aa[bi]+1]&mask[bb[bi]+1,aa[bi]+1];flags[di,ri,mi]=ok
    part[ref][role]['down_supported'][di[ok]]+=power[di[ok]];part[ref][role]['down_unsupported'][di[~ok]]+=power[di[~ok]]
  return {'scene_role':roles,'background_endpoint':xyz,'source_native':native,'availability':flags}
 # Initial front reflection uses exactly retained direction; no optical retrace.
 reserve({'encounters':2*N});ledger['initial_cached_events']=2*N
 camera=np.zeros((N,3));camera[:,2]=-1
 RF=optical(go.fresnel_components,N,4,nf[:,2],1.,1.5);RB=optical(go.fresnel_components,N,4,np.sum(internal*nb,axis=1),1.5,1.)
 assert np.isfinite(RF).all() and np.all((RF>=0)&(RF<=1)) and np.array_equal(RB,np.ones((N,2)))
 initial_reflected=.5*RF;W=.5*(1-RF);front_roles=endpoints(entry,front_direction,initial_reflected,np.ones(N,bool),cached=front_endpoint);initialclosure=closure(W)
 np.savez_compressed(O/'event-01.npz',point=entry,outward_normal=nf,incoming_direction=camera,cached_inside_direction=internal,reflected_direction=front_direction,R_sp=RF,incoming_power_sp=np.full((N,2),.5),reflected_power_sp=initial_reflected,remaining_internal_sp=W,**front_roles)
 plane(entry,internal,nf);plane(back,internal,nb);direction=optical(go.reflect_direction,N,4,internal,nb);plane(direction=direction)
 np.savez_compressed(O/'event-02.npz',point=back,outward_normal=nb,incoming_direction=internal,reflected_direction=direction,R_sp=RB,discriminant=disc,transmission_blocked=np.ones(N,bool),incoming_power_sp=W,remaining_internal_sp=W)
 point=back.copy();first_exit=np.zeros(N,np.int16);first_role=np.zeros(N,np.int8);first_side=np.zeros(N,np.int8);first_power=np.zeros((N,2));events=[];global_closure=initialclosure
 for eventnumber in range(3,17):
  clock();reserve({'new_segments':N,'encounters':N});reserve({'level_points':80*N,'delegate_units':510*N},mutate=False)
  event=optical(go.next_convex_boundary,N,16,solid,point,direction,tolerance=1e-11,max_iterations=64)
  if not event['complete'].all():raise RuntimeError('Unexpected unresolved ellipsoid boundary; all incoming power retained unknown')
  p=event['point'];normal=event['outward_normal'];planecheck=plane(p,direction,normal)
  outgoing,blocked,k=optical(go.refract,N,6,direction,-normal,1.5,1.)
  Rsp=optical(go.fresnel_components,N,4,np.sum(direction*normal,axis=1),1.5,1.)
  reflected=optical(go.reflect_direction,N,4,direction,normal)
  assert np.isfinite(Rsp).all() and np.all((Rsp>=0)&(Rsp<=1))
  assert np.array_equal(blocked,k<=0) and np.isnan(outgoing[blocked]).all() and np.array_equal(Rsp[blocked],np.ones((int(blocked.sum()),2)))
  assert np.all(k[~blocked]>0) and np.isfinite(outgoing[~blocked]).all()
  # Check planes without projection, including all finite transmitted branches.
  assert np.max(abs(np.sum(reflected*s,axis=1)))<=1e-9 and np.max(abs(np.linalg.norm(reflected,axis=1)-1))<=1e-10
  if (~blocked).any():assert np.max(abs(np.sum(outgoing[~blocked]*s[~blocked],axis=1)))<=1e-9 and np.max(abs(np.linalg.norm(outgoing[~blocked],axis=1)-1))<=1e-10
  Tin=W*(1-Rsp);nextW=W*Rsp;endpoint=endpoints(p,outgoing,Tin,~blocked)
  new=(first_exit==0)&~blocked;first_exit[new]=eventnumber;first_role[new]=endpoint['scene_role'][new];u=p[:,2]+depth;first_side[new]=np.where(u[new]>0,1,np.where(u[new]<0,-1,0));first_power[new]=Tin[new]
  np.savez_compressed(O/f'event-{eventnumber:02d}.npz',point=p,outward_normal=normal,incoming_direction=direction,reflected_direction=reflected,transmitted_direction=outgoing,transmission_blocked=blocked,discriminant=k,critical=(k==0),R_one_without_TIR=(~blocked)&np.any(Rsp==1,axis=1),R_sp=Rsp,incoming_power_sp=W,transmitted_power_sp=Tin,remaining_internal_sp=nextW,bracket=event['bracket'],level_residual=event['residual'],**endpoint)
  W=nextW;point=p;direction=reflected;err=closure(W);global_closure=max(global_closure,err)
  row={'number':eventnumber,'encounters':N,'TIR':int((k<0).sum()),'critical':int((k==0).sum()),'available_transmissions':int((~blocked).sum()),'zero_weight_available':int(((Tin.sum(1)==0)&~blocked).sum()),'downward':int((endpoint['scene_role']==1).sum()),'upward':int((endpoint['scene_role']==2).sum()),'lateral':int((endpoint['scene_role']==3).sum()),'max_remaining_internal_power':float(W.sum(1).max()),'closure_max':err,'plane_residual':planecheck}
  events.append(row);save('progress.json',{'at':now(),'last_event':eventnumber,'events':events,'ledger':ledger});print('EVENT',eventnumber,row['TIR'],row['downward'],row['max_remaining_internal_power'],flush=True)
 for roles in part.values():
  for cats in roles.values():cats['tail']+=W
 finalclosure=closure(np.zeros((N,2)));global_closure=max(global_closure,finalclosure)
 out={'flat_indices':selected,'first_internal_exit_event':first_exit,'first_exit_scene_role':first_role,'first_exit_hemisphere':first_side,'first_exit_power_sp':first_power,'tail_sp':W}
 for ref,roles in part.items():
  for role,cats in roles.items():
   for cat,a in cats.items():out[f'{ref}_{role}_{cat}_sp']=a
 np.savez_compressed(O/'partitions.npz',**out)
 summary={ref:{role:{cat:{'sum_s':float(a[:,0].sum()),'sum_p':float(a[:,1].sum()),'sum_unpolarized':float(a.sum()),'mean_unpolarized':float(a.sum(1).mean())} for cat,a in cats.items()} for role,cats in roles.items()} for ref,roles in part.items()}
 save('summary.json',{'power_partitions':summary,'events':events,'first_internal_exit':{'none':int((first_exit==0).sum()),'upward':int((first_role==2).sum()),'downward':int((first_role==1).sum()),'lateral':int((first_role==3).sum()),'upper_hemisphere':int((first_side==1).sum()),'lower_hemisphere':int((first_side==-1).sum())},'max_tail_unpolarized':float(W.sum(1).max()),'mean_tail_unpolarized':float(W.sum(1).mean()),'closure_max':global_closure,'power_closure_guard':P['tolerances']['power_closure'],'radiance_assigned':False})
 result['status']='ALL549_TIR_CONTINUATIONS_AUDITED_TO_EVENT16';result['events']=events;result['closure_max']=global_closure;result['no_selected_state_change']=True
except Exception as exc:
 result['status']='STOPPED_FIRST_FAILURE';result['failure']=repr(exc)
 if W is not None:
  np.savez_compressed(O/'stopped-unknown-power.npz',remaining_internal_sp=W)
finally:
 result['finished']=now();(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(O/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FINAL',result['status'],result.get('failure'),flush=True)
