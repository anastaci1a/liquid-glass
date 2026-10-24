"""One fixed curved-front geometry, complete source-first observation."""
from pathlib import Path
import sys, json, datetime, hashlib, ast
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response, incident_source_filter
from music_miniplayer_family import load_family, surface_for_member
from raised_front_optics import trace_raised_front_orthographic, VerticalScaleBack
from environment_radiance import annular_environment, decode_srgb, encode_srgb
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'))
F=load_family();ledger={k:0 for k in P['caps']};cv2.setNumThreads(1)
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline'
def charge(key,n):
 gate();assert ledger[key]+n<=P['caps'][key],key
 ledger[key]+=int(n);save('ledger.json',ledger)
def count(label,n):
 charge('back_height_point_calls',n)
 charge('conservative_nested_surface_units',(6 if label=='height' else 8)*n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Reuse only the frozen score/presentation function definitions, never its
# experiment body. No source/ray execution occurs while extracting these.
helpers=ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
tree=ast.parse(helpers.read_text());selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image','images']]
exec(compile(ast.Module(body=selected,type_ignores=[]),str(helpers),'exec'))
assert not (OUT/'started.json').exists(),'One final comparison only'
save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tracer_controls':'miniplayer-curved-front-08/checkpoint.json'})
records=[];bindings={}
for member in ['expanded','compact']:
 gate();surface=VerticalScaleBack(surface_for_member(member),.5)
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
  data[k]=dict(s=s,m=masks,case=case,known=known,accepted=accepted,required=required)
  for file in [work/k/'case.json',maskpath,*[work/k/n for n in s.case['source_sha256']]]:bindings[str(file.relative_to(ROOT))]=sha(file)
 assert data['a']['case']['center']==data['b']['case']['center']
 case=data['a']['case'];x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;L=F['length_unit_native_pixels']
 yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-case['center'][0])/L;y=(yy-.25-case['center'][1])/L
 charge('native_grid_rays',x.size);charge('snell_interface_points',2*x.size);charge('fresnel_interface_points',2*x.size);charge('front_reflection_points',x.size)
 q=trace_raised_front_orthographic(surface,x,y,1.,F['optics']['index'],F['optics']['background_distance'],count)
 np.savez_compressed(OUT/f'{member}-paths.npz',**q)
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
  gate();s=d['s'];charge('incident_fields',1);field,safemask,r=incident_source_filter(s.source,d['known'],6.75);assert r==21 and np.array_equal(safemask,d['safe'])
  def sample(field,mask):
   ii,jj=np.nonzero(mask);charge('source_RGB_queries',len(ii));a=aa[ii,jj];b=bb[ii,jj];wx=(X[ii,jj]-a)[:,None];wy=(Y[ii,jj]-b)[:,None]
   return (field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
  raw=np.full(X.shape+(3,),np.nan);raw[inside]=sample(field,inside);clear=~inside&d['supported'];raw[clear]=sample(s.source,clear)
  values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias'])
  baseC=d['accepted']['complete'];oldcoverage=d['accepted']['coverage']
  frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'] if member=='compact' else oldcoverage
  partial=d['m']['glass']&(frozen<1);crops=P['fixed_crops'][member];before=score(s,baseC,d['m'],partial,crops)
  for amplitude in [1.,4.]:
   lin=decode_srgb(values[inside])+amplitude*unit[:,None];encoded=encode_srgb(lin);clips=int((encoded>1).sum())
   changed=values.copy();changed[inside]=np.clip(encoded,0,1)
   pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy())
   now=score(s,C,d['m'],partial,crops)
   guards={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};guards.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);guards.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()})
   prefix=f'{member}-{k}-light{int(amplitude)}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=coverage,raw_source=raw)
   images(prefix,s,baseC,C,crops,int(amplitude))
   row=dict(member=member,reference=k,amplitude=amplitude,scores=now,baseline=before,guards=guards,all_pass=all(guards.values()),clipped_channels=clips,conditional_scene=True,tail_max_power=float(np.nanmax(q['retained_back_power'])))
   records.append(row);save(prefix+'-metrics.json',row);print(json.dumps({'member':member,'ref':k,'light':amplitude,'E':now['E'],'oldE':before['E'],'guards':guards}),flush=True);gate()
save('result.json',{'status':'FIXED_CURVED_FRONT_OBSERVATIONS_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'adopted':False})
save('input-hashes.json',bindings)
