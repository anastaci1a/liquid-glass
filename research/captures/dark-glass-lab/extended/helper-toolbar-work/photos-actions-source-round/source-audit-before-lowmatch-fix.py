"""One donor batch +one uncovered-paper field proposal, no optical fit/photo invention."""
import os,json,hashlib,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
R=Path('/evidence/extended/helper-toolbar-work/photos-actions-source-round');os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
if (R/'source-audit.json').exists():raise RuntimeError('Complete audit exists, no repeat')
start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'))
T=np.asarray(Image.open(R/'frames/310.0.png').convert('RGB'));yy,xx=np.mgrid[:1080,:1920];centers={'person':[663,644],'bulb':[1225,646]};disks={n:np.hypot(xx-c[0],yy-c[1])<46 for n,c in centers.items()};exclude=np.zeros(xx.shape,bool)
for c in centers.values():exclude|=np.hypot(xx-c[0],yy-c[1])<70
region=(xx>595)&(xx<1305)&(yy>20)&(yy<725);exposed=region&~exclude;sift=cv2.SIFT_create(nfeatures=5000);G=cv2.cvtColor(T,cv2.COLOR_RGB2GRAY);feature_mask=(xx>600)&(xx<1290)&(yy>30)&(yy<580)&~exclude;kt,dt=sift.detectAndCompute(G,np.uint8(feature_mask)*255);rows=[];union=np.zeros(xx.shape,bool);held=((xx//32+3*(yy//32))%4)==0
for donor in [307.0,309.5,311.5]:
 S=np.asarray(Image.open(R/f'frames/{donor:05.1f}.png').convert('RGB'));ks,ds=sift.detectAndCompute(cv2.cvtColor(S,cv2.COLOR_RGB2GRAY),np.uint8(feature_mask)*255);pairs=[m for m,n in cv2.BFMatcher().knnMatch(ds,dt,k=2) if m.distance<.7*n.distance];a=np.array([ks[m.queryIdx].pt for m in pairs],np.float32);b=np.array([kt[m.trainIdx].pt for m in pairs],np.float32);h=((np.floor(b[:,0]/32)+3*np.floor(b[:,1]/32))%4)==0;M,inliers=cv2.estimateAffinePartial2D(a[~h],b[~h],method=cv2.RANSAC,ransacReprojThreshold=1.25,maxIters=5000);dist=np.linalg.norm(a@M[:,:2].T+M[:,2]-b,axis=1);support=exposed.copy()
 if donor==311.5:support&=~((xx<920)&(yy>470)) # visible expanded left menu, not a clean donor
 support=cv2.erode(np.uint8(support),np.ones((5,5),np.uint8));v=cv2.warpAffine(support.astype(float),M,(1920,1080),flags=cv2.INTER_LINEAR)>=.999999;warped=cv2.warpAffine(S.astype(float)/255,M,(1920,1080),flags=cv2.INTER_LINEAR);m=v&exposed&held;err=(warped-T/255)[m]*255;union|=v
 row=dict(donor_seconds=donor,matches=len(pairs),train_ransac_inliers=int(inliers.sum()),held_matches=int(h.sum()),held_median_geometric_px=float(np.median(dist[h])),held_p90_geometric_px=float(np.percentile(dist[h],90)),similarity=M.tolist(),held_pixel_count=int(m.sum()),held_pixel_rgb_rmse=float(np.sqrt(np.mean(err**2))),provisional_disk_potential_support={n:int((v&disk).sum()) for n,disk in disks.items()},masked_menu=donor==311.5);rows.append(row);np.savez_compressed(R/f'donor-{donor:g}-support.npz',valid=v);print('DONOR',json.dumps(row),flush=True)
# A separate affine RGB plane is permitted ONLY on uncovered footer paper, not photo.
X=np.stack([np.ones_like(xx),(xx-960)/700,(yy-680)/100],-1);train_region=(xx>=735)&(xx<=1160)&(yy>=650)&(yy<=720)&~exclude;train=train_region&~held;internal=train_region&held;left=(xx>=640)&(xx<=700)&(yy>=716)&(yy<=730)&~exclude;right=(xx>=1200)&(xx<=1260)&(yy>=716)&(yy<=730)&~exclude
co=np.linalg.lstsq(X[train],T[train]/255,rcond=None)[0];field=X@co;controls=[]
for name,m in [('spatial_heldout',internal),('independent_left_footer',left),('independent_right_footer',right)]:
 e=(field-T/255)[m]*255;controls.append(dict(name=name,pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(e**2))),signed_rgb=e.mean(0).tolist(),p95_abs=float(np.percentile(np.abs(e),95))))
domain=(yy>=650)&(yy<=730)&(xx>=630)&(xx<=1260);np.savez_compressed(R/'paper-only-estimated-input-proposal.npz',field_rgb=field.astype(np.float32),modeled_domain=domain,training_mask=train,held_internal=internal,held_left=left,held_right=right,observed_donor_potential=union)
proposal=dict(kind='SEPARATE estimated uncovered-footer RGB affine field; NOT observed truth or optical gain',basis=['1','(x-960)/700','(y-680)/100'],coefficient_rgb=co.tolist(),training_pixels=int(train.sum()),controls=controls,allowed_domain='ONLY x630..1260/y650..730 footer paper; photo, seam and hidden object/word details remain UNKNOWN',under_disk_modeled_paper_fraction={n:float(domain[disk].mean()) for n,disk in disks.items()},source_adopted=False,optical_gain=False,uncertainty='Held residuals are empirical validation, not a guarantee/CI for hidden pixels. Native video texture/moire, illumination and faint shadow tail may remain. No paper field applied over photo or glass target.')
save('paper-only-estimated-input-proposal.json',proposal)
fontpath=Path('/evidence/extended/icon-source/SF-Pro.ttf');font=TTFont(fontpath);gs=font.getGlyphSet();vectors=[]
for glyph in ['person.bust.tag.color.large','person.cut.portrait.tag.color.large','lightbulb.tag.color.large']:
 assert glyph in gs;pen=SVGPathPen(gs);gs[glyph].draw(pen);bp=BoundsPen(gs);gs[glyph].draw(bp);l,b,r,t=bp.bounds;name=glyph+'.svg';svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {t-b}"><path fill="#000" transform="translate({-l} {t}) scale(1 -1)" d="{pen.getCommands()}"/></svg>\n';(R/name).write_text(svg);vectors.append(dict(glyph=glyph,file=name,sha256=sha(R/name),bounds=list(bp.bounds),adopted=False,limits='Exact original font solid outline/defaultwdth100opsz28wght400; no target matte or fitting. Person candidates not yet selected/placed.'))
save('original-vector-provenance.json',dict(font_sha256=sha(fontpath),font_file=str(fontpath),vectors=vectors))
obs=[]
for n,disk in disks.items():
 photo=disk&(yy<640);gap=disk&(yy>=640)&(yy<650);theta=np.linspace(0,2*np.pi,360,endpoint=False);r=np.arange(41,52,.25);cx,cy=centers[n];px=(cx+np.cos(theta)[:,None]*r).astype(np.float32);py=(cy+np.sin(theta)[:,None]*r).astype(np.float32);s=cv2.remap(G.astype(float),px,py,cv2.INTER_LINEAR);peak=r[s.argmax(1)]
 obs.append(dict(label=n,center_estimate=centers[n],provisional_radius=46,disk_pixels=int(disk.sum()),potential_observed_donor_pixels=int((union&disk).sum()),partial_modeled_paper_pixels=int((domain&disk).sum()),photo_unknown_pixels=int(photo.sum()),seam_unknown_pixels=int(gap.sum()),no_optical_ray_proof='No opticalmap/kernel selected. These are provisional image-domain masks, not emitted/ALL-scored opticalsupport proof.',observed_style='Same native shot/resting circular action family; different actual foregrounds and photo-floor/footer regions. Consistent pose/style is evidence for a shared model, not proof of proprietary material identity.',bright_ridge_diagnostic=dict(median=float(np.median(peak)),p10_p90=np.percentile(peak,[10,90]).tolist(),not_physical_alpha=True)))
save('source-audit.json',dict(target_seconds=310,donor_batch=rows,observations=obs,temporal_background_diversity=False,spatial_backgrounds='Left person and right bulb are distinct same-style controls with different photo-floor/footer surroundings, not two temporal backgrounds of identical icon.',paper_estimated_proposal=proposal,optical_fit=False,source_adopted=False,hidden_photodetail_filled=0));print('COMPLETE',json.dumps(obs),flush=True)
