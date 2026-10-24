"""Complete geometry-selected boundary integration; optical state is frozen."""
from pathlib import Path
import sys,json,datetime,hashlib,ast
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from music_miniplayer_family import load_working_family,surface_for_member
from pixel_quadrature import rounded_rectangle_pixel_rule
from hermite_height_back import HermiteFootprintBack
from bevel_footprint_back import BevelFootprintBack
from raised_front_optics import trace_raised_front_orthographic
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,planar_annular_emitter
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline';d={k:int(n)}
 if k=='score_calls':d.update(metric_gaussians=5*n,metric_erosions=n)
 assert all(ledger[a]+b<=P['caps'][a] for a,b in d.items()),d
 for a,b in d.items():ledger[a]+=int(b)
 save('ledger.json',ledger)
def count(label,n):charge('surface_points',n);charge('adapter_units',20*n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(X,Y,mask):
 charge('source_audit_points',len(X));assert np.isfinite(X).all() and np.isfinite(Y).all();a=np.floor(X).astype(int);b=np.floor(Y).astype(int);assert ((a>=0)&(b>=0)&(a+1<mask.shape[1])&(b+1<mask.shape[0])).all();charge('bilinear_mask_lookups',4*len(X));assert (mask[b,a]&mask[b,a+1]&mask[b+1,a]&mask[b+1,a+1]).all(),'Unsupported source before RGB'
def sample(field,X,Y):
 charge('RGB_queries',len(X));a=np.floor(X).astype(int);b=np.floor(Y).astype(int);wx=(X-a)[:,None];wy=(Y-b)[:,None];return (field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(helper),'exec'))
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});TEMP=Path('/tmp/boundary-quadrature');TEMP.mkdir();F=load_working_family();L=F['length_unit_native_pixels'];model=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/back-profile.json').read_text());recipe=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());preserved=json.loads((ROOT/'research/experiments/miniplayer-shared-transfer-06/preservation.json').read_text())['rows'];data={};identities=[];bindings={};geometry={};proof=[];files=[]
for row in preserved:
 member,k=row['member'],row['reference'];work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');assert sha(work/k/'case.json')==row['case_sha256']
 for n,digest in row['hashes'].items():assert sha(work/k/n)==digest;bindings[str((work/k/n).relative_to(ROOT))]=digest
 charge('Study_mask_points',1360*250 if member=='expanded' else 920*240);s=Study(work/k);known=cv2.imread(str(work/k/'known.png'),0)>0;charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 old=np.load(ROOT/f'research/experiments/miniplayer-finite-emitter-48/{member}-{k}.npz');pre=old['pre_foreground'];C=old['complete'];charge('identity_composites',1);assert np.array_equal(s.apply_foreground(pre.copy()),C,equal_nan=True)
 masks=np.load(work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz');coverage=np.load(ROOT/f'research/experiments/miniplayer-shallow-native-42/{member}-{k}-light4.npz')['coverage'];frozen=coverage if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'];partial=masks['glass']&(frozen<1);crops=json.loads((ROOT/'research/experiments/miniplayer-shallow-native-42/protocol.json').read_text())['fixed_crops'][member];before=score(s,C,masks,partial,crops);assert before==json.loads((ROOT/f'research/experiments/miniplayer-finite-emitter-48/{member}-{k}-metrics.json').read_text())['scores']
 data[(member,k)]={'s':s,'known':known,'safe':safe,'pre':pre,'C':C,'coverage':coverage,'masks':masks,'partial':partial,'crops':crops,'before':before};identities.append({'member':member,'reference':k,'complete_and_scores_exact':True})
save('identities-FIRST.json',identities);save('input-hashes.json',bindings)
for member in ['expanded','compact']:
 old=surface_for_member(member);back=HermiteFootprintBack(old,model);front=BevelFootprintBack(old.coordinate,recipe['depth'],recipe['power']);s=data[(member,'a')]['s'];case=s.case;x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0
 center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 yy,xx=np.mgrid[y0:y1,x0:x1];delta=np.abs(np.stack([xx-center[0],yy-center[1]],-1));core=(np.array(old.half)-old.radius)*L;r=old.radius*L;dmin=np.linalg.norm(np.maximum(delta-.5-core,0),axis=-1);dmax=np.linalg.norm(np.maximum(delta+.5-core,0),axis=-1);mask=(dmin<=r)&(dmax>=r);iy,ix=np.nonzero(mask);pixels=np.c_[ix+x0,iy+y0];charge('boundary_pixels',len(pixels));geometry[member]=(iy,ix,pixels)
 cp=np.concatenate([p+np.array([[-.25,-.25],[.25,-.25],[-.25,.25],[.25,.25]]) for p in pixels]);geometry[(member,'clear')]=cp
 for k in ['a','b']:audit(cp[:,0],cp[:,1],data[(member,k)]['known'])
 for order in [8,16]:
  for start in range(0,len(pixels),128):
   block=pixels[start:start+128];zz=[rounded_rectangle_pixel_rule(p,(old.half[0]*L,old.half[1]*L),r,center=center,order=order) for p in block];points=np.concatenate([z['points'] for z in zz]);w=np.concatenate([z['weights'] for z in zz]);idx=np.concatenate([np.full(len(z['weights']),start+i,int) for i,z in enumerate(zz)]);n=len(w);charge('quadrature_nodes',n)
   if not n:continue
   charge('native_rays',n);charge('Snell_points',2*n);charge('Fresnel_points',2*n);charge('reflection_points',n);q=trace_raised_front_orthographic(back,(points[:,0]-center[0])/L,(points[:,1]-center[1])/L,1,1.5,F['optics']['background_distance'],count,front_surface=front);assert q['inside'].all() and q['complete'].all() and not q['boundary_unresolved'].any();X=q['X']*L+center[0];Y=q['Y']*L+center[1]
   for k in ['a','b']:audit(X,Y,data[(member,k)]['safe']);audit(points[:,0],points[:,1],data[(member,k)]['known'])
   charge('panel_intersections',n);em=planar_annular_emitter(q['front']*L+np.array([*center,0]),q['front_reflection_direction'],panel_z=1770,center_xy=(960,540));assert em['reaches_panel'].all();f=TEMP/f'{member}-{order}-{start}.npz';np.savez(f,X=X,Y=Y,points=points,w=w,idx=idx,T=q['primary_power'],light=q['front_reflection_power']*em['unit_radiance']);files.append((member,order,f));proof.append({'member':member,'order':order,'start':start,'paths':n,'both_references_supported':True,'cache_sha256':sha(f)})
   if not (OUT/'checkpoint.json').exists():save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_identities_exact':True,'first_chunk_source_both_pass_before_RGB':True,'ledger':dict(ledger)})
save('source-FIRST.json',{'status':'ALL_NEW_BOUNDARY_NODES_BOTH_REFERENCES_ORDERS_PASS_BEFORE_RGB','records':proof,'kernel_radius':21,'observed_truth':False,'unchanged_interiors':'Prior48 source proof transfers through exact unchanged coordinates and inputs. No interior convergence claim.'})
records=[];values={}
for (member,k),d in data.items():
 charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(d['s'].source,d['known'],6.75);assert r==21 and np.array_equal(safe,d['safe']);iy,ix,pixels=geometry[member];cp=geometry[(member,'clear')];fullclear=sample(d['s'].source,cp[:,0],cp[:,1]).reshape(-1,4,3).mean(1)
 for order in [8,16]:
  boundary=fullclear.copy();area=np.zeros(len(pixels));clips=0
  for m,o,f in files:
   if m!=member or o!=order:continue
   z=np.load(f);raw=sample(field,z['X'],z['Y']);clear=sample(d['s'].source,z['points'][:,0],z['points'][:,1]);graded=neutral_color_response(raw,gain=F['material']['gain'],bias=F['material']['bias']);enc=encode_srgb(z['T'][:,None]*decode_srgb(graded)+4*z['light'][:,None]);clips+=int(((enc<0)|(enc>1)).sum());glass=np.clip(enc,0,1);np.add.at(boundary,z['idx'],z['w'][:,None]*(glass-clear));np.add.at(area,z['idx'],z['w'])
  assert np.all((area>=0)&(area<=1+1e-12)) and np.isfinite(boundary).all();pre=d['pre'].copy();pre[iy,ix]=boundary.astype(np.float32);unchanged=np.ones(pre.shape[:2],bool);unchanged[iy,ix]=False;assert np.array_equal(pre[unchanged],d['pre'][unchanged],equal_nan=True);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy());scores=score(d['s'],C,d['masks'],d['partial'],d['crops']);coverage=d['coverage'].copy();coverage[iy,ix]=area;prefix=f'{member}-{k}-order{order}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=coverage);row={'member':member,'reference':k,'order':order,'scores':scores,'old_AA2_scores':d['before'],'clipped_channels':clips,'non_boundary_pre_pixels_exact':True};save(prefix+'-metrics.json',row);records.append(row);values[(member,k,order)]=C
  if order==16:
   H,W=pre.shape[:2];width=min(W,1080);height=round(H*width/W);im=Image.new('RGB',(2*width+2,height+64),'white');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=16)
   for i,(v,label) in enumerate([(d['s'].target_crop,'Apple reference'),(C,'Fixed optics; geometric boundary integration16')]):im.paste(to_image(v).resize((width,height),Image.Resampling.LANCZOS),(i*(width+2),64));draw.text((i*(width+2)+8,20),label,fill='black',font=font)
   im.save(OUT/f'{member}-{k}-comparison.png')
summary=[]
for member in ['expanded','compact']:
 for k in ['a','b']:
  iy,ix,_=geometry[member];err=abs(values[(member,k,8)][iy,ix]-values[(member,k,16)][iy,ix]);summary.append({'member':member,'reference':k,'max_completed_boundary_RGB_difference_8_16':float(err.max()),'RMS_completed_boundary_RGB_difference_8_16':float(np.sqrt(np.mean(err**2)))})
save('result.json',{'status':'ALL_GEOMETRIC_BOUNDARY_PIXELS_RENDERED_TWO_FIXED_ORDERS','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'order_comparison':summary,'ledger':ledger,'optical_parameters_changed':False,'selected_model_changed':False,'full_image_continuous_convergence':False,'path_retention':'Source-proof chunk hashes and reproducible quadrature recipe retained. Full ephemeral new path arrays not archived; original42 paths remain untouched.'});print(json.dumps({'summary':summary,'ledger':ledger}),flush=True)
