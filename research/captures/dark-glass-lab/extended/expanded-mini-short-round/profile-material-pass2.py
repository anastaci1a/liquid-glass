"""ONE outer-profile + analytic23-material update, strict ten foreground guards."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/expanded-mini-short-round');OUT=ROOT/'profile-material-pass2'
spec=importlib.util.spec_from_file_location('preflight',ROOT/'preflight.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec=importlib.util.spec_from_file_location('compact_composite',ROOT/'composition_helpers.py')
comp=importlib.util.module_from_spec(spec);spec.loader.exec_module(comp)
from paired_fit import Cached
from vector_foreground import coverage
from preview_size import dimensions
cv2.setNumThreads(1)

def save(name,v):
    (OUT/name).write_text(json.dumps(v,indent=2)+'\n')

def foreground_factor(s):
    """Exact linear-background chain, frozen SVG opacities and catalogue art."""
    x0,y0,x1,y1=s.crop;factor=np.ones((y1-y0,x1-x0))
    assert not s.transmission_layers
    for box,alpha,_ in s.foreground_layers:
        vector=s.vector_layers.get(tuple(box))
        if vector:
            style=s.case.get('foreground_styles',{}).get(vector.get('style_key',vector['vector_asset']),{})
            assert 'response' not in style,'Current expanded uses fixed color/opacity only'
            alpha=coverage(s.folder,vector)*style.get('opacity',vector.get('opacity',1.))
        a,b,c,d=box;factor[b-y0:d-y0,a-x0:c-x0]*=1-alpha
    return factor

def local_forms(cache,co,base,plus,minus,index):
    s=cache.study;H,W=cache.H,cache.W;C,J=cache.C,cache.J
    core=J[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:]
    z=C*gain+co[3:6]+(J[...,:-1]@co[6:-3])[...,None]
    # Three existing profile columns normalized to delta_c/.0005; actual centered native secants.
    rim=np.stack([(a.astype(float)-b.astype(float))/2 for a,b in zip(plus,minus)],axis=-1)
    full=s.apply_foreground(base.copy())
    rimfg=np.stack([(s.apply_foreground(a.copy()).astype(float)-s.apply_foreground(b.copy()).astype(float))/2 for a,b in zip(plus,minus)],axis=-1)
    factor=foreground_factor(s);error=base.astype(float)-s.target_crop;fgerror=full.astype(float)-s.target_crop
    masks={'glass':s.valid,'rim':s.rim};boxes={};x0,y0,_,_=s.crop
    for layer in s.case['foreground_layers']:
        a,b,c,d=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')))
        boxes[key]=np.s_[b-y0:d-y0,a-x0:c-x0]
    result={k:[np.zeros((26,26)),np.zeros(26)] for k in [*masks,*boxes]}
    def accum(key,D,e):
        X=D.reshape(-1,26);e=e.ravel();weight=255**2/(3*len(e))
        result[key][0]+=X.T@X*weight;result[key][1]+=X.T@e*weight
    saved=np.lib.format.open_memmap(OUT/f'ref{index}-normalized-material-J.npy',mode='w+',dtype=np.float32,shape=(H,W,3,23))
    np.save(OUT/f'ref{index}-normalized-rim-J.npy',rim.astype(np.float32))
    for c in range(3):
        active=(z[...,c]>0)&(z[...,c]<1)
        avg=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
        F=np.zeros((H,W,23));F[...,c]=avg(active*C[...,c]*(1-core));F[...,c+3]=avg(active)
        F[...,6:20]=avg(active[...,None]*J[...,:-1]);F[...,c+20]=avg(active*C[...,c]*core)
        if s.kernel_sigma(cache.p,'post_sigma')>.001:F=cv2.GaussianBlur(F,(0,0),s.kernel_sigma(cache.p,'post_sigma'))
        F*=.005;saved[:,:,c,:]=F
        D=np.empty((H,W,26));D[...,:3]=rim[...,c,:];D[...,3:]=F
        for key,mask in masks.items():accum(key,D[mask],error[...,c][mask])
        D[...,:3]=rimfg[...,c,:];D[...,3:]*=factor[...,None]
        for key,sl in boxes.items():accum(key,D[sl],fgerror[...,c][sl])
    saved.flush();del saved
    result['loss']=[.7*result['glass'][k]+.3*result['rim'][k] for k in range(2)]
    return result

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Joint study complete; no repeat.');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial Jacobian/trials before recovery')
    assert json.loads((ROOT/'preflight-result.json').read_text())['fit_authorized_by_source']
    OUT.mkdir(exist_ok=True)
    save('started.json',dict(pid=os.getpid(),budget='ONE shared26-parameter update: savedouterprofilecolumns + ONEanalytic23materialJacobian, max4actualnativebacktracks',code='frozen expanded code snapshot from maina1b8b1b5',normalization=dict(outer_profile=.0005,material=.005)))
    native=json.loads((ROOT/'pass-02/pass-02.json').read_text());p=native['parameters'];co=np.asarray(native['material']);baseline=native['scores']
    studies=[m.Study(ROOT/n) for n in ['a','b']];models=[];zeros=[]
    for i,s in enumerate(studies):
        base=np.load(ROOT/f'pass-02/ref{i}-material.npy')
        minus=[];plus=[]
        for key in ['c0','c1','c2']:
            pair=[]
            for sign in [-1,1]:
                q={**p,key:p[key]+sign*.0005};array=s.render(q,co);np.save(OUT/f'{key}-sign{sign}-ref{i}-material.npy',array);pair.append(array)
            minus.append(pair[0]);plus.append(pair[1])
        cache=Cached(s,p);zero=cache.render(co);zeros.append(float(abs(zero-base).max()));assert zeros[-1]<2e-6
        models.append(local_forms(cache,co,base,plus,minus,i));del cache
        print('JACOBIAN',i,'cache_zero',zeros[-1],flush=True)
    save('zero-controls.json',dict(max_pixel_difference=zeros,native_baseline_repeats=0,profile_response_repeats=0))
    save('forms.json',[{k:dict(H=v[0].tolist(),g=v[1].tolist()) for k,v in scene.items()} for scene in models])
    keys=['loss','glass',*baseline[0]['foreground_mse']]
    def norm(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i]['glass']['rmse']**2 if k=='glass' else baseline[i]['foreground_mse'][k])
    def value(i,k,v):
        H,g=models[i][k];return float(2*g@v+v@H@v)
    def jac(i,k,v):
        H,g=models[i][k];return 2*(g+H@v)
    fun=lambda v:sum(value(i,'loss',v)/norm(i,'loss') for i in range(2))/2
    funjac=lambda v:sum((jac(i,'loss',v)/norm(i,'loss') for i in range(2)))/2
    constraints=lambda v:np.array([-value(i,k,v)/norm(i,k) for i in range(2) for k in keys])
    constraintsjac=lambda v:np.array([-jac(i,k,v)/norm(i,k) for i in range(2) for k in keys])
    opt=minimize(fun,np.zeros(26),jac=funjac,method='SLSQP',bounds=[(-1,1)]*26,constraints=[dict(type='ineq',fun=constraints,jac=constraintsjac)],options=dict(maxiter=100,ftol=1e-12))
    dw=.0005*opt.x[:3];dc=.005*opt.x[3:]
    save('proposal.json',dict(delta_profile=dw.tolist(),delta_material=dc.tolist(),model_relative_loss_change=float(opt.fun),solver_success=bool(opt.success),message=opt.message,model_constraint_residuals=constraints(opt.x).tolist(),limits='ONElocal clipped shading+fixed-compositor Jacobian; savedactualoutersecants; no new target/glyph/image coefficients. Model/solver status never accepts.'))
    trials=[];candidate=None
    # Quantization-derived meaningfulness check is NOT a regression allowance.
    noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
    if opt.fun < -1e-12:
        for j,t in enumerate([1.,.5,.25,.125]):
            q={**p,**{f'c{k}':float(p[f'c{k}']+t*dw[k]) for k in range(3)}};new=co+t*dc
            imgs=[s.render(q,new) for s in studies];scores=[m.guards(s,q,a)[0] for s,a in zip(studies,imgs)]
            row=dict(factor=t,parameters=q,material=new.tolist(),scores=scores,guarded=comp.good(scores,baseline),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
            for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
            trials.append(row);save('trials.json',trials)
            print('NATIVE',t,[s['E'] for s in scores],'guarded',row['guarded'],flush=True)
            if not(row['guarded'] and row['meaningful']):continue
            candidate=dict(parameters=q,material=new.tolist(),scores=scores,source_proof='FRESH changed-map original whole+ALLscored finite3sigma proof below')
            candidate['source_proof']=[m.emitted(s,q,i) for i,s in enumerate(studies)]
            assert all(r['passed'] for r in candidate['source_proof']), 'Changed-map support failure; do not accept'
            save('candidate-native.json',candidate)
            public=json.loads((ROOT/'authoritative-paired21.json').read_text());qq=q.copy();qq['sigma']/=studies[0].L;qq['post_sigma']/=studies[0].L;public['parameters']=qq;public['material']=new.tolist();public['scores']=scores;save('candidate-normalized.json',public)
            for i,(s,a) in enumerate(zip(studies,imgs)):
                np.save(OUT/f'ref{i}-complete.npy',comp.composition(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q))
                old=np.load(ROOT/f'pass-02/ref{i}-material.npy');panels=[s.target_crop,comp.composition(s,p,old,True),comp.composition(s,q,a,True)]
                size=dimensions(*[s.crop[2]-s.crop[0],s.crop[3]-s.crop[1]],large=True)
                for label,array in zip(['target','baseline','candidate'],panels):
                    image=cv2.resize(array,size,interpolation=cv2.INTER_LINEAR)
                    cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(image,0,1)*255).astype(np.uint8)[...,::-1])
            break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=0,native_resolution_noise_floor=noise,limits='No fixed percent gain; strict bothE/glass/exterior+ALL10glyph/artwork. Onejoint existing update, no source/shape/blur/style/AA/mask epoch change; primary acceptance before count/commit.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
