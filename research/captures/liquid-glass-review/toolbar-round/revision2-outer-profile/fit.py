"""ONE existing outer-normal family with constrained native quadratic steps.

No renderer change. Each objective/probe uses accepted crowned_tensor4x4.
Native nonlinear guards validate every proposed step against accepted rev2.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-evidence-package/code')
import numpy as np
import cv2
from PIL import Image
from scipy.optimize import minimize
import crowned_tensor as model
from progress_gate import error,evaluate
cv2.setNumThreads(1)
package=Path('/tmp/agent-toolbar-evidence-package');out=Path('/tmp/agent-toolbar-revision2-outer-fit');out.mkdir(exist_ok=True);(out/'evaluations').mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text());before=json.loads((package/'primary-verification.json').read_text())['candidate'];case=p['case'];x0,y0,x1,y1=case['crop']
source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1]
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fm=np.load(package/'derived-foreground.npz');a0=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy')
shadow=model.gaussian_coverage_shadow(case,p);publicfg=json.loads((package/'primary-scores.json').read_text())['foreground']
baseguard=np.array([before['observations']['A']['glass']['rmse'],before['observations']['A']['rim']['rmse'],before['observations']['A']['shadow'],publicfg['archivebox']['rmse'],publicfg['plus']['rmse']]);baseE=error(before['observations']['A']);limits=np.array([[-.15,.15]]*4)
rows=[];cache={};fits=[];began=time.time();phase='baseline';small_scales=np.array([1.,1.,.01,.01,.01])

def preset(v):
    q=copy.deepcopy(p)
    for i,val in enumerate(v):q['parameters']['coefficients'][i]+=float(val)
    return q

def compose(C):
    full=C*a0[...,None]+B*(1-shadow[...,None])*(1-a0[...,None])
    for layer in p['foreground_layers']:
        aa=fm[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    return full

def native(v,save=None):
    key=tuple(map(float,v));new=key not in cache
    if new:
        t0=time.time()
        if np.array_equal(np.asarray(v),np.zeros(4)):C=C0;actual_render=False
        else:
            C,a=model.render(source,case,preset(v),samples=4);assert np.array_equal(a,a0);actual_render=True
        path=out/'evaluations'/f'{len(rows):04d}.npz';np.savez_compressed(path,material=C)
        sc={}
        for name in ['glass','rim']:
            D=(C-T)[masks[name]]*255;sc[name]={'rmse':float(np.sqrt(np.mean(D**2))),'pixels':int(masks[name].sum())}
        nofg=C*a0[...,None]+B*(1-shadow[...,None])*(1-a0[...,None]);sc['shadow']=float(np.sqrt(np.mean(((nofg-T)[masks['exterior']]*255)**2)))
        full=compose(C);fg={}
        for layer in p['foreground_layers']:
            a,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-T[b-y0:d-y0,a-x0:c-x0])**2))*255)
        g=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']]);state={'epoch':before['epoch'],'observations':{'A':sc}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
        row={'index':len(rows),'v':list(key),'E':error(sc),'scores':state,'foreground':fg,'guard_values':g.tolist(),'all_nonregression':bool(np.all(g<=baseguard)),'nonregression':dict(zip(['glass','rim','exterior','archivebox','plus'],map(bool,g<=baseguard))),'gate':gate,'numerical_qualifier':bool(np.all(g<=baseguard) and gate['observations']['A']['passed']),'phase':phase,'native_actual_render':actual_render,'material_cache':str(path),'seconds':time.time()-t0};rows.append(row);cache[key]=row
        (out/'native-evaluations.json').write_text(json.dumps({'before':before,'bounds':limits.tolist(),'evaluations':rows,'counted_passes':0},indent=2)+'\n');print('NATIVE',len(rows),phase,row['E'],row['all_nonregression'],row['numerical_qualifier'],flush=True)
    else:
        row=cache[key];C=np.load(row['material_cache'])['material']
    if save:
        folder=out/save;folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(preset(v),indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(row['scores'],indent=2)+'\n');(folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a0);np.save(folder/'complete.npy',compose(C));Image.fromarray(np.uint8(np.rint(np.clip(compose(C),0,1)*255))).save(folder/'complete-preview.png')
    return row,C

def residual(C):
    D=(C.astype(float)-T)*255
    return np.concatenate([D[masks['glass']].ravel()*np.sqrt(.7/(3*masks['glass'].sum())),D[masks['rim']].ravel()*np.sqrt(.3/(3*masks['rim'].sum()))])

def violation(row):return float(np.linalg.norm(np.maximum(np.array(row['guard_values'])-baseguard,0)/small_scales))

r0,_=native(np.zeros(4));assert abs(r0['E']-baseE)<1e-12 and np.max(np.abs(np.array(r0['guard_values'])-baseguard))<1e-9
print('BASELINE METRIC RECOVERY EXACT FROM IMMUTABLE NATIVE MATERIAL',flush=True)
for seed,start in enumerate([np.zeros(4),np.array([.04,-.04,.04,-.04])],1):
    phase=f'seed-{seed}-initial';current,C=native(start);v=np.array(start);trust=np.full(4,.02);logs=[];stopped='iteration_budget_8';t0=time.time();initial_index=len(rows)
    for iteration in range(8):
        phase=f'seed-{seed}-trust-{iteration+1}';current,C=native(v);R=residual(C);gcur=np.array(current['guard_values']);h=np.minimum(.002,np.maximum(.00025,trust*.1));J=[];guardJ=np.zeros((5,4));derivatives=[]
        for i in range(4):
            vp=v.copy();vm=v.copy();vp[i]=min(limits[i,1],v[i]+h[i]);vm[i]=max(limits[i,0],v[i]-h[i]);rp,Cp=native(vp);rm,Cm=native(vm);den=vp[i]-vm[i];dc=(Cp.astype(float)-Cm)/den;J.append(residual(C+dc)-R);guardJ[:,i]=(np.array(rp['guard_values'])-np.array(rm['guard_values']))/den
            if seed==1 and iteration==0:derivatives.append(dc.astype(np.float32))
        J=np.stack(J,axis=1);G=J.T@J;grad=J.T@R
        if derivatives:np.savez_compressed(out/'baseline-outer-derivatives.npz',derivative=np.stack(derivatives),finite_steps=h,indices=np.arange(4))
        H=(G*trust[:,None]*trust[None,:])/baseE**2;g=grad*trust/baseE**2;A=guardJ*trust[None,:]/small_scales[:,None];b=(baseguard-gcur)/small_scales
        bounds=[(max(-1.,(lo-x)/t),min(1.,(hi-x)/t)) for (lo,hi),x,t in zip(limits,v,trust)]
        proposal=minimize(lambda z:.5*z@H@z+g@z,np.zeros(4),jac=lambda z:H@z+g,method='SLSQP',bounds=bounds,constraints={'type':'ineq','fun':lambda z:b-A@z,'jac':lambda z:-A},options={'maxiter':100,'ftol':1e-12})
        log={'iteration':iteration+1,'center':v.tolist(),'center_E':current['E'],'center_violation':violation(current),'trust':trust.tolist(),'finite_steps':h.tolist(),'Gram':G.tolist(),'gradient':grad.tolist(),'guard_Jacobian':guardJ.tolist(),'guard_names':['glass','rim','exterior','archivebox','plus'],'quadratic_success':bool(proposal.success),'quadratic_message':str(proposal.message),'line_search':[],'used_for_search':False,'source_and_alpha_fixed':True}
        if proposal.success:
            step=trust*proposal.x;predicted=float(-(2*grad@step+step@G@step));log['predicted_E_squared_reduction']=predicted
            for factor in [1.,.5,.25,.125]:
                trialv=np.clip(v+factor*step,limits[:,0],limits[:,1]);trial,trialC=native(trialv);log['line_search'].append({'scale':factor,'index':trial['index'],'E':trial['E'],'violation':violation(trial),'all_nonregression':trial['all_nonregression']})
                improving=(trial['all_nonregression'] and trial['E']<current['E']) if current['all_nonregression'] else (trial['all_nonregression'] or violation(trial)<.9*violation(current))
                if improving:
                    oldE=current['E'];v=trialv;current=trial;C=trialC;log['used_for_search']=True;actual=oldE**2-trial['E']**2;rho=actual/max(predicted*factor,1e-12);log['actual_vs_predicted_ratio']=rho
                    if rho<.25:trust*=.5
                    elif rho>.75 and np.max(np.abs(proposal.x*factor))>.8:trust=np.minimum(trust*1.5,.04)
                    log['accepted_step_max_abs']=float(np.max(np.abs(factor*step)))
                    break
        if not log['used_for_search']:trust*=.5
        logs.append(log);(out/f'seed-{seed}-iterations.json').write_text(json.dumps(logs,indent=2)+'\n')
        if np.max(trust)<.0003:stopped='trust_below_.0003_after_nonlinear_guard_checks';break
        if len(logs)>=3 and current['all_nonregression'] and all(t.get('used_for_search') and t.get('accepted_step_max_abs',1)<.0003 for t in logs[-3:]):stopped='three_consecutive_steps_below_.0003';break
    final,_=native(v,save=f'seed-{seed}');record={'seed':seed,'initial':start.tolist(),'final':final,'iterations':len(logs),'stop_reason':stopped,'seconds':time.time()-t0,'new_native_points':len(rows)-initial_index,'near_absolute_bounds':[bool(min(value-lo,hi-value)<.02*(hi-lo)) for value,(lo,hi) in zip(v,limits)],'no_first_threshold_stop':True};fits.append(record);(out/'fits.json').write_text(json.dumps(fits,indent=2)+'\n');print('FIT',seed,stopped,final['E'],final['all_nonregression'],flush=True)

qualifiers=[r for r in rows if r['numerical_qualifier']];feasible=[r for r in rows if r['all_nonregression']];best=min(qualifiers or feasible,key=lambda r:r['E']);raw=min(rows,key=lambda r:r['E']);native(best['v'],save='best-feasible');native(raw['v'],save='best-raw')
summary={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':before['epoch'],'one_family':True,'bounds':limits.tolist(),'fits':fits,'best_guard_feasible':best,'best_raw':raw,'any_numerical_qualifier':bool(qualifiers),'unique_native_points':len(rows),'actual_new_renders':sum(r['native_actual_render'] for r in rows),'counted_passes':0,'seconds':time.time()-began,'limits':'Existing inverse-map coefficient calibration only. Trust stopping/budget is not global convergence. All native guards compare accepted rev2, never a rejected predecessor. Primary independent replay/source/HQ/visual acceptance still required.'}
(out/'result.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT',summary['any_numerical_qualifier'],best['E'],flush=True)
