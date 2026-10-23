"""ONLY saved actual native first differences; no new optical renderer/probe."""
import json,os
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');D=R/'native-bias-co8-cone';D.mkdir();os.umask(0o002);A=np.load(R/'foreground-control/proposed-baseline-native-arrays.npz');M=A['material'].astype(float);C=A['complete'].astype(float)
from PIL import Image
case=json.loads((R/'foreground-control/proposed-a/case.json').read_text());x0,y0,x1,y1=case['crop'];T=np.asarray(Image.open(R/'foreground-control/proposed-a/target.png').convert('RGB')).astype(np.float32)/255;T=T[y0:y1,x0:x1].astype(float);xx,yy=np.meshgrid(np.arange(x0,x1),np.arange(y0,y1));sd=(np.hypot(xx-case['center'][0],yy-case['center'][1])-case['radius'])/case['radius'];masks={'glass':A['glass_mask'],'rim':A['rim_mask'],'held':A['held_mask'],'interior':A['glass_mask']&~A['rim_mask'],'glyph':A['glyph_mask'],'exterior':A['exterior_mask'],'full_visible_exterior':sd>0}
reviewb=json.loads((R/'neutral-offset-round1/review.json').read_text());reviewc=json.loads((R/'directional-thin-round1/review.json').read_text());base=reviewb['baseline'];assert reviewb['baseline']==reviewc['baseline'];cases=[];fields={}
for i in [3,4]:
 ab=np.load(R/f'neutral-offset-round1/trial-{i:02}.npz');ac=np.load(R/f'directional-thin-round1/trial-{i:02}.npz');hb=reviewb['trials'][i-1]['common_offset'];hc=reviewc['trials'][i-1]['co8_delta'];DB=(ab['material'].astype(float)-M)/hb;DC=(ac['material'].astype(float)-M)/hc;CB=(ab['complete'].astype(float)-C)/hb;CC=(ac['complete'].astype(float)-C)/hc;g={};metricsec={}
 for name,mask in masks.items():
  complete=name in ['glyph','exterior','full_visible_exterior'];e=(C-T) if complete else (M-T);bs=CB if complete else DB;cs=CC if complete else DC;g[name]=[float(2*np.mean(e[mask]*bs[mask])*255**2),float(2*np.mean(e[mask]*cs[mask])*255**2)]
  k={'exterior':'exterior','full_visible_exterior':'full_visible_exterior','glyph':'glyph'}.get(name,name);metricsec[name]=[(reviewb['trials'][i-1]['scores'][k]['rmse']**2-base[k]['rmse']**2)/hb,(reviewc['trials'][i-1]['scores'][k]['rmse']**2-base[k]['rmse']**2)/hc]
 g['negative_ssim']=[-(reviewb['trials'][i-1]['scores']['ssim']-base['ssim'])/hb,-(reviewc['trials'][i-1]['scores']['ssim']-base['ssim'])/hc];g['E2']=(.7*np.array(g['glass'])+.3*np.array(g['rim'])).tolist();cases.append(dict(saved_trial=i,secant_bias=hb,secant_co8=hc,field_gradient=g,original_f32_metric_finite_secants=metricsec));fields[f'bias_M_{i}']=DB;fields[f'co8_M_{i}']=DC;fields[f'bias_C_{i}']=CB;fields[f'co8_C_{i}']=CC
rows=[]
for z in cases:
 for name,g in z['field_gradient'].items():
  if name=='E2':continue
  row=np.array(g);n=np.linalg.norm(row)
  if n:rows.append(row/n)
G=np.array(rows);objective=np.array(cases[-1]['field_gradient']['E2']);lp=linprog(objective,A_ub=G,b_ub=np.zeros(len(G)),bounds=[(-.00025,.00025)]*2,method='highs');step=lp.x if lp.success else np.zeros(2)
# Three explicit local-model constraints prove zero cone within this FINITE-SECANT linearization, not the true nonlinear renderer.
labels=['glass','rim','exterior'];H=np.array([cases[-1]['field_gradient'][n] for n in labels]);Hn=H/np.linalg.norm(H,axis=1)[:,None];w=np.linalg.solve(np.r_[Hn.T,np.ones((1,3))],np.array([0.,0.,1.]));certificate=dict(constraints=labels,normalized_rows=Hn.tolist(),positive_weights=w.tolist(),weighted_row_sum=(w@Hn).tolist(),rank=int(np.linalg.matrix_rank(Hn)),all_weights_positive=bool((w>0).all()),meaning='In THISsavedfinite-secant first-order model, strictlypositive combination of3rank2guardnormals iszero; all3nonregimplieszero direction. Notglobalnativeimpossibilityproof andnotexactdifferentialatclippingkinks.')
q=dict(status='NO_SUPPORTED_JOINT_DIRECTION_NO_NEW_NATIVE_TRIAL',variables=['tiedneutralbiasco3:6','neutraldirectionallightco8'],global_bounds=[.002,.002],finite_trust_box=[.00025,.00025],baseline=base,cases=cases,linear_program=dict(success=bool(lp.success),step=step.tolist(),E2_directional_change=float(objective@step),zero_step=bool(np.array_equal(step,np.zeros(2)))),local_zero_cone_certificate=certificate,native_joint_trials_used=0,maximum_native_joint_trials_authorized=2,optical_renders=0,accepted_count=0,source_map_blur_shape_glyph_shadow_masks_unchanged=True,limitations='Actualsavednative finite differences include clipping/AA/postblur in observedchanges; secants are not an exact two-sidedJacobian andSSIMf32finite derivatives may be noisy. Clear glass/rim/exterior conflict alone forceszero in model, independentSSIM. No weakwaiver or promiseofglobalinfeasibility. Do not broadenfamily/sweep.',recommendation='Stop this local magnifier material settlement with all8actualfailures preserved,count0. Recommend rotation/source-ledfreshcontrol ratherthanmoreunverifiedsurrogates; no new intake oroperator without leadassignment. Exactbasisinstrumentation beyondsaved2D only ifprimary separatelyfindscone inconclusive, not automaticallyactivated.')
(D/'review.json').write_text(json.dumps(q,indent=2)+'\n');np.savez_compressed(D/'saved-native-derivative-fields.npz',**fields);print(json.dumps(q),flush=True)
