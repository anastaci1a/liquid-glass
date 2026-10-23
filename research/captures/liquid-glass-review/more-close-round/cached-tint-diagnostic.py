"""Cached opaque neutral glyph diagnostic only, no candidate/body render/fit."""
import os,json,sys
from pathlib import Path
import numpy as np,cv2
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'latest-circle-baseline';D=R/'cached-glyph-diagnostic';D.mkdir();sys.path.insert(0,str(B/'code'))
from extended_fit import Study
from vector_foreground import coverage
s=Study(B/'inputs/a');z=np.load(B/'baseline-native-arrays.npz');layer=s.case['foreground_layers'][0];l,t,r,b=layer['box'];x0,y0,_,_=s.crop;sl=np.s_[t-y0:b-y0,l-x0:r-x0];A=coverage(s.folder,layer);M=z['material'][sl];C=z['complete'][sl];T=s.target_crop[sl];assert np.all(z['alpha'][sl]==1)
# Reconstruct original BLACK model output only; never invert target pixels into
# a coverage/matte. Canonical SVG coverage alone enters all predictions.
assert np.array_equal(C,np.asarray(M*(1-A[...,None]),dtype=C.dtype))
canonical_deep=A>=.995;observed_ink=T.mean(2)*255<90;distance=cv2.distanceTransform(observed_ink.astype(np.uint8),cv2.DIST_L2,5);observed_core=distance>=1.4;core=canonical_deep&observed_core
Y,X=np.mgrid[t:b,l:r];mx=(l+r-1)/2;my=(t+b-1)/2;dx=X-mx;dy=Y-my;center=(abs(dx)+abs(dy))<=2
positive=np.abs(dx-dy)<=np.abs(dx+dy);train=core&positive&~center;held=core&~positive&~center;intersection=core&center

def stats(mask):
 v=T[mask].astype(float)*255
 return dict(pixels=int(mask.sum()),mean_rgb=v.mean(0).tolist() if len(v) else None,median_rgb=np.median(v,axis=0).tolist() if len(v) else None,std_rgb=v.std(0).tolist() if len(v) else None,luma_mean=float(v.mean()) if len(v) else None,luma_pixel_std=float(v.mean(1).std()) if len(v) else None,gray_minmax=[float(v.mean(1).min()),float(v.mean(1).max())] if len(v) else None,maximum_channel_spread=float(np.ptp(v,axis=1).max()) if len(v) else None)
# One scalar estimate from ONE branch, evaluate other branch as held evidence.
# Fixed opaque fill; no joint opacity, shape, font, per-channel or pointwise law.
q=float(np.median(T[train].mean(1))) if train.any() else None
cohorts={'canonical_deep_ALL':canonical_deep,'observed_core_ALL':observed_core,'overlap_core_ALL':core,'tint_estimation_positive_branch':train,'held_negative_branch':held,'held_center':intersection,'partial_canonical_edge':(A>.005)&(A<.995),'observed_ink_outside_canonical_support':observed_ink&(A<=.005)}
rows={}
for name,m in cohorts.items():
 row=stats(m)
 if m.any():
  old=(C-T).astype(float)[m]*255;row['black_baseline_advisory_RGB_RMSE']=float(np.sqrt(np.mean(old**2)))
  if q is not None:
   # LOCAL algebraic diagnostic, not a native candidate/composite/render.
   local=M[m].astype(float)*(1-A[m,None].astype(float))+q*A[m,None].astype(float);err=(local-T[m])*255;row['ONE_proposed_gray_advisory_RGB_RMSE']=float(np.sqrt(np.mean(err**2)));row['ONE_proposed_gray_advisory_signed_RGB']=err.mean(0).tolist()
 rows[name]=row
supported=bool(q is not None and train.sum()>=4 and held.sum()>=4 and rows['overlap_core_ALL']['luma_pixel_std']<=4 and all(rows[n]['ONE_proposed_gray_advisory_RGB_RMSE']<rows[n]['black_baseline_advisory_RGB_RMSE'] for n in ['tint_estimation_positive_branch','held_negative_branch']) and np.ptp(np.asarray(rows['overlap_core_ALL']['mean_rgb']))<=10)
result=dict(stage='CACHED_GLYPH_DIAGNOSTIC_ONLY_NO_NATIVE_CANDIDATE',approval='f8d77b37-d189-41d6-bcbb-207baed8e5e6',proposed_foreground_model='Opaque uniform neutral fill q RGBtied; opacity1 and exact canonical SVG fixed. No input/source/body/map/rim/pose/mask change.',ONE_q_estimate=q,ONE_q_native255=q*255 if q is not None else None,uniform_deep_core_support=supported,criteria_declared='Canonical coverage>=.995; observed darkmask<90 thenL2core>=1.4 ONLY for diagnostics. Require>=4deepcore perdiagonal, corelumastd<=4nativelevels andRGBmeanspread<=10, improveheldcore vsblack. No screenshot-derived alpha/matte used or exported.',cohorts=rows,coverage_shape_separation='Residual at canonical-edge or observedinkoutside canonicalsupport persists independently of deep tint. Observed binary masks select diagnostics only; renderer uses unchanged ORIGINAL SVG coverage. No targetcoverage inversion.',limits='Single compressed1080p observation cannot prove physicalopacity versusfill/AA/PSF. Proposedopaquegray is an empirical foregroundmodel only, not identified Applecolor. Advisory local algebra not float32native candidate, gate or acceptance. No fullcandidate arrays/recipe rendered/exported, no newbody/source fit.',body_renders=0,candidate_evaluations=0,uniform_q_diagnostic_estimates=1,glyph_geometry_fits=0,accepted_count=0,baseline_acceptance_pending=True)
(D/'diagnostic.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
