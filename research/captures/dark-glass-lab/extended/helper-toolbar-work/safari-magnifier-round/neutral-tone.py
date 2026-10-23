"""PREPARED ONLY. Run only after primary foreground freeze; one tied neutral offset.
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
base=scores(baseline['material'],baseline['complete']);err=baseline['material'].astype(float)-s.target_crop.astype(float);mean=.7*err[s.valid].mean()+.3*err[s.rim].mean();direction=-np.sign(mean);trials=[]
# Sign from saved residual ONLY is a proposal surrogate, not an exact clipping-aware material Jacobian. Actual native renders decide.
for i,f in enumerate([1,.5,.25,.125]):
 if not direction:break
 delta=float(direction*.002*f);cc=co.copy();cc[3:6]+=delta;M=s.render(p,cc);C=composite(s,p,M);q=scores(M,C)
 checks={key:q[key]['rmse']<=base[key]['rmse'] for key in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<=base['E'],ssim=q['ssim']>=base['ssim'],advisory_f64_E=q['advisory_f64_E']<=base['advisory_f64_E']);progress=q['E']<base['E'] and base['advisory_f64_E']-q['advisory_f64_E']>64*np.finfo(float).eps*max(1,base['advisory_f64_E']);qualifies=all(checks.values()) and progress
 np.savez_compressed(args.output/f'trial-{i+1:02}.npz',material=M,complete=C);row=dict(trial=i+1,backtrack=f,common_offset=delta,scores=q,checks=checks,progress=bool(progress),qualifies=bool(qualifies));trials.append(row);(args.output/f'trial-{i+1:02}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if qualifies:
  candidate={**record,'material':cc.tolist(),'scores':q,'primary_acceptance':False,'primary_foreground_approval':args.primary_foreground_approval,'source_proof':'UNCHANGED source/rays/kernels/shape/AA/glyph/masks; accepted finite whole+ALLscored/postblur proof transfers; estimated source observed0 remains'};(args.output/'candidate-native.json').write_text(json.dumps(candidate,indent=2)+'\n');np.savez_compressed(args.output/'candidate-native.npz',material=M,complete=C,alpha=baseline['alpha']);A=np.uint8(np.rint(np.clip(s.target_crop,0,1)*255));B=np.uint8(np.rint(np.clip(C,0,1)*255));w=430;h=440;pair=Image.new('RGB',(862,504),'#222');draw=ImageDraw.Draw(pair);draw.text((8,20),'Safari SINGLE A',fill='white');draw.text((440,20),'Neutral-tone proposal',fill='white');pair.paste(Image.fromarray(A).resize((w,h),Image.Resampling.LANCZOS),(0,64));pair.paste(Image.fromarray(B).resize((w,h),Image.Resampling.LANCZOS),(432,64));pair.save(args.output/'candidate-comparison.png');break
result=dict(baseline=base,trials=trials,trial_budget=4,first_qualifier_stop=True,primary_foreground_approval=args.primary_foreground_approval,no_accepted_count=True,no_source_shape_blur_vector_change=True);(args.output/'review.json').write_text(json.dumps(result,indent=2)+'\n')
