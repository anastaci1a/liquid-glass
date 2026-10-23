"""Queue16 feasibility ONLY from compatible, saved native revision2 probes."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
root=Path('/tmp/agent-toolbar-joint-core');root.mkdir(exist_ok=True)
package=Path('/tmp/agent-toolbar-evidence-package')
jpath=Path('/tmp/agent-toolbar-joint-native-settlement/native-evaluations.json')
cpath=Path('/tmp/agent-toolbar-revision2-core-fit/native-evaluations.json')
j=json.loads(jpath.read_text());c=json.loads(cpath.read_text())
p=json.loads((package/'recipe.json').read_text());before=json.loads((package/'primary-verification.json').read_text())['candidate'];epoch=before['epoch']
limit=json.loads(Path('/tmp/agent-toolbar-revision2-core-checks/target-independent-bound.json').read_text())['lambda_max']
def values(r):
    s=r['scores']['observations']['A'];return np.array([s['glass']['rmse'],s['rim']['rmse'],s['shadow'],r['foreground']['archivebox'],r['foreground']['plus']])**2
basev=np.array([0.,0.,0.,p['parameters']['tangent'],p['parameters']['tangent_band'],4.])
j0=next(r for r in j['evaluations'] if np.array_equal(r['v'],basev));c0=next(r for r in c['evaluations'] if r['amplitude']==0)
assert j0['scores']['epoch']==c0['scores']['epoch']==epoch
assert np.array_equal(values(j0),values(c0)),(values(j0),values(c0))
hashes={name:hashlib.sha256((package/'inputs'/name).read_bytes()).hexdigest() for name in ['source.png','target.png']}
assert hashes['source.png']=='6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b'
assert hashes['target.png']=='5bb59714854d0bd019d689b3e8c444dd82b057d6abdc9275ca88a8295692bbf8'
G=np.zeros((5,4));probe_evidence=[]
for i in range(3):
    plus=basev.copy();minus=basev.copy();plus[i]=.00075;minus[i]=-.00075
    rp=next(r for r in j['evaluations'] if np.array_equal(r['v'],plus));rm=next(r for r in j['evaluations'] if np.array_equal(r['v'],minus))
    G[:,i]=(values(rp)-values(rm))/.0015;probe_evidence.append({'dimension':i,'h':.00075,'plus':rp,'minus':rm})
models=[];scales=np.array([.005,.005,.005,limit/64]);weights=np.array([.7,.3,0,0,0]);base=values(j0)
for divisor in [32,64]:
    h=limit/divisor;rp=next(r for r in c['evaluations'] if r['amplitude']==h);rm=next(r for r in c['evaluations'] if r['amplitude']==-h)
    M=G.copy();M[:,3]=(values(rp)-values(rm))/(2*h);models.append({'divisor':divisor,'finite_h':h,'gradient_MSE':M.tolist(),'core_plus':rp,'core_minus':rm})
def solve(matrices,core_fixed=False):
    constraints=np.concatenate([np.asarray(m['gradient_MSE'])*scales for m in matrices]);norm=np.max(np.abs(constraints),axis=1);valid=norm>1e-18;A=constraints[valid]/norm[valid,None]
    objective=np.mean([weights@np.asarray(m['gradient_MSE']) for m in matrices],axis=0)*scales;onorm=np.max(np.abs(objective))
    bounds=[(-1,1)]*4
    if core_fixed:bounds[3]=(0,0)
    opt=linprog(objective/max(onorm,1e-30),A_ub=A,b_ub=np.zeros(len(A)),bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    direction=scales*opt.x if opt.success else None
    return {'success':bool(opt.success),'message':str(opt.message),'core_fixed':core_fixed,'direction':direction.tolist() if direction is not None else None,'predicted_MSE_changes':[(np.asarray(m['gradient_MSE'])@direction).tolist() for m in matrices] if direction is not None else None,'predicted_objective_MSE_change':float(objective@opt.x) if opt.success else None,'normalized_guard_max':float(np.max(A@opt.x)) if opt.success else None}
individual=[solve([m]) for m in models];robust=solve(models);inner_only=solve(models,True)
constraints=np.concatenate([np.asarray(m['gradient_MSE'])*scales for m in models]);norm=np.max(np.abs(constraints),axis=1);valid=norm>1e-18;A=constraints[valid]/norm[valid,None]
objective=np.mean([weights@np.asarray(m['gradient_MSE']) for m in models],axis=0)*scales;onorm=np.max(np.abs(objective))
strict_lp=linprog([0,0,0,0,-1],A_ub=np.vstack([np.column_stack([A,np.ones(len(A))]),np.r_[objective/max(onorm,1e-30),0][None,:]]),b_ub=np.r_[np.zeros(len(A)),.25*robust['predicted_objective_MSE_change']/max(onorm,1e-30)],bounds=[(-1,1)]*4+[(0,1)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
strict={'success':bool(strict_lp.success),'message':str(strict_lp.message),'direction':(scales*strict_lp.x[:4]).tolist() if strict_lp.success else None,'normalized_guard_margin':float(strict_lp.x[4]) if strict_lp.success else None,'predicted_objective_MSE_change':float(objective@strict_lp.x[:4]) if strict_lp.success else None}
supported=bool(robust['success'] and robust['predicted_objective_MSE_change']<-1e-7 and robust['normalized_guard_max']<=1e-8)
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':epoch,'input_hashes':hashes,'baseline_MSE_identical_across_saved_families':True,'baseline_MSE':base.tolist(),'guard_order':['glass','rim','exterior','archivebox','plus'],'equation':'F=F0(c4–6+delta)-grad(Psi_lambda), Psi=.5*lambda*(major_axis dot x)^2*S(d/.30L), actual grad(d)','global_bounds':[[-.15,.15]]*3+[[-limit,limit]],'local_cone_scales':scales.tolist(),'saved_profile_probes':probe_evidence,'core_models':models,'individual_models':individual,'robust_both_core_steps':robust,'inner_only_comparison':inner_only,'joint_improvement_supported_for_bounded_native_proposal':supported,'new_renders':0,'counted_passes':0,'limitations':'Finite-difference local metric cone is proposal evidence, not exact nonlinear feasibility/global convergence or a qualifying optical improvement. Both core finite-step models constrained, profile probes are original baseline not transported from nonzero centers; same masks/input/shadow/vectors. No isolated study repeated.'}
report['strict_interior_proposal']=strict
(root/'feasibility.json').write_text(json.dumps(report,indent=2)+'\n')
print('STRICT',strict,flush=True)
print(json.dumps({'supported':supported,'robust':robust,'inner_only':inner_only,'baseline':base.tolist()},indent=2),flush=True)
