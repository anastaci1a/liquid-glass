"""Unlensed SF-vector identity/pose check. Never trace photographic coverage."""
import os,sys,json,hashlib
from pathlib import Path
from io import BytesIO
import numpy as np,cv2,cairosvg
from PIL import Image
from scipy.optimize import minimize
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from font_vector import export
os.umask(0o002);cv2.setNumThreads(1);D=Path('/evidence/extended/blue-slider-short-round');O=D/'icon-background-online';O.mkdir(exist_ok=True)
font=Path('/evidence/extended/icon-source/fonts/Library/Fonts/SF-Pro-Display-Regular.otf');A=np.asarray(Image.open(D/'sequence/frame-00.png').convert('RGB')).astype(float)/255;B=np.asarray(Image.open(D/'sequence/frame-07.png').convert('RGB')).astype(float)/255;P=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/slider-source.png').convert('RGB')).astype(float)/255
color=np.median(A[544:556,600:800],axis=(0,1));rows=[]
for name,roiA,roiB in [('tortoise',(420,510,530,590),(380,510,486,590)),('hare',(1420,510,1540,590),(1410,510,1525,590))]:
 variants=[]
 for suffix in ['original-outline']:
  glyph=name+'.'+suffix;svg=(D/(name+'-online-outline.svg')).read_text();meta=json.loads((D/(name+'-online-outline.json')).read_text());(O/(glyph+'.svg')).write_text(svg);(O/(glyph+'.json')).write_text(json.dumps(meta,indent=2)+'\n');alpha=np.asarray(Image.open(BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=1000))).convert('RGBA'))[:,:,3].astype(np.float32)/255;ratio=alpha.shape[0]/alpha.shape[1]
  def fit(T,roi,core_only):
   x0,y0,x1,y1=roi;target=T[y0:y1,x0:x1];bg=P[y0:y1,x0:x1];ink=(target[:,:,2]-target[:,:,0]>.32)&(target[:,:,0]<.5);iy,ix=np.where(ink);assert len(ix)>100
   start=[x0+float(ix.min())-.5,y0+float(iy.min())-.5,float(ix.max()-ix.min()+1)];bounds=[(start[0]-3,start[0]+3),(start[1]-3,start[1]+3),(start[2]-6,start[2]+6)]
   Y,X=np.mgrid[y0:y1:.25,x0:x1:.25];X=X-.375;Y=Y-.375;yy,xx=np.mgrid[y0:y1,x0:x1];spatial=(xx//4+3*(yy//4))%3;support=ink if core_only else np.ones_like(ink);train=support&(spatial!=0);held=support&(spatial==0)
   def coverage(v):
    left,top,w=v;h=w*ratio;u=((X-left+.5)*alpha.shape[1]/w-.5).astype(np.float32);z=((Y-top+.5)*alpha.shape[0]/h-.5).astype(np.float32)
    return cv2.remap(alpha,u,z,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT).reshape(y1-y0,4,x1-x0,4).mean((1,3))
   def field(v):
    a=coverage(v);return bg*(1-a[...,None])+color*a[...,None]
   def objective(v):return float(np.mean((field(v)[train]-target[train])**2))
   opt=minimize(objective,start,method='Powell',bounds=bounds,options=dict(maxfev=240,xtol=.001,ftol=1e-8));pred=field(opt.x);a=coverage(opt.x)
   return dict(placement=[float(opt.x[0]),float(opt.x[1]),float(opt.x[0]+opt.x[2]),float(opt.x[1]+opt.x[2]*ratio)],training_rgb_rmse=float(np.sqrt(np.mean((pred[train]-target[train])**2))*255),held_rgb_rmse=float(np.sqrt(np.mean((pred[held]-target[held])**2))*255),support='predeclared high-blue core only (unknown surrounding halo excluded)' if core_only else 'entire exposed icon ROI, spatialheldblocks',train_pixels=int(train.sum()),held_pixels=int(held.sum()),evaluations=int(opt.nfev),solver_success=bool(opt.success),solver_message=str(opt.message),limits='Only translation/uniformscale of ORIGINAL clean SVG; fixed color from independently exposed blue track, no outline/alpha edits or fitted source-PSF. B scoresdoNOTvalidate surroundinghalo/backdrop.'),pred,a
  res,pred,aa=fit(A,roiA,False);variants.append((res['held_rgb_rmse'],glyph,svg,res,alpha,ratio));Image.fromarray(np.rint(np.clip(pred,0,1)*255).astype(np.uint8)).resize((480,320)).save(O/(glyph+'-A-proposal.png'));print(name,suffix,res['training_rgb_rmse'],res['held_rgb_rmse'],flush=True)
 # Select icon identity ONLY from independent unoccluded A; B is held for pose.
 best=min(variants,key=lambda v:v[0]);_,glyph,svg,res,alpha,ratio=best
 # fit() closure reads current alpha/ratio, explicitly restored to selected SVG.
 rb,predB,ab=fit(B,roiB,True);(O/(name+'.svg')).write_text(svg);np.save(O/(name+'-B-source-coverage.npy'),ab);Image.fromarray(np.rint(np.clip(predB,0,1)*255).astype(np.uint8)).resize((460,320)).save(O/(name+'-B-source-proposal.png'))
 rows.append(dict(icon=name,glyph=best[1],source_svg_sha256=hashlib.sha256(svg.encode()).hexdigest(),A_identity_check=res,B_pose_only=rb,all_A_variants=[dict(glyph=v[1],held_rgb_rmse=v[0]) for v in variants]))
(O/'result.json').write_text(json.dumps(dict(color_rgb=color.tolist(),color_calibration='Independent uncovered Arest blue-track interior544:556,600:800; no glyph/halo/lensed pixels used',icons=rows,status='SOURCE PROPOSAL ONLY; no Bbackground/benchmark adoption, no opticalpass',limits='Original SF outlines reused; placementfits neveralter vectorgeometry/aspectratio. A matches select available font variant, not conclusive Apple configuration proof; inspect training/held errors. Bhalo absent from incident reconstruction by design, not copied into source.'),indent=2)+'\n')
