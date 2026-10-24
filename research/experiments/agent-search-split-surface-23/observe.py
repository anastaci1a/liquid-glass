from pathlib import Path
import sys,json,datetime,hashlib,ast
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;ROOT=O.parents[2];B=O.parent/'agent-music-search-baseline-01';T=O.parent/'agent-music-search-neutral-05';WORK=ROOT/'.evidence-working/music-search-baseline-01'
P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def gate(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if checkpoint else 'deadline'].replace('Z','+00:00')),'Original deadline'
def save(f,v):gate();(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def count(label,n):
 charge('height_boundary_points',n);charge('delegated_units',(16 if label=='height' else 20)*n)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert not (O/'started.json').exists(),'Single execution only'
assert json.loads((O/'input-identity-FIRST.json').read_text())['all_real_bytes_match']
save('started.json',{'at':now()});result={'status':'STARTED','records':[],'ledger':ledger}
try:
 sys.path.insert(0,str(ROOT/'reconstruction'))
 import raised_front_optics as ro
 from geometric_optics import HarmonicCircularBack
 from geometric_render import neutral_color_response,incident_source_filter
 from extended_fit import Study
 from environment_radiance import annular_environment,decode_srgb,encode_srgb
 cv2.setNumThreads(1)
 par=json.loads((B/'protocol.json').read_text())['parameters'];R=par['R'];L=par['L'];center=np.array(par['center'])
 class RadiusBack:
  def __init__(self):self.base=HarmonicCircularBack(.15,.4);self.maximum_height=self.base.maximum_height;self.slope_bound=self.base.slope_bound/R
  def height_gradient(self,x,y):
   h,hx,hy,inside=self.base.height_gradient(np.asarray(x)/R,np.asarray(y)/R);return h,hx/R,hy/R,inside
  def boundary_mask(self,x,y):return self.base.boundary_mask(np.asarray(x)/R,np.asarray(y)/R)
 surface=ro.VerticalScaleBack(RadiusBack(),.5)
 # Runtime wrappers charge actual shared interface delegates; equations unchanged.
 for name,key in [('refract','snell_points'),('fresnel_components','fresnel_points'),('reflect_direction','reflect_points')]:
  original=getattr(ro,name)
  def wrapper(*a,_fn=original,_key=key,**kw):
   n=np.asarray(a[0]).size if _key=='fresnel_points' else np.asarray(a[0]).size//3
   charge(_key,n);return _fn(*a,**kw)
  setattr(ro,name,wrapper)
 def trace(x,y,n,native=False):
  N=np.broadcast_arrays(x,y)[0].size;charge('native_rays' if native else 'fixture_rays',N)
  assert ledger['height_boundary_points']+47*N<=P['caps']['height_boundary_points'],'Reserve graph points'
  assert ledger['delegated_units']+756*N<=P['caps']['delegated_units'],'Reserve delegated units'
  return ro.trace_raised_front_orthographic(surface,x,y,1.,n,2.,count)
 x=np.array([-.7,-.3,.2,.6]*4)*R;y=np.repeat([-.5,-.2,.3,.55],4)*R
 u=trace(x,y,1.);np.testing.assert_allclose(u['X'],x,atol=1e-10,rtol=0);np.testing.assert_allclose(u['Y'],y,atol=1e-10,rtol=0)
 f=trace(x,y,1.5);m=trace(-x,-y,1.5);np.testing.assert_allclose(m['X'],-f['X'],atol=1e-9,rtol=0);np.testing.assert_allclose(m['Y'],-f['Y'],atol=1e-9,rtol=0)
 assert u['complete'].all() and f['complete'].all() and m['complete'].all()
 for q0 in [u,f,m]:
  assert np.max(abs(q0['back_residual']))<=2e-11 and np.all(q0['outgoing_back_clearance']>0) and np.all(q0['reflection_front_clearance']>0)
 np.savez_compressed(O/'fixture-paths.npz',x=x,y=y,**f)
 gate(True);save('checkpoint.json',{'at':now(),'status':'PASS_INPUT_IDENTITY_UNIT_INDEX_MIRROR_GRAPH_ESCAPE','fixture_rays':ledger['fixture_rays'],'old_gradient_radius_controls_reused':True,'new_source_sampling':0,'ledger':ledger.copy()});print('CHECKPOINT_PASS',now(),flush=True)
 # Use original exact native phase, corrected center and original L.
 x0,y0,x1,y1=json.loads((WORK/'a/case.json').read_text())['crop'];H,W=y1-y0,x1-x0
 yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-center[0])/L;y=(yy-.25-center[1])/L
 save('native-reservation.json',{'at':now(),'rays':int(x.size),'max_height_boundary_points':47*int(x.size),'max_delegated_units':756*int(x.size),'ledger_before':ledger.copy()})
 q=trace(x,y,1.5,True);np.savez_compressed(O/'native-paths.npz',**q)
 inside=q['inside'];assert q['complete'].all(),'Incomplete native path'
 cov=inside.reshape(H,2,W,2).mean((1,3));X=q['X']*L+center[0];Y=q['Y']*L+center[1];a=np.floor(X).astype(int);b=np.floor(Y).astype(int)
 data={};proof=[]
 for k in ['a','b']:
  charge('Study_constructors',1);charge('mask_points',H*W);s=Study(WORK/k);masks=dict(np.load(B/f'{k}-masks.npz',allow_pickle=False));old=np.load(T/f'full-{k}-candidate.npz',allow_pickle=False)
  assert np.array_equal(s.valid,masks['glass']) and np.array_equal(s.rim,masks['rim']) and np.array_equal(s.held,masks['held'])
  assert np.array_equal(cov,old['coverage']) and int((masks['glass']&(cov<1)).sum())==38
  known=np.array(Image.open(WORK/k/'known.png'))>0;charge('source_mask_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0).astype(bool)
  bounds=np.isfinite(X)&np.isfinite(Y)&(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);rr,cc=np.nonzero(bounds);rawok=np.zeros_like(bounds);blurok=rawok.copy()
  for dst,mask in [(rawok,known),(blurok,safe)]:
   charge('known_corner_lookups',4*len(rr));dst[rr,cc]=mask[b[rr,cc],a[rr,cc]]&mask[b[rr,cc]+1,a[rr,cc]]&mask[b[rr,cc],a[rr,cc]+1]&mask[b[rr,cc]+1,a[rr,cc]+1]
  supported=np.where(inside,blurok,rawok);required=inside|np.repeat(np.repeat(masks['required'],2,0),2,1)
  proof.append({'reference':k,'whole':int(inside.sum()),'required':int(required.sum()),'unsupported_required':int((required&~supported).sum()),'unknown_unscored':int((~supported&~required).sum()),'radius':21,'native_subray_audits':int(x.size),'support_before_RGB':True})
  save('source-FIRST.json',{'status':'IN_PROGRESS','records':proof});assert not (required&~supported).any(),'Unsupported required sample'
  np.savez_compressed(O/f'{k}-support.npz',support=supported,required=required,incident_known=safe)
  data[k]=dict(s=s,m=masks,old=old,known=known,safe=safe,supported=supported)
 save('source-FIRST.json',{'status':'PASS_BOTH_BEFORE_RGB','records':proof,'observed_truth':False})
 # Score helper is the already validated exact Search completed/preFG guard scope.
 previous=O.parent/'agent-search-outline-light-21/observe.py';tree=ast.parse(previous.read_text());defs=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in ['score','diagnostic','display','im']];exec(compile(ast.Module(body=defs,type_ignores=[]),str(previous),'exec'))
 crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];luma=np.array([.2126,.7152,.0722]);charge('environment_queries',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);tail=q['retained_back_power'][inside]
 for k,d in data.items():
  s=d['s'];m=d['m'];old=d['old'];baseline=score(s,old['pre_foreground'],old['complete'],m)
  assert baseline==json.loads((T/f'full-{k}-result.json').read_text())['scores']['complete']
  charge('incident_fields',1);charge('source_mask_erosions',1);field,mask,r=incident_source_filter(s.source,d['known'],6.75);assert r==21 and np.array_equal(mask,d['safe'])
  raw=np.full(X.shape+(3,),np.nan)
  for use,texture in [(inside,field),(~inside&d['supported'],s.source)]:
   rr,cc=np.nonzero(use);charge('RGB_queries',len(rr))
   for first in range(0,len(rr),65536):
    ri=rr[first:first+65536];ci=cc[first:first+65536];aa=a[ri,ci];bb=b[ri,ci];fx=(X[ri,ci]-aa)[:,None];fy=(Y[ri,ci]-bb)[:,None]
    raw[ri,ci]=(texture[bb,aa]*(1-fx)+texture[bb,aa+1]*fx)*(1-fy)+(texture[bb+1,aa]*(1-fx)+texture[bb+1,aa+1]*fx)*fy
  oldraw=np.load(B/f'{k}-candidate.npz',allow_pickle=False)['sample_before_response'];assert np.array_equal(raw[~inside],oldraw[~inside],equal_nan=True),'Clear identity'
  values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=.5193880051291454,bias=.4473611800152188)
  partial=m['glass']&(cov<1);beforepart=float(np.sqrt(np.mean(((old['complete']-s.target_crop)[partial]*255)**2)))
  for amp in [1.,4.]:
   lin=decode_srgb(values[inside])+amp*unit[:,None];encoded=encode_srgb(lin);changed=values.copy();changed[inside]=np.clip(encoded,0,1);pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
   charge('candidate_composites',1);C=s.apply_foreground(pre.copy());z=score(s,pre,C,m);part=float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2)))
   guards={n:z[n]['rmse']<=baseline[n]['rmse'] for n in ['glass','rim','held','interior']};guards.update(E=z['E']<=baseline['E'],SSIM=z['ssim']>=baseline['ssim'],exterior=z['exterior_RMSE']<=baseline['exterior_RMSE'],foreground=z['foreground_RMSE']<=baseline['foreground_RMSE'],partial38=part<=beforepart)
   prefix=f'{k}-light{int(amp)}';np.savez_compressed(O/f'{prefix}.npz',sample_before_response=raw,sample_after_response=changed,pre_foreground=pre,complete=C,coverage=cov,linear_inside=lin,encoded_preclip_inside=encoded,unassigned_back_power=tail)
   row={'reference':k,'amplitude':amp,'scores':z,'baseline':baseline,'guards':guards,'all_guards_pass':all(guards.values()),'partial38_RMSE':part,'partial38_baseline':beforepart,'clipped_channels':int((encoded>1).sum()),'crops':diagnostic(s,C),'baseline_crops':diagnostic(s,old['complete']),'clear_exact':True,'unassigned_back_power_max':float(tail.max()),'scene':'Unobserved annular direct-front reflection, effective calibrated-primary hybrid; no complete radiometry'}
   result['records'].append(row);save(prefix+'-metrics.json',row)
   canvas=Image.new('RGB',(1444,534),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=17)
   for i,(arr,label) in enumerate([(s.target_crop,'Apple reference'),(old['complete'],'Selected Search'),(C,f'Split surfaces, light {int(amp)}')]):
    canvas.paste(im(arr).resize((480,470),Image.Resampling.NEAREST),(i*482,64));draw.text((i*482+8,20),label,font=font,fill='black')
   canvas.save(O/f'{prefix}-comparison.png');print('OBSERVATION',k,amp,z['E'],guards,flush=True);gate()
 result['status']='FIXED_PAIR_COMPLETE_PENDING_PRIMARY';result['selected_changed']=False
except Exception as e:result['status']='STOPPED_FIRST_INVARIANT';result['failure']=repr(e)
finally:
 result['finished']=now();(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(O/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FINAL',result['status'],result.get('failure'),flush=True)
