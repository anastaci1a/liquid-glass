from pathlib import Path
import sys,json,datetime,hashlib,zipfile,ast,struct,math
import numpy as np,cv2
from PIL import Image,ImageDraw
O=Path(__file__).parent;ROOT=O.parents[2];B=O.parent/'agent-music-search-baseline-01';T=O.parent/'agent-music-search-neutral-05';OLD=O.parent/'agent-search-perimeter-transfer-38';LAST=OLD;WORK=ROOT/'.evidence-working/music-search-baseline-01';P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']};functions={};meta={'header_bytes':0,'decoded_NPY_bytes':0,'decoded_NPY_members':0,'PNG_decoded_pixels':0,'metadata_helper_calls':0};headers=[]
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Original clock'
def save(f,x):(O/f).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 gate();n=int(n);assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=n
# All selected NPY headers are checked before loading their array payloads.
def load(path,names):
 gate();out={}
 with zipfile.ZipFile(path) as z:
  assert len(z.namelist())<=64 and len(set(z.namelist()))==len(z.namelist())
  for name in names:
   with z.open(name+'.npy') as f:
    assert f.read(6)==b'\x93NUMPY';v=tuple(f.read(2));assert v in [(1,0),(2,0)];n=struct.unpack('<H' if v==(1,0) else '<I',f.read(2 if v==(1,0) else 4))[0];assert n<=4096;h=ast.literal_eval(f.read(n).decode('latin1'));d=np.dtype(h['descr']);assert not d.hasobject and not h['fortran_order'];size=math.prod(h['shape'])*d.itemsize;assert z.getinfo(name+'.npy').file_size==8+(2 if v==(1,0) else 4)+n+size;assert meta['decoded_NPY_bytes']+size<=P['decode_limits']['logical_decoded_payload_bytes'];meta['header_bytes']+=n+12;headers.append({'path':str(path.relative_to(ROOT)),'member':name,'shape':h['shape'],'dtype':d.str,'bytes':size})
   with np.load(path,allow_pickle=False) as q:out[name]=q[name]
   meta['decoded_NPY_bytes']+=size;meta['decoded_NPY_members']+=1
 return out
# Inspect PNG headers before Study/filter/known decode; reserve container sizes explicitly.
for k in ['a','b']:
 for n in ['source.png','target.png','known.png']:
  raw=(WORK/k/n).read_bytes()[:33];assert raw[:8]==b'\x89PNG\r\n\x1a\n';w,h,depth,color,*_=struct.unpack('>IIBBBBB',raw[16:29]);assert w<=1920 and h<=1080 and depth==8;headers.append({'path':str((WORK/k/n).relative_to(ROOT)),'PNG_size':[w,h],'bitdepth':depth,'color_type':color})
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response,incident_source_filter
from bevel_footprint_back import BevelFootprintBack
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from hermite_height_back import HermiteFootprintBack
import raised_front_optics as ro,geometric_optics as go
from environment_radiance import decode_srgb,encode_srgb,annular_environment
cv2.setNumThreads(1)
mods={str(Path(m.__file__).resolve()):m for m in [ro,go,sys.modules['bevel_footprint_back'],sys.modules['hermite_height_back'],sys.modules['rounded_rectangle_back']]}
generated={BevelFootprintBack.__init__.__code__:'BevelFootprintBack.generated_init',RoundedRectangleHarmonicBack.__init__.__code__:'RoundedRectangle.generated_init'}
scalar={'__post_init__','half','radius','maximum_height','slope_bound','upper','<lambda>'}
def profile(frame,event,arg):
 if event!='call':return
 code=frame.f_code;file=str(Path(code.co_filename).resolve()) if not code.co_filename.startswith('<') else code.co_filename
 if code in generated:label=generated[code];n=1
 elif file in mods:
  gate();name=code.co_name;a=frame.f_locals;label=Path(file).name+':'+name
  if name in ['<module>']:return
  if name in ['count','hg','level','expand']:
   meta['metadata_helper_calls']+=1
   # hg/level delegates are charged at actual model entry; expand is only metadata scatter.
   return
  if name in scalar:n=1
  elif name=='__init__':n=4096 if 'model' in a else 1
  elif name in ['height_gradient','boundary_mask','footprint','trace_raised_front_orthographic']:n=np.asarray(a['x']).size
  elif name=='profile':n=np.asarray(a['r']).size
  elif name=='bevel_profile':n=np.asarray(a['rho']).size
  elif name=='radial_profile':n=np.asarray(a['radius']).size
  elif name in ['refract','reflect_direction']:n=np.asarray(a['incident']).size//3
  elif name=='fresnel_components':n=np.asarray(a['cosine']).size
  elif name in ['escape_clearance','monotone_front_reflection_escape']:n=np.asarray(a['direction']).size//3
  else:raise RuntimeError('Undeclared selected delegate '+label)
 else:return
 charge('nested_units',n);functions[label]=functions.get(label,0)+int(n)
def build(radius,scale):
 c=RoundedRectangleHarmonicBack((radius,radius),radius,cap_join_width=0);f=BevelFootprintBack(c,recipe['depth']*scale,recipe['power']);m={**model,'radius_nodes':(np.asarray(model['radius_nodes'])/Rf*radius).tolist(),'heights':(np.asarray(model['heights'])*scale).tolist()};b=HermiteFootprintBack(f,m);return f,b
def trace(f,b,x,y,n=1.5,native=False,D0=None):
 N=np.asarray(x).size;charge('native_rays' if native else 'fixture_parity_records',N);return ro.trace_raised_front_orthographic(b,x,y,1.,n,D if D0 is None else D0,front_surface=f)
F=json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text());Rf=F['geometry']['corner_radius'];R=.9972124917582454;scl=R/Rf;D=2.1*scl;L=89;center=np.array([1511.2043368857017,672.8753258356955]);recipe=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());model=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/back-profile.json').read_text());gain=.5552987769129158;bias=.3908368353448866
result={'status':'STARTING','records':[]};data={}
try:
 for p,h in json.loads((O/'first-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 qold=load(OLD/'native-paths.npz',['X','Y','inside']);Iold=qold['inside'];charge('cached_annular_evaluations',int(Iold.sum()));oldpaths=load(OLD/'native-paths.npz',['primary_power','front_reflection_power','front_reflection_direction']);oldunit=oldpaths['front_reflection_power'][Iold]*annular_environment(oldpaths['front_reflection_direction'][Iold])
 for k in ['a','b']:
  charge('Study_constructors',1);st=Study(WORK/k);H,W=st.valid.shape;charge('mask_points',H*W);meta['PNG_decoded_pixels']+=2*1920*1080;m=load(B/f'{k}-masks.npz',['glass','rim','held','exterior','foreground','required']);assert np.array_equal(st.valid,m['glass']) and np.array_equal(st.rim,m['rim']) and np.array_equal(st.held,m['held'])
  old=load(OLD/f'{k}-candidate.npz',['sample_before_response','coverage','inside','support']);last=load(LAST/f'{k}-candidate.npz',['pre_foreground','complete']);raw=old['sample_before_response'];v=raw.copy();v[Iold]=np.clip(encode_srgb(oldpaths['primary_power'][Iold,None]*decode_srgb(neutral_color_response(raw[Iold],gain=gain,bias=bias))+4*oldunit[:,None]),0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=st.apply_foreground(pre.copy());assert np.array_equal(pre,last['pre_foreground'],equal_nan=True) and np.array_equal(C,last['complete'],equal_nan=True),'Search38 zero identity';data[k]=dict(st=st,m=m,old=old,last=last,raw=raw)
 # No selected shared numerical body has run before installing this persistent hook.
 save('call-chain-and-reservation.json',{'selected_modules':list(mods),'generated_constructors':list(generated.values()),'numeric_units':'Every selected shared entry, including nested Bevel properties, HG/boundary, bevel_profile, coordinate, Hermite profile, Snell/reflection/Fresnel, monotone and escape. Metadata-only closure scatter separately counted.','static_native_bound':'19*N + 4*(34+2)*I + 9*I + 10000 scalar/property units; reserve before actual native launch','setup_and_fixtures_reserved_units':250000,'PNG_Study_reserved_pixels':8294400,'known_PNG_reserved_pixels':4147200,'source_field_filter_pixels':4147200,'finite_kernel':43,'new_fields':2,'filter_and_proof_erosions':4,'score_calls':4,'metric_Gaussians':20,'metric_erosions':4,'cache_limit_bytes':536870912,'geometry_FD_atol':1e-5,'position_scale_mirror_atol':1e-9,'normal_scale_atol':1e-9})
 assert ledger['nested_units']+250000<=P['caps']['nested_units'];sys.setprofile(profile);front,back=build(R,scl);fc,bc=build(Rf,1.)
 xs=np.repeat([0.,.3,.6,.9,.98],4);a=np.tile(np.array([[1,0],[-1,0],[0,1],[0,-1]]),(5,1));x=xs*a[:,0]*R;y=xs*a[:,1]*R
 qa=trace(front,back,x,y);qc=trace(fc,bc,x/scl,y/scl,D0=2.1);assert qa['complete'].all() and qc['complete'].all()
 for n in ['X','Y']:np.testing.assert_allclose(qa[n],scl*qc[n],atol=1e-9,rtol=0)
 for n in ['front_normal','outward_normal','interior_direction','exit_direction']:np.testing.assert_allclose(qa[n],qc[n],atol=1e-9,rtol=0)
 for n in ['front','back']:np.testing.assert_allclose(qa[n],scl*qc[n],atol=1e-9,rtol=0)
 xx=np.r_[x,[R,-R,0,0]];yy=np.r_[y,[0,0,R,-R]];qi=trace(front,back,xx,yy,n=1.);assert qi['complete'][:-4].all() and not qi['complete'][-4:].any() and qi['boundary_unresolved'][-4:].all() and np.isnan(qi['X'][-4:]).all();np.testing.assert_allclose(qi['X'][:-4],xx[:-4],atol=1e-9,rtol=0);np.testing.assert_allclose(qi['Y'][:-4],yy[:-4],atol=1e-9,rtol=0)
 mirror=trace(front,back,-x,-y);np.testing.assert_allclose(mirror['X'],-qa['X'],atol=1e-9,rtol=0);np.testing.assert_allclose(mirror['Y'],-qa['Y'],atol=1e-9,rtol=0)
 errors=[]
 for f in [front,back]:
  for X,Y in [(R*.2,R*.2),(R*.7,R*.3),(R*.94,0)]:
   e=1e-6;h,hx,hy,_=f.height_gradient(X,Y);dx=(f.height_gradient(X+e,Y)[0]-f.height_gradient(X-e,Y)[0])/(2*e);dy=(f.height_gradient(X,Y+e)[0]-f.height_gradient(X,Y-e)[0])/(2*e);error=max(abs(dx-hx),abs(dy-hy));assert error<1e-5;errors.append(float(error))
 gate(True);save('checkpoint.json',{'status':'PASS_INPUTS_TWO_38_IDENTITIES_AND_NEW_GEOMETRY_CONTROLS','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gradient_errors':errors,'scaled_depth':front.depth,'power':front.power,'D':D,'same_height_normal_order_escape_checks':True,'ledger':ledger.copy()});print('CHECKPOINT_PASS',flush=True)
 # Native, source and RGB phase follows below without a permission wait.
 yy,xx=np.mgrid[560:795:.5,1395:1635:.5];x=(xx-.25-center[0])/L;y=(yy-.25-center[1])/L;inside_expected=front.coordinate.footprint(x,y)[0]<=1;I=int(inside_expected.sum());N=x.size;maxhi=(front.maximum_height+back.maximum_height)/math.sqrt(1-(math.sin(math.atan(front.slope_bound)))**2);iterations=math.ceil(math.log2(maxhi/1e-11));assert iterations<=34;reservation=19*N+4*(iterations+2)*I+9*I+10000;assert ledger['nested_units']+reservation<=P['caps']['nested_units'];save('native-reservation.json',{'before':ledger['nested_units'],'N':N,'I':I,'max_bisections':iterations,'reserved_nested_upper':reservation,'global_cap':P['caps']['nested_units']});q=trace(front,back,x,y,native=True);np.savez_compressed(O/'native-paths.npz',**q);assert q['complete'].all(),'Incomplete primary';inside=q['inside'];assert np.array_equal(inside,inside_expected) and np.array_equal(inside,Iold);cov=inside.reshape(H,2,W,2).mean((1,3));X=q['X']*L+center[0];Y=q['Y']*L+center[1];aa=np.floor(X).astype(int);bb=np.floor(Y).astype(int);proof=[]
 for k,d in data.items():
  assert np.array_equal(cov,d['old']['coverage']);known=np.asarray(Image.open(WORK/k/'known.png'))>0;meta['PNG_decoded_pixels']+=known.size;charge('erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0).astype(bool);bounds=np.isfinite(X)&np.isfinite(Y)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);rr,cc=np.nonzero(bounds);rawok=np.zeros_like(bounds);blurok=rawok.copy()
  for dst,mask in [(rawok,known),(blurok,safe)]:
   charge('corner_lookups',4*len(rr));dst[rr,cc]=mask[bb[rr,cc],aa[rr,cc]]&mask[bb[rr,cc]+1,aa[rr,cc]]&mask[bb[rr,cc],aa[rr,cc]+1]&mask[bb[rr,cc]+1,aa[rr,cc]+1]
  charge('source_audit_subrays',N);supported=np.where(inside,blurok,rawok);required=inside|np.repeat(np.repeat(d['m']['required'],2,0),2,1);row={'reference':k,'whole':I,'required':int(required.sum()),'unsupported_required':int((required&~supported).sum()),'unknown_unscored':int((~supported&~required).sum()),'RGB_before':ledger['RGB_queries']};proof.append(row);save('source-FIRST.json',{'status':'IN_PROGRESS','records':proof});assert not (required&~supported).any(),'Unsupported required source';assert np.array_equal(q['X'][~inside],qold['X'][~inside]) and np.array_equal(q['Y'][~inside],qold['Y'][~inside]),'Clear coordinate identity';assert np.array_equal(supported[~inside],d['old']['support'][~inside]),'Clear support identity';d.update(known=known,safe=safe,support=supported)
 save('source-FIRST.json',{'status':'PASS_BOTH_BEFORE_FIELDS_OR_RGB','records':proof,'observed_truth':False});print('SOURCE_PASS',flush=True)
 # Material/output work only below. Persistent geometry ledger remains intact.
 charge('cached_annular_evaluations',I);unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops']
 def metric(st,arr,m):
  charge('score_calls',1);charge('metric_Gaussians',5);charge('metric_erosions',1);z=st.scores(arr);z['E']=float(np.sqrt(z['loss']));err=(arr-st.target_crop)*255;z['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));z['foreground_RMSE']=float(np.sqrt(np.mean(err[m['foreground']]**2)));return z
 def local(st,C):
  out={};x0,y0,_,_=st.crop;luma=np.array([.2126,.7152,.0722])
  for name,(a,b,c,d) in crops.items():
   e=(C[b-y0:d-y0,a-x0:c-x0].astype(float)-st.target_crop[b-y0:d-y0,a-x0:c-x0].astype(float))*255;e=e[np.isfinite(e).all(2)];v=e@luma;ch=e-v[:,None];out[name]={'bounds':[a,b,c,d],'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean(v*v))),'chroma_RMSE':float(np.sqrt(np.mean(ch*ch))),'signed_RGB':e.mean(0).tolist()}
  return out
 for k,d in data.items():
  gate();st=d['st'];m=d['m'];charge('incident_fields',1);charge('erosions',1);field,sm,r=incident_source_filter(st.source,d['known'],6.739785650363237);assert r==21 and np.array_equal(sm,d['safe']);raw=d['raw'].copy();rr,cc=np.nonzero(inside);charge('RGB_queries',len(rr))
  for start in range(0,len(rr),65536):
   ri=rr[start:start+65536];ci=cc[start:start+65536];a=aa[ri,ci];b=bb[ri,ci];wx=(X[ri,ci]-a)[:,None];wy=(Y[ri,ci]-b)[:,None];raw[ri,ci]=(field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
  # Shared sampler AST parity on six 2x2 raw/AA patches, including clear misses.
  tree=ast.parse((ROOT/'reconstruction/geometric_render.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render_rows');nodes=[];started=False
  for node in fn.body:
   txt=ast.unparse(node)
   if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='C' for t in node.targets):started=True
   if started and (txt.startswith('C = np.full') or isinstance(node,ast.If) and ast.unparse(node.test) in ['defined.all() and (not exact_bilinear)','incident_source is not None'] or isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='result' for t in node.targets)):nodes.append(node)
  assert len(nodes)==4;sampler=compile(ast.Module(body=nodes,type_ignores=[]),'shared-sampler-only','exec');parity=[]
  for name,mask in [('lens',(cov==1)&m['glass']),('clear',(cov==0)&m['exterior']),('partial',(cov>0)&(cov<1)&m['required'])]:
   coords=np.argwhere(mask);rp,cp=coords[len(coords)//2];top=int(min(max(rp-1,0),H-2));left=int(min(max(cp-1,0),W-2));sub=(slice(2*top,2*(top+2)),slice(2*left,2*(left+2)));defined=d['support'][sub];charge('fixture_parity_records',16);charge('RGB_queries',int(defined.sum()+(defined&inside[sub]).sum()));ns={'np':np,'cv2':cv2,'source':st.source,'incident_source':field,'X':X[sub],'Y':Y[sub],'defined':defined,'exact_bilinear':True,'q':{'inside':inside[sub]},'start':0,'stop':2,'s':2,'x0':0,'x1':2};exec(sampler,ns);expected=raw[sub].reshape(2,2,2,2,3).mean((1,3)).astype(np.float32);assert np.array_equal(ns['C'],raw[sub],equal_nan=True) and np.array_equal(ns['result'],expected,equal_nan=True),'Exact shared sampler parity';parity.append({'cohort':name,'patch':[left,top],'raw_and_AA_exact':True})
  grade,preclip=neutral_color_response(raw[inside],gain=gain,bias=bias,return_preclip=True);linear=q['primary_power'][inside,None]*decode_srgb(grade)+4*unit[:,None];encoded=encode_srgb(linear);v=raw.copy();v[inside]=np.clip(encoded,0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=st.apply_foreground(pre.copy());scores={'original':metric(st,pre,m),'complete':metric(st,C,m)};scores['original']['foreground_RMSE']=scores['complete']['foreground_RMSE'];partial=m['glass']&(cov<1);assert int(partial.sum())==38;part=float(np.sqrt(np.mean(((C-st.target_crop)[partial]*255)**2)));prior=json.loads((LAST/f'{k}-metrics.json').read_text());selected=json.loads((T/f'full-{k}-result.json').read_text())['scores'];guards={}
  for name,base in [('selected',selected),('transfer38',prior['scores'])]:
   g={}
   for role in ['original','complete']:
    now=scores[role];before=base[role];g[role]={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};g[role].update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior_RMSE']<=before['exterior_RMSE'],foreground=now['foreground_RMSE']<=before['foreground_RMSE'])
   g['partial38']=part<=(prior['partial_selected'] if name=='selected' else prior['partial38_RMSE']);guards[name]=g
  assert np.array_equal(raw[~inside],d['raw'][~inside],equal_nan=True)
  np.savez_compressed(O/f'{k}-candidate.npz',sample_before_response=raw,sample_after_response=v,linear_inside=linear,encoded_preclip_inside=encoded,neutral_preclip_inside=preclip,coverage=cov,inside=inside,support=d['support'],pre_foreground=pre,complete=C,unassigned_back_power=q['retained_back_power'])
  row={'reference':k,'scores':scores,'guards':guards,'partial38_RMSE':part,'partial_selected':prior['partial_selected'],'partial38_baseline':prior['partial38_RMSE'],'clipping':{'neutral_low':int((preclip<0).sum()),'neutral_high':int((preclip>1).sum()),'encoded_low':int((encoded<0).sum()),'encoded_high':int((encoded>1).sum())},'clear_reused_exact':True,'fixed_crops':local(st,C),'parity':parity,'tail_unassigned':True};result['records'].append(row);save(k+'-metrics.json',row)
  canvas=Image.new('RGB',(1926,540),'white');draw=ImageDraw.Draw(canvas)
  for j,(arr,label) in enumerate([(st.target_crop,'Apple'),(load(T/f'full-{k}-candidate.npz',['complete'])['complete'],'Selected Search'),(d['last']['complete'],'Transfer38'),(C,'Shallow transfer39')]):
   finite=np.isfinite(arr).all(2);ry,rx=np.indices(finite.shape);display=np.where(finite[...,None],arr,np.where(((rx//6+ry//6)%2)[...,None],.72,.9));im=Image.fromarray(np.uint8(np.rint(np.clip(display,0,1)*255)));canvas.paste(im.resize((480,470),Image.Resampling.NEAREST),(482*j,64));draw.text((482*j+8,20),label,fill='black')
  canvas.save(O/f'{k}-comparison.png');print('CANDIDATE',k,scores['complete']['E'],guards,flush=True)
 result['status']='ONE_UNFITTED_SHALLOW_TRANSFER_PAIR_READY';result['selected_state_changed']=False
except Exception as e:result.update(status='STOPPED_FIRST_INVARIANT',failure=repr(e));print('STOP',repr(e),flush=True)
finally:
 sys.setprofile(None);result.update(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),ledger=ledger);save('result.json',result);save('ledger.json',ledger);save('function-units.json',functions);save('decode-and-metadata.json',{'actual':meta,'headers':headers});print('FINAL',result['status'],ledger,flush=True)
