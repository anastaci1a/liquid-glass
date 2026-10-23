"""ONE authorized neutral-additive family g1,bRGBtied. Max4nativebacktracks.
Originalsettledmap/render/shade output unchanged; observational clipcounters only.
"""
import os,json,copy,sys
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
R=Path('/evidence/extended/helper-toolbar-work/flower-next-round');B=R/'neutral-playback-baseline';P=R/'neutral-additive-round2';D=R/'neutral-additive-round3';D.mkdir();os.umask(0o002);cv2.setNumThreads(1);sys.path.insert(0,str(B/'code'))
from extended_fit import Study
import settled
from vector_revision import composite
s=Study(B/'inputs/a');rec=json.loads((P/'candidate-native.json').read_text());p0=rec['preset'];a=np.load(B/'baseline-native-arrays.npz');base=json.loads((B/'baseline-native.json').read_text())['scores'];assert np.array_equal(s.valid,a['glass_mask']);assert np.array_equal(s.rim,a['rim_mask'])
def save(n,v):(D/n).write_text(json.dumps(v,indent=2)+'\n')
def metrics(M,C):
 q=s.scores(M);q['E']=float(np.sqrt(q['loss']));err=(M.astype(float)-s.target_crop.astype(float))*255;q['advisory_f64_E']=float(np.sqrt(.7*np.mean(err[s.valid]**2)+.3*np.mean(err[s.rim]**2)))
 for n,k in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=a[k];q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
 return q
a=dict(a);previous=np.load(P/'candidate-native.npz');a.update({k:previous[k] for k in ['material','complete','alpha']});base=metrics(a['material'],a['complete']);assert base==rec['scores']
original_mapping=settled.mapping;original_shade=settled.shade
post_radius=json.loads((B/'source-proof-FIRST.json').read_text())['post_kernel']['radius'];post_scope=cv2.dilate(((a['alpha']>0)|s.valid).astype(np.uint8),np.ones((2*post_radius+1,2*post_radius+1),np.uint8))>0
trials=[];save('assignment.json',dict(approval='a04be8ed-3cdc-4c5b-876c-12a794b2032f',family='C=clip(S+b,0,1), gainsall1/offsetallb/14light0',NOT_tau=True,b0_equivalent_to_accepted_tau1=True,first_b=.075,accepted_b=.05,native_trial_budget=4,source_proof='Acceptedmap/kernel/shape/source/masks/SVG unchanged, existingprooftransfers',no_source_fit_or_map_change=True))
for number,f in enumerate([1,.5,.25,.125],1):
 b=.05+.025*f;p=copy.deepcopy(p0);co=np.zeros(23);co[:3]=co[-3:]=1.;co[3:6]=b;p['material']=co.tolist();predM=np.clip(a['material']+(b-.05),0,1);predC=composite(s,p,predM);prediction=metrics(predM,predC)
 # Counts are collected INSIDE thisoneactualnativebodypass fromexact source samples.
 state={'row':0};clip={n:dict(subrays=0,lower_clipped_subrays=0,upper_clipped_subrays=0,lower_clipped_channels=0,upper_clipped_channels=0,at_endpoints_subrays=0,min_unclipped=1e9,max_unclipped=-1e9) for n in ['whole','scored','postfootprint']}
 def observed_mapping(x,y,preset,boundary=None):
  X,Y=original_mapping(x,y,preset,boundary);state.update(x=x,y=y,top=state['row'],bottom=state['row']+x.shape[0]//2);return X,Y
 def observed_shade(sample,light,material):
  colored=light.ndim==sample.ndim+1;core=light[...,0,-1] if colored else light[...,-1];gain=(1-core[...,None])*material[:3]+core[...,None]*material[-3:];L=light[...,:-1]@material[6:-3]
  if not colored:L=L[...,None]
  pre=sample*gain+material[3:6]+L;actual=original_shade(sample,light,material);assert np.array_equal(actual,np.clip(pre,0,1))
  whole=s.shape(state['x'],state['y'],p)[-1][0]<=0;start,end=state['top'],state['bottom'];score=np.repeat(np.repeat(s.valid[start:end],2,0),2,1);post=np.repeat(np.repeat(post_scope[start:end],2,0),2,1)
  for n,m in [('whole',whole),('scored',score),('postfootprint',post)]:
   z=pre[m];q=clip[n];q['subrays']+=int(m.sum());q['lower_clipped_subrays']+=int((z<0).any(1).sum());q['upper_clipped_subrays']+=int((z>1).any(1).sum());q['lower_clipped_channels']+=int((z<0).sum());q['upper_clipped_channels']+=int((z>1).sum());q['at_endpoints_subrays']+=int(((z==0)|(z==1)).any(1).sum());q['min_unclipped']=min(q['min_unclipped'],float(z.min()) if z.size else 1.);q['max_unclipped']=max(q['max_unclipped'],float(z.max()) if z.size else 0.)
  state['row']=end;return actual
 settled.mapping=observed_mapping;settled.shade=observed_shade
 try:M=settled.render(s.source,s.case,p,samples=2)
 finally:settled.mapping=original_mapping;settled.shade=original_shade
 assert state['row']==s.crop[3]-s.crop[1];assert clip['whole']['subrays']==162445 and clip['scored']['subrays']==124476
 C=composite(s,p,M);q=metrics(M,C);checks={n:q[n]['rmse']<=base[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<=base['E'],SSIM=q['ssim']>=base['ssim'],advisory_f64_E=q['advisory_f64_E']<=base['advisory_f64_E']);progress=q['E']<base['E'] and base['advisory_f64_E']-q['advisory_f64_E']>64*np.finfo(float).eps*max(base['advisory_f64_E'],1);qualifies=bool(all(checks.values()) and progress)
 row=dict(trial=number,b=b,g=1.,backtrack=f,prediction_ONLY=prediction,actual_native=q,checks=checks,meaningful_progress=bool(progress),qualifies=qualifies,clipping_counts=clip,prediction_max_absolute_material_difference=float(np.max(abs(M.astype(float)-predM.astype(float)))),source_and_sampling='Frozen exactselectedsettledrender samples2, observationalwrappers returnoriginalmap/shade unchanged; no baselinererender ornewraysweeps')
 save(f'trial-{number:02}.json',row);np.savez_compressed(D/f'trial-{number:02}.npz',material=M,complete=C,alpha=a['alpha']);trials.append(row);print(json.dumps(row),flush=True)
 if qualifies:
  candidate=copy.deepcopy(rec);candidate.pop('tau',None);candidate.update(preset=p,material_family='NEUTRAL_AFFINE_Cclip(g*S+b),g1,bsharedRGB',g=1.,b=b,material_contract='Gainsall1/offsetsb/all14light0. NEWdeclaredneutraladditivegrading, NOTtau/whiteveiling, encodedRGBempiricalnotphysicalradiance/Appleproof',baseline_equivalence='Acceptedpass2 g1,b.05, sourceepoch/nativeprotocolsame',stage='CANDIDATE_FOR_PRIMARY_INDEPENDENT_REVIEW_NOT_ACCEPTED',assignment='a04be8ed-3cdc-4c5b-876c-12a794b2032f',scores=q,clipping_counts=clip,accepted_passes=2,source_proof_transfer='OnlyscalarRGBtiedbchanged aftersampling; source/map/kernels/shape/AA/sourceconfidence/SVG/native/scoringmasks unchanged. AcceptedWHOLE+ALLscored+post prooftransfers, observed0. No refraction/dispersion/blurvalidation.');save('candidate-native.json',candidate);np.savez_compressed(D/'candidate-native.npz',material=M,complete=C,alpha=a['alpha']);x0,y0,x1,y1=s.crop;w=2*(x1-x0);h=2*(y1-y0);im=Image.new('RGB',(2*w+2,h+64),'#222');dr=ImageDraw.Draw(im);dr.text((8,20),'Original NEXT',fill='white');dr.text((w+12,20),f'Candidate neutralgrading b={b}',fill='white')
  for i,rgb in enumerate([s.target_crop,C]):im.paste(Image.fromarray(np.uint8(np.rint(np.clip(rgb,0,1)*255))).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64))
  im.save(D/'candidate-comparison.png');break
save('review.json',dict(status='FIRST_NATIVE_QUALIFIER_STOPPED_FOR_PRIMARY' if any(q['qualifies'] for q in trials) else 'ALL_BOUNDED_BACKTRACKS_NEGATIVE',baseline=base,trials=trials,actual_native_trial_count=len(trials),family='neutral-affine g1/bRGBtied NOTtau',firstqualifier_stop=True,accepted_count=2,no_furtherfit_before_primary=True))
