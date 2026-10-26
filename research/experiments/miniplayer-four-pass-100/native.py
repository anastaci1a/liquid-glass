"""One smooth-family observation, with original inputs and source-first gates."""
from pathlib import Path
import sys,json,datetime,hashlib,ast,zipfile,time
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from shoulder_core_coordinate import ShoulderCoreSplineBack
from hermite_height_back import HermiteFootprintBack
from raised_front_optics import trace_raised_front_orthographic,VerticalScaleBack
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,annular_environment
PLAN=OUT;REDUCTION=float(sys.argv[1]);assert REDUCTION in [0.5,1.0,1.5];OUT=PLAN/f'native-s{REDUCTION}';OUT.mkdir(exist_ok=True)
P=json.loads((PLAN/'plan.json').read_text());END=datetime.datetime.fromisoformat(P['geometry_deadline']);F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());g=F['geometry'];L=F['length_unit_native_pixels'];cv2.setNumThreads(1)
ORIGINAL_RADIUS=g['corner_radius'];g['corner_radius']=ORIGINAL_RADIUS-1.25/L
ledger=dict.fromkeys(P['geometry_caps'],0);aux=dict.fromkeys(['mask_points','score_calls','SSIM_Gaussians','metric_erosions','cached_environment_points','new_environment_points','parity_RGB_queries'],0)
auxcaps={'mask_points':1121600,'score_calls':8,'SSIM_Gaussians':40,'metric_erosions':8,'cached_environment_points':2243200,'new_environment_points':2243200,'parity_RGB_queries':128}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Geometry clock'
 table,cap=(ledger,P['geometry_caps']) if k in ledger else (aux,auxcaps)
 assert table[k]+n<=cap[k],(k,table[k],n);table[k]+=int(n)
 if k=='score_calls':charge('SSIM_Gaussians',5*n);charge('metric_erosions',n)
def flush():save('native-ledger.json',{'geometry_cumulative':ledger,'separate_categories':aux})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path,keys):
 with zipfile.ZipFile(path) as z:
  for key in keys:
   with z.open(key+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_payload_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(path,allow_pickle=False) as z:return {k:z[k] for k in keys}
metric=ROOT/'research/experiments/miniplayer-outline-light-07/render.py';tree=ast.parse(metric.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(metric),'exec'))
def guards(now,before):
 z={k:now[k]['rmse']<=before[k]['rmse'] for k in ['glass','rim','held','interior']};z.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);z.update({k:v<=before['foreground'][k] for k,v in now['foreground'].items()});return z

def panels(prefix,s,base,C):
 H,W=C.shape[:2];sheet=Image.new('RGB',(3*W+4,H+38),'white');d=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=16)
 for i,(v,label) in enumerate([(s.target_crop,'Reference'),(base,'Original working20'),(C,'Separate tips and shoulders; incident blur retained')]):sheet.paste(to_image(v),(i*(W+2),38));d.text((i*(W+2)+4,8),label,font=font,fill='black')
 sheet.save(OUT/f'{prefix}-comparison.png')

def run():
 assert not (OUT/'native-started.json').exists();save('native-started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});save('native-reservations.json',{'additional_categories':auxcaps,'original_clock_and_caps_unchanged':True,'bitmap_policy':'Entire unchanged constructor inventory from57, excluding final panels; four extra known-mask decodes counted. Header/input hashes checked again before constructor.'})
 first={};data={};assert sha(ROOT/g['back_profile'])==g['back_profile_sha256'];first[g['back_profile']]=sha(ROOT/g['back_profile']);inv=json.loads((ROOT/'research/experiments/agent-outline-series-replay-57/headers-and-decode-reservation.json').read_text())
 # Bind all source/style/artwork bytes and masks before any Study or native ray.
 for row in json.loads((ROOT/'research/experiments/agent-outline-series-replay-57/foreground-assets-review.json').read_text())['assets']:
  assert sha(ROOT/row['file'])==row['sha256'];first[row['file']]=row['sha256']
 for f in [Path(__file__),ROOT/'reconstruction/shoulder_core_coordinate.py',ROOT/'reconstruction/raised_front_optics.py',ROOT/'reconstruction/hermite_height_back.py',ROOT/'reconstruction/spline_height_back.py',ROOT/'reconstruction/geometric_render.py',ROOT/'reconstruction/environment_radiance.py',ROOT/'reconstruction/families/music-mini-player-working.json']:
  first[str(f.relative_to(ROOT))]=sha(f)
 for member in ['expanded','compact']:
  work=ROOT/f'.evidence-working/{member}-geometry-0{2 if member=="expanded" else 1}'
  for k in ['a','b']:
   cp=work/k/'case.json';case=json.loads(cp.read_text());first[str(cp.relative_to(ROOT))]=sha(cp)
   for name,h in case['source_sha256'].items():assert sha(work/k/name)==h;first[str((work/k/name).relative_to(ROOT))]=h
   mp=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz';first[str(mp.relative_to(ROOT))]=sha(mp)
 for row in inv['bitmaps']:
  if row['role']=='Final saved comparison inspection':continue
  if 'dimensions' in row and not row['file'].endswith('.svg'):
   with Image.open(ROOT/row['file']) as im:assert list(im.size)==row['dimensions']
  charge('total_bitmap_pixels',row['pixels'])
 save('native-inputs-FIRST.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hashes':first,'all_constructor_dependencies_bound':True,'bitmap_reservation':ledger['total_bitmap_pixels']})
 for member in ['expanded','compact']:
  work=ROOT/f'.evidence-working/{member}-geometry-0{2 if member=="expanded" else 1}';center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
  if member=='compact':
   pr=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];c=json.loads((work/'a/case.json').read_text());center=np.array(c['center'])+L*np.array([pr['shape_dx'],pr['shape_dy']])
  center=center+np.array([-.5,0.])
  op=ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-paths.npz';oq=read(op,['inside','primary_power','front_reflection_power','front_reflection_direction']);first[str(op.relative_to(ROOT))]=sha(op);I=oq['inside'];charge('cached_environment_points',int(I.sum()));ou=oq['front_reflection_power'][I]*annular_environment(oq['front_reflection_direction'][I])
  for k in ['a','b']:
   charge('Studies',1);s=Study(work/k);H,W=s.valid.shape;charge('mask_points',H*W)
   mp=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz';m=read(mp,['glass','rim','held','exterior']);assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
   bp=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz';z=read(bp,['pre_foreground','complete','coverage']);first[str(bp.relative_to(ROOT))]=sha(bp)
   oldrawp=ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-{k}-light4.npz';raw=read(oldrawp,['raw_source'])['raw_source'];first[str(oldrawp.relative_to(ROOT))]=sha(oldrawp)
   vals=raw.copy();prim=neutral_color_response(raw[I],gain=F['material']['gain'],bias=F['material']['bias']);vals[I]=np.clip(encode_srgb(oq['primary_power'][I,None]*decode_srgb(prim)+4*ou[:,None]),0,1);pre=vals.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,z['pre_foreground'],equal_nan=True) and np.array_equal(C,z['complete'],equal_nan=True),'Original identity'
   frozen=z['coverage'] if member=='expanded' else read(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz',['coverage'])['coverage'];partial=m['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22)
   crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops'][member];before=score(s,C,m,partial,crops);original=json.loads((ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5-metrics.json').read_text())['scores'];assert before==original,'Original metrics replay'
   required=m['glass']|m['rim']|m['held']|m['exterior'];x0,y0,x1,y1=s.crop
   for layer in s.case['foreground_layers']:
    a,b,c,d=layer['box'];required[b-y0:d-y0,a-x0:c-x0]=True
   charge('total_bitmap_pixels',1920*1080);known=cv2.imread(str(work/k/'known.png'),0)>0
   data[(member,k)]=dict(s=s,m=m,partial=partial,crops=crops,baseline=z['complete'],before=before,known=known,required=required,center=center)
  del oq,raw,vals,z,pre,C
 save('identity-checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_pre_foreground_complete_and_metric_identities_exact':True,'original_masks_preserved':True});flush();print('FOUR IDENTITIES EXACT',flush=True)
 charge('geometry_configurations',1)
 save('active-recipe.json',{'shoulder_inset_native':REDUCTION,'dilation_reduction_native':1.25,'major_half_increment_native':1.5,'center_x_shift_native':-.5,'radius':g['corner_radius'],'incident_sigma':P['incident_sigma'],'same_normalized_height_laws':True,'Hermite_radial_nodes_scaled_and_derivatives_inverse_scaled':True})
 records=[]
 for member in ['expanded','compact']:
  d=data[(member,'a')];s=d['s'];center=d['center'];H,W=s.valid.shape;x0,y0,x1,y1=s.crop;half=(F['members'][member]['major_half']+1.5/L,g['minor_half']);base=ShoulderCoreSplineBack(half,g['corner_radius'],REDUCTION/L,g['breaks'],g['height_controls'],charge);profile=json.loads((ROOT/g['back_profile']).read_text());scale=base.radius/profile['radius_nodes'][-1];profile['radius_nodes']=(np.array(profile['radius_nodes'])*scale).tolist();profile['radius_nodes'][-1]=base.radius;profile['derivatives']=(np.array(profile['derivatives'])/scale).tolist();back=HermiteFootprintBack(base,profile);front=VerticalScaleBack(base,g['front_scale']);q={};metadata={}
  # Fresh unit-index and same-height derivative controls, before this native grid.
  Xc=np.array([-.8,-.4,.4,.8])*half[0];Yc=np.array([-.6,.6,-.6,.6])*half[1];eps=1e-6
  maxerr=0.
  for surf in [front,back]:
   charge('height_point_queries',len(Xc));hh,gx,gy,inside_control=surf.height_gradient(Xc,Yc)
   charge('height_point_queries',4*len(Xc));dx=(surf.height_gradient(Xc+eps,Yc)[0]-surf.height_gradient(Xc-eps,Yc)[0])/(2*eps);dy=(surf.height_gradient(Xc,Yc+eps)[0]-surf.height_gradient(Xc,Yc-eps)[0])/(2*eps)
   maxerr=max(maxerr,float(np.max(abs(dx-gx))),float(np.max(abs(dy-gy))))
  assert maxerr<1e-7
  charge('fixture_rays',len(Xc));fixture=trace_raised_front_orthographic(back,Xc,Yc,1.,1.,F['optics']['background_distance'],lambda label,n:charge('height_point_queries',n),front_surface=front)
  assert fixture['complete'].all() and np.max(abs(fixture['X']-Xc))<1e-9 and np.max(abs(fixture['Y']-Yc))<1e-9
  save(f'{member}-fixture-checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_gradient_error=maxerr,unit_index_straight=True,rays=len(Xc)))
  for start in range(0,2*H,32):
   stop=min(start+32,2*H);yy,xx=np.mgrid[start:stop,0:2*W];x=(x0+xx*.5-.25-center[0])/L;y=(y0+yy*.5-.25-center[1])/L;charge('native_rays',x.size)
   c=trace_raised_front_orthographic(back,x,y,1.,F['optics']['index'],F['optics']['background_distance'],lambda label,n:charge('height_point_queries',n),front_surface=front)
   np.savez_compressed(OUT/f'{member}-chunk-{start:04d}.npz',**c)
   for key,v in c.items():
    if v.ndim<2:
     if key=='iterations':metadata[key]=np.array(max(int(metadata.get(key,0)),int(v)))
     elif key=='front_reflection_escape_certificate':metadata[key]=np.array('Per-chunk certificates retained; regular launches certified individually')
     else:metadata[key]=v
     continue
    if key not in q:q[key]=np.empty((2*H,2*W)+v.shape[2:],dtype=v.dtype)
    q[key][start:stop]=v
   flush();save('native-progress.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'member':member,'subrows_complete':stop,'total_subrows':2*H});print('TRACE',member,stop,'/',2*H,flush=True)
  assert q['complete'].all(),'Incomplete native primary path';q.update(metadata);np.savez_compressed(OUT/f'{member}-paths.npz',**q);inside=q['inside'];coverage=inside.reshape(H,2,W,2).mean((1,3));X=q['X']*L+center[0];Y=q['Y']*L+center[1];aa=np.floor(X).astype(int);bb=np.floor(Y).astype(int);proof=[]
  for k in ['a','b']:
   d=data[(member,k)];known=d['known'];charge('source_audit_subrays',X.size);charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((39,39),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
   bounds=np.isfinite(X)&np.isfinite(Y)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);ii,jj=np.nonzero(bounds);rawok=np.zeros_like(bounds);blur=np.zeros_like(bounds)
   for out,mask in [(rawok,known),(blur,safe)]:
    charge('source_corner_lookups',4*len(ii));out[ii,jj]=mask[bb[ii,jj],aa[ii,jj]]&mask[bb[ii,jj]+1,aa[ii,jj]]&mask[bb[ii,jj],aa[ii,jj]+1]&mask[bb[ii,jj]+1,aa[ii,jj]+1]
   supported=np.where(inside,blur,rawok);required=inside|np.repeat(np.repeat(d['required'],2,0),2,1);row={'reference':k,'whole_body':int(inside.sum()),'required_subrays':int(required.sum()),'unsupported_required':int((required&~supported).sum()),'unknown_unscored':int((~supported&~required).sum())};proof.append(row);save(f'{member}-source-FIRST.json',{'status':'PENDING','records':proof});assert not (required&~supported).any(),'Unsupported required source';d.update(safe=safe,supported=supported)
  save(f'{member}-source-FIRST.json',{'status':'BOTH_PASS_BEFORE_RGB','records':proof,'kernel_radius':19});charge('new_environment_points',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside])
  for k in ['a','b']:
   d=data[(member,k)];s=d['s'];charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(s.source,d['known'],6.075);assert r==19 and np.array_equal(safe,d['safe'])
   def sample(arr,mask):
    i,j=np.nonzero(mask);charge('RGB_queries',len(i));a,b=aa[i,j],bb[i,j];wx=(X[i,j]-a)[:,None];wy=(Y[i,j]-b)[:,None]
    result=(arr[b,a]*(1-wx)+arr[b,a+1]*wx)*(1-wy)+(arr[b+1,a]*(1-wx)+arr[b+1,a+1]*wx)*wy
    ids=np.unique(np.linspace(0,len(i)-1,min(8,len(i)),dtype=int));charge('parity_RGB_queries',len(ids));charge('RGB_queries',len(ids))
    for ix in ids:
     u,v=float(wx[ix,0]),float(wy[ix,0]);weights=np.array([(1-u)*(1-v),u*(1-v),(1-u)*v,u*v]);corners=np.stack([arr[b[ix],a[ix]],arr[b[ix],a[ix]+1],arr[b[ix]+1,a[ix]],arr[b[ix]+1,a[ix]+1]])
     reference=weights@corners;assert np.max(abs(reference-result[ix]))<2e-15,'Independent sampler parity'
    return result
   raw=np.full(X.shape+(3,),np.nan);raw[inside]=sample(field,inside);clear=~inside&d['supported'];raw[clear]=sample(s.source,clear)
   values=raw.copy();prim=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias']);encoded=encode_srgb(q['primary_power'][inside,None]*decode_srgb(prim)+4*unit[:,None]);clips=int(((encoded<0)|(encoded>1)).sum());values[inside]=np.clip(encoded,0,1)
   pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy());now=score(s,C,d['m'],d['partial'],d['crops']);gr=guards(now,d['before']);prefix=f'{member}-{k}-geometry';np.savez_compressed(OUT/f'{prefix}.npz',complete=C,pre_foreground=pre,raw_source=raw,encoded_subrays=values,coverage=coverage,inside=inside,supported=d['supported'],incident_field=field)
   panels(prefix,s,d['baseline'],C);row={'member':member,'reference':k,'scores':now,'baseline':d['before'],'guards':gr,'all_pass':all(gr.values()) and clips==0,'clipped_channels':clips,'new_partial_pixels':int(((coverage>0)&(coverage<1)).sum()),'old_partial_pixels':int(d['partial'].sum())};records.append(row);save(prefix+'-metrics.json',row);print('RESULT',member,k,now['E'],[n for n,v in gr.items() if not v],flush=True)
  del q,field,raw,values,encoded
 last={f:sha(ROOT/f) for f in first};assert first==last;save('native-first-hashes.json',first);save('native-last-hashes.json',last);save('geometry-result.json',{'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'family_qualifier':all(r['all_pass'] for r in records),'selected_state_changed':False,'conditional_source':True});flush()
try:run()
except Exception as e:
 save('native-failure.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':repr(e)});flush();raise
