import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.optimize import minimize
import toolbar_candidate as model
from reproduce import scores
from progress_gate import evaluate,error
package=Path('/tmp/agent-toolbar-evidence-package');root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-revision2-joint');out.mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text());before=json.loads((package/'primary-verification.json').read_text())['candidate'];case=p['case'];source=np.asarray(Image.open(package/'inputs/source.png')).astype(float)/255;target=np.asarray(Image.open(package/'inputs/target.png')).astype(np.float32)/255
x0,y0,x1,y1=case['crop'];B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1];masks=np.load(root/'frozen-masks.npz');shadow=model.gaussian_coverage_shadow(case,p);C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a0=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');fm=np.load(package/'derived-foreground.npz')
def fg(full):
    for layer in p['foreground_layers']:
        aa=fm[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    result={}
    for layer in p['foreground_layers']:
        a,b,c,d=layer['box'];result[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-T[b-y0:d-y0,a-x0:c-x0])**2))*255)
    return result
before_fg=fg(C0*a0[...,None]+B*(1-shadow[...,None])*(1-a0[...,None]));public_fg=json.loads((package/'primary-scores.json').read_text())['foreground'];assert all(abs(v-public_fg[k]['rmse'])<1e-9 for k,v in before_fg.items())
basev=[0,0,0,p['parameters']['tangent'],p['parameters']['tangent_band'],4.];bounds=[(-.08,.08)]*3+[(.1,.3),(.3,.75),(3.,10.)];records=[];native=[]
def preset(v):
    q=copy.deepcopy(p)
    for i,val in zip([4,5,6],v[:3]):q['parameters']['coefficients'][i]+=float(val)
    q['parameters']['tangent']=float(v[3]);q['parameters']['tangent_band']=float(v[4]);q['tangent_exponent']=float(v[5]);return q
C,a=model.render(source,case,preset(basev));assert float(np.max(np.abs(C-C0)))==0;print('BASE RECOVERY EXACT',flush=True)
for seed,start in enumerate([basev,[.015,.025,-.045,.18,.60,7.]],1):
    rows=[];best=[float('inf'),start];t0=time.time()
    def objective(v):
        C,_=model.render(source,case,preset(v),samples=1);D=(C-T)*255;L=float(.7*np.mean(D[masks['glass']]**2)+.3*np.mean(D[masks['rim']]**2));rows.append({'v':list(map(float,v)),'training_L':L})
        if L<best[0]:best[:]=[L,list(map(float,v))]
        if len(rows)%30==0:
            print('TRAIN',seed,len(rows),best,flush=True);(out/'in-progress.json').write_text(json.dumps({'seed':seed,'best':best,'training_evaluations':rows,'accepted':False},indent=2)+'\n')
        return L
    objective(start);fit=minimize(objective,start,method='Powell',bounds=bounds,options={'maxfev':600,'xtol':.00015,'ftol':1e-8});q=preset(best[1]);C,a=model.render(source,case,q);sc=scores(C,T,case);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);ext=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)));after_fg=fg(full);fg_guard={k:after_fg[k]<=before_fg[k] for k in before_fg};state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':ext}}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ok=all(r['passed'] for r in gate['observations'].values()) and all(fg_guard.values());E=error(state['observations']['A'])
    record={'seed':seed,'start':start,'best_v':best[1],'training_L':best[0],'training_evaluations':rows,'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'seconds':time.time()-t0,'bound_activity':[{'index':i,'value':v,'bounds':list(bounds[i]),'near_bound':min(v-bounds[i][0],bounds[i][1]-v)<.02*(bounds[i][1]-bounds[i][0])} for i,v in enumerate(best[1])],'scores':state,'E':E,'gate':gate,'foreground_before':before_fg,'foreground_after':after_fg,'foreground_nonregression':fg_guard,'native_all_guards_pass':ok,'counted_passes':0};records.append(record);native.append((ok,E,q,state,C,a,full));folder=out/f'seed-{seed}';folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(state,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(folder/'clean-preview.png');(out/'study.json').write_text(json.dumps({'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','before':before,'trials':records,'counted_passes':0,'training':'1x1 raster objective approximate; all final scores4x4; source/masks/outer0-3/shape/material/blur/shadow fixed'},indent=2)+'\n');print('NATIVE',seed,E,ext,after_fg,ok,fit.success,flush=True)
valid=[x for x in native if x[0]];best=min(valid or native,key=lambda x:x[1]);(out/'result.json').write_text(json.dumps({'any_numerical_qualifier':bool(valid),'best_E':best[1],'best_recipe':best[2],'best_scores':best[3],'counted_passes':0,'note':'ONE joint profile/tangent family, all starts/settlements are not extra passes; primary independent acceptance required'},indent=2)+'\n');print('RESULT',bool(valid),best[1],flush=True)
