from common import *
import ast,math
from PIL import Image,ImageDraw,ImageFont
assert (O/'checkpoint.json').exists() and not (O/'native-started.json').exists(),'Single native phase after checkpoint'
result={'status':'STARTING_NATIVE','records':[],'ledger':ledger}
try:
 save('native-started.json',{'at':now(),'same_clock':P['deadline']})
 data=studies();x0,y0,x1,y1=data['a']['s'].crop;H,W=y1-y0,x1-x0;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-center[0])/L;y=(yy-.25-center[1])/L
 rho=base.coordinate.footprint(x,y)[0];Ninside=int((rho<=1).sum());delta=np.arctan(front.slope_bound)-np.arcsin(np.sin(np.arctan(front.slope_bound))/1.5);hi=(front.maximum_height+back.maximum_height)/np.cos(delta)*(1+16*np.finfo(float).eps);iterations=int(np.ceil(np.log2(hi/1e-11)));assert iterations<=34
 bound=19*x.size+4*(iterations+2)*Ninside+7*Ninside
 assert ledger['nested_units']+bound<=P['caps']['nested_units'],'Full native shared/delegate reservation'
 save('native-reservation.json',{'at':now(),'inside':Ninside,'max_bisections':iterations,'maximum_upper_bracket':float(hi),'conservative_nested_native_bound':int(bound),'nested_before':ledger['nested_units'],'formula':'18full-grid adapter batches +toptracer1;4shared delegates per backheight query for high+midpoints+final;7regular primitive/escape rows. Scalar setup and prior fixtures already charged.','source_audits_reserved':2*int(x.size),'RGB_native_plus_parity_upper':2*int(x.size)+192})
 q=trace(back,front,x,y,D,1.5,True);np.savez_compressed(O/'native-paths.npz',**q);assert q['complete'].all(),'Incomplete native primary path';assert np.array_equal(q['inside'],rho<=1)
 inside=q['inside'];cov=inside.reshape(H,2,W,2).mean((1,3));X=q['X']*L+center[0];Y=q['Y']*L+center[1];aa=np.floor(X).astype(int);bb=np.floor(Y).astype(int);proof=[]
 for k,d in data.items():
  st=d['s'];m=d['m'];assert np.array_equal(cov,d['old']['coverage']) and int((m['glass']&(cov<1)).sum())==38
  known=np.asarray(Image.open(WORK/k/'known.png'))>0;charge('erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0).astype(bool)
  bounds=np.isfinite(X)&np.isfinite(Y)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);rr,cc=np.nonzero(bounds);rawok=np.zeros_like(bounds);blurok=rawok.copy()
  for target,mask in [(rawok,known),(blurok,safe)]:
   charge('corner_lookups',4*len(rr));target[rr,cc]=mask[bb[rr,cc],aa[rr,cc]]&mask[bb[rr,cc]+1,aa[rr,cc]]&mask[bb[rr,cc],aa[rr,cc]+1]&mask[bb[rr,cc]+1,aa[rr,cc]+1]
  charge('source_audit_subrays',int(x.size));supported=np.where(inside,blurok,rawok);required=inside|np.repeat(np.repeat(m['required'],2,0),2,1)
  row={'reference':k,'whole':int(inside.sum()),'required':int(required.sum()),'unsupported_required':int((required&~supported).sum()),'unknown_unscored':int((~supported&~required).sum()),'kernel_radius':21,'source_RGB_queries_at_gate':ledger['RGB_queries']};proof.append(row);save('source-FIRST.json',{'status':'IN_PROGRESS','records':proof});assert not (required&~supported).any(),'Unsupported required source'
  np.savez_compressed(O/f'{k}-support.npz',known=known,incident_known=safe,support=supported,required=required)
  d.update(known=known,safe=safe,supported=supported)
 save('source-FIRST.json',{'status':'PASS_BOTH_BEFORE_CHANGED_FIELDS_RGB','records':proof,'observed_truth':False})
 # Independent reference uses EXACT unchanged shared sampling/AA statements only.
 # No second tracer and no repeated source proof; all coordinates are already certified.
 sourcefile=ROOT/'reconstruction/geometric_render.py';tree=ast.parse(sourcefile.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render_rows');nodes=[];start=False
 for node in fn.body:
  text=ast.unparse(node)
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='C' for t in node.targets):start=True
  if start and (text.startswith('C = np.full') or (isinstance(node,ast.If) and (ast.unparse(node.test)=='defined.all() and (not exact_bilinear)' or ast.unparse(node.test)=='incident_source is not None')) or (isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='result' for t in node.targets))):nodes.append(node)
 assert len(nodes)==4,('Shared sampler AST structure',len(nodes));sampler=compile(ast.Module(body=nodes,type_ignores=[]),str(sourcefile),'exec')
 crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];parity=[]
 def metric(st,arr,m):
  z=st.scores(arr);z['E']=float(np.sqrt(z['loss']));err=(arr-st.target_crop)*255;z['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));z['foreground_RMSE']=float(np.sqrt(np.mean(err[m['foreground']]**2)));return z
 def local(st,C):
  out={};luma=np.array([.2126,.7152,.0722])
  for name,(a,b,c,d) in crops.items():
   e=(C[b-y0:d-y0,a-x0:c-x0].astype(float)-st.target_crop[b-y0:d-y0,a-x0:c-x0].astype(float))*255;e=e[np.isfinite(e).all(2)];Y0=e@luma;ch=e-Y0[:,None];out[name]={'bounds':[a,b,c,d],'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean(Y0*Y0))),'chroma_RMSE':float(np.sqrt(np.mean(ch*ch))),'signed_RGB':e.mean(0).tolist()}
  return out
 unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside])
 for k,d in data.items():
  gate();st=d['s'];m=d['m'];supported=d['supported'];charge('incident_fields',1);charge('erosions',1);field,safe,radius=incident_source_filter(st.source,d['known'],6.739785650363237);assert radius==21 and np.array_equal(safe,d['safe'])
  raw=np.full(X.shape+(3,),np.nan)
  for use,texture in [(inside,field),(~inside&supported,st.source)]:
   rr,cc=np.nonzero(use);charge('RGB_queries',len(rr))
   for first in range(0,len(rr),65536):
    ri=rr[first:first+65536];ci=cc[first:first+65536];a=aa[ri,ci];b=bb[ri,ci];fx=(X[ri,ci]-a)[:,None];fy=(Y[ri,ci]-b)[:,None];raw[ri,ci]=(texture[b,a]*(1-fx)+texture[b,a+1]*fx)*(1-fy)+(texture[b+1,a]*(1-fx)+texture[b+1,a+1]*fx)*fy
  for name,mask in [('lens',(cov==1)&m['glass']),('clear',(cov==0)&m['exterior']),('partial',(cov>0)&(cov<1)&m['required'])]:
   coords=np.argwhere(mask);assert len(coords);rr,cc=coords[len(coords)//2];top=int(min(max(rr-1,0),H-2));left=int(min(max(cc-1,0),W-2));sub=(slice(2*top,2*(top+2)),slice(2*left,2*(left+2)));defined=supported[sub];charge('fixture_parity_records',16);charge('RGB_queries',int(defined.sum()+(defined&inside[sub]).sum()))
   ns={'np':np,'cv2':cv2,'source':st.source,'incident_source':field,'X':X[sub],'Y':Y[sub],'defined':defined,'exact_bilinear':True,'q':{'inside':inside[sub]},'start':0,'stop':2,'s':2,'x0':0,'x1':2}
   exec(sampler,ns);expected=raw[sub].reshape(2,2,2,2,3).mean((1,3)).astype(np.float32);assert np.array_equal(ns['C'],raw[sub],equal_nan=True) and np.array_equal(ns['result'],expected,equal_nan=True),'Shared raw/AA parity mismatch'
   parity.append({'reference':k,'cohort':name,'patch':[left,top,left+2,top+2],'raw_RGB_exact':True,'AA_integral_exact':True,'geometry_retraced':False,'source_proof_repeated':False});save('parity.json',{'records':parity,'shared_AST_nodes':4,'shared_source_sha256':sha(sourcefile)})
  values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=.596189238519786,bias=.3290237590837732);linear=decode_srgb(values[inside])+4*unit[:,None];encoded=encode_srgb(linear);changed=values.copy();changed[inside]=np.clip(encoded,0,1)
  pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=st.apply_foreground(pre.copy());original=metric(st,pre,m);complete=metric(st,C,m);before=json.loads((T/f'full-{k}-result.json').read_text())['scores'];partial=m['glass']&(cov<1);part=float(np.sqrt(np.mean(((C-st.target_crop)[partial]*255)**2)));oldpart=float(np.sqrt(np.mean(((d['old']['complete']-st.target_crop)[partial]*255)**2)))
  guards={}
  for role,score in [('original',original),('complete',complete)]:
   guards[role]={n:score[n]['rmse']<=before[role][n]['rmse'] for n in ['glass','rim','held','interior']};guards[role].update(E=score['E']<=before[role]['E'],SSIM=score['ssim']>=before[role]['ssim'],exterior=score['exterior_RMSE']<=before[role]['exterior_RMSE'],foreground=score['foreground_RMSE']<=before[role]['foreground_RMSE'])
  guards['partial38']=part<=oldpart
  oldraw=np.load(B/f'{k}-candidate.npz',allow_pickle=False)['sample_before_response'];assert np.array_equal(raw[~inside],oldraw[~inside],equal_nan=True),'Clear raw identity'
  np.savez_compressed(O/f'{k}-candidate.npz',sample_before_response=raw,sample_after_response=changed,linear_inside=linear,encoded_preclip_inside=encoded,inside=inside,support=supported,coverage=cov,raw_lens=np.where(inside[...,None],raw,np.nan),raw_clear=np.where((~inside)[...,None],raw,np.nan),pre_foreground=pre,complete=C,unassigned_back_power=q['retained_back_power'])
  row={'reference':k,'scores':{'original':original,'complete':complete},'baseline':before,'guards':guards,'partial38_RMSE':part,'partial38_baseline':oldpart,'clipped_channels':int((encoded>1).sum()),'raw_sample_clips':[int((raw[supported]<0).sum()),int((raw[supported]>1).sum())],'clear_exact':True,'fixed_crops':local(st,C),'baseline_crops':local(st,d['old']['complete']),'conditional_scene':True,'tail_unassigned':True};result['records'].append(row);save(f'{k}-metrics.json',row)
  def display(a):
   finite=np.isfinite(a).all(2);yy,xx=np.indices(finite.shape);return np.where(finite[...,None],a,np.where(((xx//6+yy//6)%2)[...,None],.72,.9))
  canvas=Image.new('RGB',(1444,534),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=17)
  for j,(image,label) in enumerate([(st.target_crop,'Apple reference'),(d['old']['complete'],'Selected Search'),(C,'Shared family transfer, light 4')]):
   img=Image.fromarray(np.uint8(np.rint(np.clip(display(image),0,1)*255)));canvas.paste(img.resize((480,470),Image.Resampling.NEAREST),(482*j,64));draw.text((482*j+8,20),label,font=font,fill='black')
  canvas.save(O/f'{k}-comparison.png');print('OBSERVATION',k,complete['E'],guards,flush=True)
 result['status']='ONE_UNFITTED_SHARED_FAMILY_PAIR_COMPLETE_PENDING_PRIMARY';result['selected_state_changed']=False
except Exception as exc:result['status']='STOPPED_FIRST_INVARIANT';result['failure']=repr(exc)
finally:
 result['finished']=now();(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(O/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FINAL',result['status'],result.get('failure'),ledger,flush=True)
