import os,json,sys,datetime
from pathlib import Path
import numpy as np,cv2
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'epoch02';D=B/'final-ab-feasibility';D.mkdir();sys.path.insert(0,str(R/'latest-circle-baseline/code'));from extended_fit import Study;from vector_foreground import coverage
s=Study(B/'inputs/a');z=np.load(B/'gray-pass01/candidate-native.npz');m=np.load(B/'baseline-arrays.npz');base=json.loads((B/'gray-pass01/candidate-native.json').read_text())['scores'];direction=np.load(R/'rim-amplitude-round1/cached-direction.npz')['d_material_da'].astype(float);J0=.025*direction;J1=-.0005*np.ones_like(J0);J=np.stack([J0,J1],axis=-1);e=z['material'].astype(float)-s.target_crop.astype(float)
# u=(a-.125)/.025 >=0, k=(.07500000000000001-b)/.0005 >=0.
# C is affine in M under frozen shape/foreground/shadow; no source queries.
factor=z['alpha'].astype(float).copy();layer=s.case['foreground_layers'][0];A=coverage(s.folder,layer);l,t,r,b=layer['box'];factor[t-160:b-160,l-720:r-720]*=1-A.astype(float);JC=J*factor[...,None,None];ec=z['complete'].astype(float)-s.target_crop.astype(float);quadratics={}
for label,key,err,j in [('glass','glass_mask',e,J),('rim','rim_mask',e,J),('held','held_mask',e,J),('interior','interior_mask',e,J),('glyph','glyph_mask',ec,JC),('exterior','exterior_mask',ec,JC),('full_visible_exterior','full_visible_exterior_mask',ec,JC)]:
 mask=m[key];v=j[mask].reshape(-1,2)*255;ee=err[mask].reshape(-1)*255;g=2*np.mean(ee[:,None]*v,axis=0);H=2*(v.T@v)/len(ee);quadratics[label]=dict(pixels=int(mask.sum()),gradient_MSE_normalized_uk=g.tolist(),Hessian_MSE_normalized_uk=H.tolist(),baseline_MSE=float(np.mean(ee**2)),model='Fixed-source unclipped-affine material/foreground mean-square; nativefloat32operationorder still scores.')
quadratics['E_squared']=dict(gradient_MSE_normalized_uk=(.7*np.array(quadratics['glass']['gradient_MSE_normalized_uk'])+.3*np.array(quadratics['rim']['gradient_MSE_normalized_uk'])).tolist())
# Finite saved SSIM sensitivities: NEVER call them exact native derivatives.
amp=json.loads((B/'rim-amplitude-pass02/cached-review.json').read_text())['predictions'];coupled=json.loads((B/'coupled-pass02/cached-review.json').read_text())['predictions'];s0=base['ssim'];amp_slopes=[]
for row in amp:
 u=(row['amplitude']-.125)/.025;amp_slopes.append(dict(u=u,k=0,delta_SSIM=row['prediction_ONLY']['ssim']-s0,secant_u=(row['prediction_ONLY']['ssim']-s0)/u))
su=amp_slopes[0]['secant_u'];bias_slopes=[]
for row in coupled:
 u=(row['amplitude']-.125)/.025;k=(.07500000000000001-row['bias'])/.0005;delta=row['prediction_ONLY']['ssim']-s0;bias_slopes.append(dict(u=u,k=k,delta_SSIM=delta,conditional_secant_k_after_linear_amp=(delta-su*u)/k))
# MSE linear guard-cone interval for k/u, with u>=0,k>=0.
lo=0.;hi=float('inf');cone=[]
for label,q in quadratics.items():
 ga,gk=q['gradient_MSE_normalized_uk'];bound=None
 if gk>0:hi=min(hi,-ga/gk);bound='upper'
 elif gk<0:lo=max(lo,-ga/gk);bound='lower'
 elif ga>0:hi=-1.;bound='no_positive_u'
 cone.append(dict(guard=label,gradient=[ga,gk],ratio_bound_type=bound))
ssim_block=all(q['secant_u']<0 for q in amp_slopes) and all(q['conditional_secant_k_after_linear_amp']<0 for q in bias_slopes)
report=dict(stage='FEASIBILITY_FIRST_STOP_BEFORE_OPTIMIZER',assignment='e86cfb75-31e4-4897-9adb-d78f1c8f5fb1',completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),parameters=dict(u='(a-.125)/.025 in[0,1]',k='(.07500000000000001-b)/.0005 in[0,1]',width=.028,gray=.24982225414468506),MSE_quadratics=quadratics,MSE_linear_guard_cone=dict(ratio_k_over_u_lower=lo,ratio_k_over_u_upper=hi if np.isfinite(hi) else None,details=cone),saved_SSIM_secants_amplitude=amp_slopes,saved_SSIM_conditional_bias_secants=bias_slopes,concrete_blocking_guard='SSIM',no_common_direction_in_saved_response_first_order_model=bool(ssim_block),decision='Stop beforeoptimizer: all saved bounded amplitude secants and inferred negative-bias sensitivities reduce SSIM. In nonnegative(u,k) quadrant this empirical local SSIM model has no nonzero feasible tangent; original SSIM guard unchanged.',SSIM_limitations='Finite secants from frozen float32guard, not exact derivatives or rigorous globalmonotonicity. Conditionalbias estimates disagree in magnitude, indicating nonlinear/numerical/trust uncertainty; cannot exclude finitecurvature/interactions elsewhere in bounds. No claim globalmaterial infeasibility or actualnative failure. Do not chase dead/uncertain directions or replace SSIM.',new_full_guard_evaluations=0,budget_max=30,optimizer_calls=0,new_body_renders=0,new_source_or_field_queries=0,foreground_coverage_reused_not_refitted=True,count=1,old_failed_points_unchanged=True)
assert ssim_block;(D/'review.json').write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(D/'analytic-normalized-J.npz',dM_du=J0,dM_dk=J1,foreground_source_fixed_factor=factor);print(json.dumps(report),flush=True)
