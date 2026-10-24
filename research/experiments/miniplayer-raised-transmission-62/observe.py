from pathlib import Path
import sys,json,datetime,ast,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from music_miniplayer_family import load_working_family,surface_for_member
from raised_perimeter_back import RaisedPerimeterRoundedBack
from geometric_optics import trace_flat_front_orthographic,fresnel_components
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import decode_srgb,encode_srgb
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n)
 if k=='score_calls':
  ledger['metric_gaussians']+=5*n;ledger['metric_erosions']+=n;assert ledger['metric_gaussians']<=P['caps']['metric_gaussians'] and ledger['metric_erosions']<=P['caps']['metric_erosions']
 save('ledger.json',ledger)
class Counted:
 def __init__(self,base):self.base=base;self.maximum_height=base.maximum_height;self.slope_bound=base.slope_bound
 def height_gradient(self,x,y):
  n=np.asarray(x).size;charge('height_points',n);charge('adapter_units',20*n);return self.base.height_gradient(x,y)
 def boundary_mask(self,x,y):
  n=np.asarray(x).size;charge('height_points',n);charge('adapter_units',20*n);return self.base.boundary_mask(x,y)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(helper),'exec'))
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});F=load_working_family();L=F['length_unit_native_pixels'];g=F['geometry'];data={};paths={};proof=[];controls=[];bindings={};preserved=json.loads((ROOT/'research/experiments/miniplayer-shared-transfer-06/preservation.json').read_text())['rows']
for row in preserved:
 member,k=row['member'],row['reference'];work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');assert sha(work/k/'case.json')==row['case_sha256']
 for n,d in row['hashes'].items():assert sha(work/k/n)==d;bindings[str((work/k/n).relative_to(ROOT))]=d
 charge('Study_mask_points',1360*250 if member=='expanded' else 920*240);s=Study(work/k);known=cv2.imread(str(work/k/'known.png'),0)>0;charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;mf=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz';m=np.load(mf);required=m['glass']|m['rim']|m['held']|m['exterior'];x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];required[b-y0:d-y0,a-x0:c-x0]=True
 data[(member,k)]={'s':s,'known':known,'safe':safe,'m':m,'required':required}
save('inputs-FIRST.json',bindings)
for member in ['expanded','compact']:
 old=surface_for_member(member);models={'monotone':old,'raised':RaisedPerimeterRoundedBack(old.half,old.radius,depth=.4,core_ratio=.1,crown_depth=.4,cap_join_width=0)}
 for name,b in models.items():
  surface=Counted(b);assert surface.slope_bound<1/np.sqrt(1.5**2-1);fx=np.array([0.,.2,-.2,old.half[0]-.2]);fy=np.array([.4,-.4,.6,0.]);charge('fixture_rays',4);charge('Snell_points',4);q=trace_flat_front_orthographic(surface,fx,fy,1.,F['optics']['background_distance']);assert q['complete'].all() and max(np.max(abs(q['X']-fx)),np.max(abs(q['Y']-fy)))<1e-12
  eps=1e-6;h,hx,hy,_=surface.height_gradient(fx,fy);dx=(surface.height_gradient(fx+eps,fy)[0]-surface.height_gradient(fx-eps,fy)[0])/(2*eps);dy=(surface.height_gradient(fx,fy+eps)[0]-surface.height_gradient(fx,fy-eps)[0])/(2*eps);err=max(np.max(abs(dx-hx)),np.max(abs(dy-hy)));assert err<1e-7;controls.append({'member':member,'model':name,'M':surface.slope_bound,'H':surface.maximum_height,'unit_index_identity':True,'gradient_FD_max':float(err)})
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_inputs_frozen':True,'controls':controls,'new_RGB_queries':0,'ledger':dict(ledger)})
for member in ['expanded','compact']:
 old=surface_for_member(member);models={'monotone':old,'raised':RaisedPerimeterRoundedBack(old.half,old.radius,depth=.4,core_ratio=.1,crown_depth=.4,cap_join_width=0)};case=data[(member,'a')]['s'].case;x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-center[0])/L;y=(yy-.25-center[1])/L
 for name,b in models.items():
  surface=Counted(b);charge('native_rays',x.size);charge('Snell_points',x.size);q=trace_flat_front_orthographic(surface,x,y,1.5,F['optics']['background_distance']);assert q['complete'].all();inside=q['inside'];X=q['X']*L+center[0];Y=q['Y']*L+center[1];a=np.floor(X).astype(int);bb=np.floor(Y).astype(int);paths[(member,name)]=(q,X,Y,a,bb);np.savez_compressed(OUT/f'{member}-{name}-paths.npz',X=q['X'],Y=q['Y'],inside=inside,complete=q['complete'],back=q['back'],outward_normal=q['outward_normal'])
  for k in ['a','b']:
   d=data[(member,k)];known=d['known'];safe=d['safe'];charge('source_audit_subrays',x.size);bounds=np.isfinite(X)&np.isfinite(Y)&(a>=0)&(bb>=0)&(a+1<known.shape[1])&(bb+1<known.shape[0]);ii,jj=np.nonzero(bounds);rawok=np.zeros_like(bounds);blurok=np.zeros_like(bounds)
   for out,mask in [(rawok,known),(blurok,safe)]:charge('bilinear_mask_lookups',4*len(ii));out[ii,jj]=mask[bb[ii,jj],a[ii,jj]]&mask[bb[ii,jj]+1,a[ii,jj]]&mask[bb[ii,jj],a[ii,jj]+1]&mask[bb[ii,jj]+1,a[ii,jj]+1]
   supported=np.where(inside,blurok,rawok);required=inside|np.repeat(np.repeat(d['required'],2,0),2,1);bad=int((required&~supported).sum());row={'member':member,'model':name,'reference':k,'whole':int(inside.sum()),'required':int(required.sum()),'unsupported_required':bad,'unknown_unscored':int((~supported&~required).sum()),'kernel_radius':21};proof.append(row);save('source-FIRST.json',{'status':'IN_PROGRESS_NO_RGB','records':proof});assert bad==0,'Undefined required source: stop without RGB';d[(name,'supported')]=supported
save('source-FIRST.json',{'status':'ALL_MODELS_MEMBERS_REFERENCES_PASS_BEFORE_RGB','records':proof,'observed_truth':False})
records=[]
for (member,k),d in data.items():
 charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(d['s'].source,d['known'],6.75);assert r==21 and np.array_equal(safe,d['safe']);H,W=d['s'].valid.shape
 for name in ['monotone','raised']:
  q,X,Y,a,bb=paths[(member,name)];inside=q['inside'];raw=np.full(X.shape+(3,),np.nan);supported=d[(name,'supported')]
  def sample(src,mask):
   ii,jj=np.nonzero(mask);charge('RGB_queries',len(ii));ia=a[ii,jj];ib=bb[ii,jj];wx=(X[ii,jj]-ia)[:,None];wy=(Y[ii,jj]-ib)[:,None];return (src[ib,ia]*(1-wx)+src[ib,ia+1]*wx)*(1-wy)+(src[ib+1,ia]*(1-wx)+src[ib+1,ia+1]*wx)*wy
  raw[inside]=sample(field,inside);clear=~inside&supported;raw[clear]=sample(d['s'].source,clear);charge('Fresnel_points',int(inside.sum()));R=fresnel_components(-q['outward_normal'][inside,2],1.5,1.).mean(-1);T=.96*(1-R);graded=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias']);encoded=encode_srgb(T[:,None]*decode_srgb(graded));clips=int(((encoded<0)|(encoded>1)).sum());changed=raw.copy();changed[inside]=np.clip(encoded,0,1);pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy());coverage=inside.reshape(H,2,W,2).mean((1,3));frozen=coverage if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'];partial=d['m']['glass']&(frozen<1);crops=json.loads((ROOT/'research/experiments/miniplayer-outline-light-07/protocol.json').read_text())['fixed_crops'][member];metrics=score(d['s'],C,d['m'],partial,crops);prefix=f'{member}-{k}-{name}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=coverage);row={'member':member,'reference':k,'model':name,'scores':metrics,'clipped_channels':clips,'retained_back_power_max':float((.96*R).max()),'full_radiance':False};records.append(row);save(prefix+'-metrics.json',row)
  width=min(W,1080);height=round(H*width/W);im=Image.new('RGB',(2*width+2,height+64),'white');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=16)
  for i,(v,label) in enumerate([(d['s'].target_crop,'Apple reference'),(C,f'Matched flat-front primary only: {name}')]):im.paste(to_image(v).resize((width,height),Image.Resampling.LANCZOS),(i*(width+2),64));draw.text((i*(width+2)+8,20),label,fill='black',font=font)
  im.save(OUT/f'{prefix}-comparison.png');print(member,k,name,metrics['E'],flush=True)
save('result.json',{'status':'ONE_RAISED_HEIGHT_AND_MATCHED_MONOTONE_CONTROL_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'fits':0,'full_radiance':False,'selected_model_changed':False,'scope':'Matched AA2 primary-transmission diagnostic; no complete-boundary or radiance fidelity claim. No full raw sample arrays archived; source coordinates, normals, inputs and complete outputs retained.'})
