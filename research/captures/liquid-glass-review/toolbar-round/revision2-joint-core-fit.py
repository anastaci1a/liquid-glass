"""ONE bounded joint family, conditional on saved native feasibility evidence.

Metric trust models propose; original native score/foreground guards decide.
All evaluations cached durably; no completed isolated native probes repeated.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
from scipy.optimize import minimize,linprog
import toolbar_core_strain as model
from progress_gate import error,evaluate
cv2.setNumThreads(1)
out=Path('/tmp/agent-toolbar-joint-core');out.mkdir(exist_ok=True);(out/'evaluations').mkdir(exist_ok=True)
feas=json.loads((out/'feasibility.json').read_text());assert feas['joint_improvement_supported_for_bounded_native_proposal']
package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());p['core_strain']={'amplitude':0.,'width':.30}
before=json.loads((package/'primary-verification.json').read_text())['candidate'];case=p['case'];x0,y0,x1,y1=case['crop']
source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;backdrop=source[y0:y1,x0:x1]
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fm=np.load(package/'derived-foreground.npz');alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy')
shadow=model.baseline.gaussian_coverage_shadow(case,p);base=np.array(feas['baseline_MSE']);weights=np.array([.7,.3,0,0,0]);baseL=float(weights@base);limit=feas['global_bounds'][3][1];bounds=np.array(feas['global_bounds']);scales=np.array(feas['local_cone_scales']);h0=np.array([.00075]*3+[limit/64]);names=feas['guard_order']
rows=[];cache={};iterations=[];phase='baseline';started=time.time()
def preset(v):
    q=copy.deepcopy(p)
    for i,z in enumerate(v[:3]):q['parameters']['coefficients'][i+4]+=float(z)
    q['core_strain']['amplitude']=float(v[3]);return q
def compose(C):
    full=C*alpha[...,None]+backdrop*(1-shadow[...,None])*(1-alpha[...,None])
    for layer in p['foreground_layers']:
        a=fm[layer['name']][...,None];full=full*(1-a)+np.asarray(layer['color'])*a
    return full
def metrics(C):
    sc={}
    for name in ['glass','rim']:
        D=(C-T)[masks[name]]*255;sc[name]={'rmse':float(np.sqrt(np.mean(D**2))),'pixels':int(masks[name].sum())}
    nofg=C*alpha[...,None]+backdrop*(1-shadow[...,None])*(1-alpha[...,None]);sc['shadow']=float(np.sqrt(np.mean(((nofg-T)[masks['exterior']]*255)**2)));full=compose(C);fg={}
    for layer in p['foreground_layers']:
        a,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-T[b-y0:d-y0,a-x0:c-x0])**2))*255)
    return sc,fg
def save_state():
    (out/'native-evaluations.json').write_text(json.dumps({'evaluations':rows,'bounds':bounds.tolist(),'guard_order':names,'baseline_MSE':base.tolist(),'counted_passes':0},indent=2)+'\n')
def native(v,save=None):
    v=np.asarray(v,float);key=tuple(map(float,v));assert np.all(v>=bounds[:,0]-1e-13) and np.all(v<=bounds[:,1]+1e-13)
    if key not in cache:
        t=time.time();inherited=False
        if np.all(v==0):C=C0;inherited=True
        elif v[3]==0 and np.count_nonzero(v[:3])==1 and np.max(np.abs(v[:3]))==.00075:
            # Saved pure-profile material was not retained, so do not render it.
            # Its exact metrics/derivative are reused below instead.
            raise ValueError('Would duplicate completed isolated profile probe')
        else:C,a=model.render(source,case,preset(v));assert np.array_equal(a,alpha)
        sc,fg=metrics(C);values=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']])**2
        state={'epoch':before['epoch'],'observations':{'A':sc}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
        path=out/'evaluations'/f'{len(rows):04d}.npz';np.savez_compressed(path,material=C)
        r={'index':len(rows),'v':list(key),'E':error(sc),'MSE':values.tolist(),'scores':state,'foreground':fg,'all_nonregression':bool(np.all(values<=base)),'nonregression':dict(zip(names,map(bool,values<=base))),'gate':gate,'numerical_qualifier':bool(np.all(values<=base) and gate['observations']['A']['passed']),'phase':phase,'native_actual_render':not inherited,'material_cache':str(path),'seconds':time.time()-t};rows.append(r);cache[key]=r;save_state();print('JOINT',len(rows),phase,r['E'],r['all_nonregression'],r['nonregression'],flush=True)
    else:r=cache[key];C=np.load(r['material_cache'])['material']
    if save:
        folder=out/save;folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(preset(v),indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(r['scores'],indent=2)+'\n');(folder/'measurement.json').write_text(json.dumps(r,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',alpha);np.save(folder/'complete.npy',compose(C));Image.fromarray(np.uint8(np.rint(np.clip(compose(C),0,1)*255))).save(folder/'complete-preview.png')
    return r
def saved_baseline_model():
    G=np.asarray(feas['core_models'][1]['gradient_MSE']);D=np.zeros((5,4))
    for i,probe in enumerate(feas['saved_profile_probes']):
        def val(r):
            s=r['scores']['observations']['A'];return np.array([s['glass']['rmse'],s['rim']['rmse'],s['shadow'],r['foreground']['archivebox'],r['foreground']['plus']])**2
        D[:,i]=(val(probe['plus'])+val(probe['minus'])-2*base)/probe['h']**2
    cm=feas['core_models'][1];D[:,3]=(np.asarray(cm['core_plus']['guard_values'])**2+np.asarray(cm['core_minus']['guard_values'])**2-2*base)/cm['finite_h']**2
    return G,D
def proposal(v,current,G,D,trust):
    f=np.asarray(current['MSE']);diag=np.maximum(D,0.)*1.5;J=G*trust[None,:];Q=.5*diag*trust[None,:]**2;normal=np.maximum(np.max(np.abs(J)+Q,axis=1),1e-12)
    lb=np.maximum(-1,(bounds[:,0]-v)/trust);ub=np.minimum(1,(bounds[:,1]-v)/trust)
    def predict(z):return f+J@z+Q@(z*z)
    def obj(z):return float(weights@(predict(z)-f)/baseL)
    def jac(z):return weights@(J+2*Q*z[None,:])/baseL
    def con(z):return (base-predict(z))/normal
    def cjac(z):return -(J+2*Q*z[None,:])/normal[:,None]
    opt=minimize(obj,np.zeros(4),jac=jac,bounds=list(zip(lb,ub)),constraints=[{'type':'ineq','fun':con,'jac':cjac}],method='SLSQP',options={'ftol':1e-12,'maxiter':300})
    pred=predict(opt.x);return opt,trust*opt.x,pred,normal
v=np.zeros(4);r0=native(v);assert np.array_equal(np.asarray(r0['MSE']),base)
trust=scales.copy();h=h0.copy();contractions=0;termination='iteration budget12, no global convergence certificate'
phase='strict-native-feasibility-validation';direction=np.array(feas['strict_interior_proposal']['direction'])
initial=[]
for factor in [1.,.5,.25,.125,.0625,.03125]:
    r=native(factor*direction);initial.append({'factor':factor,'row':r['index'],'all_nonregression':r['all_nonregression'],'E':r['E']})
    if r['all_nonregression'] and r['E']<r0['E']:v=factor*direction;break
(out/'initial-validation.json').write_text(json.dumps(initial,indent=2)+'\n')
for it in range(12):
    current=native(v);f=np.array(current['MSE']);phase=f'local-model-{it+1}'
    if np.all(v==0):G,D=saved_baseline_model();derivatives='saved exact baseline native probes'
    else:
        G=np.zeros((5,4));D=np.zeros((5,4));derivatives=[]
        for i in range(4):
            dh=min(h[i],max((bounds[i,1]-v[i])*.9,1e-12),max((v[i]-bounds[i,0])*.9,1e-12));vp=v.copy();vm=v.copy();vp[i]+=dh;vm[i]-=dh
            rp=native(vp);rm=native(vm);fp=np.array(rp['MSE']);fn=np.array(rm['MSE']);G[:,i]=(fp-fn)/(2*dh);D[:,i]=(fp+fn-2*f)/dh**2;derivatives.append({'dimension':i,'h':dh,'plus':rp['index'],'minus':rm['index']})
    opt,step,pred,norm=proposal(v,current,G,D,trust);record={'iteration':it+1,'center':v.tolist(),'center_E':current['E'],'trust':trust.tolist(),'finite_h':h.tolist(),'derivatives':derivatives,'gradient_MSE':G.tolist(),'diagonal_second_MSE':D.tolist(),'model_success':bool(opt.success),'model_message':str(opt.message),'model_iterations':int(opt.nit),'predicted_MSE':pred.tolist(),'proposed_step':step.tolist(),'line_search':[],'accepted':False}
    phase=f'trust-proposal-{it+1}'
    if opt.success and weights@(pred-f)<-1e-10 and np.all(pred<=base+1e-10):
        for factor in [1.,.5,.25,.125,.0625]:
            trial=native(np.clip(v+factor*step,bounds[:,0],bounds[:,1]));record['line_search'].append({'factor':factor,'row':trial['index'],'E':trial['E'],'all_nonregression':trial['all_nonregression']})
            if trial['all_nonregression'] and trial['E']<current['E']-1e-10:
                v=np.array(trial['v']);record['accepted']=True;contractions=0
                if factor==1:trust=np.minimum(trust*1.5,np.array([.025,.025,.025,limit/8]))
                break
    if not record['accepted']:
        trust*=.5;h=np.maximum(h*.5,np.array([.00005,.00005,.00005,limit/1024]));contractions+=1
    iterations.append(record);(out/'iterations.json').write_text(json.dumps(iterations,indent=2)+'\n')
    print('TRUST',it+1,record['accepted'],native(v)['E'],contractions,flush=True)
    if contractions>=4:
        termination='Four consecutive contracted native metric models found no accepted improving step; local numerical/model limit, NOT global infeasibility/convergence proof';break
best=min((r for r in rows if r['all_nonregression']),key=lambda r:r['E']);native(best['v'],save='best-feasible');native(min(rows,key=lambda r:r['E'])['v'],save='best-raw')
result={'best':best,'initial_validation':initial,'iterations':len(iterations),'termination':termination,'bounds':bounds.tolist(),'best_bound_distances':np.minimum(np.array(best['v'])-bounds[:,0],bounds[:,1]-np.array(best['v'])).tolist(),'unique_new_joint_evaluations':len(rows)-1,'new_renders':sum(r['native_actual_render'] for r in rows),'cached_baseline':1,'counted_passes':0,'elapsed_seconds':time.time()-started,'limits':'One family. Exact original native guards decide, finite quadratic models only propose. No new source/mask/epoch/shadow/glyph fit. Qualifier still needs fresh HQ/source checks and independent lead acceptance.'};(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT',json.dumps({'E':best['E'],'qualifier':best['numerical_qualifier'],'termination':termination,'new_renders':result['new_renders']}),flush=True)
