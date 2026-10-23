"""ONE saved rim response + analytic shared generated-shadow opacity step."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');OUT=ROOT/'rim-shadow-compensation'
spec=importlib.util.spec_from_file_location('rim_helpers',ROOT/'rim-width-first.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);m=h.m
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 os.umask(0o002)
 if (OUT/'result.json').exists():print('Complete,no repeat');return
 if (OUT/'started.json').exists():raise RuntimeError('Inspect partialprocess/artifacts first')
 OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),budget='ONE savedrim+commonopacity compensation,width<=.000125/opacity<=.0005,max4nativebacktracks',source='UNCHANGED existingmodeled epoch; missingobservedRGB not evidence',derivatives='Reuse saved actualwidthtrial2/3, analyticgeneratedshadow only. No repeatedwidthderivative.'))
 native=json.loads((ROOT/'baseline-native-recipe.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];old=[np.load(ROOT/f'ref{i}-baseline-material.npy') for i in range(2)];models=[]
 for i,s in enumerate(studies):
  minus=np.load(ROOT/f'rim-width-first/trial2-ref{i}-material.npy');plus=np.load(ROOT/f'rim-width-first/trial3-ref{i}-material.npy');Drim=(plus.astype(float)-minus.astype(float))/2
  full=np.load(ROOT/f'ref{i}-baseline-complete.npy');ext=(s.sd>0)&(s.sd<.35);alpha=s.shape_coverage(p);x0,y0,x1,y1=s.crop;Y,X=np.mgrid[y0:y1,x0:x1].astype(np.float32);x=(X-s.case['center'][0])/s.L;y=(Y-s.case['center'][1])/s.L;q=p['shadow'];sd=s.shape(x-q['offset'][0],y-q['offset'][1],p)[-1][0]
  exterior=s.source if s.exterior_source is None else s.exterior_source;B=cv2.remap(exterior,X,Y,cv2.INTER_LINEAR)
  Dopacity=-B*np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2)[...,None]*(1-alpha[...,None])*.0005
  Dfullrim=(m.clean_composite(s,p,plus).astype(float)-m.clean_composite(s,p,minus).astype(float))/2
  D=np.stack([Drim,np.zeros_like(Drim)],axis=-1);Df=np.stack([Dfullrim,Dopacity],axis=-1);err=old[i].astype(float)-s.target_crop;ef=full.astype(float)-s.target_crop
  forms={}
  def form(k,d,e):
   A=d.reshape(-1,2);v=e.ravel();w=255**2/len(v);forms[k]=[A.T@A*w,A.T@v*w]
  form('glass',D[s.valid],err[s.valid]);form('rim',D[s.rim],err[s.rim]);form('shadow',Df[ext],ef[ext]);forms['loss']=[.7*forms['glass'][k]+.3*forms['rim'][k] for k in range(2)];models.append(forms)
 save('forms.json',[{k:dict(H=a.tolist(),g=b.tolist()) for k,(a,b) in f.items()} for f in models])
 def norm(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i][k]['rmse']**2)
 def value(i,k,v):H,g=models[i][k];return float(2*g@v+v@H@v)/norm(i,k)
 def jac(i,k,v):H,g=models[i][k];return 2*(g+H@v)/norm(i,k)
 fun=lambda v:sum(value(i,'loss',v) for i in range(2))/2;fj=lambda v:sum((jac(i,'loss',v) for i in range(2)))/2
 constraints=lambda v:np.array([-value(i,k,v) for i in range(2) for k in ['loss','glass','shadow']]);cj=lambda v:np.array([-jac(i,k,v) for i in range(2) for k in ['loss','glass','shadow']])
 opt=minimize(fun,np.zeros(2),jac=fj,method='SLSQP',bounds=[(-1,1)]*2,constraints=[dict(type='ineq',fun=constraints,jac=cj)],options=dict(maxiter=60,ftol=1e-13))
 dw,do=opt.x*np.array([.000125,.0005]);save('proposal.json',dict(delta_width=float(dw),delta_shadow_opacity=float(do),model_relative_loss_change=float(opt.fun),solver_success=bool(opt.success),message=opt.message,model_constraints=constraints(opt.x).tolist(),limits='Savedrim finite secant/analytic opacity surrogate only. Actualnative fullcomposite originalguards decide.'))
 print('PROPOSAL',dw,do,opt.fun,opt.message,flush=True);trials=[];candidate=None
 noise=json.loads((ROOT/'rim-width-first/result.json').read_text())['native_resolution_noise_floor']
 if opt.fun < -1e-12:
  for j,t in enumerate([1.,.5,.25,.125]):
   q={**p,'rim_width':float(p['rim_width']+t*dw),'shadow':{**p['shadow'],'opacity':float(p['shadow']['opacity']+t*do)}};imgs=[s.render(q,co) for s in studies];scores=[m.score(s,q,a)[0] for s,a in zip(studies,imgs)];prec=[h.precision(s,o,a) for s,o,a in zip(studies,old,imgs)]
   row=dict(factor=t,parameters=q,scores=scores,advisory_double=prec,guarded=all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['shadow']['rmse']<=b['shadow']['rmse'] for s,b in zip(scores,baseline)),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
   for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
   trials.append(row);save('trials.json',trials);print('NATIVE',t,[s['E'] for s in scores],row['guarded'],flush=True)
   if not(row['guarded'] and row['meaningful'] and all(v['nonincreasing'] for v in prec)):continue
   candidate=dict(parameters=q,material=co.tolist(),scores=scores,advisory_double=prec,source_proof='Nativeintake whole/ALLscored base/RGB+reflection/context proof transfers: ONLY rimlightingwidth+generatedshadowopacity; no map/kernel/source/mask change. Original estimatedhiddenRGB contract retained, NOTobservationaltruth.')
   save('candidate-native.json',candidate);public=json.loads((ROOT/'authoritative-revision6.json').read_text());public.update(parameters=q,scores=scores);save('candidate-public-native.json',public)
   for i,(s,a) in enumerate(zip(studies,imgs)):
    np.save(OUT/f'ref{i}-complete.npy',m.clean_composite(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=h.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=False)
    for name,array in zip(['target','baseline','candidate'],[s.target_crop,m.clean_composite(s,p,old[i]),m.clean_composite(s,q,a)]):cv2.imwrite(str(OUT/f'ref{i}-{name}-preview.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
   break
 save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=0,source_proof_transferred=True,limits='OriginalbothE/glass/fixedexteriorshadowstrict; no newsource/shape/blur/dispersion/operator/epoch. Zerooriginalglyphlayers. Native+advisory checked, no epsilon or modelacceptance. Ifnegative nextauthorizedordinarypostblur +/- .05nativepx separately.'))
 print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
