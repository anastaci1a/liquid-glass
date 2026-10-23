"""Cached map differentiation + analytic d-crop Jacobian, never image addresses."""
from pathlib import Path
import sys,json
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));sys.path.insert(0,str(P/'code'))
from checkpoint import actual_hessian_and_Jxx
from harmonic_crowned_back import HarmonicCrownedBack
X=np.load(P/'X-0.15.npy',mmap_mode='r');Y=np.load(P/'Y-0.15.npy',mmap_mode='r');inside=np.load(P/'inside-0.15.npy',mmap_mode='r')
folds=0;count=0;low=float('inf');high=-low;bounds=[float('inf'),float('inf'),-float('inf'),-float('inf')]
for top in range(1,X.shape[0]-1,48):
    bot=min(top+48,X.shape[0]-1)
    valid=inside[top:bot,1:-1]&inside[top-1:bot-1,1:-1]&inside[top+1:bot+1,1:-1]&inside[top:bot,:-2]&inside[top:bot,2:]
    ux=(X[top:bot,2:]-X[top:bot,:-2])/.5;uy=(X[top+1:bot+1,1:-1]-X[top-1:bot-1,1:-1])/.5
    vx=(Y[top:bot,2:]-Y[top:bot,:-2])/.5;vy=(Y[top+1:bot+1,1:-1]-Y[top-1:bot-1,1:-1])/.5
    det=ux*vy-uy*vx;bad=valid&(det<0);folds+=int(bad.sum());count+=int(valid.sum())
    if valid.any():low=min(low,float(det[valid].min()));high=max(high,float(det[valid].max()))
    row,col=np.nonzero(bad)
    if len(row):
        px=475+(col+1+.5)/4-.5;py=285+(row+top+.5)/4-.5
        bounds=[min(bounds[0],float(px.min())),min(bounds[1],float(py.min())),max(bounds[2],float(px.max())),max(bounds[3],float(py.max()))]
s=HarmonicCrownedBack();yy,xx=np.mgrid[468:550,960:1120];nx=(xx-960)/170;ny=(yy-542)/170
hxx,J=actual_hessian_and_Jxx(s,nx,ny)
np.savez(P/'d-crop-analytic-Jxx.npz',native_x=xx,native_y=yy,hxx=hxx,source_X_x=J)
alpha=np.load(P/'alpha-0.15.npy');old=np.load('/evidence/extended/toolbar-response-primary-review/alpha.npy');M=np.load(P/'material-0.15.npy');C=np.load(P/'complete-0.15.npy')
r={'scope':'Cached geometry only and analytic derivative diagnostic checked in checkpoint. No image/source resampling or new rays.', 'folds':{'valid_complete_interior_subray_stencils':count,'negative_determinant_stencils':folds,'determinant_range':[low,high],'negative_stencil_reference_bounds':bounds,'limits':'Native4x4 lattice finite differences, strict interior fivepoint stencils. Numerical fold evidence, not rigorousglobalcaustic locus.'},'d_crop_exact_analytic':{'rectangle':[960,468,1120,550],'points':int(J.size),'Jxx_range':[float(J.min()),float(J.max())],'hxx_range':[float(hxx.min()),float(hxx.max())],'source_X_x_at_x960_top_center_bottom':[float(J[0,0]),float(J[542-468,0]),float(J[-1,0])],'limits':'Derivative of same actual height + Snell/background equation, never used to generate/render coordinates. Not a fitted warp.'},'frozen_alpha_exact_historical':bool(np.array_equal(alpha,old)),'raw_material_range':[float(M.min()),float(M.max())],'raw_complete_range':[float(C.min()),float(C.max())],'out_of_range_values':int(((M<0)|(M>1)).sum()+((C<0)|(C>1)).sum())}
(P/'saved-diagnostics.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
