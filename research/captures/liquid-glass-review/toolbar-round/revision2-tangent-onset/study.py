import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.optimize import minimize
import toolbar_candidate as model
from reproduce import scores
from progress_gate import evaluate,error
package=Path('/tmp/agent-toolbar-evidence-package');root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-revision2-tangent');out.mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text());before=json.loads((package/'primary-verification.json').read_text())['candidate'];case=p['case'];source=np.asarray(Image.open(package/'inputs/source.png')).astype(float)/255;target=np.asarray(Image.open(package/'inputs/target.png')).astype(np.float32)/255
x0,y0,x1,y1=case['crop'];B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1];masks=np.load(root/'frozen-masks.npz');shadow=model.gaussian_coverage_shadow(case,p);old=np.load('/tmp/agent-toolbar-inner-settlement/material.npy')
C,a=model.render(source,case,p);assert float(np.max(np.abs(C-old)))==0
basev=[p['parameters']['tangent'],p['parameters']['tangent_band'],4.];records=[];native=[];bounds=[(.1,.3),(.3,.75),(3.,10.)]
def preset(v):
    q=copy.deepcopy(p);q['parameters']['tangent']=float(v[0]);q['parameters']['tangent_band']=float(v[1]);q['tangent_exponent']=float(v[2]);return q
C,a=model.render(source,case,preset(basev));assert float(np.max(np.abs(C-old)))==0;print('BASE RECOVERY EXACT',before,flush=True)
for seed,start in enumerate([basev,[.22,.6,7.]],1):
    rows=[];best=[float('inf'),start];t0=time.time()
    def objective(v):
        C,_=model.render(source,case,preset(v),samples=1);D=(C-T)*255;L=float(.7*np.mean(D[masks['glass']]**2)+.3*np.mean(D[masks['rim']]**2));rows.append({'v':list(map(float,v)),'training_L':L})
        if L<best[0]:best[:]=[L,list(map(float,v))]
        if len(rows)%30==0:print('TRAIN',seed,len(rows),best,flush=True)
        return L
    objective(start);fit=minimize(objective,start,method='Powell',bounds=bounds,options={'maxfev':300,'xtol':.00015,'ftol':1e-8});q=preset(best[1]);C,a=model.render(source,case,q);sc=scores(C,T,case);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);ext=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)));state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':ext}}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ok=all(x['passed'] for x in gate['observations'].values());E=error(state['observations']['A'])
    record={'seed':seed,'start':start,'best_v':best[1],'training_L':best[0],'training_evaluations':rows,'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'seconds':time.time()-t0,'bound_activity':[min(v-lo,hi-v)<.02*(hi-lo) for v,(lo,hi) in zip(best[1],bounds)],'scores':state,'E':E,'gate':gate,'native_pass':ok,'counted_passes':0};records.append(record);native.append((ok,E,q,state,C,a,full));folder=out/f'seed-{seed}';folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(state,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(folder/'clean-preview.png');(out/'study.json').write_text(json.dumps({'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','before':before,'trials':records,'counted_passes':0},indent=2)+'\n');print('NATIVE',seed,E,ext,ok,fit.success,flush=True)
valid=[x for x in native if x[0]];best=min(valid or native,key=lambda x:x[1]);(out/'result.json').write_text(json.dumps({'any_numerical_qualifier':bool(valid),'best_E':best[1],'best_recipe':best[2],'best_scores':best[3],'counted_passes':0,'note':'ONE bounded tangent family, two starts; full4x4 native guards, independent primary review pending'},indent=2)+'\n');print('RESULT',bool(valid),best[1],flush=True)
