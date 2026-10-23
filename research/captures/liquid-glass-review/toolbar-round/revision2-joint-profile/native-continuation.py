import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.optimize import linprog
import toolbar_candidate as model
from progress_gate import evaluate,error
package=Path('/tmp/agent-toolbar-evidence-package');root=Path('/tmp/agent-toolbar-run');coarse=Path('/tmp/agent-toolbar-revision2-joint');prior=Path('/tmp/agent-toolbar-joint-native-settlement');out=Path('/tmp/agent-toolbar-joint-native-continuation');out.mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text());before=json.loads((package/'primary-verification.json').read_text())['candidate'];case=p['case'];source=np.asarray(Image.open(package/'inputs/source.png')).astype(float)/255;target=np.asarray(Image.open(package/'inputs/target.png')).astype(np.float32)/255;x0,y0,x1,y1=case['crop'];B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1];masks=np.load(root/'frozen-masks.npz');shadow=model.gaussian_coverage_shadow(case,p);fm=np.load(package/'derived-foreground.npz');public_fg=json.loads((package/'primary-scores.json').read_text())['foreground']
basev=np.array([0,0,0,p['parameters']['tangent'],p['parameters']['tangent_band'],4.]);limits=np.array([[-.08,.08]]*3+[[.1,.3],[.3,.75],[3.,10.]]);trust=np.array([.005,.005,.005,.012,.025,.25]);h=np.array([.00075,.00075,.00075,.0015,.003,.03]);cache={};rows=[];iteration_log=[]
baseguard=np.array([before['observations']['A']['glass']['rmse'],before['observations']['A']['rim']['rmse'],before['observations']['A']['shadow'],public_fg['archivebox']['rmse'],public_fg['plus']['rmse']]);baseL=error(before['observations']['A'])**2

def preset(v):
    q=copy.deepcopy(p)
    for i,val in zip([4,5,6],v[:3]):q['parameters']['coefficients'][i]+=float(val)
    q['parameters']['tangent']=float(v[3]);q['parameters']['tangent_band']=float(v[4]);q['tangent_exponent']=float(v[5]);return q

def native(v,save=False):
    key=tuple(map(float,v))
    if key in cache and not save:return cache[key]
    q=preset(v);C,a=model.render(source,case,q,samples=4)
    metrics={}
    for name,mask in [('glass',masks['glass']),('rim',masks['rim'])]:
        D=(C-T)[mask]*255;metrics[name]={'rmse':float(np.sqrt(np.mean(D**2))),'pixels':int(mask.sum())}
    full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);metrics['shadow']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
    for layer in p['foreground_layers']:
        alpha=fm[layer['name']][...,None];full=full*(1-alpha)+np.asarray(layer['color'])*alpha
    foreground={}
    for layer in p['foreground_layers']:
        A,b,c,d=layer['box'];foreground[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,A-x0:c-x0]-T[b-y0:d-y0,A-x0:c-x0])**2))*255)
    L=error(metrics)**2;guards=np.array([metrics['glass']['rmse'],metrics['rim']['rmse'],metrics['shadow'],foreground['archivebox'],foreground['plus']]);feasible=bool(np.all(guards<=baseguard));r={'v':list(key),'E':float(np.sqrt(L)),'L':L,'scores':{'epoch':before['epoch'],'observations':{'A':metrics}},'foreground':foreground,'guard_values':guards.tolist(),'all_nonregression':feasible,'milestone':L<=baseL*.995**2};cache[key]=r;rows.append(r)
    (out/'native-evaluations.json').write_text(json.dumps({'baseline':before,'baseline_foreground':public_fg,'evaluations':rows,'counted_passes':0},indent=2)+'\n');print('NATIVE_EVAL',len(rows),r['E'],feasible,flush=True)
    if save:
        (out/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(out/'scores.json').write_text(json.dumps(r['scores'],indent=2)+'\n');np.save(out/'material.npy',C);np.save(out/'alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(out/'complete-preview.png')
    return r

# Continue saved evaluations/constraints; do not repeat completed native probes.
previous=json.loads((prior/'native-evaluations.json').read_text())
rows=previous['evaluations']
for row in rows:
    sc=row['scores']['observations']['A'];fg=row['foreground']
    row['guard_values']=[sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']]
    row['all_nonregression']=bool(np.all(np.array(row['guard_values'])<=baseguard))
    cache[tuple(map(float,row['v']))]=row
iteration_log=json.loads((prior/'iterations.json').read_text())
assert len(iteration_log)==2
trust=np.array(iteration_log[-1]['trust']);h=np.array(iteration_log[-1]['finite_steps'])
if not iteration_log[-1]['used_for_search']:trust*=.5;h*=.5
r0=native(basev);assert abs(r0['L']-baseL)<1e-10 and np.max(np.abs(np.array(r0['guard_values'])-baseguard))<1e-9
starts=[r0]
for r in json.loads((coarse/'study.json').read_text())['trials']:starts.append(native(np.array(r['best_v'])))
feasible=[r for r in rows if r['all_nonregression']];current=min(feasible,key=lambda r:r['L']);v=np.array(current['v'])
for iteration in range(2,4):
    current=native(v);f=np.array([current['L'],*current['guard_values']]);J=np.zeros((6,6));probes=[]
    for i in range(6):
        plus=v.copy();minus=v.copy();plus[i]=min(limits[i,1],v[i]+h[i]);minus[i]=max(limits[i,0],v[i]-h[i]);rp=native(plus);rm=native(minus);J[:,i]=(np.array([rp['L'],*rp['guard_values']])-np.array([rm['L'],*rm['guard_values']]))/(plus[i]-minus[i]);probes.append([rp['v'],rm['v']])
    A=(J[1:]/baseguard[:,None])*trust[None,:];b=(baseguard-f[1:])/baseguard;zbound=[(max(-1.,(lo-x)/t),min(1.,(hi-x)/t)) for (lo,hi),x,t in zip(limits,v,trust)]
    lp=linprog(J[0]*trust/baseL,A_ub=A,b_ub=b,bounds=zbound,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    info={'iteration':iteration+1,'center':v.tolist(),'center_E':current['E'],'trust':trust.tolist(),'finite_steps':h.tolist(),'Jacobian':J.tolist(),'lp_success':bool(lp.success),'lp_message':str(lp.message),'line_search':[],'used_for_search':False}
    if lp.success:
        step=trust*lp.x
        for scale in [1.,.5,.25]:
            proposed=np.clip(v+scale*step,limits[:,0],limits[:,1]);trial=native(proposed);info['line_search'].append({'scale':scale,'v':proposed.tolist(),'E':trial['E'],'all_nonregression':trial['all_nonregression']})
            if trial['all_nonregression'] and trial['L']<current['L']:
                v=proposed;current=trial;info['used_for_search']=True;break
    if not info['used_for_search']:trust*=.5;h*=.5
    iteration_log.append(info);(out/'iterations.json').write_text(json.dumps(iteration_log,indent=2)+'\n')
# Every point still compares with the LAST LEAD-ACCEPTED baseline, not the search predecessor.
all_feasible=[r for r in rows if r['all_nonregression']];best=min(all_feasible,key=lambda r:r['L']);native(np.array(best['v']),save=True);report={'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','best':best,'native_all_guards_and_milestone':bool(best['all_nonregression'] and best['milestone']),'evaluations':len(rows),'trust_iterations':len(iteration_log),'inherited_records':len(previous['evaluations']), 'unique_native_points':len(cache), 'counted_passes':0,'note':'Bounded native settlement of SAME joint family; finite probes and used search steps are NOT passes. LP tolerances do not weaken final exact nonregression or .5% milestone. Independent primary review required.'};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT',report['native_all_guards_and_milestone'],best['E'],flush=True)
