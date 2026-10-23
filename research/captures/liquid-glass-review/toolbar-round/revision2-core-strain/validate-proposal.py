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


previous=json.loads((out/'native-evaluations.json').read_text());rows=previous['evaluations'];cache={float(r['amplitude']):r for r in rows};inherited=len(rows);cone=json.loads((out/'guard-cone.json').read_text());phase='bounded-native-proposal-validation';tests=[]
for m in cone['models']:
    proposal=m['constrained_proposal']
    if proposal is None or proposal==0:continue
    for scale in [1.,.5,.25,.125]:
        r,C=native(scale*proposal,save='validated-'+str(len(tests)));tests.append({'scale':scale,'proposal_model_h':m['finite_h'],'measurement':r})
        if r['all_nonregression'] and r['E']<baseE:break
feasible=[r for r in rows if r['all_nonregression']];best=min(feasible,key=lambda r:r['E']);raw=min(rows,key=lambda r:r['E']);native(best['amplitude'],save='best-feasible');native(raw['amplitude'],save='best-raw')
summary={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':before['epoch'],'one_family':True,'bound':bound,'fixed_width':p['core_strain']['width'],'best_guard_feasible':best,'best_raw':raw,'any_numerical_qualifier':any(r['numerical_qualifier'] for r in rows),'unique_native_points':len(rows),'actual_new_renders':sum(r['native_actual_render'] for r in rows),'new_proposal_validation_points':len(rows)-inherited,'native_proposal_tests':tests,'counted_passes':0,'stop_reason':'Required pre-fit sensitivity gives opposing full-frame/d/foreground directions; two local constrained models disagree at raster-scale interval near zero; bounded exact-native confirmation retained','limits':'This is a bounded local study, not an exhaustive global infeasibility proof or convergence claim. No crop-only gain, native guard waiver, source/mask correction or unverified curvature combination.'};(out/'result.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT',summary['any_numerical_qualifier'],best['amplitude'],best['E'],flush=True)
