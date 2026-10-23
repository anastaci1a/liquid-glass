"""One foreground-aware existing23-coefficient shared-material update."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
BASE=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
PREV=BASE.parent/'combined-outer-saved'
OUT=BASE.parent/'pass2-shared-material'
spec=importlib.util.spec_from_file_location('prior',BASE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from paired_fit import Cached
from vector_foreground import coverage
from foreground_response import response
cv2.setNumThreads(1)

def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')

def foreground_factor(s,pred,channel):
    """Chain derivative of the FIXED nonlinear foreground compositor."""
    out=pred.copy();factor=np.ones(pred.shape[:2]);x0,y0,_,_=s.crop
    for box,alpha,color in s.foreground_layers:
        a,b,c,d=box;sl=np.s_[b-y0:d-y0,a-x0:c-x0]
        region=out[sl];vector=s.vector_layers.get(tuple(box))
        style=s.case.get('foreground_styles',{}).get(vector.get('style_key',vector['vector_asset']),{}) if vector else {}
        if 'color' in style:color=np.broadcast_to(np.asarray(style['color'],np.float32),region.shape)
        if vector:
            alpha=coverage(s.folder,vector)*style.get('opacity',vector.get('opacity',1.))
            if 'response' in style:
                alpha=coverage(s.folder,vector);pars=np.asarray(style['response'])
                B=region[...,channel];t,r,g=pars[channel]
                derivative=t*r*g*np.maximum(1-B,1e-12)**(g-1)
                derivative=np.where((B>0)&(B<1),derivative,0.)
                factor[sl]*=(1-alpha)+alpha*derivative
                color=response(region,pars)
            else:factor[sl]*=1-alpha
        else:factor[sl]*=1-alpha
        region[:]=region*(1-alpha[...,None])+color*alpha[...,None]
    assert not s.transmission_layers,'No foreground calibration allowed'
    assert np.array_equal(out,s.apply_foreground(pred.copy())),'Foreground chain changed compositor'
    return factor

def forms(cache,co,pred):
    s=cache.study;C,J=cache.C,cache.J;H,W=cache.H,cache.W
    core=J[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:]
    z=C*gain+co[3:6]+(J[...,:-1]@co[6:-3])[...,None]
    fg=s.apply_foreground(pred.copy());error=pred.astype(float)-s.target_crop;fgerror=fg.astype(float)-s.target_crop
    masks={'glass':s.valid,'rim':s.rim};boxes={}
    x0,y0,_,_=s.crop
    for layer in s.case['foreground_layers']:
        if 'vector_asset' in layer and layer['mode']!='transmission' and layer.get('fit_style',True):
            a,b,c,d=layer['box'];boxes[layer.get('style_key',layer['vector_asset'])]=np.s_[b-y0:d-y0,a-x0:c-x0]
    result={k:[np.zeros((23,23)),np.zeros(23)] for k in [*masks,*boxes]}
    def accum(key,X,e):
        X=X.reshape(-1,23);e=e.ravel();weight=255**2/(3*len(e))
        result[key][0]+=X.T@X*weight;result[key][1]+=X.T@e*weight
    for c in range(3):
        active=(z[...,c]>0)&(z[...,c]<1)
        avg=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
        F=np.zeros((H,W,23))
        F[...,c]=avg(active*C[...,c]*(1-core));F[...,c+3]=avg(active)
        F[...,6:20]=avg(active[...,None]*J[...,:-1]);F[...,c+20]=avg(active*C[...,c]*core)
        if s.kernel_sigma(cache.p,'post_sigma')>.001:F=cv2.GaussianBlur(F,(0,0),s.kernel_sigma(cache.p,'post_sigma'))
        for name,mask in masks.items():accum(name,F[mask],error[...,c][mask])
        F*=foreground_factor(s,pred,c)[...,None]
        for name,sl in boxes.items():accum(name,F[sl],fgerror[...,c][sl])
    result['loss']=[.7*result['glass'][k]+.3*result['rim'][k] for k in range(2)]
    return result

def presentation(s,p,pred):
    """Nearest-defined RGB is exterior PRESENTATION ONLY, never a source edit."""
    x0,y0,x1,y1=s.crop
    from scipy.ndimage import distance_transform_edt
    known=cv2.imread(str(s.folder/'known.png'),0)>0
    idx=distance_transform_edt(~known,return_distances=False,return_indices=True)
    clean=s.source[idx[0][y0:y1,x0:x1],idx[1][y0:y1,x0:x1]]
    clean=clean*(1-m.shadow(s,p,s.x,s.y)[...,None])
    alpha=s.shape_coverage(p)
    return s.apply_foreground((pred*alpha[...,None]+clean*(1-alpha[...,None])).astype(np.float32))

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Completed pass2 study retained; no rerun.');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect retained partial evidence before recovery')
    OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),budget='ONE material update, max4actual trials1,.5,.25,.125; no optical or foreground recalibration'))
    accepted=json.loads((PREV/'candidate-native.json').read_text());p=accepted['parameters'];co=np.array(accepted['material']);baseline=accepted['scores']
    studies=[m.Study(BASE/n) for n in ['a','b']];models=[];zeros=[]
    for i,s in enumerate(studies):
        cache=Cached(s,p);pred=np.load(PREV/f'trial0-ref{i}-material.npy')
        zero=cache.render(co);zeros.append(float(abs(zero-pred).max()))
        assert zeros[-1]<2e-6,'Material cache zero mismatch'
        models.append(forms(cache,co,pred));del cache
        print('MODEL',i,'zero_max',zeros[-1],flush=True)
    save('zero-controls.json',dict(max_pixel_difference=zeros,baseline_native_replay='Primary accepted-verification.json reused, no native baseline render'))
    save('local-forms.json',[{k:dict(H=v[0].tolist(),g=v[1].tolist()) for k,v in scene.items()} for scene in models])
    radius=.005
    def change(scene,key,v):
        H,g=models[scene][key];delta=radius*v
        return float(2*g@delta+delta@H@delta)
    def jac(scene,key,v):
        H,g=models[scene][key];return 2*radius*(g+H@(radius*v))
    def norm(i,key):
        s=baseline[i]
        return max(1.,s['loss'] if key=='loss' else s['glass']['rmse']**2 if key=='glass' else s['foreground_mse'][key])
    keys=['loss','glass',*baseline[0]['foreground_mse']]
    objective=lambda v:sum(change(i,'loss',v)/norm(i,'loss') for i in range(2))/2
    objective_jac=lambda v:sum((jac(i,'loss',v)/norm(i,'loss') for i in range(2)))/2
    constraints=lambda v:np.array([-change(i,k,v)/norm(i,k) for i in range(2) for k in keys])
    constraints_jac=lambda v:np.array([-jac(i,k,v)/norm(i,k) for i in range(2) for k in keys])
    result=minimize(objective,np.zeros(23),jac=objective_jac,method='SLSQP',bounds=[(-1,1)]*23,constraints=[dict(type='ineq',fun=constraints,jac=constraints_jac)],options=dict(maxiter=100,ftol=1e-12))
    delta=radius*result.x
    save('proposal.json',dict(radius=radius,delta_material=delta.tolist(),predicted_relative_loss_change=float(result.fun),solver_success=bool(result.success),message=result.message,local_constraint_residuals=constraints(result.x).tolist(),limits='Clipping/nonlinear foreground analytic local model only; original actual native guards alone accept. No color/gamma/source/geometry operator added.'))
    print('PROPOSAL',result.success,result.fun,flush=True)
    trials=[];candidate=None
    for j,factor in enumerate([1.,.5,.25,.125]):
        new=co+factor*delta
        imgs=[s.render(p,new) for s in studies];scores=[m.guards(s,p,a) for s,a in zip(studies,imgs)]
        row=dict(factor=factor,material=new.tolist(),scores=scores,guarded=m.good(scores,baseline),meaningful=any(o['E']-n['E']>1e-5 for n,o in zip(scores,baseline)))
        for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
        trials.append(row);save('trials.json',trials)
        print('NATIVE',factor,[s['E'] for s in scores],row['guarded'],flush=True)
        if not(row['guarded'] and row['meaningful']):continue
        candidate=dict(parameters=p,material=new.tolist(),scores=scores,source_support='UNCHANGED accepted pass1 center+emitted-ray proof; map/blur/material-source geometry unchanged')
        save('candidate-native.json',candidate)
        public=json.loads((PREV/'candidate-normalized.json').read_text());public['material']=new.tolist();public['scores']=scores;save('candidate-normalized.json',public)
        for i,(s,a) in enumerate(zip(studies,imgs)):
            np.save(OUT/f'ref{i}-complete.npy',m.image(s,p,a))
            np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(p))
            old=np.load(PREV/f'trial0-ref{i}-material.npy')
            panels=[s.target_crop,presentation(s,p,old),presentation(s,p,a)]
            for name,array in zip(['target','baseline','candidate'],panels):
                cv2.imwrite(str(OUT/f'ref{i}-{name}-width1080.png'),np.rint(np.clip(array,0,1)*255).astype(np.uint8)[...,::-1])
            cv2.imwrite(str(OUT/f'ref{i}-comparison-width1080.png'),np.rint(np.clip(np.concatenate(panels,axis=0),0,1)*255).astype(np.uint8)[...,::-1])
        break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=1,limits='Pass2 numeric proposal only; primary independent replay/source/1080-width visual acceptance required. One shared23coeff update, no speculative audit.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
