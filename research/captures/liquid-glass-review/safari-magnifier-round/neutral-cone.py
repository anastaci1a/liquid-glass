import os,json,sys
from pathlib import Path
import numpy as np,cv2
from scipy.optimize import linprog
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');D=R/'neutral-guard-cone';os.umask(0o002);cv2.setNumThreads(1);sys.path.insert(0,str(R/'code'))
from extended_fit import Study
s=Study(R/'foreground-control/proposed-a');A=np.load(R/'foreground-control/proposed-baseline-native-arrays.npz');M=A['material'].astype(float);C=A['complete'].astype(float);T=s.target_crop.astype(float);rec=json.loads((R/'baseline-recipe.json').read_text());p=rec['parameters'];tr=json.loads((R/'neutral-offset-round1/review.json').read_text());base=tr['baseline'];assert not (D/'review.json').exists()
# EXACT saved finite secants; not recomputed derivatives/rays/renders. No raw native sample/light bases had been retained, so gain is explicitly a surrogate.
sec=[]
for i in [3,4]:
 q=tr['trials'][i-1];arr=np.load(R/f'neutral-offset-round1/trial-{i:02}.npz');h=q['common_offset'];sec.append(dict(h=h,material=(arr['material'].astype(float)-M)/h,complete=(arr['complete'].astype(float)-C)/h))
B=sec[-1]['material'];BC=sec[-1]['complete'];co=np.array(s.case['background_estimate']['coefficient_rgb']);proof=json.loads((R/'baseline-native.json').read_text())['source_proof'];l,t,r,b=proof['ray_bounds'];rr=proof['gaussian_3sigma_native_radius'];xs=[l-rr,(l+r)/2,r+rr];ys=[t-rr,(t+b)/2,b+rr];colors=[]
for x in xs:
 for y in ys:colors.append(np.maximum(np.array([1,(x-509)/100,(y-705)/100])@co,0)**p['gamma'])
center=np.maximum(co[0],0)**p['gamma'];colors.append(center)
masks={'glass':s.valid,'rim':s.rim,'held':s.held,'interior':s.valid&~s.rim,'glyph':A['glyph_mask'],'exterior':A['exterior_mask'],'full_visible_exterior':s.sd>0}
def ssim(M,deriv=None):
 # Analytic functional derivative of Study's native graymean SSIM; f64 arithmetic is diagnostic, not a gate epoch change.
 aM=M.mean(2)*255;bM=T.mean(2)*255;G=lambda q:cv2.GaussianBlur(q,(11,11),1.5);a=G(aM);b=G(bM);n1=2*a*b+6.5025;n2=2*(G(aM*bM)-a*b)+58.5225;d1=a*a+b*b+6.5025;d2=G(aM*aM)-a*a+G(bM*bM)-b*b+58.5225;safe=cv2.erode(s.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0;den=d1*d2;num=n1*n2
 if deriv is None:return float((num/den)[safe].mean())
 q=deriv.mean(2)*255;da=G(q);dn1=2*da*b;dn2=2*(G(q*bM)-da*b);dd1=2*a*da;dd2=2*G(aM*q)-2*a*da;ds=((dn1*n2+n1*dn2)*den-num*(dd1*d2+d1*dd2))/(den*den);return float(ds[safe].mean())
def gradients(sec,color):
 cols=[sec['material'],sec['material']*color];cc=[sec['complete'],sec['complete']*color];g={}
 for name,mask in masks.items():
  e=(C-T) if name in ['glyph','exterior','full_visible_exterior'] else (M-T);fields=cc if name in ['glyph','exterior','full_visible_exterior'] else cols;g[name]=[float(2*np.mean(e[mask]*d[mask])*255**2) for d in fields]
 g['E2']=(.7*np.array(g['glass'])+.3*np.array(g['rim'])).tolist();g['negative_ssim']=[-ssim(M,d) for d in cols];return g
rows=[];labels=[];cases=[]
for i,z in enumerate(sec):
 for j,color in enumerate(colors):
  g=gradients(z,color);cases.append(dict(bias_secant=z['h'],source_constant_rgb=color.tolist(),gradients=g))
  for name in list(masks)+['negative_ssim']:
   row=np.array(g[name]);norm=np.linalg.norm(row)
   if norm>0:rows.append(row/norm);labels.append([i,j,name])
g=gradients(sec[-1],center);objective=np.array(g['E2']);fit=linprog(objective,bounds=[(-.002,.002),(-.002,.002)],A_ub=np.array(rows),b_ub=np.zeros(len(rows)),method='highs');direction=fit.x if fit.success else np.zeros(2)
# No LP status counts as a pass. Report worst raw directional derivatives; predicted array metrics are MODELONLY.
violations=[]
for case in cases:
 for name,grad in case['gradients'].items():
  v=float(np.dot(grad,direction))
  if name!='E2' and v>0:violations.append(dict(name=name,directional_derivative=v,source=case['source_constant_rgb'],bias_secant=case['bias_secant']))
MP=M+direction[0]*B+direction[1]*(B*center);CP=C+direction[0]*BC+direction[1]*(BC*center);pred={}
for name,mask in masks.items():
 val=CP if name in ['glyph','exterior','full_visible_exterior'] else MP;pred[name]=float(np.sqrt(np.mean(((val-T)[mask]*255)**2)))
pred['E']=float(np.sqrt(.7*pred['glass']**2+.3*pred['rim']**2));pred['ssim_f64_surrogate']=ssim(MP);pred['baseline_ssim_f64_functional']=ssim(M)
step=np.zeros(23);step[3:6]=direction[0];step[:3]=step[-3:]=direction[1]
result=dict(kind='PREDICTED ONLY 2D neutralbias/globalneutralgain guardcone',accepted_count=0,native_render_count=0,native_trial_count=0,raw_native_shading_bases_retained=False,bias_basis='Reused actual saved native finite secants -.0005 and-.00025; clipping/postblur included in these measured finite changes, not exact differential',gain_basis='SOURCE-CONSTANT proxy times savedbiasbasis; sourceRGB**gamma atcenter and9frozenmap/kernel-domaincorners, NOT actualnativegainJacobian',variables=['delta_bias_tied_co3:6','delta_gain_tied_co0:3_ANDco20:23'],bounds=[.002,.002],center_source_rgb=center.tolist(),source_rgb_proxy_cases=[c.tolist() for c in colors],secant_stability=dict(material_relative=float(np.linalg.norm(sec[0]['material']-sec[1]['material'])/max(np.linalg.norm(B),1e-30)),complete_relative=float(np.linalg.norm(sec[0]['complete']-sec[1]['complete'])/max(np.linalg.norm(BC),1e-30))),linear_program=dict(success=bool(fit.success),message=fit.message,objective_directional_E2=float(objective@direction),direction=direction.tolist(),strict_positive_predicted_guard_count=len(violations),largest_guard_violation=max((q['directional_derivative'] for q in violations),default=0)),coefficient_delta=step.tolist(),center_predicted_guard_values=pred,gradient_cases=cases,predicted_violations=violations,limitations='Not a native score/pass. Exact raw native shading basis was notsaved; gainaxis sourceconstant proxy may miss spatialsourcevariation, nonlinear gamma/clip and blur. Multipleconstant cases do not rigorously cover arbitrary spatialcorrelation. LP feasibility/tiny predicted gains require primary review and originalactualnative guard tests. Frozen source estimatedobserved0/Bpending. No changedmap/source/shape/blur/foreground/nativeepoch.',next='Propose this bounded vector ONLY if predictedconstraints and improvement survive inspection; otherwise no supported direction and no native fit. Then authorizedPLUSindependentinput/pose/FG/transferreview.')
(D/'review.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(D/'saved-bias-basis-and-gain-proxy.npz',bias_material=B,bias_complete=BC,gain_material_proxy=B*center,gain_complete_proxy=BC*center,predicted_material=MP,predicted_complete=CP);print(json.dumps({k:result[k] for k in ['secant_stability','linear_program','coefficient_delta','center_predicted_guard_values']}),flush=True)
