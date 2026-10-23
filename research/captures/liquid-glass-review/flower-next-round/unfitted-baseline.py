"""ONE unfitted tau1 baseline. Existing selected PLAYBACK settled.render(samples=2).
Sourceproof first; no newmap, coefficientfit or legacyiconcolorgrader.
"""
import os,sys,json,copy,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
R=Path('/evidence/extended/helper-toolbar-work/flower-next-round');D=R/'neutral-playback-baseline';os.umask(0o002);cv2.setNumThreads(1);sys.path.insert(0,str(D/'code'))
from extended_fit import Study
from settled import mapping,render
from vector_revision import composite
from source_support import masks,confidence_at
assert not (D/'baseline-native.json').exists(),'Preserve ONE completed baseline'
s=Study(D/'inputs/a');seed=json.loads((D/'selected-playback-pass03.json').read_text());p=copy.deepcopy(seed['recipe']);oldmaterial=p['material'];oldicon=p.pop('icon',None);tau=1.;co=np.zeros(23);co[:3]=tau;co[3:6]=1-tau;co[-3:]=tau;p['material']=co.tolist();assert p['shape']=={'half':[1,1],'radius':1};assert s.half.tolist()==[1.,1.] and s.radius==1.
canon=np.load(R/'sky-only-correction/canonical-public-protocol-masks-PROPOSED-v2.npz');assert np.array_equal(s.valid,canon['glass']) and np.array_equal(s.rim,canon['rim']) and np.array_equal(s.held,canon['held']);np.seterr(invalid='raise')
def kernel(sigma):
 if not sigma:return dict(sigma=0.,radius=0,weights=[1.])
 a=np.zeros((257,257),np.float32);a[128,128]=1.;b=cv2.GaussianBlur(a,(0,0),sigma);ys,xs=np.where(b!=0);radius=int(max(abs(xs-128).max(),abs(ys-128).max()));return dict(sigma=float(sigma),radius=radius,centerline_nonzero=b[128,128-radius:129+radius].tolist(),dtype='float32matchesRGBnativefield',operator='ActualOpenCV GaussianBlur ksize0/default border; nonzero finiteimpulse support, notinfiniteGaussian theorem')
ks=kernel(p['source_sigma']*s.L);kp=kernel(p['post_sigma']*s.L);defined,observed=masks(s);safe=cv2.erode(defined,np.ones((2*ks['radius']+1,2*ks['radius']+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0) if ks['radius'] else defined
alpha=s.shape_coverage(p);post=cv2.dilate(((alpha>0)|s.valid).astype(np.uint8),np.ones((2*kp['radius']+1,2*kp['radius']+1),np.uint8))>0;counts={n:0 for n in ['whole','scored','postfootprint','scored_outside_outline','whole_bad','scored_bad','postfootprint_bad']};minimum={n:1. for n in ['whole','scored','postfootprint']};bounds=[1e9,1e9,-1e9,-1e9]
for row,bottom,W,x,y in s.raster_tiles():
 # EXACTselectedmap, includingunchangedradial-tail mappingOUTSIDEshape; no identityclamp/borderextension.
 X,Y=mapping(x,y,p);rx=(X*s.L+s.case['center'][0]).astype(np.float32);ry=(Y*s.L+s.case['center'][1]).astype(np.float32);whole=s.shape(x,y,p)[-1][0]<=0;scored=np.repeat(np.repeat(s.valid[row:bottom],2,0),2,1);pm=np.repeat(np.repeat(post[row:bottom],2,0),2,1);q=confidence_at(safe,rx,ry);counts['scored_outside_outline']+=int((scored&~whole).sum())
 for name,mask in [('whole',whole),('scored',scored),('postfootprint',pm)]:counts[name]+=int(mask.sum());counts[name+'_bad']+=int((q[mask]<1-1e-7).sum());minimum[name]=min(minimum[name],float(q[mask].min()) if mask.any() else 1.)
 m=whole|scored|pm
 if m.any():bounds=[min(bounds[0],float(rx[m].min())),min(bounds[1],float(ry[m].min())),max(bounds[2],float(rx[m].max())),max(bounds[3],float(ry[m].max()))]
proof=dict(counts=counts,minimum_defined_confidence=minimum,source_bounds=bounds,source_kernel=ks,post_kernel=kp,observed_confidence=0.,passed=all(counts[n+'_bad']==0 for n in ['whole','scored','postfootprint']),limits='Actualnative2x2 WHOLE+ALLscored(notintersection)+all postkernelneighbor subrays, actualfiniteGaussian/bilinear lookup. Modeledsource definition only, hiddenobserved0; notcontinuous/infinitekernel/photographicopticsproof. Outside-map and source-border semantics preservedexact.')
(D/'source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');assert proof['passed'],'Sourcegate failed, do NOTrender baseline'
M=render(s.source,s.case,p,samples=2);C=composite(s,p,M);scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']));x0,y0,x1,y1=s.crop;yy,xx=np.mgrid[y0:y1,x0:x1];a,b,c,d=s.case['foreground'][0];fg=(xx>=a)&(xx<c)&(yy>=b)&(yy<d);ext=(s.sd>0)&(s.sd<=.35);full=s.sd>0
for n,m in [('glyph',fg),('exterior',ext),('full_visible_exterior',full)]:scores[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
np.savez_compressed(D/'baseline-native-arrays.npz',material=M,complete=C,alpha=alpha,glass_mask=s.valid,rim_mask=s.rim,held_mask=s.held,interior_mask=s.valid&~s.rim,glyph_mask=fg,exterior_mask=ext,full_visible_exterior_mask=full)
rec=dict(preset=p,tau=tau,material_contract='C=tau*S+(1-tau)*white, allRGBtied, 14lightingterms0; arrayrepresentation isnot23freeparameters/noMusiclegacycoeffs',seed_recipe_sha256=hashlib.sha256((D/'selected-playback-pass03.json').read_bytes()).hexdigest(),selected_model='playbackpublicpass03/radial-tail',samples=2,source_dtype=str(s.source.dtype),material_dtype=str(M.dtype),kernel_scaling='Dimensionlesssource_sigma/post_sigma unchanged; physicalpixels useNEWL113.698 vs reference245 viaexactsettled.render. Noquarterpixelbins/overridessampling.',old_reference_L=245,physical_length_ratio=s.L/245,legacy_icon_colorgrader_removed=oldicon is not None,legacy_material_not_reused=True,generated_shadow='NONE/zero baseline, clean source/vector_revision composite. No publish.compose/contact_context/targetresidual.',case_sha256={'a':hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()},vector_sha256={'a':{s.case['foreground_layers'][0]['vector_asset']:s.case['foreground_layers'][0]['vector_sha256']}},input_approval='121f45d5-f23c-4c7f-9071-03aa16e5cb45',stage='ONE_UNFITTED_BASELINE_BEFORE_TAU_CALIBRATION',accepted_passes=0,B_paired=False)
(D/'baseline-recipe.json').write_text(json.dumps(rec,indent=2)+'\n');result=dict(status='UNFITTED_TAU1_BASELINE_REVIEW_READY_NO_CALIBRATION',scores=scores,source_proof=proof,native_body_renders=1,material_fit_or_sweep_count=0,accepted_count=0,case_sha256=rec['case_sha256'],map='EXACTselectedsettled.mapping/render(samples2), unmodifiedinside/outside, normalizedcasepose only',source='Conditionalestimatedsky, observed0; refraction/dispersion/scattering NOTidentified/validated bylow-frequency input',canonical_white_vector='Pinnedoriginal-pathselectioncounts0, no screenshotmatte/icon_colorgrade',limits='No materialtaufit untilprimaryindependentnative/source/visualbaselinechecks. NativeEisbaselineonly, nogainclaim. Zero-shadowreferenceunderlay iscleanpresentationbaseline, nocopiedcontextremovalcredit. Pairedfuturestage.')
(D/'baseline-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
w=2*(x1-x0);h=2*(y1-y0);pair=Image.new('RGB',(2*w+2,h+64),'#222');dr=ImageDraw.Draw(pair);dr.text((8,20),'Original NEXT',fill='white');dr.text((w+12,20),'UNFITTEDneutral tau1 /fixedplaybackmap',fill='white')
for i,im in enumerate([s.target_crop,C]):pair.paste(Image.fromarray(np.uint8(np.rint(np.clip(im,0,1)*255))).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64))
pair.save(D/'baseline-comparison.png')
