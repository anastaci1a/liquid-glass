"""Bounded uncovered-control source/pose assessment; no lens/body render/fit."""
import os,json,datetime,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/options-popup-round');start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'))
p=Path('/evidence/apple-matches/219-240.png');T=np.asarray(Image.open(p).convert('RGB'));H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];initial=np.array([925.,534.,266.5,328.5,100.])
def sd(x,y,q):
 cx,cy,hx,hy,r=q;a=abs(x-cx)-(hx-r);b=abs(y-cy)-(hy-r);return np.hypot(np.maximum(a,0),np.maximum(b,0))+np.minimum(np.maximum(a,b),0)-r
sdf=sd(xx,yy,initial);region=(xx>=350)&(xx<1500)&(yy>=40)&(yy<1040);control=region&(sdf>=85)&(sdf<=210)
# Four outer strips reserved BEFORE fitting; no target-lens/shadow data used.
independent={'left':region&(sdf>=225)&(sdf<255)&(xx<660),'right':region&(sdf>=225)&(sdf<255)&(xx>1190),'upper':region&(sdf>=225)&(sdf<255)&(yy<210),'lower':region&(sdf>=155)&(sdf<185)&(yy>970)}
# Lower far control may overlap annulus: remove ALL independent masks from train/held.
for m in independent.values():control&=~m
held=(xx//17+3*(yy//17))%5==0;train=control&~held;test=control&held
u=(xx-925)/350;v=(yy-534)/400;X=np.stack([np.ones_like(u),u,v],-1);co=np.linalg.lstsq(X[train],T[train]/255,rcond=None)[0];F=X@co

def err(f,m):
 e=(f-T/255)[m]*255;return dict(pixels=int(m.sum()),rgb_rmse=float(np.sqrt(np.mean(e**2))) if e.size else None,signed_rgb=e.mean(0).tolist() if e.size else None,p95_absolute=float(np.percentile(abs(e),95)) if e.size else None)
cohorts=[('train',train),('spatial_heldout',test),*independent.items()];affine={n:err(F,m) for n,m in cohorts}
Z=np.stack([np.ones_like(u),u,v,u*u,u*v,v*v],-1);qc=np.linalg.lstsq(Z[train],T[train]/255,rcond=None)[0];Q=Z@qc;quad={n:err(Q,m) for n,m in cohorts};improve={n:quad[n]['rgb_rmse']<=affine[n]['rgb_rmse'] for n in ['spatial_heldout',*independent.keys()] if quad[n]['pixels']};supported=all(improve.values())
# Observation-derived edge landmarks only; no optical objective/source fit.
pts=[];norm=[];cx,cy,hx,hy,r=initial
for sign in [-1,1]:
 for y in np.linspace(cy-hy+r,cy+hy-r,100):pts.append([cx+sign*hx,y]);norm.append([sign,0])
 for x in np.linspace(cx-hx+r,cx+hx-r,90):pts.append([x,cy+sign*hy]);norm.append([0,sign])
for sx in [-1,1]:
 for sy in [-1,1]:
  for a in np.linspace(0,np.pi/2,50):nx=sx*np.cos(a);ny=sy*np.sin(a);pts.append([cx+sx*(hx-r)+nx*r,cy+sy*(hy-r)+ny*r]);norm.append([nx,ny])
pts=np.array(pts);norm=np.array(norm);offset=np.arange(-7,7.01,.125);A=(pts[:,0,None]+norm[:,0,None]*offset).astype(np.float32);B=(pts[:,1,None]+norm[:,1,None]*offset).astype(np.float32);gray=T.mean(2).astype(np.float32);sample=cv2.remap(gray,A,B,cv2.INTER_LINEAR);der=np.gradient(sample,.125,axis=1);idx=np.abs(der).argmax(1);landmarks=pts+norm*offset[idx,None];fit=least_squares(lambda q:sd(landmarks[:,0],landmarks[:,1],q),initial,bounds=(initial-[5,5,6,6,40],initial+[5,5,6,6,40]),loss='soft_l1',f_scale=.5,max_nfev=100);pose=fit.x
# Diagnostics only, all unadopted. Field under target is estimated, never observed.
np.savez_compressed(R/'source-assessment.npz',train=train,held=test,**independent,affine_field=F.astype(np.float32),quadratic_field=Q.astype(np.float32),landmarks=landmarks)
result=dict(stage='SOURCE_ONLY_ASSESSMENT_NO_ADOPTION_OR_BODY_RENDER',original=dict(path=str(p),png_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=[W,H],dtype='uint8RGB',seconds=240,highest_local_target='Existing full-native1080p. Cached official4k material covers709s, not this example; metadata only does not recover hidden input.'),source=dict(basis_affine=['1','u','v'],basis_quadratic=['1','u','v','u^2','uv','v^2'],coordinates=dict(u='(x-925)/350',v='(y-534)/400'),affine_coefficients=co.tolist(),affine_controls=affine,quadratic_coefficients=qc.tolist(),quadratic_controls=quad,quadratic_nonregression_by_control=improve,quadratic_supported=supported,hidden_observed_fraction=0,exclusion='Rounded popup footprint plus85nativepx, held and four independent strips reserved; no lens/foreground/reference shadow retained or copied. Broad shadow/lighting tail absence not proved.'),pose=dict(center=pose[:2].tolist(),half=pose[2:4].tolist(),radius=float(pose[4]),landmarks=len(landmarks),ridge_residual_p95=float(np.percentile(abs(sd(landmarks[:,0],landmarks[:,1],pose)),95)),limits='Single rounded-rectangle landmark prior, not true physical alpha or knownApple solid; model/pose not adopted.'),body_renders=0,optical_fits=0,count=0,elapsed_seconds=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(start['started_at'].replace('Z','+00:00'))).total_seconds())
(R/'source-assessment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
# Overlay shows only independent exposed controls, never feeds any renderer.
img=T.astype(float).copy()
for name,m,color in [('train',train,[0,255,0]),('held',test,[255,170,0]),*[(n,m,[0,255,255]) for n,m in independent.items()]]:img[m]=.4*img[m]+.6*np.asarray(color)
Image.fromarray(np.uint8(np.rint(img))).resize((960,540),Image.Resampling.NEAREST).save(R/'controls-overlay.png')
