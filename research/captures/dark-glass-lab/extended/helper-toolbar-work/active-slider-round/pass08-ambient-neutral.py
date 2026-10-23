"""ONE existing ambient0 direction; conditional same-law shared neutral co6."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');OUT=ROOT/'pass08-ambient-neutral'
spec=importlib.util.spec_from_file_location('h',ROOT/'rim-width-first.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);m=h.m
from material_context import affine,mean_source,LUMA
from render import shade
from grazing_reflection import apply,layers
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def analytic(s,p,co,base,index):
 T,offset=affine(s,p);effective=T@co+offset;mean=mean_source(s,p);brightness=float(mean@LUMA);assert 'ambient_rim_luma_range' not in p
 assert np.array_equal(T[:,6],np.eye(23)[:,6]);kappa=brightness-.5
 x0,y0,x1,y1=s.crop;H,W=y1-y0,x1-x0;D=np.empty((H,W,3));zero=np.empty((H,W,3),np.float32)
 for row,bottom,w,x,y in s.raster_tiles(1):
  C,J=s.field(x,y,p);assert J.ndim==C.ndim,'Current neutral basis must be scalar, not RGB paint'
  core=J[...,-1];gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:];z=C*gain+effective[3:6]+(J[...,:-1]@effective[6:-3])[...,None]
  F=((z>0)&(z<1))*J[...,0,None]
  D[row:bottom]=F.reshape(bottom-row,2,w,2,3).mean((1,3));zero[row:bottom]=shade(C,J,effective).reshape(bottom-row,2,w,2,3).mean((1,3))
 sigma=s.kernel_sigma(p,'post_sigma')
 if sigma>.001:D=cv2.GaussianBlur(D,(0,0),sigma);zero=cv2.GaussianBlur(zero,(0,0),sigma)
 zero=apply(s,p,zero);difference=float(abs(zero-base).max());assert difference==0,'Analytic baseline field mismatch'
 if 'grazing_reflection' in p:D*=1-layers(s,p)[0][...,None]
 np.save(OUT/f'ref{index}-analytic-neutral-co6-J.npy',D.astype(np.float32));np.save(OUT/f'ref{index}-analytic-ambient0-J.npy',(kappa*D).astype(np.float32))
 return D,kappa,dict(reference=s.folder.name,source_mean_rgb=mean.tolist(),source_luma=brightness,kappa=kappa,baseline_max_pixel_difference=difference,affine_column6_identity=True,limits='Existing source-defined mean weighting/material_context.affine unchanged; modeledhiddenRGB, not observedtruth. Derivative through clipping/AA/postGaussian/reflection; exact only locally away from clipping transitions.')

def main():
 os.umask(0o002)
 if (OUT/'result.json').exists():print('Complete,no rerun');return
 if (OUT/'started.json').exists():raise RuntimeError('Inspect partialprocess/artifacts first')
 OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),baseline='acceptedpublic08/newround2 pass07-recentered-saved/candidate-native.json',budget='ONEambient0 radius.002/max4actualbacktracks; ONLYifpairedguardsblock, ONEjointambient0+.0005co6 model/max4backtracks. Sharedsource-weighted law fixed.',saved_evidence='Oldrev4ambient packet hasdifferentgeometry/material and no compatiblepixelJ; prioractive-slider directions onlystrength/post/rim. ConstructONEcurrentstateanalyticco6basis; ambient0 column=(source_luma-.5)*basis. No repeatedopticalprobes.'))
 native=json.loads((ROOT/'pass07-recentered-saved/candidate-native.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];old=[np.load(ROOT/f'pass07-recentered-saved/trial1-ref{i}-material.npy') for i in range(2)];models=[];controls=[]
 for i,s in enumerate(studies):
  D,kappa,control=analytic(s,p,co,old[i],i);controls.append(control);X=np.stack([D*kappa*.002,D*.0005],axis=-1);alpha=s.shape_coverage(p);ext=(s.sd>0)&(s.sd<.35);full=np.load(ROOT/f'pass07-recentered-saved/ref{i}-complete.npy');forms={}
  def form(k,d,e):
   A=d.reshape(-1,2);v=e.ravel();w=255**2/len(v);forms[k]=[A.T@A*w,A.T@v*w]
  error=old[i].astype(float)-s.target_crop;form('glass',X[s.valid],error[s.valid]);form('rim',X[s.rim],error[s.rim]);form('shadow',(X*alpha[...,None,None])[ext],(full.astype(float)-s.target_crop)[ext]);forms['loss']=[.7*forms['glass'][k]+.3*forms['rim'][k] for k in range(2)];models.append(forms);print('ANALYTIC',i,'kappa',kappa,'zero',control['baseline_max_pixel_difference'],flush=True)
 save('analytic-controls.json',controls);save('forms.json',[{k:dict(H=a.tolist(),g=b.tolist()) for k,(a,b) in f.items()} for f in models]);noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
 phases=[];candidate=None;candidate_phase=None
 for phase,N in [('isolated-ambient',1),('joint-ambient-co6',2)]:
  dest=OUT/phase;dest.mkdir(exist_ok=True)
  def norm(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i][k]['rmse']**2)
  def val(i,k,v):H,g=models[i][k];return float(2*g[:N]@v+v@H[:N,:N]@v)/norm(i,k)
  def jac(i,k,v):H,g=models[i][k];return 2*(g[:N]+H[:N,:N]@v)/norm(i,k)
  fun=lambda v:sum(val(i,'loss',v) for i in range(2))/2;fj=lambda v:sum((jac(i,'loss',v) for i in range(2)))/2
  constraints=lambda v:np.array([-val(i,k,v) for i in range(2) for k in ['loss','glass','shadow']]);cj=lambda v:np.array([-jac(i,k,v) for i in range(2) for k in ['loss','glass','shadow']])
  opt=minimize(fun,np.zeros(N),jac=fj,method='SLSQP',bounds=[(-1,1)]*N,constraints=[dict(type='ineq',fun=constraints,jac=cj)],options=dict(maxiter=60,ftol=1e-13));v=np.zeros(2);v[:N]=opt.x;da,dc=v*np.array([.002,.0005]);proposal=dict(delta_ambient0=float(da),delta_co6=float(dc),model_relative_loss_change=float(opt.fun),solver_success=bool(opt.success),message=opt.message,model_constraints=constraints(opt.x).tolist(),limits='One currentstateanalytic shared model; actualnative strictguards decide, no per-background coefficients.')
  (dest/'proposal.json').write_text(json.dumps(proposal,indent=2)+'\n');print('PROPOSAL',phase,da,dc,opt.fun,flush=True);trials=[];guard_blocked=bool(opt.fun>=-1e-12)
  if opt.fun < -1e-12:
   for j,t in enumerate([1.,.5,.25,.125]):
    ambient=list(p['ambient_rim_response']);ambient[0]+=t*da;q={**p,'ambient_rim_response':ambient};new=co.copy();new[6]+=t*dc;imgs=[s.render(q,new) for s in studies];scores=[m.score(s,q,a)[0] for s,a in zip(studies,imgs)];prec=[h.precision(s,o,a) for s,o,a in zip(studies,old,imgs)]
    row=dict(factor=t,parameters=q,material=new.tolist(),scores=scores,advisory_double=prec,guarded=all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['shadow']['rmse']<=b['shadow']['rmse'] for s,b in zip(scores,baseline)),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
    for i,a in enumerate(imgs):np.save(dest/f'trial{j}-ref{i}-material.npy',a)
    trials.append(row);(dest/'trials.json').write_text(json.dumps(trials,indent=2)+'\n');guard_blocked|=not row['guarded'];print('NATIVE',phase,t,[s['E'] for s in scores],row['guarded'],flush=True)
    if not(row['guarded'] and row['meaningful'] and all(v['nonincreasing'] for v in prec)):continue
    candidate=dict(parameters=q,material=new.tolist(),scores=scores,advisory_double=prec,source_proof='TRANSFER exactaccepted08 freshwhole/ALLscored base/RGB/reflection/context proof: only ambient0+commonco6 changes; source_mean weighting/affine/source/map/kernel/shape/masks unchanged. OriginalmodeledRGB defined1/observed0, not photographictruth.')
    save('candidate-native.json',candidate);save('candidate-public-native.json',dict(parameters=q,material=new.tolist(),scores=scores,method='One bounded shared existing ambient0/commonneutralco6 proposal; source mean weighting fixed, no per-background coefficients',provenance=dict(baseline='accepted public08',phase=phase,native_trial_index=j,primary_acceptance=False)))
    for i,(s,a) in enumerate(zip(studies,imgs)):
     np.save(OUT/f'ref{i}-complete.npy',m.clean_composite(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=h.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=False)
     for name,array in zip(['target','baseline','candidate'],[s.target_crop,m.clean_composite(s,p,old[i]),m.clean_composite(s,q,a)]):cv2.imwrite(str(OUT/f'ref{i}-{name}-preview.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
    candidate_phase=phase;break
  phases.append(dict(phase=phase,proposal=proposal,trials=trials,guard_blocked=guard_blocked));save('phase-history.json',phases)
  if candidate is not None:break
  if phase=='isolated-ambient' and not guard_blocked:break
 save('result.json',dict(baseline=baseline,phases=phases,candidate=candidate,candidate_phase=candidate_phase,accepted=False,accepted_count=2,analytic_controls=controls,limits='OriginalallpairedE/glass/fixedexterior+advisoryresidual strict, zerooriginalglyphlayers. Commonlaw/affine unchanged, no source/shape/mask/epoch/operator/publicedit. Stopfirstqualifier, no nextfit beforeprimary.'))
 print('DONE',[(v['phase'],len(v['trials'])) for v in phases],'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
