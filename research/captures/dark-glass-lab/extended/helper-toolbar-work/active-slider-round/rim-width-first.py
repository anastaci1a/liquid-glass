"""ONE tiny existing neutral rim width neighborhood from current revision6."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');OUT=ROOT/'rim-width-first'
spec=importlib.util.spec_from_file_location('intake',ROOT/'intake.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from preview_size import dimensions
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def precision(s,old,new):
 row={};old=old.astype(float);new=new.astype(float);target=s.target_crop.astype(float)
 for k,mask in [('glass',s.valid),('rim',s.rim)]:
  e=old[mask]-target[mask];d=new[mask]-old[mask];row[k]=float(np.mean(2*e*d+d*d)*255**2)
 loss=.7*row['glass']+.3*row['rim'];row.update(weighted_loss_delta=loss,nonincreasing=bool(loss<=0));return row

def main():
 os.umask(0o002)
 if (OUT/'result.json').exists():print('Complete, no repeat');return
 if (OUT/'started.json').exists():raise RuntimeError('Inspect partial process first')
 intake=json.loads((ROOT/'intake-result.json').read_text());assert intake['fit_authorized_by_original_epoch_source']
 OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),budget='ONE rim_width neighborhood [-.00025,+.00025,-.000125,+.000125];max4nativepairs,stopfirststrictqualifier',rationale='Heavy dark inner rim feedback; change existing neutral lighting width only, fixed gamma/material/ordinaryblur/dispersion/geometry/source. Prior rev5 width/material study predates accepted revision6 jointgeometry/material, not compatible baseline. Old failures retained.'))
 native=json.loads((ROOT/'baseline-native-recipe.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];old=[np.load(ROOT/f'ref{i}-baseline-material.npy') for i in range(2)];trials=[];candidate=None
 noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
 for j,delta in enumerate([-.00025,.00025,-.000125,.000125]):
  q={**p,'rim_width':float(p['rim_width']+delta)};imgs=[s.render(q,co) for s in studies];scores=[m.score(s,q,a)[0] for s,a in zip(studies,imgs)];prec=[precision(s,o,a) for s,o,a in zip(studies,old,imgs)]
  row=dict(delta=delta,parameters=q,scores=scores,advisory_double=prec,guarded=all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['shadow']['rmse']<=b['shadow']['rmse'] for s,b in zip(scores,baseline)),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
  for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
  trials.append(row);save('trials.json',trials);print('NATIVE',delta,[s['E'] for s in scores],row['guarded'],'double',[v['weighted_loss_delta'] for v in prec],flush=True)
  if not(row['guarded'] and row['meaningful'] and all(v['nonincreasing'] for v in prec)):continue
  candidate=dict(parameters=q,material=co.tolist(),scores=scores,advisory_double=prec,source_proof='Unchanged transmission/RGB/reflection/context maps and kernels: reuse FRESH nativewhole+ALLscored proof from intake; rim_width lightingbasis only. Frozenestimatedsourceepoch retained.')
  save('candidate-native.json',candidate);public=json.loads((ROOT/'authoritative-revision6.json').read_text());public.update(parameters=q,scores=scores);save('candidate-public-native.json',public)
  for i,(s,a) in enumerate(zip(studies,imgs)):
   np.save(OUT/f'ref{i}-complete.npy',m.clean_composite(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=False)
   for name,array in zip(['target','baseline','candidate'],[s.target_crop,m.clean_composite(s,p,old[i]),m.clean_composite(s,q,a)]):cv2.imwrite(str(OUT/f'ref{i}-{name}-preview.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
   save(f'ref{i}-preview.json',dict(native=[s.crop[2]-s.crop[0],s.crop[3]-s.crop[1]],preview=list(size),native_size_preserved='Control nativewidth exceeds720cap, no enlargement/no4x'))
  break
 save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=0,source_epoch_unchanged=True,native_resolution_noise_floor=noise,limits='OriginalbothnativeE/glass/exteriorshadow strict; originalZEROforeground layers, no vector changes. Additional advisory residual nonregression not newscoreepoch. Onefamily,max4actualpairs, no shader/operator/source/dispersion/blur changes.'))
 print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
