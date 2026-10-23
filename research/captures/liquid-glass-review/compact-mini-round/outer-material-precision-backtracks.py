"""Only remaining .5/.25/.125 of saved outer/material proposal; no new solver."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
ROOT=Path('/evidence/extended/helper-toolbar-work/compact-mini-round');PARENT=ROOT/'outer-material-pass2';OUT=PARENT/'precision-backtracks'
spec=importlib.util.spec_from_file_location('outer_saved',ROOT/'outer-material-pass2.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);m=h.m;comp=h.comp
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def precision(s,old,new):
    old=old.astype(float);new=new.astype(float);target=s.target_crop.astype(float);row={}
    for key,mask in [('glass',s.valid),('rim',s.rim)]:
        e=old[mask]-target[mask];d=new[mask]-old[mask];row[key]=dict(baseline_mse=float(np.mean(e*e)*255**2),candidate_mse=float(np.mean((e+d)**2)*255**2),delta_mse_direct=float(np.mean(2*e*d+d*d)*255**2))
    loss=.7*row['glass']['delta_mse_direct']+.3*row['rim']['delta_mse_direct'];base=.7*row['glass']['baseline_mse']+.3*row['rim']['baseline_mse'];row.update(weighted_loss_delta=loss,E_delta=float(np.sqrt(base+loss)-np.sqrt(base)),nonincreasing_E=bool(loss<=0))
    return row

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Remaining backtracks completed; no repeats');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partials/process first')
    OUT.mkdir(exist_ok=True);h.OUT=OUT
    save('started.json',dict(pid=os.getpid(),authority='Primary precision review: ONLY remaining .5/.25/.125; no repeated full/nativeJacobian/solver',full_step='Original float32 guard pass, HELD for genuine advisory double A residual increase. Original artifacts immutable.',epoch='UNCHANGED original float32 native metrics/masks/input; float64 residual is primary precision review only'))
    native=json.loads((ROOT/'thin-material-pass1/candidate-native.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];proposal=json.loads((PARENT/'proposal.json').read_text());dp=np.array(proposal['delta_outer']);dc=np.array(proposal['delta_material'])
    assert len(json.loads((PARENT/'trials.json').read_text()))==1
    studies=[m.Study(ROOT/n) for n in ['a','b']];old=[np.load(ROOT/f'thin-material-pass1/trial2-ref{i}-material.npy') for i in range(2)]
    noise=json.loads((PARENT/'result.json').read_text())['native_resolution_noise_floor'];trials=[];candidate=None;proof=None
    for j,t in enumerate([.5,.25,.125],start=1):
        q=p.copy();q.update({f'c{k}':float(p[f'c{k}']+t*dp[k]) for k in range(3)});new=co+t*dc
        imgs=[s.render(q,new) for s in studies];scores=[m.guards(s,q,a)[0] for s,a in zip(studies,imgs)];prec=[precision(s,o,a) for s,o,a in zip(studies,old,imgs)]
        row=dict(total_trial_index=j,factor=t,parameters=q,material=new.tolist(),scores=scores,guarded=comp.good(scores,baseline),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)),advisory_double=prec,primary_precision_review_passed=all(v['nonincreasing_E'] for v in prec))
        for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
        trials.append(row);save('trials.json',trials);print('REMAINING',t,[s['E'] for s in scores],'originalguard',row['guarded'],'doubleE',[v['E_delta'] for v in prec],flush=True)
        if not(row['guarded'] and row['meaningful'] and row['primary_precision_review_passed']):continue
        proof=[h.source_proof(s,q,i) for i,s in enumerate(studies)];save('fresh-source-proof.json',proof);print('SOURCE',[v['passed'] for v in proof],flush=True)
        if not all(v['passed'] for v in proof):break
        candidate=dict(parameters=q,material=new.tolist(),scores=scores,advisory_double=prec,source_proof='FRESH smaller changed-map native whole + ALL scored incl outsideoutline, finite3sigma support; see fresh-source-proof.json',factor=t)
        save('candidate-native.json',candidate);public=json.loads((ROOT/'thin-material-pass1/candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=studies[0].L;qq['post_sigma']/=studies[0].L;public.update(parameters=qq,material=new.tolist(),scores=scores);save('candidate-normalized.json',public)
        for i,(s,a) in enumerate(zip(studies,imgs)):
            np.save(OUT/f'ref{i}-complete.npy',comp.composition(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=comp.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=True)
            for label,array in zip(['target','baseline','candidate'],[s.target_crop,comp.composition(s,p,old[i],True),comp.composition(s,q,a,True)]):cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
        break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,source_proof=proof,prior_full_step='Originalfloat32 gate PASS; primary acceptance HELD for advisorydoubleAincrease; preserved not relabeled',accepted=False,accepted_count=2,total_native_trial_pairs_including_original=1+len(trials),new_solvers=0,new_derivatives=0,limits='Original float32 scoring/source epoch unchanged. Additional primary precision-review condition float64 weightedloss<=0 both; no epsilon.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
