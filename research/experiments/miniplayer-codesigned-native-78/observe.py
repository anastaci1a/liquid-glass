"""One coherent reconstructed back under the fixed exact perimeter front."""
from pathlib import Path
import sys,json,datetime,hashlib,ast,time
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from hermite_height_back import HermiteFootprintBack
from extended_fit import Study
from geometric_render import incident_source_filter,neutral_color_response
from raised_front_optics import trace_raised_front_orthographic
from bevel_footprint_back import BevelFootprintBack
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from music_miniplayer_family import load_working_family,working_surface_pair
from environment_radiance import annular_environment,decode_srgb,encode_srgb
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=load_working_family();L=F['length_unit_native_pixels'];ledger={k:0 for k in P['caps']};tags={};cv2.setNumThreads(1);last_report=time.monotonic()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 delta={k:int(n)}
 if k=='score_calls':delta.update(SSIM_Gaussians=5*n,metric_erosions=n)
 gate_charge(delta)
def gate_charge(delta):
 global last_report
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline';assert all(ledger[k]+n<=P['caps'][k] for k,n in delta.items()),delta
 for k,n in delta.items():ledger[k]+=int(n)
 save('ledger.json',dict(ledger,callback_tags=dict(tags)))
 if time.monotonic()-last_report>15:print('PROGRESS '+datetime.datetime.now(datetime.timezone.utc).isoformat()+' '+str(ledger['surface_point_callbacks']),flush=True);last_report=time.monotonic()
def count(label,n):
 gate_charge({'surface_point_callbacks':int(n),'conservative_adapter_units':20*int(n)});tags[label]=tags.get(label,0)+int(n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ExactPerimeterFront:
 """No new height law: delegate bevel; classify exact projected axial creases."""
 def __init__(self,base):
  self.base=base;self.coordinate=base.coordinate;self.maximum_height=base.maximum_height;self.slope_bound=base.slope_bound
 def height_gradient(self,x,y):return self.base.height_gradient(x,y)
 def boundary_mask(self,x,y):
  x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));a,b=self.base.half;r=self.base.radius
  axial=((abs(x)==a)&(abs(y)<=b-r))|((abs(y)==b)&(abs(x)<=a-r))
  return self.base.boundary_mask(x,y)|axial
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
for file,names in [(helper,['score','display','to_image']),(ROOT/'research/experiments/miniplayer-direct-front-envelope-74/observe.py',['panels'])]:
 tree=ast.parse(file.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 # Only literal figure labels change; no numerical model code is imported.
 class Labels(ast.NodeTransformer):
  def visit_Constant(self,node):
   if isinstance(node.value,str):node.value=node.value.replace('Uniform upper environment, radiance 4','Front8 + back77; coherent back').replace('Uniform white scene','Front8 + back77')
   return node
 functions=[Labels().visit(n) for n in functions];exec(compile(ast.fix_missing_locations(ast.Module(body=functions,type_ignores=[])),str(file),'exec'))
def trace(back,front,x,y,index,native=False):
 n=np.asarray(x).size;delta={('native_rays' if native else 'fixture_rays'):n,'reserved_Snell_points':2*n,'reserved_Fresnel_points':2*n,'reserved_reflection_points':n,'conservative_adapter_units':10*n};gate_charge(delta)
 return trace_raised_front_orthographic(back,x,y,1.,index,F['optics']['background_distance'],charge=count,front_surface=front)
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 prior=json.loads((ROOT/'research/experiments/miniplayer-neutral-scattering-71/first-hashes.json').read_text());first={f:sha(ROOT/f) for f in prior};assert first==prior
 for f in [str(Path(__file__).relative_to(ROOT)),str(helper.relative_to(ROOT)),'reconstruction/bevel_footprint_back.py','reconstruction/raised_front_optics.py','reconstruction/hermite_height_back.py','reconstruction/geometric_optics.py','research/experiments/miniplayer-direct-front-envelope-74/observe.py']:first[f]=sha(ROOT/f)

 for member in ['expanded','compact']:
  f=f'research/experiments/miniplayer-perimeter-front-75/{member}-paths.npz';first[f]=sha(ROOT/f)
 first[P['profile']]=sha(ROOT/P['profile']);assert first[P['profile']]==P['profile_sha256'];design_model=json.loads((ROOT/P['profile']).read_text())
 save('first-hashes.json',first);data={};models={};BASE=ROOT/'research/experiments/miniplayer-incident-material-20';PATHS=ROOT/'research/experiments/miniplayer-inverse-forward-18'
 # Freeze original masks, source/vector bytes and four exact current identities first.
 for member in ['expanded','compact']:
  oldq=np.load(PATHS/f'{member}-paths.npz');inside=oldq['inside'];oldunit=oldq['front_reflection_power'][inside]*annular_environment(oldq['front_reflection_direction'][inside]);oldT=oldq['primary_power'][inside];work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for k in ['a','b']:
   charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape;source=np.load(PATHS/f'{member}-{k}-light4.npz');raw=source['raw_source'];z=np.load(BASE/f'{member}-{k}-factor0.5.npz');values=raw.copy();coded=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias']);values[inside]=np.clip(encode_srgb(oldT[:,None]*decode_srgb(coded)+4*oldunit[:,None]),0,1);pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,z['pre_foreground'],equal_nan=True) and np.array_equal(C,z['complete'],equal_nan=True)
   m=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz');assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held']);known=cv2.imread(str(work/k/'known.png'),0)>0;required=m['glass']|m['rim']|m['held']|m['exterior'];x0,y0,_,_=s.crop
   for layer in s.case['foreground_layers']:
    a,b,c,d=layer['box'];required[b-y0:d-y0,a-x0:c-x0]=True
   center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
   if member=='compact':
    oldpose=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=np.array(s.case['center'])+L*np.array([oldpose['shape_dx'],oldpose['shape_dy']])
   before=json.loads((BASE/f'{member}-{k}-factor0.5-metrics.json').read_text())['scores'];original=next(r['baseline'] for r in json.loads((PATHS/'result.json').read_text())['records'] if r['member']==member and r['reference']==k);coverage=source['coverage'];frozen=coverage if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'];partial=m['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22);crops=json.loads((PATHS/'protocol.json').read_text())['fixed_crops'][member]
   data[(member,k)]=dict(s=s,H=H,W=W,raw=raw,oldinside=inside,m=m,known=known,required=required,center=center,baseline=C,before=before,original=original,coverage=coverage,partial=partial,crops=crops)
 controls=[];sections={}
 for member in ['expanded','compact']:
  oldback,oldfront=working_surface_pair(member);back=HermiteFootprintBack(oldback,design_model);bevel=BevelFootprintBack(back.coordinate,oldfront.maximum_height,8.);front=ExactPerimeterFront(bevel);assert front.coordinate is back.coordinate;assert front.slope_bound<1/np.sqrt(3);models[member]=(back,front);a,b=bevel.half;r=bevel.radius
  gradient_error=0.
  for X,Y in [(0.,.75*b),(.5*a,.85*b),(a-r+.3*r,b-r+.4*r),(-a+r-.3*r,-b+r-.4*r)]:
   eps=1e-6;count('fixture_direct_height',5);h,hx,hy,_=back.height_gradient(X,Y);dx=(back.height_gradient(X+eps,Y)[0]-back.height_gradient(X-eps,Y)[0])/(2*eps);dy=(back.height_gradient(X,Y+eps)[0]-back.height_gradient(X,Y-eps)[0])/(2*eps);gradient_error=max(gradient_error,float(max(abs(dx-hx),abs(dy-hy))))
  assert gradient_error<1e-8
  fx,fy=np.meshgrid(np.array([-a+.2,-1.,0.,1.,a-.2]),np.array([-.5,0.,.5]));results={}
  for index in [1.,1.5]:
   q=trace(back,front,fx,fy,index);assert q['complete'].all();assert np.max(abs(q['X']+q['X'][:,::-1]))<1e-9 and np.max(abs(q['Y']-q['Y'][:,::-1]))<1e-9
   if index==1:assert np.max(abs(q['X']-fx))<1e-9 and np.max(abs(q['Y']-fy))<1e-9
   results[str(index)]={'complete':int(q['complete'].sum()),'minimum_back_clearance':float(np.nanmin(q['primary_back_clearance'])),'minimum_front_clearance':float(np.nanmin(q['primary_front_clearance']))}
  poles=trace(back,front,np.array([a,-a,0.,0.,0.]),np.array([0.,0.,b,-b,0.]),1.5);assert poles['boundary_unresolved'][:4].all() and (~poles['complete'][:4]).all() and np.isnan(poles['X'][:4]).all() and np.isnan(poles['front_normal'][:4]).all()
  for axis,span in [('x',a),('y',b)]:
   v=np.linspace(-span,span,513);zero=np.zeros_like(v);x,y=(v,zero) if axis=='x' else (zero,v);count('section_front_height',len(v));fh=front.height_gradient(x,y)[0];count('section_back_height',len(v));bh=back.height_gradient(x,y)[0];sections[f'{member}_{axis}']=np.stack([x,y,fh,-bh],axis=-1)
  controls.append(dict(member=member,front_height=bevel.depth,power=8.,front_global_slope=front.slope_bound,back_global_slope=back.slope_bound,gradient_error=gradient_error,exact_poles_unresolved=True,front_circle_control="Reused unchanged75algebra; no duplicatecircleprobe",paths=results))
 np.savez_compressed(OUT/'actual-sections.npz',**sections);now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=now.isoformat(),controls=controls,four_baseline_identities_exact=True,ledger=dict(ledger)));print('CHECKPOINT '+now.isoformat()+' new back geometry/crease controls PASS; fixed front75 controls reused',flush=True)
 proof=[];paths={}
 # Complete both grids and all four reference audits before building any RGB field.
 for member,(back,front) in models.items():
  d=data[(member,'a')];x0,y0,x1,y1=d['s'].crop;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-d['center'][0])/L;y=(yy-.25-d['center'][1])/L;print('NATIVE '+member,flush=True);q=trace(back,front,x,y,1.5,True);np.savez_compressed(OUT/f'{member}-paths.npz',**q);assert q['complete'].all(),'Incomplete native primary path';old75=np.load(ROOT/f'research/experiments/miniplayer-perimeter-front-75/{member}-paths.npz')
  for field in ['front','front_normal','interior_direction','front_reflection_direction','front_reflection_power']:
   assert np.array_equal(q[field],old75[field],equal_nan=True),('Fixed front changed',field)
  maps=[]
  for label,oldmap in [('working18',np.load(PATHS/f'{member}-paths.npz')),('front75',old75)]:
   lens=q['inside'];charge('map_component_comparisons',2*int(lens.sum()));distance=np.hypot(q['X'][lens]-oldmap['X'][lens],q['Y'][lens]-oldmap['Y'][lens]);maps.append(dict(comparison=label,maximum_source_error_L=float(distance.max()),mean_source_error_L=float(distance.mean()),maximum_source_error_native=float(distance.max()*L)))
   if label=='working18':assert distance.max()<=1e-4,'Transport preservation objective failed'
  save(f'{member}-map-diagnostic.json',dict(records=maps,direct_front_fields_exact_to75=True,actual_coordinates_never_replaced=True))
  assert np.array_equal(q['inside'],d['oldinside']),'Changed original coverage';coverage=q['inside'].reshape(d['H'],2,d['W'],2).mean((1,3));assert np.array_equal(coverage,d['coverage']);assert (q['front_reflection_direction'][q['inside'],2]>0).all();paths[member]=q
  X=q['X']*L+d['center'][0];Y=q['Y']*L+d['center'][1];a,b=np.floor(X).astype(int),np.floor(Y).astype(int)
  for k in ['a','b']:
   d=data[(member,k)];known=d['known'];charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;bounds=np.isfinite(X)&np.isfinite(Y)&(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);ii,jj=np.nonzero(bounds);rawok=np.zeros_like(bounds);blur_ok=np.zeros_like(bounds);charge('source_audit_subrays',X.size)
   for out,mask in [(rawok,known),(blur_ok,safe)]:
    charge('bilinear_known_lookups',4*len(ii));out[ii,jj]=mask[b[ii,jj],a[ii,jj]]&mask[b[ii,jj]+1,a[ii,jj]]&mask[b[ii,jj],a[ii,jj]+1]&mask[b[ii,jj]+1,a[ii,jj]+1]
   supported=np.where(q['inside'],blur_ok,rawok);required=q['inside']|np.repeat(np.repeat(d['required'],2,0),2,1);row=dict(member=member,reference=k,emitted=X.size,whole=int(q['inside'].sum()),required_union=int(required.sum()),unsupported_required=int((required&~supported).sum()),unavailable_unscored=int((~required&~supported).sum()),radius=21,RGB_queries=0);proof.append(row);save('source-FIRST.json',dict(status='IN_PROGRESS_BEFORE_RGB',records=proof));assert not (required&~supported).any(),'Unsupported required source';d.update(X=X,Y=Y,a=a,b=b,safe=safe)
 save('source-FIRST.json',dict(status='ALL_FOUR_COMPLETE_BEFORE_RGB',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=proof,observed_truth=False));print('SOURCE FIRST all four PASS',flush=True);records=[]
 for member,q in paths.items():
  inside=q['inside'];charge('environment_direction_queries',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);T=q['primary_power'][inside]
  for k in ['a','b']:
   d=data[(member,k)];charge('incident_fields',1);charge('known_erosions',1);field,safe,radius=incident_source_filter(d['s'].source,d['known'],6.75);assert radius==21 and np.array_equal(safe,d['safe']);a,b=d['a'][inside],d['b'][inside];wx=(d['X'][inside]-a)[:,None];wy=(d['Y'][inside]-b)[:,None];charge('source_RGB_queries',len(a));sample=(field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy;assert np.isfinite(sample).all();coded,preclip=neutral_color_response(sample,gain=F['material']['gain'],bias=F['material']['bias'],return_preclip=True);encoded=encode_srgb(T[:,None]*decode_srgb(coded)+4*unit[:,None]);clips=[int((preclip<0).sum()),int((preclip>1).sum()),int((encoded>1).sum())];raw=d['raw'].copy();raw[inside]=np.clip(encoded,0,1);pre=raw.reshape(d['H'],2,d['W'],2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy());now=score(d['s'],C,d['m'],d['partial'],d['crops'])
   def guards(before):
    z={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};z.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);z.update({n:x<=before['foreground'][n] for n,x in now['foreground'].items()});return z
   checks=guards(d['before']);matched=json.loads((ROOT/f'research/experiments/miniplayer-perimeter-front-75/{member}-{k}-metrics.json').read_text())['scores'];row=dict(member=member,reference=k,scores=now,baseline=d['before'],current_guards=checks,matched_front75_guards=guards(matched),original_numerical_guards=guards(d['original']),clipping=clips,all_current_pass=all(checks.values()) and not any(clips),later_reflected_power_unassigned=True);prefix=f'{member}-{k}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage']);save(prefix+'-metrics.json',row);panels(prefix,d['s'],d['baseline'],C,d['crops']);records.append(row);print(member,k,now['E'],row['all_current_pass'],flush=True)
 last={f:sha(ROOT/f) for f in first};assert last==first;save('last-hashes.json',last);save('result.json',dict(status='ONE_COHERENT_TWO_SURFACE_NATIVE_OBSERVATION_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),controls=controls,records=records,ledger=ledger,callback_tags=tags,all_family_guards_pass=all(r['all_current_pass'] for r in records),selected_model_changed=False,adopted=False,fits=0,clear_RGB_queries=0,full_radiance=False,retention='All new path fields, actual sections, pre/complete/coverage and recipes retained; new incident fields and full sampledRGB are reproducible, not separately archived.'))
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(e).__name__,message=str(e),ledger=ledger,callback_tags=tags));raise
