"""Fixed native first-return contribution, with exact zero-added-return controls."""
from pathlib import Path
from types import SimpleNamespace
import json,datetime,hashlib,zipfile,sys,ast,time
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from bevel_footprint_back import BevelFootprintBack
from hermite_height_back import HermiteFootprintBack
from first_front_return import trace_first_front_return
from polarization_transport import polarized_interface
from environment_radiance import annular_environment,decode_srgb,encode_srgb
from geometric_render import incident_source_filter,neutral_color_response
from extended_fit import Study
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};tags={};cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate(changes):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline'
 assert all(0<=v and ledger[k]+v<=P['caps'][k] for k,v in changes.items()),changes
 for k,v in changes.items():ledger[k]+=int(v)
 save('ledger.json',dict(ledger,surface_tags=dict(tags)))
def charge(k,n):
 d={k:int(n)}
 if k=='score_calls':d.update(SSIM_Gaussians=5*n,metric_erosions=n)
 gate(d)
def count(label,n):
 gate(dict(surface_point_callbacks=n,conservative_surface_units=20*n));tags[label]=tags.get(label,0)+n
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(path,fields=None):
 headers={}
 with zipfile.ZipFile(path) as z:
  for name in z.namelist():
   k=name[:-4]
   if fields is not None and k not in fields:continue
   with z.open(name) as f:
    version=np.lib.format.read_magic(f);shape,fortran,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f);size=int(np.prod(shape));assert not dtype.hasobject;headers[k]=(size,size*dtype.itemsize)
 gate(dict(cache_payload_decoded_bytes=sum(v[1] for v in headers.values()),cache_scalar_observations=sum(v[0] for v in headers.values())))
 with np.load(path,allow_pickle=False) as z:return {k:z[k] for k in headers}
def interface(*args):
 n=len(args[0]);gate(dict(polarized_interface_points=n,reserved_nested_Snell_points=n,reserved_nested_Fresnel_points=n,reserved_nested_reflection_points=n));return polarized_interface(*args)
for path,names in [(ROOT/'research/experiments/miniplayer-outline-light-07/render.py',['score','display','to_image']),(ROOT/'research/experiments/miniplayer-direct-front-envelope-74/observe.py',['panels'])]:
 tree=ast.parse(path.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 class Labels(ast.NodeTransformer):
  def visit_Constant(self,node):
   if isinstance(node.value,str):node.value=node.value.replace('Uniform upper environment, radiance 4','Actual first return; same light4').replace('Working20 annular environment','Co-designed78; direct-front only').replace('Uniform white scene','Added first return').replace('Working20','Co-designed78')
   return node
 exec(compile(ast.fix_missing_locations(ast.Module(body=[Labels().visit(n) for n in functions],type_ignores=[])),str(path),'exec'))
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});family=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());g=family['geometry'];L=family['length_unit_native_pixels'];n=family['optics']['index'];BASE=ROOT/'research/experiments/miniplayer-codesigned-native-78';RAW=ROOT/'research/experiments/miniplayer-inverse-forward-18';selected=ROOT/'research/experiments/miniplayer-incident-material-20';model_path=ROOT/'research/experiments/miniplayer-perimeter-inverse-77/back-profile.json';model=json.loads(model_path.read_text());design=json.loads((model_path.parent/'result.json').read_text())
 prior=json.loads((BASE/'first-hashes.json').read_text());assert all(sha(ROOT/f)==digest for f,digest in prior.items()),'Changed78 inputs/code';proof=json.loads((BASE/'source-FIRST.json').read_text());assert proof['status']=='ALL_FOUR_COMPLETE_BEFORE_RGB' and len(proof['records'])==4 and all(r['unsupported_required']==0 for r in proof['records'])
 first=dict(prior)
 for f in [str(Path(__file__).relative_to(ROOT)),'reconstruction/first_front_return.py','reconstruction/polarization_transport.py','reconstruction/environment_radiance.py',str((BASE/'source-FIRST.json').relative_to(ROOT))]+[str((BASE/f'{m}-paths.npz').relative_to(ROOT)) for m in ['expanded','compact']]:first[f]=sha(ROOT/f)
 save('first-hashes.json',first);save('source-proof-transfer-FIRST.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_proof_sha256=sha(BASE/'source-FIRST.json'),unchanged_primary_paths=True,all_original_input_code_hashes_exact=True,whole_all_guard_and_finite_kernel_proof_reused=True,observed_truth=False,new_backdrop_endpoints=0,condition='All existing first-return emissions must point upward; no RGB until all new events complete. Existing annular scene remains a hypothetical radiance assumption.'))
 paths={};events={};geometric=[]
 for member in ['expanded','compact']:
  a=family['members'][member]['major_half'];b=g['minor_half'];coordinate=RoundedRectangleHarmonicBack((a,b),g['corner_radius'],cap_join_width=0.);front=BevelFootprintBack(coordinate,design['front_height'],8.);charge('profile_bound_segments',len(model['radius_nodes'])-1);back=HermiteFootprintBack(SimpleNamespace(coordinate=coordinate,half=(a,b),radius=g['corner_radius']),model)
  q=load(BASE/f'{member}-paths.npz',['inside','regular_entry','X','Y','front','front_normal','back','outward_normal','interior_direction','primary_power','front_reflection_direction','front_reflection_power']);assert np.array_equal(q['inside'],q['regular_entry']);inside=q['inside'];idx=np.flatnonzero(inside);N=len(idx);event={};maxclosure=0.;maxprimary=0.;blocked_total=0
  for lo in range(0,N,65536):
   hi=min(lo+65536,N);ids=idx[lo:hi];z={k:v.reshape((-1,)+v.shape[2:])[ids] for k,v in q.items() if k in ['front','front_normal','back','outward_normal','interior_direction','primary_power']};K=len(ids);camera=np.zeros((K,3));camera[:,2]=-1;basis=np.broadcast_to(np.array([[1.,0,0],[0,1.,0]]),(K,2,3)).copy();density=np.broadcast_to(.5*np.eye(2,dtype=complex),(K,2,2)).copy();i0=interface(camera,z['front_normal'],1.,n,basis,density);i1=interface(z['interior_direction'],-z['outward_normal'],n,1.,i0['transmitted_basis'],i0['transmitted_density']);assert not i0['blocked'].any() and not i1['blocked'].any();maxprimary=max(maxprimary,float(np.max(abs(i1['transmitted_power']-z['primary_power']))));assert maxprimary<3e-13
   charge('return_segments',K);r=trace_first_front_return(front,back,z['back'],i1['reflected_direction'],charge=count);i2=interface(i1['reflected_direction'],-r['outward_normal'],n,1.,i1['reflected_basis'],i1['reflected_density']);ok=~i2['blocked'];closure=i0['reflected_power']+i1['transmitted_power']+i2['transmitted_power']+i2['reflected_power']-1;maxclosure=max(maxclosure,float(np.max(abs(closure))));assert maxclosure<3e-13;assert (i2['transmitted_direction'][ok,2]>0).all() and np.isnan(i2['transmitted_direction'][~ok]).all();blocked_total+=int((~ok).sum())
   chunk=dict(r,emitted_direction=i2['transmitted_direction'],emitted_power=i2['transmitted_power'],retained_power=i2['reflected_power'],blocked=i2['blocked'],discriminant=i2['discriminant'],initial_back_reflection_direction=i1['reflected_direction'])
   for key,v in chunk.items():
    if np.asarray(v).ndim==0:continue
    if key not in event:event[key]=np.empty((N,)+v.shape[1:],dtype=v.dtype)
    event[key][lo:hi]=v
   print('PROGRESS '+member+' '+str(hi)+'/'+str(N)+' '+datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
   if member=='expanded' and lo==0:
    np.savez_compressed(OUT/'checkpoint-first-chunk.npz',**chunk);now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=now.isoformat(),member=member,first_chunk=K,positive_margins=True,maximum_closure=maxclosure,blocked=int((~ok).sum()),RGB_queries=0,ledger=dict(ledger)));print('CHECKPOINT first expanded chunk saved; continuing',flush=True)
  np.savez_compressed(OUT/f'{member}-returns.npz',cached_regular_flat_indices=idx,**event);paths[member]=q;events[member]=event;geometric.append(dict(member=member,launches=N,blocked=blocked_total,transmitted=N-blocked_total,maximum_primary_power_error=maxprimary,maximum_closure=maxclosure,minimum_front_clearance=float(event['front_clearance'].min()),minimum_back_clearance=float(event['back_clearance'].min()),maximum_root_residual=float(np.max(abs(event['residual']))),retained_power_max=float(event['retained_power'].max()),retained_power_mean=float(event['retained_power'].mean())))
 save('all-return-events-FIRST.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_completed_before_new_RGB=True,records=geometric,later_tail_retained=True));print('ALL RETURN EVENTS PASS before RGB',flush=True)
 records=[];identities=[]
 for member,q in paths.items():
  inside=q['inside'];event=events[member];ok=~event['blocked'];charge('environment_direction_queries',int(inside.sum()));direct=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);charge('environment_direction_queries',int(ok.sum()));return_unit=np.zeros(len(ok));return_unit[ok]=event['emitted_power'][ok]*annular_environment(event['emitted_direction'][ok]);np.savez_compressed(OUT/f'{member}-scene.npz',direct_unit=direct,first_return_unit=return_unit);work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for k in ['a','b']:
   case=json.loads((work/k/'case.json').read_text());assert not case.get('exterior_source');H=case['crop'][3]-case['crop'][1];W=case['crop'][2]-case['crop'][0];vector_layers=[x for x in case['foreground_layers'] if 'vector_asset' in x];boxes=sum((v['box'][2]-v['box'][0])*(v['box'][3]-v['box'][1]) for v in case['foreground_layers']);art=sum(Image.open(work/k/v['artwork_asset']).width*Image.open(work/k/v['artwork_asset']).height for v in case['foreground_layers'] if 'artwork_asset' in v);gate(dict(Study_constructor_pixels=H*W,Study_source_target_RGB_decoded_pixels=2*1920*1080,known_mask_decoded_pixels=2*1920*1080,foreground_artwork_decoded_pixels=art,foreground_box_pixel_reservations=3*boxes,foreground_vector_coverage_visits=3*len(vector_layers)));s=Study(work/k);assert not s.transmission_layers,'No foreground refit allowed';assert s.source.shape[:2]==(1080,1920);m=load(work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz');assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
   if member=='expanded':center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
   else:
    pose=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=np.array(s.case['center'])+L*np.array([pose['shape_dx'],pose['shape_dy']])
   known=cv2.imread(str(work/k/'known.png'),0)>0;charge('incident_fields',1);charge('known_erosions',1);field,safe,radius=incident_source_filter(s.source,known,6.75);assert radius==21
   X=q['X'][inside]*L+center[0];Y=q['Y'][inside]*L+center[1];a,b=np.floor(X).astype(int),np.floor(Y).astype(int);wx=(X-a)[:,None];wy=(Y-b)[:,None];charge('source_RGB_queries',len(a));sample=(field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy;assert np.isfinite(sample).all();coded,preclip=neutral_color_response(sample,gain=family['material']['gain'],bias=family['material']['bias'],return_preclip=True);primary=q['primary_power'][inside,None]*decode_srgb(coded);zero_encoded=encode_srgb(primary+4*direct[:,None]);raw=load(RAW/f'{member}-{k}-light4.npz',['raw_source','coverage']);old=load(BASE/f'{member}-{k}.npz',['pre_foreground','complete','coverage']);v=raw['raw_source'].copy();v[inside]=np.clip(zero_encoded,0,1);zero_pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);zero_C=s.apply_foreground(zero_pre.copy());assert np.array_equal(zero_pre,old['pre_foreground'],equal_nan=True) and np.array_equal(zero_C,old['complete'],equal_nan=True),'Zero-return identity mismatch';identities.append(dict(member=member,reference=k,pre_exact=True,complete_exact=True));save('identities.json',{'records':identities})
   encoded=encode_srgb(primary+4*(direct+return_unit)[:,None]);v[inside]=np.clip(encoded,0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy());coverage=old['coverage'];frozen=coverage if member=='expanded' else load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz',['coverage'])['coverage'];partial=m['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22);crops=json.loads((RAW/'protocol.json').read_text())['fixed_crops'][member];scores=score(s,C,m,partial,crops);before=json.loads((BASE/f'{member}-{k}-metrics.json').read_text())['scores'];current=json.loads((selected/f'{member}-{k}-factor0.5-metrics.json').read_text())['scores']
   def guards(z):
    c={name:scores[name]['rmse']<=z[name]['rmse'] for name in ['glass','rim','held','interior']};c.update(E=scores['E']<=z['E'],SSIM=scores['ssim']>=z['ssim'],exterior=scores['exterior']<=z['exterior'],partial=scores['partial']['RMSE']<=z['partial']['RMSE']);c.update({name:value<=z['foreground'][name] for name,value in scores['foreground'].items()});return c
   clipping=[int((preclip<0).sum()),int((preclip>1).sum()),int((encoded>1).sum())];row=dict(member=member,reference=k,scores=scores,baseline=before,matched78_guards=guards(before),working20_guards=guards(current),clipping=clipping,first_return_scene_nonzero=int((return_unit>0).sum()),maximum_return_scene=float(return_unit.max()),later_power_unassigned=True);prefix=f'{member}-{k}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=coverage);save(prefix+'-metrics.json',row);panels(prefix,s,old['complete'],C,crops);records.append(row);print(member,k,scores['E'],clipping,flush=True)
 last={f:sha(ROOT/f) for f in first};assert last==first;save('last-hashes.json',last);save('result.json',dict(status='FIXED_FIRST_RETURN_NATIVE_OBSERVATION_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,geometry=geometric,identities=identities,ledger=ledger,surface_tags=tags,fits=0,selected_model_changed=False,full_radiance=False,adopted=False));print('COMPLETE '+datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(e).__name__,message=str(e),ledger=ledger,surface_tags=tags));raise
