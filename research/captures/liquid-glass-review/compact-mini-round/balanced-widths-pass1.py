"""One two-width proposal from retained responses; native strict guards decide."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/helper-toolbar-work/compact-mini-round');OUT=ROOT/'balanced-widths-pass1'
spec=importlib.util.spec_from_file_location('width_helpers',ROOT/'rim-width-neighborhood.py');comp=importlib.util.module_from_spec(spec);spec.loader.exec_module(comp);m=comp.m
cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Complete: no repeat');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial process/artifacts; no automatic restart')
    OUT.mkdir(exist_ok=True);save('started.json',dict(pid=os.getpid(),budget='ONE saved-response balanced widths proposal; each <=.00025; max4 actual native backtracks',baseline='accepted Compact pass1 a92fc7bd',surrogate='Rim secant uses pre-pass1 material/baseline and is NOT exact compatible Jacobian. Thin secant uses accepted pass1 material. Actual native tests alone decide.'))
    native=json.loads((ROOT/'joint-rim-material/candidate-native.json').read_text());p=native['parameters'];co=np.array(native['material']);baseline=native['scores'];studies=[m.Study(ROOT/n) for n in ['a','b']];models=[];old=[]
    for i,s in enumerate(studies):
        base=np.load(ROOT/f'joint-rim-material/trial1-ref{i}-material.npy');old.append(base)
        columns=[]
        for folder in ['rim-width-neighborhood','thin-width-pass1']:
            minus=np.load(ROOT/f'{folder}/trial0-ref{i}-material.npy').astype(float);plus=np.load(ROOT/f'{folder}/trial1-ref{i}-material.npy').astype(float);columns.append((plus-minus)/2)
        D=np.stack(columns,axis=-1);err=base.astype(float)-s.target_crop
        forms={}
        def form(key,d,e):
            X=d.reshape(-1,2);e=e.ravel();w=255**2/len(e);forms[key]=dict(H=(X.T@X*w).tolist(),g=(X.T@e*w).tolist())
        form('glass',D[s.valid],err[s.valid]);form('rim',D[s.rim],err[s.rim]);forms['loss']={k:(.7*np.array(forms['glass'][k])+.3*np.array(forms['rim'][k])).tolist() for k in ['H','g']}
        full=s.apply_foreground(base.copy()).astype(float);FgD=np.stack([(s.apply_foreground((base.astype(float)+col).astype(np.float32)).astype(float)-s.apply_foreground((base.astype(float)-col).astype(np.float32)).astype(float))/2 for col in columns],axis=-1)
        x0,y0,_,_=s.crop
        for layer in s.case['foreground_layers']:
            a,b,c,d=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));sl=np.s_[b-y0:d-y0,a-x0:c-x0];form(key,FgD[sl],(full-s.target_crop)[sl])
        models.append(forms)
    save('saved-response-forms.json',models)
    keys=['loss','glass',*baseline[0]['foreground_mse']]
    def scale(i,k):return max(1.,baseline[i]['loss'] if k=='loss' else baseline[i]['glass']['rmse']**2 if k=='glass' else baseline[i]['foreground_mse'][k])
    def val(i,k,x):f=models[i][k];return (2*np.array(f['g'])@x+x@np.array(f['H'])@x)/scale(i,k)
    def jac(i,k,x):f=models[i][k];return 2*(np.array(f['g'])+np.array(f['H'])@x)/scale(i,k)
    fun=lambda x:sum(val(i,'loss',x) for i in range(2))/2
    fj=lambda x:sum((jac(i,'loss',x) for i in range(2)))/2
    constraints=lambda x:np.array([-val(i,k,x) for i in range(2) for k in keys])
    cj=lambda x:np.array([-jac(i,k,x) for i in range(2) for k in keys])
    opt=minimize(fun,np.zeros(2),jac=fj,bounds=[(-1,1)]*2,method='SLSQP',constraints=[dict(type='ineq',fun=constraints,jac=cj)],options=dict(maxiter=60,ftol=1e-13))
    delta=.00025*opt.x;save('proposal.json',dict(delta_rim=float(delta[0]),delta_thin=float(delta[1]),model_relative_loss_change=float(opt.fun),solver_success=bool(opt.success),message=opt.message,constraints=constraints(opt.x).tolist(),limitations='Rim response from nearby PRE-pass1 material is only proposal surrogate. No new derivative, source or material change; solver does not accept native result.'))
    print('PROPOSAL',delta.tolist(),float(opt.fun),opt.message,flush=True)
    trials=[];candidate=None
    noise=[4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for b in baseline]
    if opt.fun < -1e-12 and np.max(abs(delta))>1e-12:
        for j,t in enumerate([1.,.5,.25,.125]):
            q={**p,'rim_width':float(p['rim_width']+t*delta[0]),'thin_width':float(p['thin_width']+t*delta[1])}
            imgs=[s.render(q,co) for s in studies];scores=[m.guards(s,q,a)[0] for s,a in zip(studies,imgs)]
            row=dict(factor=t,parameters=q,scores=scores,guarded=comp.good(scores,baseline),meaningful=any(b['E']-s['E']>n for s,b,n in zip(scores,baseline,noise)))
            for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
            trials.append(row);save('trials.json',trials);print('NATIVE',t,[s['E'] for s in scores],row['guarded'],flush=True)
            if not(row['guarded'] and row['meaningful']):continue
            candidate=dict(parameters=q,material=co.tolist(),scores=scores,source_proof='Only lighting widths changed: original whole/scored discrete native source proof transfers unchanged')
            save('candidate-native.json',candidate);public=json.loads((ROOT/'joint-rim-material/candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=studies[0].L;qq['post_sigma']/=studies[0].L;public.update(parameters=qq,scores=scores);save('candidate-normalized.json',public)
            for i,(s,a) in enumerate(zip(studies,imgs)):
                np.save(OUT/f'ref{i}-complete.npy',comp.composition(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q))
                size=comp.dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=True)
                for label,array in zip(['target','baseline','candidate'],[s.target_crop,comp.composition(s,p,old[i],True),comp.composition(s,q,a,True)]):
                    cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(cv2.resize(array,size,interpolation=cv2.INTER_LINEAR),0,1)*255).astype(np.uint8)[...,::-1])
            break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=1,proposal=json.loads((OUT/'proposal.json').read_text()),native_resolution_noise_floor=noise,limitations='No new derivatives. Nearby old-material rim response is proposal surrogate only. Strict original bothE/glass/exterior/all10FG, fixed acceptedpass1 material. No epsilon, count or source/epoch changes.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)
if __name__=='__main__':main()
