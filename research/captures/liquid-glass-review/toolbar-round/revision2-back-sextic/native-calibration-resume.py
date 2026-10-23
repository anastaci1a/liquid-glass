"""Small queue20 native geometric calibration, SAME complete-surface family.

Two starts, four trust steps each. Frozen source/material/shape/masks/foreground.
Restore guard feasibility before any improvement claim; all trials retained.
"""
import sys,json,copy,time,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
from scipy.optimize import linprog
import toolbar_back_surface_sextic as m
from progress_gate import evaluate,error
cv2.setNumThreads(1)
family=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-back-sextic');out=family/'native-calibration';out.mkdir(exist_ok=True);(out/'evaluations').mkdir(exist_ok=True)
package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((family/'recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];before=json.loads((package/'primary-verification.json').read_text())['candidate'];basefg=json.loads((package/'primary-scores.json').read_text())['foreground'];base=np.array([before['observations']['A']['glass']['rmse'],before['observations']['A']['rim']['rmse'],before['observations']['A']['shadow'],basefg['archivebox']['rmse'],basefg['plus']['rmse']])**2;weights=np.array([.7,.3,0,0,0]);baseL=weights@base
names=['b_major','b_minor','quartic','sextic'];scales=np.array([.03,.03,.15,.02]);source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fgmask=np.load(package/'derived-foreground.npz');alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');shadow=m.baseline.gaussian_coverage_shadow(case,p);rows=json.loads((out/'native-evaluations.json').read_text())['evaluations'];cache={tuple(r['z']):r for r in rows};logs=json.loads((out/'iterations.json').read_text());phase='resumed';began=time.time();inherited_completed_rows=len(rows)
print('RESUMED',inherited_completed_rows,'completedrows and',len(logs),'iterations; exact original parameter/cache keys retained',flush=True)
assert hashlib.sha256((package/'inputs/source.png').read_bytes()).hexdigest()=='6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b'
def preset(z):
    q=copy.deepcopy(p)
    for n,v in zip(names,np.asarray(z)*scales):q['back_surface'][n]=float(v)
    return q
def complete(C):
    full=C*alpha[...,None]+B*(1-shadow[...,None])*(1-alpha[...,None])
    for layer in p['foreground_layers']:
        aa=fgmask[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    return full
def measure(C):
    sc={}
    for name in ['glass','rim']:
        D=(C-T)[masks[name]]*255;sc[name]={'rmse':float(np.sqrt(np.mean(D**2))),'pixels':int(masks[name].sum())}
    nofg=C*alpha[...,None]+B*(1-shadow[...,None])*(1-alpha[...,None]);sc['shadow']=float(np.sqrt(np.mean(((nofg-T)[masks['exterior']]*255)**2)));full=complete(C);fg={}
    for layer in p['foreground_layers']:
        a,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-T[b-y0:d-y0,a-x0:c-x0])**2))*255)
    values=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']])**2
    return sc,fg,values
def native(z,inherited=None,save=None):
    z=np.asarray(z,float);key=tuple(map(float,z));assert np.all(np.abs(z)<=1+1e-12)
    if key not in cache:
        start=time.time()
        if inherited:C=np.load(inherited/'material.npy');actual=False
        else:C,a=m.render(source,case,preset(z));assert np.array_equal(a,alpha);actual=True
        sc,fg,values=measure(C);state={'epoch':before['epoch'],'observations':{'A':sc}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ratios=values/base;violation=float(max(np.max(ratios)-1,0));L=weights@values;merit=float(L/baseL+10*violation)
        path=out/'evaluations'/f'{len(rows):04d}.npz';np.savez_compressed(path,material=C)
        row={'index':len(rows),'z':list(key),'parameters':(z*scales).tolist(),'E':error(sc),'scores':state,'foreground':fg,'MSE':values.tolist(),'guard_MSE_ratios':ratios.tolist(),'max_guard_excess_ratio':violation,'merit':merit,'all_nonregression':bool(np.all(values<=base)),'gate':gate,'numerical_qualifier':bool(np.all(values<=base) and gate['observations']['A']['passed']),'phase':phase,'native_actual_render':actual,'inherited_from':str(inherited) if inherited else None,'material_cache':str(path),'seconds':time.time()-start};rows.append(row);cache[key]=row;(out/'native-evaluations.json').write_text(json.dumps({'baseline':before,'normalized_scales':scales.tolist(),'guard_order':['glass','rim','exterior','archivebox','plus'],'evaluations':rows,'counted_passes':0},indent=2)+'\n');print('NATIVE20',len(rows),phase,row['E'],row['max_guard_excess_ratio'],row['all_nonregression'],flush=True)
    else:row=cache[key];C=np.load(row['material_cache'])['material']
    if save:
        folder=out/save;folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(preset(z),indent=2)+'\n');(folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',alpha);np.save(folder/'complete.npy',complete(C));Image.fromarray(np.uint8(np.rint(np.clip(complete(C),0,1)*255))).save(folder/'complete-preview.png')
    return row
current20=json.loads((family/'result.json').read_text());z20=np.array(current20['projection']['z']);r20=native(z20,inherited=family);assert np.array_equal(np.sqrt(r20['MSE']),np.array(current20['guard_after']))
parent=Path('/tmp/agent-toolbar-back-surface');parentr=json.loads((parent/'result.json').read_text());zp=np.r_[parentr['projection']['z'],0.];rp=native(zp,inherited=parent);assert np.array_equal(np.sqrt(rp['MSE']),np.array(parentr['guard_after']))
start_results=[]
for seed,z in enumerate([z20,zp]):
    z=z.copy();trust=np.array([.20,.20,.20,.25]);h=np.full(4,.02)
    previous=[log for log in logs if log['seed']==seed+1]
    for old in previous:
        if old['accepted_for_search']:
            accepted=next(t for t in old['line_search'] if t['merit']<old['center_merit']-1e-9);z=np.array(rows[accepted['row']]['z'])
        else:trust*=.5;h*=.5
    for iteration in range(len(previous),4):
        current=native(z);f=np.array(current['MSE']);J=np.zeros((5,4));phase=f'seed{seed+1}-model{iteration+1}';probes=[]
        for i in range(4):
            plus=z.copy();minus=z.copy();plus[i]=z[i] if 1-z[i]<=1e-12 else min(1,z[i]+h[i]);minus[i]=z[i] if z[i]+1<=1e-12 else max(-1,z[i]-h[i]);a=native(plus);b=native(minus);J[:,i]=(np.array(a['MSE'])-np.array(b['MSE']))/(plus[i]-minus[i]);probes.append([a['index'],b['index']])
        low=np.maximum(-1,(-1-z)/trust);high=np.minimum(1,(1-z)/trust);A=J*trust[None,:]/base[:,None];bound=1-f/base;objective=np.r_[.01*(weights@J)*trust/baseL,1.]
        lp=linprog(objective,A_ub=np.column_stack([A,-np.ones(5)]),b_ub=bound,bounds=list(zip(low,high))+[(0,None)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        log={'seed':seed+1,'iteration':iteration+1,'center':z.tolist(),'center_E':current['E'],'center_merit':current['merit'],'trust':trust.tolist(),'finite_h':h.tolist(),'Jacobian_MSE':J.tolist(),'probe_rows':probes,'LP_success':bool(lp.success),'LP_message':str(lp.message),'line_search':[],'accepted_for_search':False};phase=f'seed{seed+1}-trial{iteration+1}'
        if lp.success:
            step=trust*lp.x[:4];log['proposed_normalized_step']=step.tolist();log['predicted_max_guard_excess_ratio']=float(lp.x[4])
            for factor in [1.,.5,.25]:
                trial=native(np.clip(z+factor*step,-1,1));log['line_search'].append({'factor':factor,'row':trial['index'],'E':trial['E'],'merit':trial['merit'],'all_nonregression':trial['all_nonregression']})
                if trial['merit']<current['merit']-1e-9:
                    z=np.array(trial['z']);log['accepted_for_search']=True;break
        if not log['accepted_for_search']:trust*=.5;h*=.5
        logs.append(log);(out/'iterations.json').write_text(json.dumps(logs,indent=2)+'\n');print('TRUST20',seed+1,iteration+1,log['accepted_for_search'],native(z)['E'],flush=True)
    start_results.append(native(z))
feasible=[r for r in rows if r['all_nonregression']];best=min(feasible,key=lambda r:r['E']) if feasible else None;closest=min(rows,key=lambda r:r['merit']);native(closest['z'],save='best-restoration')
if best:native(best['z'],save='best-feasible')
result={'best_feasible':best,'best_restoration':closest,'starts':start_results,'iterations':len(logs),'new_native_calibration_renders':sum(r['native_actual_render'] for r in rows),'cached_inherited_native_points':sum(not r['native_actual_render'] for r in rows),'resumed_completed_rows':inherited_completed_rows,'own_interrupted_partial_native_attempts':1,'earlier_duplicate_native_outputs':'endpoint-review-stage1/accounting.json; included honestly in actual render counts, no success/pass counts','map_native_comparison_renders':1,'termination':'Two starts×4trust-step budget, no global convergence/infeasibility or optimal-image-score claim','counted_passes':0,'elapsed_seconds':time.time()-began,'limits':'SameONE T³surface family. Photometric objective calibrates geometry ONLY. Every point retains original5guard/frozenepoch scoring; infeasible restoration steps are not accepted optical passes.'};(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('NATIVE20_CALIBRATION_COMPLETE',json.dumps({'best_feasible_E':best['E'] if best else None,'closest_E':closest['E'],'new_renders':result['new_native_calibration_renders']}),flush=True)
