import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.optimize import minimize
from scipy.interpolate import BSpline
import toolbar_candidate as base
import toolbar_supported_transition as model
from reproduce import CASES,scores
from progress_gate import error,evaluate
root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-supported-transition');out.mkdir(exist_ok=True)
case=CASES['regular'];p=json.loads((root/'candidate-with-shadow-recipe.json').read_text());before=json.loads((root/'candidate-with-shadow.json').read_text());source=np.asarray(Image.open(root/'source.png')).astype(float)/255;target=np.asarray(Image.open(root/'target.png')).astype(np.float32)/255
B=source[285:845,475:1445];T=target[285:845,475:1445];masks=np.load(root/'frozen-masks.npz');shadow=base.gaussian_coverage_shadow(case,p);C0=np.load(root/'candidate-with-shadow-material.npy');b0=p['parameters']['tangent_band'];records=[];native=[]
knots=[0]*4+[.015,.04,.09,.2,.45,.75]+[1]*4;support=[]
for i in [4,5,6]:
    co=np.zeros(10);co[i]=1;basis=BSpline(knots,co,3);lo,hi=knots[i],knots[i+4];left=float(basis(lo-1e-6));assert left==0
    support.append({'index':i,'support':[lo,hi],'left_derivatives':[float(basis.derivative(n)(lo)) for n in [0,1,2]],'right_derivatives':[float(basis.derivative(n)(hi)) for n in [0,1,2]]})
(out/'basis-support.json').write_text(json.dumps(support,indent=2)+'\n');print('SUPPORT',support,flush=True)
def preset(v,mode):
    q=copy.deepcopy(p);q['supported_transition']={'mode':mode,'exponent':float(v[0]) if mode=='expanded' else 4.,'band':float(v[1]) if mode=='expanded' else b0,'normal_delta':list(map(float,v[2:5] if mode=='expanded' else v))};return q
for mode in ['expanded','inner']:
    zero=[4,b0,0,0,0] if mode=='expanded' else [0,0,0];C,a=model.render(source,case,preset(zero,mode));delta=float(np.max(np.abs(C-C0)));assert delta==0,(mode,delta)
print('BASE IDENTITIES EXACT',flush=True)
old=[.012919459789540455,-.0024739147334620452,.014323636443880383]
for mode,seeds,bounds,limit in [('expanded',[[6.,.5484189672120531,*old],[8.,.70,*old]],[(3.,10.),(.3,.75)]+[(-.04,.04)]*3,260),('inner',[[0,0,0],[.01,0,0]],[(-.04,.04)]*3,180)]:
    for seed,start in enumerate(seeds,1):
        evaluations=[];best={'loss':float('inf'),'v':start};t0=time.time()
        def objective(v):
            q=preset(v,mode);C,_=model.render(source,case,q,samples=1);D=(C-T)*255;loss=float(.7*np.mean(D[masks['glass']]**2)+.3*np.mean(D[masks['rim']]**2));evaluations.append({'v':list(map(float,v)),'training_L':loss})
            if loss<best['loss']:best.update(loss=loss,v=list(map(float,v)))
            if len(evaluations)%30==0:
                print('TRAIN',mode,seed,len(evaluations),best['loss'],flush=True)
                (out/'in-progress.json').write_text(json.dumps({'mode':mode,'seed':seed,'best':best,'training_evaluations':evaluations,'accepted':False},indent=2)+'\n')
            return loss
        initial_loss=objective(start);fit=minimize(objective,start,method='Powell',bounds=bounds,options={'maxfev':limit,'xtol':.0002,'ftol':1e-8});v=best['v'];q=preset(v,mode);C,a=model.render(source,case,q);sc=scores(C,T,case);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);ext=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)));state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':ext}}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ok=all(r['passed'] for r in gate['observations'].values());E=error(state['observations']['A'])
        activity=[{'index':i,'value':float(t),'bounds':list(bounds[i]),'near_bound':min(t-bounds[i][0],bounds[i][1]-t)<.02*(bounds[i][1]-bounds[i][0])} for i,t in enumerate(v)]
        record={'mode':mode,'seed':seed,'initial_training_L':initial_loss,'best_training_L':best['loss'],'best_v':v,'bound_activity':activity,'training_evaluations':evaluations,'seconds':time.time()-t0,'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'scores':state,'E':E,'gate':gate,'native_pass':ok,'native_samples_per_axis':4,'training_samples_per_axis':1,'training_approximation_not_acceptance':True};records.append(record);native.append((ok,E,q,C,a,full,state));print('NATIVE',mode,seed,E,sc['all_glass']['rmse'],ext,ok,flush=True)
        folder=out/f'{mode}-{seed}';folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(state,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(folder/'clean-preview.png');(out/'study.json').write_text(json.dumps({'before':before,'trials':records,'qualifying_passes_counted':0,'limits':'two bounded variants with two starts each; same frozen inputs/guards; no independent primary review'},indent=2)+'\n')
valid=[x for x in native if x[0]];chosen=min(valid or native,key=lambda x:x[1]);ok,E,q,C,a,full,state=chosen;(out/'result.json').write_text(json.dumps({'any_numerical_qualifier':bool(valid),'best_E':E,'best_recipe':q,'best_scores':state,'counted_passes':0},indent=2)+'\n');print('RESULT',bool(valid),E,flush=True)
