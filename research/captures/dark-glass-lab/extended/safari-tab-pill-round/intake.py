"""Source-only Safari tab-count pill intake; controls frozen before fit."""
from pathlib import Path
import json,hashlib,os
import cv2,numpy as np
from PIL import Image
from scipy.optimize import least_squares
from crowned_footprint import field
cv2.setNumThreads(1);os.umask(0o002);R=Path('/evidence/extended/safari-tab-pill-round');T=np.asarray(Image.open('/evidence/apple-matches/219-290.png')).astype(float)/255;H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];X=np.stack([np.ones_like(xx),(xx-1173)/150,(yy-706)/100],-1)
# All controls are outside the glass and its immediate rim. Lower is independent.
upper=(xx>=1005)&(xx<1305)&(yy>=450)&(yy<570);left=(xx>=940)&(xx<990)&(yy>=610)&(yy<770);lower=(xx>=1030)&(xx<1300)&(yy>=810)&(yy<835);controls=(upper|left);train=controls&((xx+3*yy)%5!=0);held=controls&~train;assert not np.any(controls&lower)
co=np.linalg.lstsq(X[train],T[train],rcond=None)[0];plane=X@co
metric=lambda m:float(np.sqrt(np.mean(((plane-T)[m]*255)**2)))
# Fixed input-gradient ridge extraction, no lensed-color residuals.
G=T.mean(2);gx=cv2.Sobel(G,cv2.CV_64F,1,0,ksize=3)/8;gy=cv2.Sobel(G,cv2.CV_64F,0,1,ksize=3)/8
cx,cy,a,b=1173.,706.,126.,72.;pts=[]
# Outward-facing capsule perimeter with smooth normal along both caps.
for theta in np.linspace(0,2*np.pi,480,endpoint=False):
 n=np.array([np.cos(theta),np.sin(theta)]);q=np.array([cx+np.sign(n[0])*(a-b)+b*n[0],cy+b*n[1]])
 # Top/bottom central straight portions sampled separately below.
 offsets=np.linspace(-4,4,65);P=q+offsets[:,None]*n;v=cv2.remap(gx,P[:,0].astype('float32'),P[:,1].astype('float32'),cv2.INTER_LINEAR).ravel()*n[0]+cv2.remap(gy,P[:,0].astype('float32'),P[:,1].astype('float32'),cv2.INTER_LINEAR).ravel()*n[1];j=int(np.argmax(abs(v)))
 if abs(v[j])>.004:pts.append(P[j])
for sign in [-1,1]:
 for x in np.linspace(cx-(a-b),cx+(a-b),100):
  offsets=np.linspace(-4,4,65);Y=cy+sign*(b+offsets);P=np.stack([np.full_like(Y,x),Y],1);v=cv2.remap(gy,P[:,0].astype('float32'),P[:,1].astype('float32'),cv2.INTER_LINEAR).ravel();j=int(np.argmax(abs(v)))
  if abs(v[j])>.004:pts.append(P[j])
pts=np.array(pts);hold=np.arange(len(pts))%4==0
# Crown softness.1 is a shared prior, only pose is estimated here.
def residual(v,P):
 cx,cy,a,b=v;t,gx,gy=field(P[:,0]-cx,P[:,1]-cy,[a,b],.1);return(t-1)/np.maximum(np.hypot(gx,gy),1e-9)
fit=least_squares(lambda v:residual(v,pts[~hold]),[cx,cy,a,b],bounds=([1168,701,121,67],[1178,711,131,77]),loss='soft_l1',f_scale=.5,max_nfev=100)
# Predeclared glyph regions, only dark components inspected; no screenshot glyph matte used.
glyphs=[]
for name,box in [('count',[1085,660,1135,750]),('plus',[1180,660,1260,750])]:
 x,y,z,w=box;mask=(T[y:w,x:z].max(2)<.2).astype('uint8');n,lab,stats,_=cv2.connectedComponentsWithStats(mask,8);k=1+int(np.argmax(stats[1:,4]));u,v,ww,hh,p=stats[k];glyphs.append({'name':name,'dark_bbox':[int(x+u),int(y+v),int(x+u+ww),int(y+v+hh)],'pixels':int(p)})
report={'status':'SOURCE_POSE_ONLY_PROPOSAL_NO_RENDER_NO_PASS','source_target':'219-290.png','target_sha256':hashlib.sha256(Path('/evidence/apple-matches/219-290.png').read_bytes()).hexdigest(),'source_basis':['1','(x-1173)/150','(y-706)/100'],'source_coefficient_rgb':co.tolist(),'controls':{'train':int(train.sum()),'held':int(held.sum()),'lower':int(lower.sum())},'source_rmse_levels':{'train':metric(train),'held':metric(held),'independent_lower':metric(lower)},'source_limits':'Affine mathematical estimate beneath pill, no independently observed hidden RGB; broad parent-panel curvature/shadows remain confounds. No optical identification. Controls and glyph regions declared before fitting.','pose':{'center_half':fit.x.tolist(),'crown_softness_prior':.1,'held_gradient_normal_rmse':float(np.sqrt(np.mean(residual(fit.x,pts[hold])**2))),'landmarks':len(pts),'not_Apple_solid':True},'glyph_proposal':glyphs,'optical_fits':0,'verified_passes':0};(R/'source-pose-proposal.json').write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(R/'source-control-evidence.npz',train=train,held=held,independent_lower=lower,points=pts,pose_held=hold);Image.fromarray(np.uint8(np.rint(np.clip(plane,0,1)*255))).save(R/'source-plane.png');print(json.dumps(report))
