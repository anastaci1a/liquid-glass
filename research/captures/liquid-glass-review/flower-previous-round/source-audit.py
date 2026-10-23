"""ONE bounded donor-registration batch; canonical font path, no optical fit."""
import os,json,hashlib,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
R=Path('/evidence/extended/helper-toolbar-work/flower-previous-round');os.umask(0o002);cv2.setNumThreads(1)
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'source-audit.json').exists(),'Do not repeat completed donor batch';start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'))
T=np.asarray(Image.open(R/'frames/170.png').convert('RGB'));H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];g=T.mean(2);centers={'previous':(605,552,114),'pause':(960,552,160),'next':(1318,552,114)};disk=np.hypot(xx-605,yy-552)<=114;exposed=np.ones((H,W),bool)
for cx,cy,rad in centers.values():exposed&=np.hypot(xx-cx,yy-cy)>(rad+48)
feature_mask=exposed&(xx>=350)&(xx<=1800)&(yy>=160)&(yy<=1000);sift=cv2.SIFT_create(nfeatures=6000,contrastThreshold=.015);kt,dt=sift.detectAndCompute(cv2.cvtColor(T,cv2.COLOR_RGB2GRAY),np.uint8(feature_mask)*255);held=((xx//32+3*(yy//32))%4)==0;observed=exposed.copy();mosaic=T.astype(float)/255;rows=[]
for donor in [164,165,166,169,172,174]:
 S=np.asarray(Image.open(R/f'frames/{donor}.png').convert('RGB'));valid=np.ones((H,W),bool)
 if donor<=166:valid&=~((xx>=420)&(xx<=1490)&(yy>=330)&(yy<=820));style='closerphoto+pillongshadow conservativeexcludedrect420,330..1490,820'
 else:
  for cx,cy,rad in centers.values():valid&=np.hypot(xx-cx,yy-cy)>(rad+48)
  style='same3circlecontrol+48pxshadowneighborhood excluded'
 ks,ds=sift.detectAndCompute(cv2.cvtColor(S,cv2.COLOR_RGB2GRAY),np.uint8(valid)*255)
 if ds is None or dt is None:rows.append(dict(donor=donor,accepted_registration=False,reason='No independent exposed-photo descriptors'));continue
 pairs=[m for m,n in cv2.BFMatcher().knnMatch(ds,dt,k=2) if m.distance<.7*n.distance];row=dict(donor=donor,matches=len(pairs),donor_exclusion=style)
 if len(pairs)<12:row.update(accepted_registration=False,reason='Too few exposed-photo correspondences; no invented transform/support');rows.append(row);save('donor-progress.json',rows);print(json.dumps(row),flush=True);continue
 aa=np.array([ks[m.queryIdx].pt for m in pairs],np.float32);bb=np.array([kt[m.trainIdx].pt for m in pairs],np.float32);h=((np.floor(bb[:,0]/32)+3*np.floor(bb[:,1]/32))%4)==0
 if (~h).sum()<8 or h.sum()<4:row.update(accepted_registration=False,reason='Insufficient independent train/held correspondences',held_matches=int(h.sum()));rows.append(row);save('donor-progress.json',rows);print(json.dumps(row),flush=True);continue
 M,inliers=cv2.estimateAffinePartial2D(aa[~h],bb[~h],method=cv2.RANSAC,ransacReprojThreshold=1.25,maxIters=5000)
 if M is None:row.update(accepted_registration=False,reason='Similarity registration failed');rows.append(row);save('donor-progress.json',rows);print(json.dumps(row),flush=True);continue
 dist=np.linalg.norm(aa@M[:,:2].T+M[:,2]-bb,axis=1);good=bool(inliers.sum()>=8 and np.median(dist[h])<1.5);support=cv2.warpAffine(cv2.erode(valid.astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32),M,(W,H),flags=cv2.INTER_LINEAR)>=.999999;warped=cv2.warpAffine(S.astype(float)/255,M,(W,H),flags=cv2.INTER_LINEAR);test=support&exposed&held;err=(warped-T/255)[test]*255;potential=int((support&disk).sum());row.update(similarity=M.tolist(),train_ransac_inliers=int(inliers.sum()),held_matches=int(h.sum()),held_median_geometry_px=float(np.median(dist[h])),held_p90_geometry_px=float(np.percentile(dist[h],90)),held_RGB_RMSE=float(np.sqrt(np.mean(err**2))),held_RGB_signed=err.mean(0).tolist(),held_pixels=int(test.sum()),previous_disk_potential_pixels=potential,accepted_registration=good,limits='Independent exposed controls, not glyph/glass/targetresidual fit. Pixel coverage is IMAGEPLANE potential only; no emitted-ray/model proof. Photometric/zoom/PSF differences still require source review.')
 np.savez_compressed(R/f'donor-{donor}-registered.npz',valid=support,RGB=np.where(support[...,None],warped,np.nan).astype(np.float32),matrix=M)
 if good:
  take=support&~observed;mosaic[take]=warped[take];observed|=support
 rows.append(row);save('donor-progress.json',rows);print(json.dumps(row),flush=True)
# Source remains NaN where donors do not independently cover hidden texture; never target-disk fill/inpaint.
np.savez_compressed(R/'observed-source-UNADOPTED.npz',source=np.where(observed[...,None],mosaic,np.nan).astype(np.float32),observed=observed,previous_disk=disk,target_exposed=exposed)
# Glyph ONE known original font candidate, no variant/weight/pose fit or raster matte.
fontp=Path('/evidence/extended/icon-source/fallback/Applications/SF Symbols.app/Contents/Resources/Fonts/SFSymbolsFallback.otf');font=TTFont(fontp);gs=font.getGlyphSet();glyph='backward.end.tag.fill.color.large';pen=SVGPathPen(gs);gs[glyph].draw(pen);bp=BoundsPen(gs);gs[glyph].draw(bp);l,b,r,t=bp.bounds;svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {t-b}"><path fill="#fff" transform="translate({-l} {t}) scale(1 -1)" d="{pen.getCommands()}"/></svg>\n';(R/'backward.end.fill-original.svg').write_text(svg);font.close()
# Independently exposed glyph bbox only; no screenshot alpha. The entire declaredcandidate remains unscored/unadopted until pose/source freeze review.
white=(xx>=530)&(xx<=680)&(yy>=490)&(yy<=620)&(T.min(2)>225)&((T.max(2).astype(int)-T.min(2).astype(int))<20);gy,gx=np.where(white);glyphbox=[int(gx.min()),int(gy.min()),int(gx.max()+1),int(gy.max()+1)]
angles=np.linspace(0,2*np.pi,720,endpoint=False);rr=np.arange(106,123,.125);px=(605+np.cos(angles)[:,None]*rr).astype(np.float32);py=(552+np.sin(angles)[:,None]*rr).astype(np.float32);v=cv2.remap(g.astype(np.float32),px,py,cv2.INTER_LINEAR);ridge=rr[abs(np.gradient(v,.125,axis=1)).argmax(1)];points=np.c_[605+np.cos(angles)*ridge,552+np.sin(angles)*ridge];pose=least_squares(lambda q:np.linalg.norm(points-q[:2],axis=1)-q[2],[605,552,114],loss='soft_l1',f_scale=.5).x
covered=int((observed&disk).sum());total=int(disk.sum());result=dict(status='SOURCE_PROPOSAL_REVIEW_ONLY' if covered==total else 'INCOMPLETE_TRUE_TEXTURE_SOURCE_NO_FIT',target_seconds=170,donor_batch=rows,previous_disk=dict(center_nominal=[605,552],radius_nominal=114,pixels=total,observed_potential_pixels=covered,missing_pixels=total-covered,observed_fraction=covered/total,not_ray_proof=True),pose=dict(center=pose[:2].tolist(),gradient_landmark_radius=float(pose[2]),ridge_p10_p50_p90=np.percentile(ridge,[10,50,90]).tolist(),residual_p95=float(np.percentile(abs(np.linalg.norm(points-pose[:2],axis=1)-pose[2]),95)),limits='Photographicedges/refraction canconfound strongestgradient. Image landmark only, notknown alpha; no opticalpose fit.'),canonical_vector=dict(file='backward.end.fill-original.svg',sha256=sha(R/'backward.end.fill-original.svg'),font=str(fontp),font_sha256=sha(fontp),glyph=glyph,default_weight=400,ink_bounds=list(bp.bounds),exposed_white_bbox=glyphbox,original_font_path=True,exact_target_weight=False,no_screenshot_matte=True),source_truth='Directmaskedtemporalphoto donors ONLY; missingpixels NaN, no petals/words invented, no targetshadowcopy. Registrationquality and PSFdifferenceexplicit; sourceunadopted.',optical_fits=0,passes=0,baseline_rendered=False,seed_limit='Existingclearplay source/model NOTassumed applicable: previousfloweredge visiblyinverts highcontrastpetals, unlikegray/weaktexture. Needtrue source+pose/protocolfreeze beforeanymap/materialproposal. Dispersionvsordinaryblur notidentifiedfromsource mismatch.',paired_stage=False,next='Primaryreview sourcecoverage/provenance before anyfit; ifblocked propose rightNEXTcircle sameframeblueSky asfutureSINGLEinput fromuncoveredcontrols, notactivepair/automaticfit.')
save('source-audit.json',result);print('COMPLETE',json.dumps({k:result[k] for k in ['status','previous_disk','pose','canonical_vector']}),flush=True)
preview=np.where(observed[...,None],mosaic,np.array([1.,0.,1.]));Image.fromarray(np.uint8(np.rint(np.clip(preview,0,1)*255))).crop((420,370,790,740)).save(R/'source-coverage-preview-MAGENTA_UNKNOWN.png')
