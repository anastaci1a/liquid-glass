"""ONE bounded outer c0-2/shared-material proposal from accepted Compact pass2."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/helper-toolbar-work/compact-mini-round');OUT=ROOT/'outer-material-pass2'
spec=importlib.util.spec_from_file_location('joint_helpers',ROOT/'joint-rim-material.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);m=helper.m;comp=helper.comp
from paired_fit import Cached
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def forms(cache,co,base,profiles,index):
    s=cache.study;H,W=cache.H,cache.W;C,J=cache.C,cache.J;core=J[...,-1]
    gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:]
    z=C*gain+co[3:6]+(J[...,:-1]@co[6:-3])[...,None]
    optical=np.stack([(plus.astype(float)-minus.astype(float))/2 for minus,plus in profiles],axis=-1)
    opticalfg=np.stack([(s.apply_foreground(plus.copy()).astype(float)-s.apply_foreground(minus.copy()).astype(float))/2 for minus,plus in profiles],axis=-1)
    factor=helper.foreground_factor(s);error=base.astype(float)-s.target_crop;fgerror=s.apply_foreground(base.copy()).astype(float)-s.target_crop
    masks={'glass':s.valid,'rim':s.rim};boxes={};x0,y0,_,_=s.crop
    for layer in s.case['foreground_layers']:
        a,b,c,d=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));boxes[key]=np.s_[b-y0:d-y0,a-x0:c-x0]
    result={k:[np.zeros((26,26)),np.zeros(26)] for k in [*masks,*boxes]}
    def accum(k,D,e):
        X=D.reshape(-1,26);e=e.ravel();w=255**2/(3*len(e));result[k][0]+=X.T@X*w;result[k][1]+=X.T@e*w
    saved=np.lib.format.open_memmap(OUT/f'ref{index}-normalized-material-J.npy',mode='w+',dtype=np.float32,shape=(H,W,3,23));np.save(OUT/f'ref{index}-normalized-outer-J.npy',optical.astype(np.float32))
    for c in range(3):
        active=(z[...,c]>0)&(z[...,c]<1);avg=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
        F=np.zeros((H,W,23));F[...,c]=avg(active*C[...,c]*(1-core));F[...,c+3]=avg(active);F[...,6:20]=avg(active[...,None]*J[...,:-1]);F[...,c+20]=avg(active*C[...,c]*core)
        if s.kernel_sigma(cache.p,'post_sigma')>.001:F=cv2.GaussianBlur(F,(0,0),s.kernel_sigma(cache.p,'post_sigma'))
        F*=.002;saved[:,:,c,:]=F;D=np.empty((H,W,26));D[...,:3]=optical[...,c,:];D[...,3:]=F
        for k,mask in masks.items():accum(k,D[mask],error[...,c][mask])
        D[...,:3]=opticalfg[...,c,:];D[...,3:]*=factor[...,None]
        for k,sl in boxes.items():accum(k,D[sl],fgerror[...,c][sl])
    saved.flush();del saved;result['loss']=[.7*result['glass'][k]+.3*result['rim'][k] for k in range(2)]
    return result

def source_proof(s,p,index):
    defined,observed=m.masks(s);dsafe,radius=m.kernel_safe(defined,s,p);osafe,_=m.kernel_safe(observed,s,p)
    counts={k:0 for k in ['whole','scored','scored_outside_shape','whole_defined_bad','whole_observed_bad','scored_defined_bad','scored_observed_bad']};minimum={k:1. for k in ['whole_defined','whole_observed','scored_defined','scored_observed']};badrows=[]
    for row,bottom,W,x,y in s.raster_tiles(1):
        whole=s.shape(x,y,p)[-1][0]<=0;scored=np.repeat(np.repeat(s.valid[row:bottom],2,axis=0),2,axis=1)
        X,Y,_,_=s.geometry_field(x,y,p);X=X*s.L+s.case['center'][0];Y=Y*s.L+s.case['center'][1];dc=m.confidence_at(dsafe,X,Y);oc=m.confidence_at(osafe,X,Y)
        counts['scored_outside_shape']+=int((scored&~whole).sum())
        for key,mask in [('whole',whole),('scored',scored)]:
            counts[key]+=int(mask.sum())
            for name,c in [('defined',dc),('observed',oc)]:
                counts[key+'_'+name+'_bad']+=int((mask&(c<.999)).sum())
                if mask.any():minimum[key+'_'+name]=min(minimum[key+'_'+name],float(c[mask].min()))
        bad=(whole|scored)&((dc<.999)|(oc<.999))
        if bad.any():badrows.append(np.stack([x[bad]*s.L+s.case['center'][0],y[bad]*s.L+s.case['center'][1],X[bad],Y[bad],dc[bad],oc[bad],scored[bad],whole[bad]],axis=1))
    bad=np.concatenate(badrows) if badrows else np.empty((0,8));np.save(OUT/f'ref{index}-unsupported-rays.npy',bad)
    return dict(counts=counts,minimum_confidence=minimum,gaussian_radius_native_px=radius,passed=not any(counts[k] for k in counts if k.endswith('_bad')),limits='FRESH changed-map original native2x2 whole + ALL scored including outside corrected outline; finite3sigma source support, not continuous/infinite Gaussian theorem.')

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Complete; no rerun');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partials/process first')
    OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),baseline='accepted Compact pass2 thin-material-pass1/candidate-native.json',budget='ONE local26-columnJacobian: outer c0-2 central native secants at .001 + analytic23material .002; max4actualnativebacktracks',saved_basis='No compatible Compact outer derivative saved. Prior analytic material J has another thin_width/clippingstate; ONE acceptedpass2 local Jacobian required. No nearby response used as exact.'))
    native=json.loads((ROOT/'thin-material-pass1/candidate-native.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];models=[];zeros=[];old=[]
    for i,s in enumerate(studies):
        base=np.load(ROOT/f'thin-material-pass1/trial2-ref{i}-material.npy');old.append(base);profiles=[]
        for k in range(3):
            images=[]
            for sign in [-1,1]:
                q={**p,f'c{k}':p[f'c{k}']+sign*.001};a=s.render(q,co);np.save(OUT/f'ref{i}-c{k}-{sign:+d}-material.npy',a);images.append(a)
            profiles.append(images)
        cache=Cached(s,p);zero=cache.render(co);zeros.append(float(abs(zero-base).max()));assert zeros[-1]==0,'Accepted-state material cache mismatch'
        models.append(forms(cache,co,base,profiles,i));del cache;print('JACOBIAN',i,'cachezero',zeros[-1],flush=True)
    save('zero-controls.json',dict(max_pixel_difference=zeros,native_baseline_replays=0,local_jacobians=1,profile_derivative_renders_per_reference=6));save('forms.json',[{k:dict(H=v[0].tolist(),g=v[1].tolist()) for k,v in scene.items()} for scene in models])
    keys=['loss','glass',*baseline[0]['foreground_mse']]
    def norm(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i]['glass']['rmse']**2 if k=='glass' else baseline[i]['foreground_mse'][k])
    def value(i,k,v):H,g=models[i][k];return float(2*g@v+v@H@v)/norm(i,k)
    def jac(i,k,v):H,g=models[i][k];return 2*(g+H@v)/norm(i,k)
    fun=lambda v:sum(value(i,'loss',v) for i in range(2))/2;fj=lambda v:sum((jac(i,'loss',v) for i in range(2)))/2
    constraints=lambda v:np.array([-value(i,k,v) for i in range(2) for k in keys]);cj=lambda v:np.array([-jac(i,k,v) for i in range(2) for k in keys])
    opt=minimize(fun,np.zeros(26),jac=fj,method='SLSQP',bounds=[(-1,1)]*26,constraints=[dict(type='ineq',fun=constraints,jac=cj)],options=dict(maxiter=60,ftol=1e-12))
    dp=.001*opt.x[:3];dc=.002*opt.x[3:];save('proposal.json',dict(delta_outer=dp.tolist(),delta_material=dc.tolist(),model_relative_loss_change=float(opt.fun),solver_success=bool(opt.success),message=opt.message,model_constraints=constraints(opt.x).tolist(),limitations='ONE central-secant/analytic clipped local Jacobian only. Model/solver cannot accept native pixels; no source proof transfer for changed map.'))
    trials=[];candidate=None;proof=None;noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
    if opt.fun < -1e-12:
        for j,t in enumerate([1.,.5,.25,.125]):
            q=p.copy();q.update({f'c{k}':float(p[f'c{k}']+t*dp[k]) for k in range(3)});new=co+t*dc;imgs=[s.render(q,new) for s in studies];scores=[m.guards(s,q,a)[0] for s,a in zip(studies,imgs)]
            row=dict(factor=t,parameters=q,material=new.tolist(),scores=scores,guarded=comp.good(scores,baseline),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
            for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
            trials.append(row);save('trials.json',trials);print('NATIVE',t,[s['E'] for s in scores],row['guarded'],flush=True)
            if not(row['guarded'] and row['meaningful']):continue
            proof=[source_proof(s,q,i) for i,s in enumerate(studies)];save('fresh-source-proof.json',proof);print('SOURCE',[v['passed'] for v in proof],flush=True)
            if not all(v['passed'] for v in proof):break
            candidate=dict(parameters=q,material=new.tolist(),scores=scores,source_proof='FRESH whole and ALL scored original native2x2 rays including outside corrected outline; see fresh-source-proof.json')
            save('candidate-native.json',candidate);public=json.loads((ROOT/'thin-material-pass1/candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=studies[0].L;qq['post_sigma']/=studies[0].L;public.update(parameters=qq,material=new.tolist(),scores=scores);save('candidate-normalized.json',public)
            for i,(s,a) in enumerate(zip(studies,imgs)):
                np.save(OUT/f'ref{i}-complete.npy',comp.composition(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q));size=comp.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=True)
                for label,array in zip(['target','baseline','candidate'],[s.target_crop,comp.composition(s,p,old[i],True),comp.composition(s,q,a,True)]):cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
            break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,source_proof=proof,accepted=False,accepted_count=2,native_resolution_noise_floor=noise,limits='ONE short existing c0-2+sharedmaterial proposal, unchangedsource/shape/kernel/foreground/masks/epoch; actual all10FG+bothE/glass/exterior strict, no epsilon or solver success acceptance.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
