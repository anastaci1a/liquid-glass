# Appended to the exact fit.py definitions after the original bounded run exits.
# Continues SAME family. Prior cached native evaluations are never rerendered.
prior=Path('/tmp/agent-toolbar-revision2-outer-fit')
assert (prior/'result.json').exists(),'Preserve the running bounded two-start fit; do not overlap/restart it'
previous=json.loads((prior/'native-evaluations.json').read_text());rows=previous['evaluations'];inherited_count=len(rows)
cache={tuple(map(float,r['v'])):r for r in rows}
best=min([r for r in rows if r['all_nonregression']],key=lambda r:r['E']);v=np.array(best['v']);trust=np.full(4,.02);settlement=[];stop_reason='six_step_settlement_budget'
fg_transmission=np.ones(C0.shape[:2],float)
for layer in p['foreground_layers']:fg_transmission*=1-fm[layer['name']]

def guard_residuals(C,dc):
    # Five native residual systems give quadratic glass/rim/exterior/FG models.
    D=(C.astype(float)-T)*255;groups=[]
    for name in ['glass','rim']:
        mask=masks[name];groups.append((D[mask].ravel(),(dc[:,mask]*255).reshape(4,-1).T))
    nofg=C*a0[...,None]+B*(1-shadow[...,None])*(1-a0[...,None]);D=(nofg-T)*255;mask=masks['exterior']
    groups.append((D[mask].ravel(),(dc[:,mask]*(a0[mask][None,:,None])*255).reshape(4,-1).T))
    full=compose(C);D=(full-T)*255
    for layer in p['foreground_layers']:
        a,b,c,d=layer['box'];sl=(slice(b-y0,d-y0),slice(a-x0,c-x0));f=(a0*fg_transmission)[sl]
        groups.append((D[sl].ravel(),(dc[(slice(None),*sl)]*f[None,...,None]*255).reshape(4,-1).T))
    grams=[];grads=[]
    for residual_values,jacobian in groups:
        grams.append(jacobian.T@jacobian/len(residual_values));grads.append(jacobian.T@residual_values/len(residual_values))
    return np.array(grams),np.array(grads)

for iteration in range(6):
    phase=f'quadratic-guard-settlement-{iteration+1}';current,C=native(v);h=np.minimum(.002,np.maximum(.00025,trust*.1));derivatives=[]
    for i in range(4):
        vp=v.copy();vm=v.copy();vp[i]=min(limits[i,1],v[i]+h[i]);vm[i]=max(limits[i,0],v[i]-h[i]);_,Cp=native(vp);_,Cm=native(vm);derivatives.append((Cp.astype(float)-Cm)/(vp[i]-vm[i]))
    dc=np.array(derivatives);GG,gg=guard_residuals(C,dc);G=.7*GG[0]+.3*GG[1];grad=.7*gg[0]+.3*gg[1]
    H=(G*trust[:,None]*trust[None,:])/baseE**2;g=grad*trust/baseE**2;current_squared=np.array(current['guard_values'])**2;limit_squared=baseguard**2;scales=np.maximum(limit_squared,1.)
    safety=1.5
    def guard_function(z):
        delta=trust*z
        return (limit_squared-current_squared-2*gg@delta-safety*np.einsum('i,kij,j->k',delta,GG,delta))/scales
    def guard_jacobian(z):
        delta=trust*z
        return -(2*gg+2*safety*np.einsum('kij,j->ki',GG,delta))*trust[None,:]/scales[:,None]
    bounds=[(max(-1.,(lo-x)/t),min(1.,(hi-x)/t)) for (lo,hi),x,t in zip(limits,v,trust)]
    proposal=minimize(lambda z:.5*z@H@z+g@z,np.zeros(4),jac=lambda z:H@z+g,method='SLSQP',bounds=bounds,constraints={'type':'ineq','fun':guard_function,'jac':guard_jacobian},options={'maxiter':120,'ftol':1e-12})
    log={'iteration':iteration+1,'center':v.tolist(),'center_E':current['E'],'trust':trust.tolist(),'finite_steps':h.tolist(),'objective_Gram':G.tolist(),'objective_gradient':grad.tolist(),'guard_names':['glass','rim','exterior','archivebox','plus'],'guard_Grams':GG.tolist(),'guard_gradients':gg.tolist(),'proposal_curvature_safety_factor':safety,'quadratic_success':bool(proposal.success),'quadratic_message':str(proposal.message),'line_search':[],'used_for_search':False,'note':'Safety factor only constrains optimization proposals; it never alters renderer/scoring/guard tolerances'}
    if proposal.success:
        step=trust*proposal.x;predicted=float(-(2*grad@step+step@G@step));log['predicted_E_squared_reduction']=predicted
        for factor in [1.,.5,.25,.125]:
            trialv=np.clip(v+factor*step,limits[:,0],limits[:,1]);trial,_=native(trialv);log['line_search'].append({'scale':factor,'index':trial['index'],'E':trial['E'],'all_nonregression':trial['all_nonregression']})
            if trial['all_nonregression'] and trial['E']<current['E']:
                actual=current['E']**2-trial['E']**2;rho=actual/max(predicted*factor,1e-12);v=trialv;log['used_for_search']=True;log['accepted_step_max_abs']=float(np.max(np.abs(factor*step)));log['actual_vs_predicted_ratio']=rho
                if rho<.25:trust*=.5
                elif rho>.75 and np.max(np.abs(proposal.x*factor))>.8:trust=np.minimum(trust*1.5,.04)
                break
    if not log['used_for_search']:trust*=.5
    settlement.append(log);(out/'settlement-iterations.json').write_text(json.dumps(settlement,indent=2)+'\n')
    if np.max(trust)<.0003:stop_reason='trust_below_.0003';break
    if len(settlement)>=3 and all(x.get('used_for_search') and x.get('accepted_step_max_abs',1)<.0003 for x in settlement[-3:]):stop_reason='three_consecutive_steps_below_.0003';break

qualifiers=[r for r in rows if r['numerical_qualifier']];feasible=[r for r in rows if r['all_nonregression']];best=min(qualifiers or feasible,key=lambda r:r['E']);raw=min(rows,key=lambda r:r['E']);native(best['v'],save='best-feasible');native(raw['v'],save='best-raw')
summary={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':before['epoch'],'one_family':True,'prior_two_start_result':str(prior/'result.json'),'inherited_points':inherited_count,'new_native_points':len(rows)-inherited_count,'unique_native_points_total':len(rows),'settlement_iterations':len(settlement),'stop_reason':stop_reason,'best_guard_feasible':best,'best_raw':raw,'any_numerical_qualifier':bool(qualifiers),'counted_passes':0,'bounds':limits.tolist(),'limits':'Quadratic guard settlement justified by positive nonlinear exterior curvature observed at linearized-guard steps. No changed model/source/epoch/silhouette/material/glyphs; full native nonlinear guards remain exact. Budget or trust termination is not global convergence.'}
(out/'result.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT',summary['any_numerical_qualifier'],best['E'],flush=True)
