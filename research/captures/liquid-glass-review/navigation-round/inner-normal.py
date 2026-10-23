"""ONE accepted-pass1 inner c3–6 Jacobian and at most four native trials."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
BASE=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
PREV=BASE.parent/'combined-outer-saved';OUT=BASE.parent/'inner-normal-pass1'
spec=importlib.util.spec_from_file_location('prior',BASE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from revision_replay import subpixel_support
spec=importlib.util.spec_from_file_location('material_presentation',BASE/'pass2-material-run.py')
presentation_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(presentation_module)

def save(name,v):
    (OUT/name).write_text(json.dumps(v,indent=2)+'\n')

def local_forms(s,pred,J,complete,FGJ):
    result={};scale=255**2
    def form(D,e):
        X=D.reshape(-1,4).astype(float);e=e.ravel().astype(float)
        return [X.T@X*scale/len(e),X.T@e*scale/len(e)]
    for key,mask in [('glass',s.valid),('rim',s.rim)]:result[key]=form(J[mask],(pred.astype(float)-s.target_crop)[mask])
    result['loss']=[.7*result['glass'][k]+.3*result['rim'][k] for k in range(2)]
    x0,y0,_,_=s.crop
    for layer in s.case['foreground_layers']:
        if 'vector_asset' in layer and layer['mode']!='transmission' and layer.get('fit_style',True):
            a,b,c,d=layer['box'];sl=np.s_[b-y0:d-y0,a-x0:c-x0]
            result[layer.get('style_key',layer['vector_asset'])]=form(FGJ[sl],(complete.astype(float)-s.target_crop)[sl])
    return result

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Already complete, no repeat.');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial Jacobian/trials before recovery')
    OUT.mkdir(exist_ok=True)
    save('started.json',dict(pid=os.getpid(),budget='ONE c3–6 Jacobian: central3,4,6; forward5; max4native trial factors1,.5,.25,.125',reuse='No saved compatible normal derivative arrays found; material forms differentiate different parameters; accepted pass1 native arrays/source/input freeze reused'))
    accepted=json.loads((PREV/'candidate-native.json').read_text());p=accepted['parameters'];co=np.asarray(accepted['material']);baseline=accepted['scores'];h=.002
    studies=[m.Study(BASE/n) for n in ['a','b']];models=[];zeros=[]
    for i,s in enumerate(studies):
        cache=m.ProfileCache(s,p,co);coeff=np.array([p[f'c{k}'] for k in range(7)])
        base=np.load(PREV/f'trial0-ref{i}-material.npy');complete=s.apply_foreground(base.copy())
        zeros.append(float(abs(cache.render(coeff)-base).max()));assert zeros[-1]<2e-6
        J=np.empty((*base.shape,4),np.float32);FGJ=np.empty_like(J)
        for j,k in enumerate(range(3,7)):
            v=coeff.copy();v[k]+=h;plus=cache.render(v)
            np.save(OUT/f'jacobian-ref{i}-c{k}-plus.npy',plus)
            fgplus=s.apply_foreground(plus.copy())
            if k==5:
                minus=base;fgminus=complete;denom=1.
            else:
                v=coeff.copy();v[k]-=h;minus=cache.render(v)
                np.save(OUT/f'jacobian-ref{i}-c{k}-minus.npy',minus)
                fgminus=s.apply_foreground(minus.copy());denom=2.
            # J is per normalized unit delta_c/.002, not per raw coefficient.
            J[...,j]=(plus-minus)/denom;FGJ[...,j]=(fgplus-fgminus)/denom
            print('JACOBIAN',i,k,'forward' if k==5 else 'central',flush=True)
        np.save(OUT/f'ref{i}-normalized-J.npy',J);np.save(OUT/f'ref{i}-foreground-normalized-J.npy',FGJ)
        models.append(local_forms(s,base,J,complete,FGJ));del cache,J,FGJ
    save('zero-controls.json',dict(material_max_diff=zeros,native_baseline='PRIMARY accepted pass1 cached material, no native baseline rerender'))
    save('forms.json',[{k:dict(H=v[0].tolist(),g=v[1].tolist()) for k,v in scene.items()} for scene in models])
    keys=['loss','glass',*baseline[0]['foreground_mse']]
    def norm(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i]['glass']['rmse']**2 if k=='glass' else baseline[i]['foreground_mse'][k])
    def val(i,k,v):
        H,g=models[i][k];return float(2*g@v+v@H@v)
    def jac(i,k,v):
        H,g=models[i][k];return 2*(g+H@v)
    fun=lambda v:sum(val(i,'loss',v)/norm(i,'loss') for i in range(2))/2
    funjac=lambda v:sum((jac(i,'loss',v)/norm(i,'loss') for i in range(2)))/2
    constraints=lambda v:np.array([-val(i,k,v)/norm(i,k) for i in range(2) for k in keys])
    constraintsjac=lambda v:np.array([-jac(i,k,v)/norm(i,k) for i in range(2) for k in keys])
    bounds=[(max(-1.,-p[f'c{k}']/h),min(1.,(2.5-p[f'c{k}'])/h)) for k in range(3,7)]
    opt=minimize(fun,np.zeros(4),jac=funjac,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=constraints,jac=constraintsjac)],options=dict(maxiter=100,ftol=1e-12))
    delta=h*opt.x
    save('proposal.json',dict(delta_c3_to_6=delta.tolist(),normalization_h=h,bounds=bounds,solver_success=bool(opt.success),message=opt.message,predicted_relative_loss_change=float(opt.fun),model_constraint_residuals=constraints(opt.x).tolist(),limits='ONE local native table-sampler Jacobian; c5 legal forward difference, others central. Fixed compositor differentiated by actual perturbed images. Local quadratic only; solver status never native acceptance.'))
    trials=[];candidate=None
    # If no local descent exists, do not dispatch a zero/tie native fit.
    if opt.fun < -1e-12 and np.max(abs(delta))>1e-12:
        for j,factor in enumerate([1.,.5,.25,.125]):
            q={**p,**{f'c{k}':float(p[f'c{k}']+factor*delta[k-3]) for k in range(3,7)}}
            imgs=[s.render(q,co) for s in studies];scores=[m.guards(s,q,a) for s,a in zip(studies,imgs)]
            row=dict(factor=factor,parameters=q,scores=scores,guarded=m.good(scores,baseline),meaningful=any(o['E']-n['E']>1e-5 for n,o in zip(scores,baseline)))
            for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
            trials.append(row);save('trials.json',trials)
            print('NATIVE',factor,[s['E'] for s in scores],row['guarded'],flush=True)
            if not(row['guarded'] and row['meaningful']):continue
            row['center_support']=[m.coverage_report(s,q) for s in studies]
            row['emitted_support']=[subpixel_support(s,q,1) for s in studies]
            save('trials.json',trials)
            if not(all(m.supported(s,r) for s,r in zip(studies,row['center_support'])) and all(r['passed'] for r in row['emitted_support'])):continue
            candidate=dict(parameters=q,material=co.tolist(),scores=scores,center_support=row['center_support'],emitted_support=row['emitted_support'])
            save('candidate-native.json',candidate)
            public=json.loads((PREV/'candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=113.5;qq['post_sigma']/=113.5;public['parameters']=qq;public['scores']=scores;save('candidate-normalized.json',public)
            for i,(s,a) in enumerate(zip(studies,imgs)):
                np.save(OUT/f'ref{i}-complete.npy',m.image(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q))
                old=np.load(PREV/f'trial0-ref{i}-material.npy')
                panels=[s.target_crop,presentation_module.presentation(s,p,old),presentation_module.presentation(s,q,a)]
                for label,array in zip(['target','baseline','candidate'],panels):
                    cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(array,0,1)*255).astype(np.uint8)[...,::-1])
                cv2.imwrite(str(OUT/f'ref{i}-comparison-width1080.png'),np.rint(np.clip(np.concatenate(panels,axis=0),0,1)*255).astype(np.uint8)[...,::-1])
            break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=1,local_jacobians=1,native_backtracking_trials=len(trials),limits='Source/shape/material/blur/glyphs/AA/masks fixed. Primary independent replay/1080width visual/source acceptance required before count; earlier failures retained.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
