"""ONE same-example similarity-registration family on exposed pixels; no optical/source fit."""
import os,json,hashlib,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
R=Path('/evidence/extended/helper-toolbar-work/compose-source-pose-round');os.umask(0o002);cv2.setNumThreads(1)
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if (R/'donor-audit.json').exists():raise RuntimeError('Existing complete donor audit, no repeat')
start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'))
y,x=np.mgrid[:1080,:1920];radius=np.hypot(x-960,y-532);inside=radius<114;region=(x>20)&(x<1150)&(y>20)&(y<730);exposed=region&(radius>165);held=((x//32+3*(y//32))%4)==0
sift=cv2.SIFT_create(nfeatures=6000);cache={}
def get(t):
 if t not in cache:
  rgb=np.asarray(Image.open(R/f'frames/{t:03d}.png').convert('RGB'));gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);kp,des=sift.detectAndCompute(gray,np.uint8(exposed)*255);cache[t]=(rgb,gray,kp,des)
 return cache[t]
rows=[];valids={};
for target,donors,label in [(400,[396,398,402],'text-A'),(410,[404,406,408,412],'photo-B')]:
 T,G,kt,dt=get(target);union=np.zeros(inside.shape,bool);tests=[]
 for donor in donors:
  S,SG,ks,ds=get(donor);pairs=[]
  if ds is not None and dt is not None:
   pairs=[m for m,n in cv2.BFMatcher().knnMatch(ds,dt,k=2) if m.distance<.7*n.distance]
  if len(pairs)<12:tests.append(dict(donor=donor,matched=len(pairs),accepted_registration=False,reason='Too few exposed feature matches'));continue
  a=np.array([ks[m.queryIdx].pt for m in pairs],np.float32);b=np.array([kt[m.trainIdx].pt for m in pairs],np.float32);hi=((np.floor(b[:,0]/32)+3*np.floor(b[:,1]/32))%4)==0;train=~hi
  if train.sum()<10:tests.append(dict(donor=donor,accepted_registration=False,reason='Too few exposed nonheldout matches'));continue
  M,inliers=cv2.estimateAffinePartial2D(a[train],b[train],method=cv2.RANSAC,ransacReprojThreshold=1.25,maxIters=5000,confidence=.999);pred=a@M[:,:2].T+M[:,2];distance=np.linalg.norm(pred-b,axis=1);held_dist=distance[hi];held_good=held_dist[held_dist<3];scale=float(np.hypot(M[0,0],M[1,0]));angle=float(np.degrees(np.arctan2(M[1,0],M[0,0])));good=bool(inliers.sum()>=12 and held_good.size>=4 and np.sqrt(np.mean(held_good**2))<1)
  warped=cv2.warpAffine(S.astype(np.float64)/255,M,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT);source_valid=cv2.erode(np.uint8(exposed),np.ones((5,5),np.uint8));v=cv2.warpAffine(source_valid.astype(float),M,(1920,1080),flags=cv2.INTER_LINEAR)>=.999999
  control=v&exposed&held;err=(warped-T/255)[control]*255
  if good:union|=v
  row=dict(donor=donor,matched=len(pairs),train_matches=int(train.sum()),ransac_inliers=int(inliers.sum()),held_matches=int(hi.sum()),held_inliers_under3px=int(held_good.size),held_inlier_rms_px=float(np.sqrt(np.mean(held_good**2))) if held_good.size else None,held_all_median_px=float(np.median(held_dist)) if held_dist.size else None,similarity=M.tolist(),scale=scale,rotation_degrees=angle,accepted_registration=good,held_pixel_count=int(control.sum()),held_pixel_rgb_rmse=float(np.sqrt(np.mean(err**2))) if control.any() else None,held_pixel_signed_rgb=err.mean(0).tolist() if control.any() else None,button_original_disk_observed_fraction=float(v[inside].mean()),source_observed_mask='Eroded exposed original donor only; no glass/shadow/corner source or fills')
  tests.append(row);print(label,donor,'good',good,'scale',scale,'delta',M[:,2].tolist(),'support',row['button_original_disk_observed_fraction'],'heldRMSE',row['held_pixel_rgb_rmse'],flush=True)
  np.savez_compressed(R/f'{label}-donor{donor}-valid.npz',valid=v)
  if good:Image.fromarray(np.rint(np.clip(warped,0,1)*255).astype(np.uint8)).save(R/f'{label}-donor{donor}-projected.png')
  save('donor-audit-partial.json',dict(completed=rows,current=dict(label=label,target=target,tests=tests)))
 valids[label]=union;holes=inside&~union;rows.append(dict(label=label,target_seconds=target,donors=tests,button_disk_pixels=int(inside.sum()),union_observed_pixels=int((union&inside).sum()),union_observed_fraction=float(union[inside].mean()),remaining_hidden_pixels=int(holes.sum()),union_full_disk=bool(union[inside].all()),source_adopted=False,limits='Registration fit only exposed background; held pixel RMSE not optical score. No model/footprint/optical source-ray bounds selected yet; full_disk is provisional circle diagnostic, never whole/ALL-scored optical proof. Gaussian source support remains unassigned.'))
 np.savez_compressed(R/f'{label}-source-support.npz',observed=union,provisional_body_disk=inside,missing=holes)
 # Pose ridge diagnostic: measured bright ring, not a claim of physical alpha/boundary.
 theta=np.linspace(0,2*np.pi,720,endpoint=False);r=np.arange(108,123,.25);xx=(960+np.cos(theta)[:,None]*r).astype(np.float32);yy=(532+np.sin(theta)[:,None]*r).astype(np.float32);samples=cv2.remap(G.astype(float),xx,yy,cv2.INTER_LINEAR);peak=r[samples.argmax(1)];rows[-1]['bright_ridge_not_physical_shape']=dict(assumed_center=[960,532],median_radius_px=float(np.median(peak)),radius_p10_p90=np.percentile(peak,[10,90]).tolist(),note='Same camera/button position appears fixed. Ridge location depends on exterior/content/material and is not alpha truth.')
fontpath=Path('/evidence/extended/icon-source/SF-Pro.ttf');font=TTFont(fontpath);gs=font.getGlyphSet();name='square.and.pencil.tag.color.large';assert name in gs;pen=SVGPathPen(gs);gs[name].draw(pen);bp=BoundsPen(gs);gs[name].draw(bp);left,bottom,right,top=bp.bounds;svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {right-left} {top-bottom}"><path fill="#000" transform="translate({-left} {top}) scale(1 -1)" d="{pen.getCommands()}"/></svg>\n';(R/'square-and-pencil-original.svg').write_text(svg)
save('original-vector-provenance.json',dict(font_file=str(fontpath),font_sha256=sha(fontpath),glyph=name,font_variation='Original default axes wdth100/opsz28/wght400; no target fit or mask',glyph_bounds=list(bp.bounds),svg_sha256=sha(R/'square-and-pencil-original.svg'),adopted=False,scored=False,limit='Original solid font outline establishes a genuine vector candidate; target weight/size/placement/state not calibrated or certified.'))
save('donor-audit.json',dict(family='ONE similarity registration per saved same-example donor; no optical/source-photometry fit',observations=rows,unknown_pixels_filled=0,optical_fit=False,source_adopted=False));print('DONE',[(r['label'],r['union_observed_fraction']) for r in rows],flush=True)
