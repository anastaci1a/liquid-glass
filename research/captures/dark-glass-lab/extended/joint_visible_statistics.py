"""Native joint proposals with visible exterior/fixed-crop constraints.
Only for fixed shape and shadow; geometry/coverage derivatives are not included.
"""
import numpy as np
from joint_material_jacobian import material_channels
from revision_replay import clean_composite
CROPS={'upper-left':[.12,.06,.40,.31],'lower-left':[.12,.64,.42,.87],'right-rim':[.72,.28,.91,.70],'center':[.35,.35,.65,.65]}
def visible_masks(s):
 H,W=s.target_crop.shape[:2];out={'shadow':(s.sd>0)&(s.sd<.35)}
 for name,box in CROPS.items():
  a,b,c,d=[round(v*n) for v,n in zip(box,[W,H,W,H])];m=np.zeros((H,W),bool);m[b:d,a:c]=True;out['crop_'+name]=m
 return out
def measures(s,p,im):
 C=clean_composite(s,p,im);error=(C-s.target_crop)*255
 return {name:dict(rmse=float(np.sqrt(np.mean(error[mask]**2)))) for name,mask in visible_masks(s).items()}
def statistics(cache,co,optical_derivatives,scales,prediction=None):
 s=cache.study;N=len(optical_derivatives);count=N+23;p=cache.p;pred=cache.render(co) if prediction is None else prediction
 residual=pred.astype(np.float64)-s.target_crop;visible_residual=clean_composite(s,p,pred).astype(np.float64)-s.target_crop;alpha=s.shape_coverage(p)
 masks={'glass':s.valid,'rim':s.rim,**visible_masks(s)};forms={k:[np.zeros((count,count)),np.zeros(count)] for k in masks}
 for channel,F in material_channels(cache,co):
  for name,mask in masks.items():
   visible=name not in ['glass','rim'];D=np.empty((int(mask.sum()),count),np.float64)
   for k,im in enumerate(optical_derivatives):D[:,k]=im[...,channel][mask]*scales[k]
   D[:,N:]=F[mask]*np.asarray(scales[N:])
   if visible:D*=alpha[mask,None]
   r=(visible_residual if visible else residual)[...,channel][mask];factor=255**2/(3*mask.sum())
   forms[name][0]+=(D.T@D)*factor;forms[name][1]+=(D.T@r)*factor
 return forms
