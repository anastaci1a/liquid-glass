"""ONE saved-response strength+postblur compensation; no new derivatives."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');OUT=ROOT/'pass08-fresh-strength'
spec=importlib.util.spec_from_file_location('h',ROOT/'rim-width-first.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);m=h.m
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 os.umask(0o002)
 if (OUT/'result.json').exists():print('Complete,no repeat');return
 if (OUT/'started.json').exists():raise RuntimeError('Inspect partial process first')
 OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),budget='ONE authorized FRESH smallerstrengthsecant + savedpost direction <=.0005/.0125reference-nativepx,max4actualnativebacktracks; no repeatedcompletedprobes/derivatives',trigger='Acceptedpass08/newround2; Savedmodel4backtracks allties/subnoise; oneFRESH acceptedpass08 strengthsecant +/- .0005, savedrevision6 postdirection remains nearbySURROGATE. No repeatedcompletedprobes.',source='Original modeledhidden-track contract, not observedtruth. OrdinarypostGaussian separate from RGB dispersion.'))
 native=json.loads((ROOT/'pass07-recentered-saved/candidate-native.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];old=[np.load(ROOT/f'pass07-recentered-saved/trial1-ref{i}-material.npy') for i in range(2)];models=[]
 fresh_records=[]
 for i,study in enumerate(studies):
  for sign in [-1,1]:
   q={**p,'directional_transmission':{**p['directional_transmission'],'strength':float(p['directional_transmission']['strength']+sign*.0005)}}
   a=study.render(q,co);np.save(OUT/f'ref{i}-fresh-strength-{sign:+d}-material.npy',a)
   fresh_records.append(dict(reference=i,parameters=q,file=f'ref{i}-fresh-strength-{sign:+d}-material.npy'))
 save('fresh-secant-records.json',dict(records=fresh_records,derivative_pairs=2,per_reference_halfstep=.0005,source='ONLY one fresh smaller strength secant; not optical acceptance/backtracking trial'))
 for i,s in enumerate(studies):
  cols=[];fullcols=[]
  for kind in ['fresh-strength','saved-post']:
   if kind=='fresh-strength':minus=np.load(OUT/f'ref{i}-fresh-strength--1-material.npy');plus=np.load(OUT/f'ref{i}-fresh-strength-+1-material.npy');divisor=2
   else:minus=np.load(ROOT/f'postblur-first/trial0-ref{i}-material.npy');plus=np.load(ROOT/f'postblur-first/trial1-ref{i}-material.npy');divisor=8
   cols.append((plus.astype(float)-minus.astype(float))/divisor);fullcols.append((m.clean_composite(s,p,plus).astype(float)-m.clean_composite(s,p,minus).astype(float))/divisor)
  D=np.stack(cols,axis=-1);Df=np.stack(fullcols,axis=-1);err=old[i].astype(float)-s.target_crop;ef=np.load(ROOT/f'pass07-recentered-saved/ref{i}-complete.npy').astype(float)-s.target_crop;ext=(s.sd>0)&(s.sd<.35);forms={}
  def form(k,d,e):
   X=d.reshape(-1,2);v=e.ravel();w=255**2/len(v);forms[k]=[X.T@X*w,X.T@v*w]
  form('glass',D[s.valid],err[s.valid]);form('rim',D[s.rim],err[s.rim]);form('shadow',Df[ext],ef[ext]);forms['loss']=[.7*forms['glass'][k]+.3*forms['rim'][k] for k in range(2)];models.append(forms)
 save('forms.json',[{k:dict(H=a.tolist(),g=b.tolist()) for k,(a,b) in f.items()} for f in models])
 def norm(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i][k]['rmse']**2)
 def value(i,k,v):H,g=models[i][k];return float(2*g@v+v@H@v)/norm(i,k)
 def jac(i,k,v):H,g=models[i][k];return 2*(g+H@v)/norm(i,k)
 fun=lambda v:sum(value(i,'loss',v) for i in range(2))/2;fj=lambda v:sum((jac(i,'loss',v) for i in range(2)))/2
 constraints=lambda v:np.array([-value(i,k,v) for i in range(2) for k in ['loss','glass','shadow']]);cj=lambda v:np.array([-jac(i,k,v) for i in range(2) for k in ['loss','glass','shadow']])
 opt=minimize(fun,np.zeros(2),jac=fj,method='SLSQP',bounds=[(-1,1)]*2,constraints=[dict(type='ineq',fun=constraints,jac=cj)],options=dict(maxiter=60,ftol=1e-13))
 ds,db=opt.x*np.array([.0005,.0125]);save('proposal.json',dict(delta_strength=float(ds),delta_postblur_reference_nativepx=float(db),model_relative_loss_change=float(opt.fun),solver_success=bool(opt.success),message=opt.message,model_constraints=constraints(opt.x).tolist(),limits='FRESHacceptedpass08 strengthsecant +/- .0005 plus oldrevision6post secantSURROGATE; no extra probes. No solver or model acceptance, strict native/advisory review.'))
 print('PROPOSAL',ds,db,opt.fun,opt.message,flush=True);trials=[];candidate=None;noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
 registry=[]
 for folder in ['rim-width-first','postblur-first','strength-first','strength-postblur-joint','pass07-recentered-saved','pass08-recentered-saved']:
  prior=json.loads((ROOT/folder/'result.json').read_text())
  for j,row in enumerate(prior['trials']):registry.append((json.dumps(row['parameters'],sort_keys=True),folder,j))
 def render_or_reuse(q):
  key=json.dumps(q,sort_keys=True)
  paired=[row for row in fresh_records if json.dumps(row['parameters'],sort_keys=True)==key]
  if len(paired)==2:return [np.load(OUT/next(row['file'] for row in paired if row['reference']==i)) for i in range(2)],dict(reused_exact=True,folder='CURRENT freshsecant',trial='signedhalfstep')
  for fingerprint,folder,j in registry:
   if key==fingerprint:return [np.load(ROOT/f'{folder}/trial{j}-ref{i}-material.npy') for i in range(2)],dict(reused_exact=True,folder=folder,trial=j)
  return [s.render(q,co) for s in studies],dict(reused_exact=False)
 if opt.fun < -1e-12:
  for j,t in enumerate([1.,.5,.25,.125]):
   q={**p,'post_sigma':float(p['post_sigma']+t*db),'directional_transmission':{**p['directional_transmission'],'strength':float(p['directional_transmission']['strength']+t*ds)}};imgs,origin=render_or_reuse(q);scores=[m.score(s,q,a)[0] for s,a in zip(studies,imgs)];prec=[h.precision(s,o,a) for s,o,a in zip(studies,old,imgs)]
   row=dict(factor=t,parameters=q,image_origin=origin,scores=scores,advisory_double=prec,guarded=all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['shadow']['rmse']<=b['shadow']['rmse'] for s,b in zip(scores,baseline)),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
   for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
   trials.append(row);save('trials.json',trials);print('NATIVE',t,[s['E'] for s in scores],row['guarded'],flush=True)
   if not(row['guarded'] and row['meaningful'] and all(v['nonincreasing'] for v in prec)):continue
   m.ROOT=OUT;proof=[m.audit(s,q,i) for i,s in enumerate(studies)];save('fresh-source-proof.json',proof)
   if not all(v['passed'] for v in proof):break
   candidate=dict(parameters=q,material=co.tolist(),scores=scores,advisory_double=prec,source_proof='FRESH nativewhole+ALLscored base/RGB+reflection/context originalsourceGaussian proof; output-scatteringconfidence NOTinferred. OriginalexplicitmodeledhiddenRGB unchanged.')
   save('candidate-native.json',candidate);public=json.loads((ROOT/'pass07-recentered-saved/candidate-public-native.json').read_text());public.update(parameters=q,scores=scores);save('candidate-public-native.json',public)
   for i,(s,a) in enumerate(zip(studies,imgs)):
    np.save(OUT/f'ref{i}-complete.npy',m.clean_composite(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=h.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=False)
    for name,array in zip(['target','baseline','candidate'],[s.target_crop,m.clean_composite(s,p,old[i]),m.clean_composite(s,q,a)]):cv2.imwrite(str(OUT/f'ref{i}-{name}-preview.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
   break
 save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=2,source_epoch_unchanged=True,limits='ONEexistingjointdirection, savedprobesonly; originalpairedE/glass/fixedexterior strict. No newsource/shape/ordinarysourcekernel/material/foreground, no epsilon. Negative=>advisorymodel/cropreview only, notmorefits.'))
 print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
