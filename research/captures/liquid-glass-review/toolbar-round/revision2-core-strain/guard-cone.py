"""ONE scalar potential core-strain family; original native nonlinear gates.

Initial geometry-based bracket nodes are followed by quadratic native guard
intervals. No material/source/silhouette/glyph fitting or per-crop coefficients.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_core_strain as model
from progress_gate import error,evaluate
cv2.setNumThreads(1)
package=Path('/tmp/agent-toolbar-evidence-package');out=Path('/tmp/agent-toolbar-revision2-core-fit');out.mkdir(exist_ok=True);(out/'evaluations').mkdir(exist_ok=True)
checks=Path('/tmp/agent-toolbar-revision2-core-checks');assert (checks/'invariants.json').exists()
bound=json.loads((checks/'target-independent-bound.json').read_text());limit=bound['lambda_max']
p=json.loads((package/'recipe.json').read_text());p['core_strain']={'amplitude':0.,'width':.30*min(p['shape']['half'])}
before=json.loads((package/'primary-verification.json').read_text())['candidate'];case=p['case'];x0,y0,x1,y1=case['crop']
source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;backdrop=source[y0:y1,x0:x1]
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fm=np.load(package/'derived-foreground.npz');a0=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy')
shadow=model.baseline.gaussian_coverage_shadow(case,p);publicfg=json.loads((package/'primary-scores.json').read_text())['foreground'];baseguard=np.array([before['observations']['A']['glass']['rmse'],before['observations']['A']['rim']['rmse'],before['observations']['A']['shadow'],publicfg['archivebox']['rmse'],publicfg['plus']['rmse']]);baseE=error(before['observations']['A'])
fg_transmission=np.ones(a0.shape,float)
for layer in p['foreground_layers']:fg_transmission*=1-fm[layer['name']]
rows=[];cache={};logs=[];phase='baseline';began=time.time()

def preset(value):
    q=copy.deepcopy(p);q['core_strain']['amplitude']=float(value);return q

def compose(C):
    full=C*a0[...,None]+backdrop*(1-shadow[...,None])*(1-a0[...,None])
    for layer in p['foreground_layers']:
        aa=fm[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    return full

def native(value,save=None):
    value=float(value)
    if abs(value)>limit+1e-12:raise ValueError('Declared displacement bracket exceeded')
    if value not in cache:
        t0=time.time()
        if value==0:C=C0;actual_render=False
        else:
            C,a=model.render(source,case,preset(value));assert np.array_equal(a,a0);actual_render=True
        path=out/'evaluations'/f'{len(rows):04d}.npz';np.savez_compressed(path,material=C)
        sc={}
        for name in ['glass','rim']:
            D=(C-T)[masks[name]]*255;sc[name]={'rmse':float(np.sqrt(np.mean(D**2))),'pixels':int(masks[name].sum())}
        nofg=C*a0[...,None]+backdrop*(1-shadow[...,None])*(1-a0[...,None]);sc['shadow']=float(np.sqrt(np.mean(((nofg-T)[masks['exterior']]*255)**2)));full=compose(C);fg={}
        for layer in p['foreground_layers']:
            a,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-T[b-y0:d-y0,a-x0:c-x0])**2))*255)
        g=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']]);state={'epoch':before['epoch'],'observations':{'A':sc}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
        row={'index':len(rows),'amplitude':value,'E':error(sc),'scores':state,'foreground':fg,'guard_values':g.tolist(),'all_nonregression':bool(np.all(g<=baseguard)),'nonregression':dict(zip(['glass','rim','exterior','archivebox','plus'],map(bool,g<=baseguard))),'gate':gate,'numerical_qualifier':bool(np.all(g<=baseguard) and gate['observations']['A']['passed']),'phase':phase,'native_actual_render':actual_render,'material_cache':str(path),'seconds':time.time()-t0};rows.append(row);cache[value]=row
        (out/'native-evaluations.json').write_text(json.dumps({'before':before,'fixed_width':p['core_strain']['width'],'amplitude_bounds':[-limit,limit],'evaluations':rows,'counted_passes':0},indent=2)+'\n');print('NATIVE',len(rows),phase,value,row['E'],row['all_nonregression'],row['numerical_qualifier'],flush=True)
    else:
        row=cache[value];C=np.load(row['material_cache'])['material']
    if save:
        folder=out/save;folder.mkdir(exist_ok=True);(folder/'recipe.json').write_text(json.dumps(preset(value),indent=2)+'\n');(folder/'scores.json').write_text(json.dumps(row['scores'],indent=2)+'\n');(folder/'measurement.json').write_text(json.dumps(row,indent=2)+'\n');np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a0);np.save(folder/'complete.npy',compose(C));Image.fromarray(np.uint8(np.rint(np.clip(compose(C),0,1)*255))).save(folder/'complete-preview.png')
    return row,C

def guard_quadratics(C,dc):
    D=(C.astype(float)-T)*255;groups=[]
    for name in ['glass','rim']:
        mask=masks[name];groups.append((D[mask].ravel(),(dc[mask]*255).ravel()))
    nofg=C*a0[...,None]+backdrop*(1-shadow[...,None])*(1-a0[...,None]);mask=masks['exterior'];groups.append((((nofg-T)[mask]*255).ravel(),(dc[mask]*a0[mask,None]*255).ravel()))
    full=compose(C)
    for layer in p['foreground_layers']:
        a,b,c,d=layer['box'];sl=(slice(b-y0,d-y0),slice(a-x0,c-x0));groups.append((((full-T)[sl]*255).ravel(),(dc[sl]*(a0*fg_transmission)[sl][...,None]*255).ravel()))
    A=np.array([float(np.mean(J*J)) for R,J in groups]);B=np.array([float(2*np.mean(R*J)) for R,J in groups]);return A,B

def feasible_interval(A,B,C,lower,upper):
    for a,b,c in zip(A,B,C):
        if a>1e-22:
            discriminant=b*b-4*a*c
            if discriminant<0:return None
            root=np.sqrt(max(discriminant,0));lo=(-b-root)/(2*a);hi=(-b+root)/(2*a);lower=max(lower,lo);upper=min(upper,hi)
        elif abs(b)>1e-22:
            edge=-c/b
            if b>0:upper=min(upper,edge)
            else:lower=max(lower,edge)
        elif c>0:return None
    return None if lower>upper else (lower,upper)


# Saved pre-fit native points are immutable; only new small finite probes run.
previous=json.loads((out/'native-evaluations.json').read_text());rows=previous['evaluations'];cache={float(r['amplitude']):r for r in rows};inherited=len(rows);r0,C=native(0.);assert abs(r0['E']-baseE)<1e-12;phase='local-native-guard-cone';models=[]
for divisor in [32.,64.]:
    h=limit/divisor;rp,Cp=native(h,save='small-plus-'+str(divisor));rm,Cm=native(-h,save='small-minus-'+str(divisor));dc=(Cp.astype(float)-Cm)/(2*h);A,B=guard_quadratics(C,dc);objective_A=.7*A[0]+.3*A[1];objective_B=.7*B[0]+.3*B[1];interval=feasible_interval(1.5*A,B,np.array(r0['guard_values'])**2-baseguard**2,-limit,limit);proposal=float(np.clip(-objective_B/(2*objective_A),*interval)) if interval is not None and objective_A>0 else None
    crop_changes={}
    for name,(a,b,c,d) in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
        sl=(slice(b-y0,d-y0),slice(a-x0,c-x0));mask=masks['glass'][sl];crop_changes[name]={'baseline':float(np.sqrt(np.mean(((C-T)[sl][mask]*255)**2))),'negative_probe':float(np.sqrt(np.mean(((Cm-T)[sl][mask]*255)**2))),'positive_probe':float(np.sqrt(np.mean(((Cp-T)[sl][mask]*255)**2)))}
    models.append({'finite_h':h,'guard_names':['glass','rim','exterior','archivebox','plus'],'guard_quadratic_A':A.tolist(),'guard_quadratic_B':B.tolist(),'proposal_curvature_safety':1.5,'local_model_feasible_interval':list(interval) if interval is not None else None,'unconstrained_quadratic_amplitude':-objective_B/(2*objective_A),'constrained_proposal':proposal,'crops':crop_changes,'positive_native':rp,'negative_native':rm});print('CONE',h,interval,proposal,flush=True)
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':before['epoch'],'fixed_width':p['core_strain']['width'],'bound':bound,'models':models,'inherited_prefit_points':inherited,'new_finite_probe_points':len(rows)-inherited,'unique_native_points':len(rows),'counted_passes':0,'limits':'Local native quadratic constrained proposal analysis, not a global infeasibility proof or an optical improvement. No full-frame/foreground guard relaxed; same one-scalar family.'};(out/'guard-cone.json').write_text(json.dumps(report,indent=2)+'\n');print('GUARD CONE COMPLETE',flush=True)
