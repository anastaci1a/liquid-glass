"""PREPARED ONLY. Run only after primary foreground freeze; one co8 directional thin-light coefficient.
Inputs explicitly name the approved baseline. No source/shape/map/blur/vector fit.
"""
import argparse,sys,json,os
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--arrays',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--primary-foreground-approval',required=True,help='Exact lead approval message ID, recorded for review');args=ap.parse_args();R=args.root;assert not args.output.exists(),'Never duplicate/overwrite trials';args.output.mkdir(parents=True);os.umask(0o002);sys.path.insert(0,str(R/'code'))
import cv2
cv2.setNumThreads(1)
from PIL import Image,ImageDraw
from extended_fit import Study
from vector_revision import composite
s=Study(args.input);record=json.loads(args.recipe.read_text());p=record['parameters'];co=np.asarray(record['material']);baseline=np.load(args.arrays)
def scores(M,C):
 q=s.scores(M);q['E']=float(np.sqrt(q['loss']));d=(M.astype(np.float64)-s.target_crop.astype(np.float64))*255;q['advisory_f64_E']=float(np.sqrt(.7*np.mean(d[s.valid]**2)+.3*np.mean(d[s.rim]**2)))
 for key,mask in [('glyph',baseline['glyph_mask']),('exterior',baseline['exterior_mask']),('full_visible_exterior',s.sd>0)]:q[key]=dict(pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2))))
 return q
base=scores(baseline['material'],baseline['complete']);err=baseline['material'].astype(float)-s.target_crop.astype(float)
sd,nx,ny=s.shape(s.x,s.y,p)[-1];depth=np.maximum(-sd,0);D=np.exp(-(depth/p['thin_width'])**2)*ny
if s.kernel_sigma(p,'post_sigma')>.001:D=cv2.GaussianBlur(D,(0,0),s.kernel_sigma(p,'post_sigma'))
DD=np.repeat(D[...,None],3,axis=2);slope=.7*2*np.mean(err[s.valid]*DD[s.valid])+.3*2*np.mean(err[s.rim]*DD[s.rim]);direction=-np.sign(slope);trials=[]
(args.output/'sign-proposal.json').write_text(json.dumps(dict(assignment='158bae53-e566-46c6-b50b-c8187cb1cac7',basis='Existing thin*ny analytic NATIVE-CENTER +postblur surrogate, NOT exact clipped2x2shading derivative; rawsamplebasis notretained',selected_sign=float(direction),E2_derivative_proxy=float(slope*255**2),opposite_delta=float(-direction*.002),opposite_predicted_E2_change=float(-direction*.002*slope*255**2),no_opposite_native_probe=True),indent=2)+'\n')
# Sign from saved residual ONLY is a proposal surrogate, not an exact clipping-aware material Jacobian. Actual native renders decide.
for i,f in enumerate([1,.5,.25,.125]):
 if not direction:break
 delta=float(direction*.002*f);cc=co.copy();cc[8]+=delta;M=s.render(p,cc);C=composite(s,p,M);q=scores(M,C)
 checks={key:q[key]['rmse']<=base[key]['rmse'] for key in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<=base['E'],ssim=q['ssim']>=base['ssim'],advisory_f64_E=q['advisory_f64_E']<=base['advisory_f64_E']);progress=q['E']<base['E'] and base['advisory_f64_E']-q['advisory_f64_E']>64*np.finfo(float).eps*max(1,base['advisory_f64_E']);qualifies=all(checks.values()) and progress
 np.savez_compressed(args.output/f'trial-{i+1:02}.npz',material=M,complete=C);row=dict(trial=i+1,backtrack=f,co8_delta=delta,scores=q,checks=checks,progress=bool(progress),qualifies=bool(qualifies));trials.append(row);(args.output/f'trial-{i+1:02}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if qualifies:
  candidate={**record,'material':cc.tolist(),'scores':q,'primary_acceptance':False,'primary_foreground_approval':args.primary_foreground_approval,'primary_directional_assignment':'158bae53-e566-46c6-b50b-c8187cb1cac7','source_proof':'UNCHANGED source/rays/kernels/shape/AA/glyph/masks; accepted finite whole+ALLscored/postblur proof transfers; estimated source observed0 remains'};(args.output/'candidate-native.json').write_text(json.dumps(candidate,indent=2)+'\n');np.savez_compressed(args.output/'candidate-native.npz',material=M,complete=C,alpha=baseline['alpha']);A=np.uint8(np.rint(np.clip(s.target_crop,0,1)*255));B=np.uint8(np.rint(np.clip(C,0,1)*255));w=430;h=440;pair=Image.new('RGB',(862,504),'#222');draw=ImageDraw.Draw(pair);draw.text((8,20),'Safari SINGLE A',fill='white');draw.text((440,20),'Directional thin-light proposal',fill='white');pair.paste(Image.fromarray(A).resize((w,h),Image.Resampling.LANCZOS),(0,64));pair.paste(Image.fromarray(B).resize((w,h),Image.Resampling.LANCZOS),(432,64));pair.save(args.output/'candidate-comparison.png');break
result=dict(baseline=base,trials=trials,trial_budget=4,first_qualifier_stop=True,primary_foreground_approval=args.primary_foreground_approval,no_accepted_count=True,no_source_shape_blur_vector_change=True,only_co8_changed=True);(args.output/'review.json').write_text(json.dumps(result,indent=2)+'\n')
