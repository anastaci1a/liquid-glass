"""One fixed curved-front geometry, complete source-first observation."""
from pathlib import Path
import sys, json, datetime, hashlib, ast
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response, incident_source_filter
from music_miniplayer_family import load_working_family, surface_for_member
from raised_front_optics import trace_raised_front_orthographic, VerticalScaleBack
from hermite_height_back import HermiteFootprintBack
from bevel_footprint_back import BevelFootprintBack
from environment_radiance import annular_environment, decode_srgb, encode_srgb
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'))
F=load_working_family();ledger={k:0 for k in P['caps']};cv2.setNumThreads(1)
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline'
def charge(key,n):
 gate();assert ledger[key]+n<=P['caps'][key],key
 ledger[key]+=int(n);save('ledger.json',ledger)
def count(label,n):
 charge('surface_point_queries',n)
 charge('conservative_adapter_units',20*n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Reuse only the frozen score/presentation function definitions, never its
# experiment body. No source/ray execution occurs while extracting these.
helpers=ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
tree=ast.parse(helpers.read_text());selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image','images']]
exec(compile(ast.Module(body=selected,type_ignores=[]),str(helpers),'exec'))
assert not (OUT/'started.json').exists(),'One final comparison only'
save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tracer_controls':'miniplayer-curved-front-08/checkpoint.json'})
preserved=json.loads((ROOT/'research/experiments/miniplayer-shared-transfer-06/preservation.json').read_text())['rows']
expected=json.loads((ROOT/'research/experiments/miniplayer-split-surface-09/result.json').read_text())['records']
input_rows=[]
for row in preserved:
 member,key=row['member'],row['reference'];work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 assert sha(work/key/'case.json')==row['case_sha256']
 for name,digest in row['hashes'].items():assert sha(work/key/name)==digest
 maskfile=work/f'{key}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{key}-masks.npz'
 masks=np.load(maskfile);charge('reference_mask_archive_pixels',masks['glass'].size)
 before=next(r['baseline'] for r in expected if r['member']==member and r['reference']==key)
 assert int(masks['glass'].sum())==before['glass']['pixels'] and int(masks['rim'].sum())==before['rim']['pixels'] and int(masks['held'].sum())==before['held']['pixels']
 input_rows.append(dict(member=member,reference=key,case_hash_exact=True,input_hashes_exact=True,mask_archive_sha256=sha(maskfile)))
save('inputs-FIRST.json',dict(status='PASS_BEFORE_NEW_RAY_CONTROLS',records=input_rows))
model=json.loads((ROOT/'research/experiments/miniplayer-perimeter-curvature-39/back-profile.json').read_text())

front_recipe=json.loads((ROOT/'research/experiments/miniplayer-perimeter-curvature-39/front-geometry.json').read_text())
records=[];bindings={}
for member in ['expanded','compact']:
 gate();original=surface_for_member(member);charge('profile_bound_segments',len(model['heights'])-1);surface=HermiteFootprintBack(original,model);front=BevelFootprintBack(original.coordinate,front_recipe['depth'],front_recipe['power'])
 if member=='expanded':
  a=original.half[0];fx,fy=np.meshgrid(np.array([-a+.2,-1.,0.,1.,a-.2]),np.array([-.5,0.,.5]))
  for index in [1.,1.5]:
   charge('fixture_comparator_rays',fx.size);charge('reserved_Snell_interface_points',2*fx.size);charge('reserved_Fresnel_interface_points',2*fx.size);charge('reserved_reflection_points',fx.size)
   actual=trace_raised_front_orthographic(surface,fx,fy,1.,index,F['optics']['background_distance'],count,front_surface=front)
   assert actual['complete'].all() and np.max(abs(actual['X']+actual['X'][:,::-1]))<1e-9
   if index==1:assert np.max(abs(actual['X']-fx))<1e-9 and np.max(abs(actual['Y']-fy))<1e-9
  for X,Y in [(0.,original.half[1]-original.radius+.5*original.radius),(a-original.radius+.5*original.radius,0.),(a-original.radius+.3*original.radius,original.half[1]-original.radius+.3*original.radius)]:
   eps=1e-6;count('height',5);h,hx,hy,_=surface.height_gradient(X,Y);dx=(surface.height_gradient(X+eps,Y)[0]-surface.height_gradient(X-eps,Y)[0])/(2*eps);dy=(surface.height_gradient(X,Y+eps)[0]-surface.height_gradient(X,Y-eps)[0])/(2*eps)
   assert max(abs(dx-hx),abs(dy-hy))<P['geometry_tolerances']['gradient_FD']
  save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_shared_tracer_controls_reused=True,independent_front_controls=True,fixture_rays=ledger['fixture_comparator_rays'],source_RGB_queries=0,ledger=ledger))
 oldbase=ROOT/('research/experiments/expanded-contrast-guard-02' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06')
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 data={}
 for k in ['a','b']:
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240)
  s=Study(work/k);maskpath=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz'
  masks=np.load(maskpath);assert np.array_equal(s.valid,masks['glass']) and np.array_equal(s.rim,masks['rim']) and np.array_equal(s.held,masks['held'])
  case=dict(s.case)
  if member=='expanded':case['center']=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
  else:
   prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters']
   case['center']=(np.asarray(case['center'])+s.L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
  known=cv2.imread(str(work/k/'known.png'),0)>0
  accepted=np.load(oldbase/(f'{k}-candidate.npz' if member=='expanded' else f'compact-{k}-candidate.npz'))
  required=masks['glass']|masks['rim']|masks['held']|masks['exterior']
  for layer in s.case['foreground_layers']:
   a,b,c,d=layer['box'];cx0,cy0,_,_=s.crop;required[b-cy0:d-cy0,a-cx0:c-cx0]=True
  working=np.load(ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz');charge('identity_composites',1);identity=s.apply_foreground(working['pre_foreground'].copy());assert np.array_equal(identity,working['complete'],equal_nan=True)
  data[k]=dict(s=s,m=masks,case=case,known=known,accepted=accepted,required=required,working=working)
  for file in [work/k/'case.json',maskpath,*[work/k/n for n in s.case['source_sha256']]]:bindings[str(file.relative_to(ROOT))]=sha(file)
 assert data['a']['case']['center']==data['b']['case']['center']
 case=data['a']['case'];x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;L=F['length_unit_native_pixels']
 yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-case['center'][0])/L;y=(yy-.25-case['center'][1])/L
 charge('native_grid_rays',x.size);charge('reserved_Snell_interface_points',2*x.size);charge('reserved_Fresnel_interface_points',2*x.size);charge('reserved_reflection_points',x.size)
 q=trace_raised_front_orthographic(surface,x,y,1.,F['optics']['index'],F['optics']['background_distance'],count,front_surface=front)
 np.savez_compressed(OUT/f'{member}-paths.npz',**q)
 priorpath=ROOT/('research/experiments/expanded-spline-observation-01/native-paths.npz' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06/compact-paths.npz');priorq=np.load(priorpath);valid=q['inside']
 save(f'{member}-map-diagnostic.json',dict(maximum_coordinate_error_L=float(max(np.max(abs(q['X'][valid]-((priorq['X'][valid]-case['center'][0])/L if member=='expanded' else priorq['X'][valid]))),np.max(abs(q['Y'][valid]-((priorq['Y'][valid]-case['center'][1])/L if member=='expanded' else priorq['Y'][valid]))))),role='Diagnostic only; actual source coordinates never overwritten.'))
 inside=q['inside'];assert q['complete'].all(),'Incomplete path before source/RGB'
 coverage=inside.reshape(H,2,W,2).mean((1,3));assert np.array_equal(coverage,data['a']['accepted']['coverage'])
 X=q['X']*L+case['center'][0];Y=q['Y']*L+case['center'][1];aa=np.floor(X).astype(int);bb=np.floor(Y).astype(int)
 proof=[]
 for k,d in data.items():
  known=d['known'];charge('source_audit_subrays',x.size);charge('known_erosions',1)
  safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  bounds=np.isfinite(X)&np.isfinite(Y)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);ii,jj=np.nonzero(bounds)
  rawok=np.zeros_like(bounds);blur_ok=np.zeros_like(bounds)
  for out,mask in [(rawok,known),(blur_ok,safe)]:
   charge('bilinear_known_lookups',4*len(ii));out[ii,jj]=mask[bb[ii,jj],aa[ii,jj]]&mask[bb[ii,jj]+1,aa[ii,jj]]&mask[bb[ii,jj],aa[ii,jj]+1]&mask[bb[ii,jj]+1,aa[ii,jj]+1]
  supported=np.where(inside,blur_ok,rawok);required=inside|np.repeat(np.repeat(d['required'],2,0),2,1)
  row={'reference':k,'whole':int(inside.sum()),'required':int(required.sum()),'unsupported_required':int((required&~supported).sum()),'unknown_unscored':int((~supported&~required).sum()),'kernel_radius':21,'RGB_queries':0}
  proof.append(row);save(f'{member}-source-FIRST.json',{'status':'IN_PROGRESS','records':proof})
  assert not (required&~supported).any(),'Unsupported required source before RGB'
  d.update(supported=supported,safe=safe)
 save(f'{member}-source-FIRST.json',{'status':'PASS_BOTH_BEFORE_RGB','records':proof,'observed_truth':False})
 charge('environment_direction_queries',int(inside.sum()))
 unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside])
 for k,d in data.items():
  gate();s=d['s'];charge('incident_fields',1);charge('known_erosions',1);field,safemask,r=incident_source_filter(s.source,d['known'],6.75);assert r==21 and np.array_equal(safemask,d['safe'])
  def sample(field,mask):
   ii,jj=np.nonzero(mask);charge('source_RGB_queries',len(ii));a=aa[ii,jj];b=bb[ii,jj];wx=(X[ii,jj]-a)[:,None];wy=(Y[ii,jj]-b)[:,None]
   return (field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
  raw=np.full(X.shape+(3,),np.nan);raw[inside]=sample(field,inside);clear=~inside&d['supported'];raw[clear]=sample(s.source,clear)
  values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias'])
  baseC=d['working']['complete'];oldcoverage=d['accepted']['coverage']
  frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'] if member=='compact' else oldcoverage
  partial=d['m']['glass']&(frozen<1);crops=P['fixed_crops'][member];before=score(s,baseC,d['m'],partial,crops)
  for amplitude in [4.]:
   lin=q['primary_power'][inside,None]*decode_srgb(values[inside])+amplitude*unit[:,None];encoded=encode_srgb(lin);clips=int((encoded>1).sum())
   changed=values.copy();changed[inside]=np.clip(encoded,0,1)
   pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy())
   now=score(s,C,d['m'],partial,crops)
   guards={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};guards.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);guards.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()})
   original=json.loads((ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-{k}-light4-metrics.json').read_text())['baseline'];original_guards={n:now[n]['rmse']<=original[n]['rmse'] for n in ['glass','rim','held','interior']};original_guards.update(E=now['E']<=original['E'],SSIM=now['ssim']>=original['ssim'],exterior=now['exterior']<=original['exterior'],partial=now['partial']['RMSE']<=original['partial']['RMSE']);original_guards.update({n:v<=original['foreground'][n] for n,v in now['foreground'].items()})
   prefix=f'{member}-{k}-light{int(amplitude)}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=coverage,raw_source=raw)
   images(prefix,s,baseC,C,crops,int(amplitude))
   row=dict(member=member,reference=k,amplitude=amplitude,scores=now,baseline=before,guards=guards,original_guards=original_guards,all_original_pass=all(original_guards.values()),all_pass=all(guards.values()),clipped_channels=clips,conditional_scene=True,tail_max_power=float(np.nanmax(q['retained_back_power'])))
   records.append(row);save(prefix+'-metrics.json',row);print(json.dumps({'member':member,'ref':k,'light':amplitude,'E':now['E'],'oldE':before['E'],'guards':guards}),flush=True);gate()
save('result.json',{'status':'PERIMETER_CURVATURE_FORWARD_OBSERVATIONS_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'adopted':False})
save('input-hashes.json',bindings)
