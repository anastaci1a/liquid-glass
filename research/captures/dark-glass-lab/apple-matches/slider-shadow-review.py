"""Reusable exterior contact shadow and source-colored halo; no retained rim."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import least_squares
from reproduce import CASES,points
from render import case_geometry

root=Path('/evidence/apple-matches');folder=root/'curvature-contour';out=root/'pass04-candidates';out.mkdir(exist_ok=True)
case=CASES['slider'];source=cv2.imread(str(out/'slider-corrected-source.png'))[:,:,::-1].astype(np.float32)/255;target=cv2.imread(str(folder/'slider-target.png'))[:,:,::-1].astype(np.float32)/255
x0,y0,x1,y1=case['crop'];B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1];xs,ys,x,y=points(case);sd,*_=case_geometry(case,x,y)
mask=sd>1.;held=((xs.astype(int)//32+3*(ys.astype(int)//32))%4)==0;train=mask&~held;test=mask&held
body=B[sd<0].mean(0);paper=B[(sd>30)&(sd<60)].mean(0);delta=body-paper;chroma=delta-delta@np.array([.2126,.7152,.0722])
def shade(v,b,d):
 contact=v[0]*np.exp(-.5*(np.maximum(d-v[1],0)/v[2])**2)
 halo=v[3]*np.exp(-.5*(np.maximum(d,0)/v[4])**2)
 return np.clip(b*(1-contact[...,None])+halo[...,None]*chroma,0,1)
fit=least_squares(lambda v:(shade(v,B[train],sd[train])-T[train]).ravel(),[.08,.5,2,1,30],bounds=([0,0,.2,0,3],[.7,3,8,8,80]),max_nfev=300)
v=fit.x;pred=shade(v,B,sd);output=source.copy();output[y0:y1,x0:x1]=pred
metrics={key:float(np.sqrt(np.mean((pred[m]-T[m])**2))*255)for key,m in [('training_rmse',train),('withheld_rmse',test),('outer_8px_rmse',mask&(sd<8))]}
plain={key:float(np.sqrt(np.mean((B[m]-T[m])**2))*255)for key,m in [('training_rmse',train),('withheld_rmse',test),('outer_8px_rmse',mask&(sd<8))]}
f=dict(parameters=dict(contact_opacity=float(v[0]),contact_spread_px=float(v[1]),contact_sigma_px=float(v[2]),halo_strength=float(v[3]),halo_sigma_px=float(v[4])),source_derived_chroma=chroma.tolist(),scores=metrics,unmodified_background_scores=plain,formulas={'contact':'alpha_c*exp(-0.5*(max(d-spread,0)/sigma_c)^2)','halo':'strength*exp(-0.5*(max(d,0)/sigma_h)^2)*source_chroma','output':'clip(background*(1-contact)+halo,0,1)'},limits='Exterior-only approximation in encoded RGB; hue comes from mean source under lens minus neighboring page, projected off neutral luma. No recovered Apple lighting rig or physical scattering claim. Interior is composed separately; no reference exterior pixels need be retained in this crop.')
cv2.imwrite(str(out/'slider-generated-exterior.png'),np.uint8(np.clip(output,0,1)*255)[:,:,::-1]);(out/'slider-generated-exterior.json').write_text(json.dumps(f,indent=2)+'\n');print(json.dumps(f,indent=2),flush=True)
