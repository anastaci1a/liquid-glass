"""Saved arrays only. Fixed advisory crops + neutral/luma/chroma components; no render/fit."""
import os,sys,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');D=R/'saved-residual-review';D.mkdir();os.umask(0o002);cv2.setNumThreads(1)
# Declare/freeze original-native rectangles before inspecting residual statistics. No score mask changes.
crops={'upper_rim':[451,628,568,658],'lower_rim':[451,752,568,784],'left_rim':[433,661,462,749],'right_rim':[558,661,588,749],'core_glyph':[465,661,551,747]};(D/'crops.json').write_text(json.dumps(crops,indent=2)+'\n');sys.path.insert(0,str(R/'code'));from extended_fit import Study
s=Study(R/'foreground-control/proposed-a');base=np.load(R/'foreground-control/proposed-baseline-native-arrays.npz');T=s.target_crop;M=base['material'];C=base['complete'];trials=json.loads((R/'neutral-offset-round1/review.json').read_text());rows=[]
def met(error,m):
 if not m.any():return None
 e=error[m].astype(float)*255;Y=e@np.array([.2126,.7152,.0722]);ch=e-Y[:,None];return dict(pixels=int(m.sum()),rgb_rmse=float(np.sqrt(np.mean(e**2))),luma_rmse=float(np.sqrt(np.mean(Y**2))),chroma_rmse=float(np.sqrt(np.mean(ch**2))),signed_rgb=e.mean(0).tolist(),signed_luma=float(Y.mean()),signed_chroma=ch.mean(0).tolist())
x0,y0,x1,y1=s.crop;yy,xx=np.mgrid[y0:y1,x0:x1]
for name,(a,b,c,d) in crops.items():
 mask=(xx>=a)&(xx<c)&(yy>=b)&(yy<d);row=dict(name=name,rect=[a,b,c,d],baseline_complete=met(C-T,mask),baseline_glass=met(M-T,mask&s.valid),trials=[])
 for q in trials['trials']:
  arr=np.load(R/f"neutral-offset-round1/trial-{q['trial']:02}.npz");row['trials'].append(dict(trial=q['trial'],common_offset=q['common_offset'],complete=met(arr['complete']-T,mask),glass=met(arr['material']-T,mask&s.valid)))
 rows.append(row)
components={}
for name,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim),('foreground',base['glyph_mask']),('exterior',base['exterior_mask'])]:components[name]=met((C if name in ['foreground','exterior'] else M)-T,mask)
# Existing geometry/material core basis, evaluated analytically from frozen signed depth. This is not a new optical evaluation.
d=np.maximum(-s.sd,0);z=np.clip(d/.3,0,1);core=z**3*(z*(6*z-15)+10);e=(M-T).astype(float);bins=[]
for lo,hi in [(0,.05),(.05,.2),(.2,.3),(.3,1.01)]:
 mask=s.valid&(d>=lo)&(d<hi);bins.append(dict(depth=[lo,hi],residual=met(e,mask),mean_core_weight=float(core[mask].mean()) if mask.any() else None))
# Sign-support comparator only, not an actual Jacobian: common core gain approximately weighs sourcegray*core, clipping and outputpostblur still need native confirmation.
proxy={}
for name,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim)]:proxy[name]=dict(residual_dot_core=float(np.mean(e[mask]*core[mask,None])),residual_dot_constant=float(e[mask].mean()))

# Additional source-gray weighted sign controls, still saved-array/analytic only.
rec=json.loads((R/'baseline-recipe.json').read_text());rgb=np.array(s.case['background_estimate']['coefficient_rgb'][0])**rec['parameters']['gamma'];gainproxy={}
for name,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim)]:gainproxy[name]=dict(neutral_outer_gain_dot_proxy=float(np.mean(e[mask]*((1-core[mask,None])*rgb))),neutral_core_gain_dot_proxy=float(np.mean(e[mask]*(core[mask,None]*rgb))))
ec=C.astype(float)-T.astype(float);em=base['exterior_mask'];exteriorproxy=float(np.mean(ec[em]*(base['alpha'][em,None]*(1-core[em,None])*rgb)))
result=dict(kind='SAVED_NATIVE advisory residual inventory, no fit/render/source change',crops=rows,components=components,depth_bins=bins,core_gain_sign_surrogate=proxy,limitations='Estimated low-frequency source vs tone/light/shadow remain confounded. No refraction, ordinaryblur or dispersion identification. Proxy uses analytic depth weight but ignores native clipped subrays/postblur, not an exact Jacobian or feasible-step proof. Crop diagnostics never score/fit masks.',next_proposal='ONE common existing CORE RGB gain co20:23 direction, tied neutral delta<=.002 if core/interior residual supports lowering; rim/core opposition may permit core-weighted change where constantoffset failed. No sweep or actualfit authorized until primary review; full held/SSIM/glyph/exterior guards may still block.')
result['neutral_gain_color_weighted_surrogate']=gainproxy;result['exterior_outer_gain_dot_surrogate']=exteriorproxy
result['next_proposal']='NO isolatedneutralgain supportedacrossallguards: outergainnegative predicts exteriorworse; coregainnegative predicts rim/heldworse. Request one existingdirectionalthin-lightco8control onlyifprimaryauthorizes; upper/lower signedglass opposition is evidence, exteriorcouplingremainsrisk.'
result['prior_core_only_note']='Core-only decrement has wrong predicted sign forrim andheld; no nativeprobe'
result['proposal_status']='NO_NEUTRAL_GAIN_FIT_JUSTIFIED; next family request only'
(D/'review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(components=components,depth_bins=bins,core_gain_sign_surrogate=proxy)),flush=True)
# Native crop evidence ONLY, fixed full native215x220 arrays. Scale presentation430 per side permitted, no optical rerender.
can=Image.new('RGB',(3*430+4,504),'#222');draw=ImageDraw.Draw(can)
for i,(im,title) in enumerate([(T,'Reference'),(C,'Accepted input baseline'),(np.load(R/'neutral-offset-round1/trial-02.npz')['complete'],'Rejected -.001 offset')]):
 tile=Image.fromarray(np.uint8(np.rint(np.clip(im,0,1)*255))).resize((430,440),Image.Resampling.LANCZOS);dr=ImageDraw.Draw(tile)
 for name,(a,b,c,d) in crops.items():dr.rectangle(((a-x0)*2,(b-y0)*2,(c-x0)*2-1,(d-y0)*2-1),outline='#ffcc33',width=1)
 can.paste(tile,(i*432,64));draw.text((i*432+6,20),title,fill='white')
can.save(D/'fixed-crop-sheet.png')
