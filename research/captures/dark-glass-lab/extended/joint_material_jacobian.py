"""Private analytic material Jacobian for native joint-fit proposals.

Same clipped-affine material derivative as public material_local.statistics;
retain exact native optical finite differences and all optical/material cross
terms. Only proposal construction changes. Nonlinear native gates still decide.
"""
import numpy as np,cv2

def material_channels(cache,co):
 s=cache.study;H,W=cache.H,cache.W;C,J=cache.C,cache.J
 T=getattr(cache,'material_transform',np.eye(23));effective=T@co+getattr(cache,'material_offset',0)
 core=J[...,-1];gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:]
 z=C*gain+effective[3:6]+(J[...,:-1]@effective[6:-3])[...,None]
 for channel in range(3):
  active=(z[...,channel]>0)&(z[...,channel]<1)
  def average(v):return v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
  F=np.zeros((H,W,23),np.float64)
  F[...,channel]=average(active*C[...,channel]*(1-core))
  F[...,channel+3]=average(active)
  F[...,6:20]=average(active[...,None]*J[...,:-1])
  F[...,channel+20]=average(active*C[...,channel]*core)
  F=F@T
  sigma=s.kernel_sigma(cache.p,'post_sigma')
  if sigma>.001:F=cv2.GaussianBlur(F,(0,0),sigma)
  if 'grazing_reflection' in cache.p:
   from grazing_reflection import layers
   F*=1-layers(s,cache.p)[0][...,None]
  yield channel,F

def statistics(cache,co,optical_derivatives,scales,prediction=None):
 s=cache.study;N=len(optical_derivatives);count=N+23
 pred=cache.render(co) if prediction is None else prediction
 residual=pred.astype(np.float64)-s.target_crop
 forms={name:[np.zeros((count,count)),np.zeros(count)] for name in ['glass','rim']}
 for channel,F in material_channels(cache,co):
  for name,mask in [('glass',s.valid),('rim',s.rim)]:
   D=np.empty((int(mask.sum()),count),np.float64)
   for k,im in enumerate(optical_derivatives):D[:,k]=im[...,channel][mask]*scales[k]
   D[:,N:]=F[mask]*np.asarray(scales[N:])
   r=residual[...,channel][mask];factor=255**2/(3*mask.sum())
   forms[name][0]+=(D.T@D)*factor;forms[name][1]+=(D.T@r)*factor
 return forms
