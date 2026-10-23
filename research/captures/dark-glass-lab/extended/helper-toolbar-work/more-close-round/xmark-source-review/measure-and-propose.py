"""Original SF control + ONE clean symmetric X, input-only cached-body reeval."""
import os,json,copy,sys,hashlib,datetime,shutil
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');D=R/'xmark-source-review';B=R/'latest-circle-baseline';P=R/'foreground-gray-round1';st=json.loads((D/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(st['deadline_at'].replace('Z','+00:00'))
sys.path.insert(0,str(B/'code'));from extended_fit import Study;from vector_foreground import coverage;from vector_revision import composite
s=Study(B/'inputs/a');case=copy.deepcopy(s.case);layer=case['foreground_layers'][0];rec=json.loads((P/'candidate-native.json').read_text());arr=np.load(P/'candidate-native.npz');maskarr=np.load(B/'baseline-native-arrays.npz');M=arr['material'];incC=arr['complete'];p=rec['preset'];T=s.target;gray=T.mean(2)*255;l,t,r,b=layer['box'];x0,y0,x1,y1=s.crop;mx,my=(l+r-1)/2,(t+b-1)/2;C0=np.array([mx,my]);yy,xx=np.mgrid[:gray.shape[0],:gray.shape[1]];dx=xx-mx;dy=yy-my;rho=np.hypot(dx,dy)
# Geometry detection only: constant observed ink/background levels, NEVER
# inverted into a target alpha/matte; render color remains accepted q.1422.
obs_ink_level=json.loads((R/'cached-glyph-diagnostic/diagnostic.json').read_text())['ONE_q_native255'];bg_mask=(rho<=16)&(np.minimum(abs(dx-dy),abs(dx+dy))/np.sqrt(2)>=3.5);bg_level=float(np.median(gray[bg_mask]));level=(obs_ink_level+bg_level)/2
v1=np.array([1.,1.])/np.sqrt(2);v2=np.array([1.,-1.])/np.sqrt(2);arms=[('SE',v1,1,True),('NW',v1,-1,True),('NE',v2,1,True),('SW',v2,-1,False)]
def sample(points,image=gray):return cv2.remap(image.astype(np.float32),points[:,0].astype(np.float32)[None,:],points[:,1].astype(np.float32)[None,:],cv2.INTER_LINEAR)[0]
def interval(x,y,threshold,below=True):
 inside=y<threshold if below else y>=threshold;idx=np.flatnonzero(inside);assert len(idx);k=idx[np.argmin(abs(x[idx]))];a0=k;b0=k
 while a0>0 and inside[a0-1]:a0-=1
 while b0<len(x)-1 and inside[b0+1]:b0+=1
 assert a0>0 and b0<len(x)-1
 cross=lambda i,j:float(x[i]+(threshold-y[i])*(x[j]-x[i])/(y[j]-y[i]))
 return cross(a0-1,a0),cross(b0,b0+1)
profiles=[];offset=np.arange(-4,4.0001,.0625)
for name,v,sign,train in arms:
 n=np.array([-v[1],v[0]])
 for along in [4.,6.,8.]:
  points=C0+sign*along*v+offset[:,None]*n;values=sample(points);left,right=interval(offset,values,level);profiles.append(dict(arm=name,train=train,along=along,normal=n.tolist(),left=left,right=right,mid=(left+right)/2,halfwidth=(right-left)/2))
training=[q for q in profiles if q['train']];rstroke=float(np.median([q['halfwidth'] for q in training]));mid1=float(np.median([q['mid'] for q in training if q['arm'] in ['SE','NW']]));mid2=float(np.median([q['mid'] for q in training if q['arm']=='NE']));n1=np.array([-v1[1],v1[0]]);n2=np.array([-v2[1],v2[0]]);center=C0+mid1*n1+mid2*n2
ends=[];alonggrid=np.arange(5,15.0001,.0625)
for name,v,sign,train in arms:
 values=sample(center+sign*alonggrid[:,None]*v);inside=np.flatnonzero(values<level);assert len(inside);j=inside[-1];assert j<len(alonggrid)-1;tip=float(alonggrid[j]+(level-values[j])*(alonggrid[j+1]-alonggrid[j])/(values[j+1]-values[j]));ends.append(dict(arm=name,train=train,tip_distance=tip))
halfseg=float(np.median([q['tip_distance']-rstroke for q in ends if q['train']]));end_component=halfseg/np.sqrt(2);geometry_bounds=[center[0]-end_component-rstroke,center[1]-end_component-rstroke,center[0]+end_component+rstroke,center[1]+end_component+rstroke];canvas=[l-.5,t-.5,r-.5,b-.5];overflow=[max(canvas[0]-geometry_bounds[0],0),max(canvas[1]-geometry_bounds[1],0),max(geometry_bounds[2]-canvas[2],0),max(geometry_bounds[3]-canvas[3],0)]
held=[]
for q in profiles:
 if not q['train']:
  n=np.array(q['normal']);shift=float(n@(center-C0));held.append(dict(arm=q['arm'],along=q['along'],left_error=shift-rstroke-q['left'],right_error=shift+rstroke-q['right'],halfwidth_error=rstroke-q['halfwidth']))
held_tip=[halfseg+rstroke-q['tip_distance'] for q in ends if not q['train']]
# Standard exact vector primitives only, two identical round-cap segments.
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {b-t}">'
for v in [v1,v2]:
 a0=center-halfseg*v-np.array(canvas[:2]);a1=center+halfseg*v-np.array(canvas[:2]);svg+=f'<line x1="{a0[0]:.12g}" y1="{a0[1]:.12g}" x2="{a1[0]:.12g}" y2="{a1[1]:.12g}" stroke="#000" stroke-width="{2*rstroke:.12g}" stroke-linecap="round"/>'
svg+='</svg>\n';(D/'xmark-clean-approx.svg').write_text(svg)
# One original Semibold-font control; fixed uniform placement, no weight sweep.
original_info=json.loads((D/'original-one-control.json').read_text());ol,ob,orr,ot=original_info['bounds'];ow=orr-ol;oh=ot-ob;scale=min((r-l)/ow,(b-t)/oh);original_place=[mx-ow*scale/2,my-oh*scale/2,mx+ow*scale/2,my+oh*scale/2]
controls=[('original-w600','xmark-original-w600.svg',original_place),('clean-approx','xmark-clean-approx.svg',canvas)];variants=[];old_valid=s.valid.copy();oldrim=s.rim.copy();oldheld=s.held.copy();oldsafe=cv2.erode(old_valid.astype(np.uint8),np.ones((11,11),np.uint8))>0
for name,asset,place in controls:
 Ainput=D/f'a-{name}';Ainput.mkdir();newcase=copy.deepcopy(case);newlayer={**layer,'vector_asset':asset,'vector_sha256':hashlib.sha256((D/asset).read_bytes()).hexdigest(),'vector_box':place,'style_key':layer['vector_asset']};newcase['foreground_layers']=[newlayer];newcase['foreground_provenance_proposal']=dict(stage='INPUT_ONLY_UNADOPTED_COUNT0',old_asset=layer['vector_asset'],old_sha256=layer['vector_sha256'],source_variant=name,exact_Apple_UI_weight=False,no_color_or_opacity_change=True,source_and_body_frozen=True)
 for n in case['source_sha256']:shutil.copyfile(B/'inputs/a'/n,Ainput/n)
 shutil.copyfile(D/asset,Ainput/asset);(Ainput/'case.json').write_text(json.dumps(newcase,indent=2)+'\n');ss=Study(Ainput);assert np.array_equal(ss.valid,old_valid) and np.array_equal(ss.rim,oldrim) and np.array_equal(ss.held,oldheld);assert np.array_equal(cv2.erode(ss.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0,oldsafe);A=coverage(Ainput,newlayer);old_case=ss.case
 try:ss.case={**old_case,'foreground_styles':rec['foreground_styles']};C=composite(ss,p,M)
 finally:ss.case=old_case
 assert np.array_equal(C[~maskarr['glyph_mask']],incC[~maskarr['glyph_mask']]);q=ss.scores(M);q['E']=float(np.sqrt(q['loss']));fg=maskarr['glyph_mask'];q['glyph']=dict(pixels=int(fg.sum()),rmse=float(np.sqrt(np.mean(((C-ss.target_crop)[fg]*255)**2))))
 # Held-arm halfcoverage geometry check, same sampling as observed profiles.
 held_model=[]
 for pr in profiles:
  if not pr['train']:
   namearm,v,sign,train=next(z for z in arms if z[0]==pr['arm']);n=np.array(pr['normal']);pts=C0+sign*pr['along']*v+offset[:,None]*n;localpts=pts-np.array([l,t]);av=sample(localpts,image=A);left,right=interval(offset,av,.5,below=False);held_model.append(dict(along=pr['along'],left_error=left-pr['left'],right_error=right-pr['right']))
 np.savez_compressed(Ainput/'CACHEDM-reevaluation-NOT-ADOPTED.npz',material=M,complete=C,alpha=arr['alpha']);info=dict(name=name,asset=asset,vector_sha256=newlayer['vector_sha256'],placement=place,box_unchanged=newlayer['box']==layer['box'],all_native_glass_rim_held_SSIM_masks_exact=True,source_png_hashes_unchanged=True,case_fingerprint=hashlib.sha256(json.dumps(newcase,sort_keys=True).encode()).hexdigest(),original_case_fingerprint=rec['case_sha256']['a'],accepted_foreground_gray_fixed=rec['foreground_gray'],opacity_fixed=1,body_material_bit_exact=True,outside_foreground_C_bit_exact=True,baseline_body_E=q['E'],foreground_RMSE_before=rec['scores']['glyph']['rmse'],foreground_RMSE_source_proposal=q['glyph']['rmse'],held_arm_halfcoverage_errors=held_model,not_cross_epoch_gain=True,count=0,limits='Inputproposalonly, notexactAppleUIweight; allcolour/opacity/body/source heldfixed. No adoption/newopticalfit orverifiedpass.')
 variants.append(info);(Ainput/'review.json').write_text(json.dumps(info,indent=2)+'\n')
 # Reusable source-evidence preview, NOT accepted reconstruction.
 width=2*(x1-x0);height=2*(y1-y0);im=Image.new('RGB',(2*width+2,height+64),'#222');draw=ImageDraw.Draw(im);draw.text((3,20),'Apple CLOSE',fill='white');draw.text((width+5,20),name,fill='white')
 for i,rgb in enumerate([ss.target_crop,C]):im.paste(Image.fromarray(np.uint8(np.rint(np.clip(rgb,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS),(i*(width+2),64))
 im.save(Ainput/'source-proposal-comparison.png')
result=dict(stage='SOURCE_ONLY_ORIGINAL_ONE_CONTROL_PLUS_ONE_CLEAN_FALLBACK_UNADOPTED',geometry_measurement=dict(observed_ink_level_native255=obs_ink_level,observed_background_level_native255=bg_level,halfcontrast_level_for_edge_measurement_ONLY=level,render_tint_unchanged=rec['foreground_gray'],center=center.tolist(),stroke_width_native=2*rstroke,segment_half_length_native=halfseg,endpoint_component=end_component,source_geometry_bounds=geometry_bounds,original_canvas_edges=canvas,canvas_overflow_pixels=overflow,training_arms=['SE','NW','NE'],held_arm='SW',profiles=profiles,endpoint_evidence=ends,held_training_geometry_errors=held,held_endpoint_error=held_tip,approximate_not_exact_Apple=True,no_blur_dilation_or_target_alpha=True),original_control=original_info,variants=variants,body_renders=0,foreground_cached_source_reevaluations=2,optical_fits=0,source_adopted=False,cross_epoch_gains=0,accepted_count_unchanged=1,elapsed_seconds=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(st['started_at'].replace('Z','+00:00'))).total_seconds(),limits='Sourceglyphvariantproposal only. Native18px glyph cannot uniquely identifyweight/AA/codec. ONEfontw600control andONEcleanX only; no sweep, no tunedfill/opacity/background or SGbodyrender. Fixedglassmask confirmed; overflowifany must be considered beforeadoption.')
(D/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
