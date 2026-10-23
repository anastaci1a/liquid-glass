"""Measure central affine correspondence; diagnostic only, no rendered correction."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import least_squares
from extended_fit import Study
folder=Path('/evidence/extended/active-segmented-selector');rows=[]
for label,root in [('A',folder),('B',folder/'second-observation')]:
 s=Study(root);source=np.clip((s.source[:,:,0]-s.source[:,:,1])/.65,0,1);target=np.clip((s.target[:,:,0]-s.target[:,:,1])/.65,0,1)
 a,b,c,d=s.crop;near=cv2.dilate((target[b:d,a:c]>.03).astype(np.uint8),np.ones((17,17),np.uint8));mask=s.valid&(-s.sd>.5)&(near>0)
 yy,xx=np.where(mask);X=xx+a;Y=yy+b;cx=s.source.shape[1]/2;cy=s.source.shape[0]/2;L=s.L
 v=np.array([.9,.9,0.,0.,1.]);lo=np.array([.65,.65,-.4,-.4,.7]);hi=np.array([1.2,1.2,.4,.4,1.4])
 for sigma in [3.,1.,0.]:
  S=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;T=cv2.GaussianBlur(target,(0,0),sigma) if sigma else target;expected=T[Y,X]
  def f(v):
   mx=cx+(X-cx)*v[0]+v[2]*L;my=cy+(Y-cy)*v[1]+v[3]*L
   pred=cv2.remap(S,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR).ravel()
   return (v[4]*pred-expected).astype(float)
  def jac(v):
   J=[]
   for i in range(len(v)):
    up=v.copy();dn=v.copy();up[i]+=1e-3;dn[i]-=1e-3;J.append((f(up)-f(dn))/.002)
   return np.array(J).T
  fit=least_squares(f,v,jac=jac,bounds=(lo,hi),max_nfev=150,ftol=1e-10,xtol=1e-9,gtol=1e-9);v=fit.x
 rows.append(dict(label=label,source_map_scale=v[:2].tolist(),source_map_translation_over_L=v[2:4].tolist(),contrast=v[4],alpha_rmse=float(np.sqrt(np.mean(f(v)**2))),pixels=len(X)))
(folder/'crown-review/core-correspondence.json').write_text(json.dumps(dict(rows=rows,limits='Advisory affine correspondence in existing frozen core region. No parameters applied to renderer or source. Does not distinguish content-state scaling from optical magnification.'),indent=2)+'\n')
print(json.dumps(rows))
