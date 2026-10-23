"""Unlensed capsule-cap controls. Distinguish end CENTER from outer boundary."""
import os,sys,json
from pathlib import Path
import numpy as np,cv2
from PIL import Image
from scipy.optimize import minimize
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from background import paper
os.umask(0o002);cv2.setNumThreads(1);D=Path('/evidence/extended/blue-slider-short-round');O=D/'track-cap-controls';O.mkdir(exist_ok=False)
read=lambda p:np.asarray(Image.open(p).convert('RGB')).astype(np.float32)/255
rest=read(D/'sequence/frame-00.png');excluded=np.zeros(rest.shape[:2],bool);excluded[500:610,540:1450]=True;bg,evidence=paper(rest,excluded);np.save(O/'paper.npy',bg)
rows=[]
for name,path,side,roi,colbox,initial in [('rest-right',D/'sequence/frame-00.png','right',(1330,530,1410,570),(1100,544,1250,556),1377.5),('A-right',Path('/evidence/apple-matches/public-settled-replay/slider-target.png'),'right',(1330,530,1410,570),(1100,544,1250,556),1377.5),('B-right',D/'sequence/frame-07.png','right',(1320,530,1400,570),(1100,544,1250,556),1365),('left-exposed-frame13',D/'sequence/frame-13.png','left',(540,530,630,570),(800,544,1000,556),579.5)]:
 T=read(path);x0,y0,x1,y1=roi;cx0,cy0,cx1,cy1=colbox;color=np.median(T[cy0:cy1,cx0:cx1],axis=(0,1));target=T[y0:y1,x0:x1];B=bg[y0:y1,x0:x1];Y,X=np.mgrid[y0:y1:.25,x0:x1:.25];X=X-.375;Y=Y-.375;yy,xx=np.mgrid[y0:y1,x0:x1];train=(xx+3*yy)%3!=0
 def field(v):
  end,cy,r=v;dx=np.maximum(X-end,0) if side=='right' else np.maximum(end-X,0)
  a=(dx*dx+(Y-cy)**2<=r*r).reshape(y1-y0,4,x1-x0,4).mean((1,3));return B*(1-a[...,None])+color*a[...,None]
 opt=minimize(lambda v:np.mean(((field(v)-target)[train])**2),[initial,549.5,10],method='Powell',bounds=[(initial-15,initial+15),(548,551),(8,12)],options=dict(maxfev=180,xtol=.01,ftol=1e-8));pred=field(opt.x);e=opt.x
 rows.append(dict(name=name,path=str(path),side=side,endpoint_center_x=float(e[0]),center_y=float(e[1]),radius=float(e[2]),outer_horizontal_boundary_x=float(e[0]+(e[2] if side=='right' else -e[2])),train_rgb_rmse=float(np.sqrt(np.mean(((pred-target)[train])**2))*255),held_rgb_rmse=float(np.sqrt(np.mean(((pred-target)[~train])**2))*255),evaluations=int(opt.nfev),success=bool(opt.success),message=str(opt.message),color_rgb=color.tolist(),limits='Unlensed cap only; no lens rays or hidden endpoint fitting. Quantized4x4 capsule coverage; unknown video PSF remains. Exposed left cap from different interaction time is corroboration, not proof of same minimum-state layout.'))
 Image.fromarray(np.rint(np.clip(pred,0,1)*255).astype(np.uint8)).resize((640,320)).save(O/(name+'-proposal.png'))
(O/'result.json').write_text(json.dumps(dict(observations=rows,paper=evidence,correction='Prior raw positive-gradient edges were OUTER boundaries, not capsule endpoint centers. Compare center-to-center or outer-to-outer; earlier13px discrepancy was not a valid semantic cap comparison. Global icon registration still fails heldout matches and is not adopted.'),indent=2)+'\n');print(json.dumps(rows),flush=True)
