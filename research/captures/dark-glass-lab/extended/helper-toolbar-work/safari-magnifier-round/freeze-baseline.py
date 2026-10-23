import os,sys,json,hashlib,copy,shutil
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');sys.path.insert(0,str(R/'code'));os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (R/'baseline-native.json').exists(),'Completed native baseline cannot repeat'
T=np.asarray(Image.open(R/'frame-300/target.png').convert('RGB'));yy,xx=np.mgrid[:1080,:1920];r=np.hypot(xx-509,yy-705);X=np.stack([np.ones_like(xx),(xx-509)/100,(yy-705)/100],-1)
# ONE visible-boundary mask correction: upper and right uncovered sectors avoid the observed parent panel corner. Old controls/errors retained in source-pose.json.
upper=(xx>=430)&(xx<=690)&(yy>=530)&(yy<=595)
right=(xx>=625)&(xx<=710)&(yy>=610)&(yy<=805)
controls=(upper|right)&(r>=110);held=((xx//16+3*(yy//16))%4)==0;train=controls&~held
co=np.linalg.lstsq(X[train],T[train]/255,rcond=None)[0];field=X@co
checks=[]
for name,m in [('held_upper_right',controls&held),('independent_left_uncovered',(xx>=420)&(xx<=430)&(yy>=640)&(yy<=730)),('independent_lower_uncovered',(xx>=510)&(xx<=585)&(yy>=815)&(yy<=825))]:
 e=(field-T/255)[m]*255;checks.append(dict(name=name,pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(e**2))),signed_rgb=e.mean(0).tolist(),p95_absolute=float(np.percentile(abs(e),95))))
# Independent absolute-gradient silhouette landmark; not a fit of the rendered glass or source beneath it.
a=np.linspace(0,2*np.pi,720,endpoint=False);rr=np.arange(67,79,.125);px=(509+np.cos(a)[:,None]*rr).astype(np.float32);py=(705+np.sin(a)[:,None]*rr).astype(np.float32);g=T.mean(2).astype(np.float32);v=cv2.remap(g,px,py,cv2.INTER_LINEAR);dv=abs(np.gradient(v,.125,axis=1));ridge=rr[dv.argmax(1)];pts=np.c_[509+np.cos(a)*ridge,705+np.sin(a)*ridge];pose=least_squares(lambda q:np.linalg.norm(pts-q[:2],axis=1)-q[2],[509,705,72],loss='soft_l1',f_scale=.5).x
# Rounded pose is frozen input construction, never credited as optical improvement.
cx,cy,rad=[round(float(q),3) for q in pose];folder=R/'a';folder.mkdir();shutil.copyfile(R/'frame-300/target.png',folder/'target.png');shutil.copyfile('/evidence/extended/music-search-vector/paired/a/search.svg',folder/'search.svg')
domain=(xx>=400)&(xx<=740)&(yy>=490)&(yy<=840);source=np.where(domain[...,None],np.clip(field,0,1),0);Image.fromarray(np.uint8(np.rint(source*255))).save(folder/'source.png');Image.fromarray(np.uint8(domain)*255).save(folder/'known.png');observed=np.zeros(domain.shape,np.uint8);Image.fromarray(observed).save(folder/'observed.png');targetvisible=np.ones(domain.shape,np.uint8)*255;Image.fromarray(targetvisible).save(folder/'target-visible.png')
# Seed unidentifiable map/kernel and material from accepted MusicSearch public pass03. Only pose-specific pixel widths scale, as its recipe declares.
seed=json.loads((R/'music-search-seed.json').read_text());p=copy.deepcopy(seed['parameters']);p['sigma']*=rad/89;p['post_sigma']*=rad/89
for k in ['shape_dx','shape_dy','half_x_delta','half_y_delta','radius_delta']:p[k]=0.
box=[470,667,548,746];placement=[475.5,672.5,541.5,738.5] # square placement from dark native bounds476..541,673..739; no coverage inversion.
case=dict(id='safari-isolated-search-single-a',category='Safari isolated magnifier SINGLE A',radial=True,center=[cx,cy],half=[rad,rad],radius=rad,crop=[405,595,620,815],foreground=[box],foreground_layers=[dict(mode='mask',box=box,color=[0,0,0],threshold=.33,vector_asset='search.svg',vector_box=placement,vector_sha256=sha(folder/'search.svg'),opacity=1.)],reference=dict(video='219',seconds=300,original_file='apple-matches/219-hd.mp4',video_sha256='3d58f9e843f0b8c22e99d76de6b5201ef5b17de5bb4bf5732862ba7dbf9be60e'),source_observation_mask='observed.png',target_observation_mask='target-visible.png',allow_estimated_background=True,background_estimate=dict(kind='Separate frozen affine RGB plane from uncovered upper/right controls ONLY',basis=['1','(x-509)/100','(y-705)/100'],coefficient_rgb=co.tolist(),source_defined_domain=[400,490,741,841],direct_observed_fraction=0.,controls=checks,uncertainty='Held residuals constrain uncovered field, not hidden truth. Left/bottom extrapolation and parent lighting/shadow remain confounded. No photographic recovery or refraction/blur identification.'),foreground_provenance=dict(kind='Reused canonical MusicSearch symmetric circular-ring/45degree rounded-capsule solid SVG',original_apple_svg=False,geometry_sha256=sha(folder/'search.svg'),placement='Native exposed dark bbox476,673,541,739; square66px placement475.5,672.5,541.5,738.5. No target alpha.',color='Black opacity1 seed; exposed ink medianRGB0,0,2. Codec residual not vector geometry.'),exterior_reference_shape={k:0 for k in ['shape_dx','shape_dy','half_x_delta','half_y_delta','radius_delta','cap_join_width']})
case['source_sha256']={n:sha(folder/n) for n in ['source.png','target.png','known.png','observed.png','target-visible.png']};(folder/'case.json').write_text(json.dumps(case,indent=2)+'\n')
record=dict(parameters=p,material=seed['material'],stage='SINGLE_A_FROZEN_BASELINE_PROPOSAL_NOT_ACCEPTED',seed='Committed public MusicSearch pass03; shape offsets zeroed to independently measured Safari pose. Source-width kernels scaled by L/89 as declared.',source_adopted=False,baseline_not_optical_gain=True,case_sha256={'a':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()},vector_sha256={'a':{'search.svg':sha(folder/'search.svg')}},large=False)
save('baseline-recipe.json',record)
np.savez_compressed(R/'source-final-controls.npz',train=train,held=controls&held,defined=domain,field_rgb=np.where(domain[...,None],field,np.nan).astype(np.float32))
from extended_fit import Study
from vector_revision import composite
from source_support import coverage_report,masks,kernel_safe,confidence_at
s=Study(folder);M=s.render(p,np.asarray(record['material']));C=composite(s,p,M);alpha=s.shape_coverage(p);scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']));x0,y0,x1,y1=s.crop;YC,XC=np.mgrid[y0:y1,x0:x1];ext=(s.sd>0)&(s.sd<=.35);fg=(XC>=box[0])&(XC<box[2])&(YC>=box[1])&(YC<box[3]);full=s.sd>0
for key,mask in [('glyph',fg),('exterior',ext),('full_visible_exterior',full)]:scores[key]=dict(pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2))))
np.savez_compressed(R/'baseline-native-arrays.npz',material=M,complete=C,alpha=alpha,glass_mask=s.valid,rim_mask=s.rim,glyph_mask=fg,exterior_mask=ext,held_mask=s.held)
# Actual native2x2 emission support: WHOLE corrected shape plus ALLscored, including any scored rays outside outline. Finite Gaussian3sigma+bilinear confidence, never infinite-support/physical proof.
defd,obs=masks(s);safe,k=kernel_safe(defd,s,p);osafe,_=kernel_safe(obs,s,p);counts={q:0 for q in ['whole','scored','scored_outside_outline','whole_bad','scored_bad']};minimum={'whole_defined':1.,'scored_defined':1.,'whole_observed':1.,'scored_observed':1.};bounds=[1e9,1e9,-1e9,-1e9]
for row,bottom,W,x,y in s.raster_tiles():
 Xr,Yr,d,J=s.geometry_field(x,y,p);RX=(Xr*s.L+cx).astype(np.float32);RY=(Yr*s.L+cy).astype(np.float32);whole=s.shape(x,y,p)[-1][0]<=0;scored=np.repeat(np.repeat(s.valid[row:bottom],2,axis=0),2,axis=1);counts['scored_outside_outline']+=int((scored&~whole).sum());dc=confidence_at(safe,RX,RY);oc=confidence_at(osafe,RX,RY)
 for key,mask in [('whole',whole),('scored',scored)]:
  counts[key]+=int(mask.sum());counts[key+'_bad']+=int((dc[mask]<.999999).sum());minimum[key+'_defined']=min(minimum[key+'_defined'],float(dc[mask].min()) if mask.any() else 1.);minimum[key+'_observed']=min(minimum[key+'_observed'],float(oc[mask].min()) if mask.any() else 1.)
 mask=whole|scored
 if mask.any():bounds=[min(bounds[0],float(RX[mask].min())),min(bounds[1],float(RY[mask].min())),max(bounds[2],float(RX[mask].max())),max(bounds[3],float(RY[mask].max()))]
proof=dict(counts=counts,minimum_confidence=minimum,ray_bounds=bounds,gaussian_3sigma_native_radius=k,passed=counts['whole_bad']==counts['scored_bad']==0,limits='Fixed native2x2 whole+ALLscored, finite3sigma confidence. Estimated-source model definedness, observed0 everywhere. Not photographic source recovery/continuous/infiniteGaussian/optical validation.')
# Native render ONLY; preview is exact same arrays resized430 per side (rule min2W,maxW720).
A=np.uint8(np.rint(np.clip(s.target_crop,0,1)*255));B=np.uint8(np.rint(np.clip(C,0,1)*255));Image.fromarray(A).save(R/'a-target-native.png');Image.fromarray(B).save(R/'a-baseline-native.png');w=430;h=440;pair=Image.new('RGB',(2*w+2,h+64),'#222');dr=ImageDraw.Draw(pair);dr.text((8,14),'Safari219300 native A',fill='white');dr.text((w+10,14),'Unfitted seed / estimated source',fill='white');pair.paste(Image.fromarray(A).resize((w,h),Image.Resampling.LANCZOS),(0,64));pair.paste(Image.fromarray(B).resize((w,h),Image.Resampling.LANCZOS),(w+2,64));pair.save(R/'a-baseline-comparison.png')
result=dict(stage='SINGLE_A_BASELINE_READY_FOR_REVIEW_BEFORE_FIT',scores=scores,source_controls=checks,source_proof=proof,center_source_proof=coverage_report(s,p),pose=dict(center=[cx,cy],radius=rad,ridge_quantiles=np.percentile(ridge,[10,50,90]).tolist(),landmark_uncertainty='Image bright/dark gradient edges, not alpha groundtruth; no later pose fit authorized'),source_adopted=False,fit_count=0,accepted_count=0,B='PENDING;290nearidenticalgraybackground and changedradius, no pairedvalidation',proposal='First short identifiable shared-tone/material-only neighborhood after primary review; freeze map/geometry/source blur/output blur/gamma/SVG. No refraction/dispersion identification from smooth input. Original E/glass/rim/held/interior/SSIM/glyph/exterior guards frozen against this baseline.')
save('baseline-native.json',result);print(json.dumps(result),flush=True)
