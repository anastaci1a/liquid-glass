"""Rank-aware solution of the SAME authorized joint ambient0/commonco6 model."""
import importlib.util,json,os
from pathlib import Path
import numpy as np,cv2
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');PARENT=ROOT/'pass08-ambient-neutral';OUT=PARENT/'shared-nullspace'
spec=importlib.util.spec_from_file_location('h',ROOT/'rim-width-first.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);m=h.m
from material_context import effective
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 os.umask(0o002)
 if (OUT/'result.json').exists():print('Same-model rankcontrol complete; no rerun');return
 if (OUT/'started.json').exists():raise RuntimeError('Inspect partials/process first')
 OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),authority='SAME alreadyauthorized jointambient0/commonco6 local quadratic, not newfamily/model/derivative',reason='Generic SLSQP returned0 at opposite collinear Aglass/exterior constraints. Solve exact existing shared-basis nullspace; preserve solver0 as model-numerics evidence.',budget='Jointfamilyremainingbudget max4nativebacktracks, spent0 sofar; same.002ambient/.0005co6bounds'))
 prior=json.loads((PARENT/'result.json').read_text());assert len(prior['phases'])==2 and all(not v['trials'] for v in prior['phases'])
 controls=json.loads((PARENT/'analytic-controls.json').read_text());forms=json.loads((PARENT/'forms.json').read_text());native=json.loads((ROOT/'pass07-recentered-saved/candidate-native.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];old=[np.load(ROOT/f'pass07-recentered-saved/trial1-ref{i}-material.npy') for i in range(2)]
 kA=controls[0]['kappa'];kB=controls[1]['kappa'];direction=np.array([1.,-kA*.002/.0005]);limit=1/max(abs(direction));gb=np.array(forms[1]['loss']['g']);Hb=np.array(forms[1]['loss']['H']);g=float(gb@direction);H=float(direction@Hb@direction);u=float(np.clip(-g/H,-limit,limit)) if H>0 else float(limit if g<0 else -limit)
 # A effective neutral coefficient is invariant by construction, independent
 # of target/crop pixels; B constraints restrict one shared-law coordinate.
 for key in ['loss','glass','shadow']:
  gg=float(np.array(forms[1][key]['g'])@direction);hh=float(direction@np.array(forms[1][key]['H'])@direction)
  if u>0 and gg>=0:u=0.
  elif u>0 and hh>0:u=min(u,-2*gg/hh)
  elif u<0 and gg<=0:u=0.
  elif u<0 and hh>0:u=max(u,-2*gg/hh)
 v=u*direction;da=float(.002*v[0]);dc=float(.0005*v[1]);save('proposal.json',dict(delta_ambient0=da,delta_co6=dc,normalized_direction=direction.tolist(),bounded_coordinate=u,source_kappa_A=kA,source_kappa_B=kB,B_effective_co6_delta=(kB-kA)*da,A_effective_co6_delta_symbolic=0,model_quadratic_B_loss_delta=float(2*gb@v+v@Hb@v),method='Closed-form one-coordinate restriction of SAME jointquadratic along exact A effective-co6 invariant. No newsourceweights/targetterms/per-backgroundcoefficients/optimizerfamily. Generic solver0retained.'))
 print('SAME_MODEL_NULL',da,dc,'Bco6',(kB-kA)*da,flush=True);trials=[];candidate=None
 noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
 if u!=0:
  for j,t in enumerate([1.,.5,.25,.125]):
   ambient=list(p['ambient_rim_response']);ambient[0]+=t*da;q={**p,'ambient_rim_response':ambient};new=co.copy();new[6]+=t*dc
   effdiff=[(effective(s,q,new)-effective(s,p,co)).tolist() for s in studies];imgs=[s.render(q,new) for s in studies];scores=[m.score(s,q,a)[0] for s,a in zip(studies,imgs)];prec=[h.precision(s,o,a) for s,o,a in zip(studies,old,imgs)]
   row=dict(factor=t,parameters=q,material=new.tolist(),effective_material_differences=effdiff,scores=scores,advisory_double=prec,A_max_native_pixel_difference=float(abs(imgs[0]-old[0]).max()),guarded=all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['shadow']['rmse']<=b['shadow']['rmse'] for s,b in zip(scores,baseline)),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
   for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
   trials.append(row);save('trials.json',trials);print('NATIVE',t,[s['E'] for s in scores],row['guarded'],'Amax',row['A_max_native_pixel_difference'],flush=True)
   if not(row['guarded'] and row['meaningful'] and all(x['nonincreasing'] for x in prec)):continue
   candidate=dict(parameters=q,material=new.tolist(),scores=scores,advisory_double=prec,source_proof='TRANSFER accepted08 whole/ALLscored base/RGB/reflection/context proof: ONLYambient0/commonco6, existing material_context.affine/source-mean fixed; all rays/kernels/grid/input/shape/masks unchanged. Defined1/observed0 originalmodeledhiddenRGB, not photographictruth.')
   save('candidate-native.json',candidate);save('candidate-public-native.json',dict(parameters=q,material=new.tolist(),scores=scores,method='ONEexistingjointambient0+commonneutralco6 compensation, exactcurrentstateanalytic sharedbasis and same-model invariantconstraint',provenance=dict(baseline='acceptedpublic08',newround_accepted_count_before=2,primary_accepted=False,per_background_coefficients=False)))
   for i,(s,a) in enumerate(zip(studies,imgs)):
    np.save(OUT/f'ref{i}-complete.npy',m.clean_composite(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=h.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=False)
    for name,array in zip(['target','baseline','candidate'],[s.target_crop,m.clean_composite(s,p,old[i]),m.clean_composite(s,q,a)]):cv2.imwrite(str(OUT/f'ref{i}-{name}-preview.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
   break
 save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=2,isolated_model_and_generic_joint_solver='Original PARENT artifacts unchanged: bothzero/no nativebacktracks. This is SAMEjointmodel rank-aware closedform handling, not a new fitfamily.',source_proof_transferred=True,limits='StrictoriginalpairedE/glass/fixedexterior + advisoryresidual, source/shape/masks/epoch fixed, no publicedit. Target-independent sourceweightlaw retained; numerical gains conditionalonestimatedhiddenRGB. Stopfirstqualifier.'))
 print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
