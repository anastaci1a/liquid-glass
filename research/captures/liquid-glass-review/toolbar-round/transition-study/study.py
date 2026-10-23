import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.optimize import minimize
import toolbar_candidate as base
import toolbar_transition as model
from reproduce import CASES,scores
from progress_gate import error,evaluate
root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-transition');out.mkdir(exist_ok=True)
case=CASES['regular'];p=json.loads((root/'candidate-with-shadow-recipe.json').read_text());before=json.loads((root/'candidate-with-shadow.json').read_text());source=np.asarray(Image.open(root/'source.png')).astype(float)/255;target=np.asarray(Image.open(root/'target.png')).astype(np.float32)/255
B=source[285:845,475:1445];T=target[285:845,475:1445];masks=np.load(root/'frozen-masks.npz');shadow=base.gaussian_coverage_shadow(case,p);C0=np.load(root/'candidate-with-shadow-material.npy');b0=p['parameters']['tangent_band'];records=[];native=[]
for family in ['empirical','coupled_difference']:
    q=copy.deepcopy(p);q['transition']={'family':family,'exponent':4.,'band':b0,'normal_delta':[0,0,0]};C,a=model.render(source,case,q);delta=float(np.max(np.abs(C-C0)));assert delta==0,(family,delta)
print('BASE IDENTITIES EXACT',flush=True)
def preset(v,family):
    q=copy.deepcopy(p);q['transition']={'family':'coupled_difference' if family==3 else 'empirical','exponent':float(v[0]),'band':float(v[1]),'normal_delta':list(map(float,v[2:5])) if family==2 else [0,0,0]};return q
warm=[4.,b0]
for family,name,bounds,limit in [(1,'shared exponent/band',[(3.,6.),(.3,.55)],90),(2,'joint exponent/band plus normal coefficients2,3,4',[(3.,6.),(.3,.55)]+[(-.02,.02)]*3,180),(3,'coupled potential difference',[(4.,6.),(.3,.55)],90)]:
    evaluations=[];start=warm+[0,0,0] if family==2 else [4.,b0];best={'loss':float('inf'),'v':start};t0=time.time()
    def objective(v):
        q=preset(v,family);C,_=model.render(source,case,q,samples=1);D=(C-T)*255;loss=float(.7*np.mean(D[masks['glass']]**2)+.3*np.mean(D[masks['rim']]**2));evaluations.append({'v':list(map(float,v)),'training_L':loss})
        if loss<best['loss']:best.update(loss=loss,v=list(map(float,v)))
        if len(evaluations)%20==0:print('TRAIN',family,len(evaluations),best['loss'],flush=True)
        return loss
    initial_loss=objective(start);fit=minimize(objective,start,method='Powell',bounds=bounds,options={'maxfev':limit,'xtol':.0003,'ftol':1e-7});v=best['v'];q=preset(v,family);C,a=model.render(source,case,q);sc=scores(C,T,case);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);ext=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)));state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':ext}}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ok=all(r['passed'] for r in gate['observations'].values());E=error(state['observations']['A'])
    record={'family':family,'name':name,'initial_training_L':initial_loss,'best_training_L':best['loss'],'best_v':v,'training_evaluations':evaluations,'seconds':time.time()-t0,'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'scores':state,'E':E,'gate':gate,'native_pass':ok,'native_samples_per_axis':4,'training_samples_per_axis':1,'training_approximation_not_acceptance':True};records.append(record);native.append((ok,E,q,C,a,full,state));print('NATIVE',family,E,sc['all_glass']['rmse'],ext,ok,flush=True)
    folder=out/f'family-{family}';folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(state,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(folder/'clean-preview.png');(out/'study.json').write_text(json.dumps({'before':before,'families':records,'qualifying_passes_counted':0,'limits':'same-frame bounded fitting, source estimates retained; no independent primary review of new proposals'},indent=2)+'\n')
    if family==1:warm=v[:2]
valid=[x for x in native if x[0]];chosen=min(valid or native,key=lambda x:x[1]);ok,E,q,C,a,full,state=chosen;(out/'result.json').write_text(json.dumps({'any_numerical_qualifier':bool(valid),'best_E':E,'best_recipe':q,'best_scores':state,'counted_passes':0,'next':'procedural model review after these3 families, primary independent acceptance before any next pass'},indent=2)+'\n');print('RESULT',bool(valid),E,flush=True)
