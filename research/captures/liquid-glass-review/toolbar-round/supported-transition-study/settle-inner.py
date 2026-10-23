import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.optimize import minimize
import toolbar_candidate as base
import toolbar_supported_transition as model
from reproduce import CASES,scores
from progress_gate import evaluate,error
root=Path('/tmp/agent-toolbar-run');prior=Path('/tmp/agent-toolbar-supported-transition');out=Path('/tmp/agent-toolbar-inner-settlement');out.mkdir(exist_ok=True)
p=json.loads((prior/'inner-2/recipe.json').read_text());before=json.loads((root/'candidate-with-shadow.json').read_text());source=np.asarray(Image.open(root/'source.png')).astype(float)/255;target=np.asarray(Image.open(root/'target.png')).astype(np.float32)/255;T=target[285:845,475:1445];B=source[285:845,475:1445];masks=np.load(root/'frozen-masks.npz');case=CASES['regular'];shadow=base.gaussian_coverage_shadow(case,p);start=p['supported_transition']['normal_delta'];rows=[];best=[1e10,start]
def preset(v):
    q=copy.deepcopy(p);q['supported_transition']['normal_delta']=list(map(float,v));return q
def objective(v):
    C,_=model.render(source,case,preset(v),samples=1);D=(C-T)*255;L=float(.7*np.mean(D[masks['glass']]**2)+.3*np.mean(D[masks['rim']]**2));rows.append({'v':list(map(float,v)),'training_L':L})
    if L<best[0]:best[:]=[L,list(map(float,v))]
    if len(rows)%30==0:print('SETTLE',len(rows),best,flush=True)
    return L
fit=minimize(objective,start,method='Powell',bounds=[(-.04,.04)]*3,options={'maxfev':300,'xtol':.0001,'ftol':1e-9});q=preset(best[1]);C,a=model.render(source,case,q);sc=scores(C,T,case);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);ext=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)));state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':ext}}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
(out/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(out/'scores.json').write_text(json.dumps(state,indent=2)+'\n');np.save(out/'material.npy',C);np.save(out/'alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(out/'clean-preview.png');report={'before':before,'scores':state,'E':error(state['observations']['A']),'start':start,'best_v':best[1],'training_evaluations':rows,'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'gate':gate,'counted_passes':0,'note':'settlement of SAME inner-coefficient family, not another pass; fixed source/material/crown/blur/shadow and original guards'};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT',report['E'],best[1],ext,fit.success,flush=True)
