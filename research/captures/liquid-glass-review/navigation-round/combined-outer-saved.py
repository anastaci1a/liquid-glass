"""One saved-score quadratic proposal, at most four native backtracks."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import minimize
BASE=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
OUT=BASE.parent/'combined-outer-saved'
spec=importlib.util.spec_from_file_location('old_driver',BASE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def save(name,v):
    (OUT/name).write_text(json.dumps(v,indent=2)+'\n')

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Already complete; no rerun.');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial artifacts before recovery')
    OUT.mkdir(exist_ok=True)
    save('started.json',dict(pid=os.getpid(),budget='ONE saved-score combined direction, factors1,.5,.25,.125 maximum'))
    state=json.loads((BASE/'baseline-public.json').read_text())
    baseline=json.loads((BASE/'baseline.json').read_text())
    old=json.loads((BASE/'trials.json').read_text())
    forms=[]
    for i in range(2):
        scene=[]
        for kind in ['E','glass']:
            value=lambda s:s['E'] if kind=='E' else s['glass']['rmse']
            z=value(baseline[i]);g=[];diag=[]
            for k in range(3):
                lo=value(next(r for r in old if r['coefficient']==k and r['delta']<0)['scores'][i])
                hi=value(next(r for r in old if r['coefficient']==k and r['delta']>0)['scores'][i])
                g.append((hi-lo)/2);diag.append(max(0.,hi+lo-2*z))
            scene.append((z,np.array(g),np.array(diag)))
        forms.append(scene)
    # x=delta_c/.002. No new native derivatives or response images.
    # Diagonal curvature ignores mixed terms; predictive proposal only.
    def constraints(v):
        x=v[:3];t=v[3];r=[1-np.sum(abs(x))]
        for scene in forms:
            for j,(z,g,h) in enumerate(scene):
                change=g@x+.5*np.dot(h,x*x)
                r.append(-change/z-(t if j==0 else 0))
        return np.array(r)
    opt=minimize(lambda v:-v[3],np.zeros(4),method='SLSQP',bounds=[(-1,1)]*3+[(0,.01)],constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=80,ftol=1e-12))
    direction=.002*opt.x[:3]
    save('proposal.json',dict(direction=direction.tolist(),model_common_relative_E_improvement=float(opt.x[3]),solver_success=bool(opt.success),solver_message=opt.message,model_constraint_residuals=constraints(opt.x).tolist(),forms=[[[z,g.tolist(),h.tolist()] for z,g,h in sc] for sc in forms],limits='Saved scalar native scores only; full six response images were not retained. No derivatives repeated to reconstruct them. Mixed curvature absent; actual native guards alone decide.'))
    trials=[];candidate=None
    if np.max(abs(direction))>1e-12 and opt.x[3]>0:
        studies=[m.Study(BASE/n) for n in ['a','b']]
        p=state['parameters'].copy();L=min(studies[0].case['half']);p['sigma']*=L;p['post_sigma']*=L
        co=np.asarray(state['material'])
        for j,factor in enumerate([1.,.5,.25,.125]):
            q={**p,**{f'c{k}':float(p[f'c{k}']+factor*direction[k]) for k in range(3)}}
            imgs=[s.render(q,co) for s in studies]
            scores=[m.guards(s,q,a) for s,a in zip(studies,imgs)]
            row=dict(factor=factor,parameters=q,scores=scores,guarded=m.good(scores,baseline),meaningful=any(o['E']-n['E']>1e-5 for n,o in zip(scores,baseline)))
            for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
            trials.append(row);save('trials.json',trials)
            print('NATIVE',factor,[s['E'] for s in scores],row['guarded'],flush=True)
            if not (row['guarded'] and row['meaningful']):continue
            row['source_support']=[m.coverage_report(s,q) for s in studies]
            save('trials.json',trials)
            if not all(m.supported(s,r) for s,r in zip(studies,row['source_support'])):continue
            candidate=row
            native=q.copy();public=q.copy();public['sigma']/=L;public['post_sigma']/=L
            save('candidate-native.json',dict(parameters=native,material=state['material'],scores=scores))
            save('candidate-normalized.json',{**state,'parameters':public,'scores':scores})
            for i,(s,a) in enumerate(zip(studies,imgs)):
                comp=m.image(s,q,a);np.save(OUT/f'ref{i}-complete.npy',comp)
                oldimg=np.load(BASE/f'{i}-baseline-material.npy')
                panel=np.concatenate([s.target_crop,m.image(s,p,oldimg),comp],axis=0)
                scale=min(1280/panel.shape[1],720/panel.shape[0],1.)
                preview=cv2.resize(panel,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
                cv2.imwrite(str(OUT/f'ref{i}-target-baseline-candidate-720.png'),np.rint(np.clip(preview,0,1)*255).astype(np.uint8)[...,::-1])
            break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,count=0,limits='New combined proposal under explicit latest authority; preceding eight failures preserved. No fixed percentage minimum. Native masks/epoch unchanged;720 preview only. Primary independent replay/visual/source acceptance required.'))
    print('COMPLETE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
