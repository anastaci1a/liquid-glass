"""ONE physical height family: map-only proposal, then original native comparison."""
import sys,json,copy,time,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from scipy.optimize import least_squares
from PIL import Image
import toolbar_back_surface as model
from progress_gate import error,evaluate
cv2.setNumThreads(1)
out=Path('/tmp/agent-toolbar-back-surface');out.mkdir(exist_ok=True);(out/'map-evaluations').mkdir(exist_ok=True)
checks=json.loads((out/'invariants.json').read_text());assert checks['model_sha256']==hashlib.sha256(Path('/tmp/agent-toolbar-code/toolbar_back_surface.py').read_bytes()).hexdigest()
package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());p['model']='toolbar_back_surface_biaxial';before=json.loads((package/'primary-verification.json').read_text())['candidate']
p['back_surface']={'thickness':.5,'background':2.5,'ior':1.5,'b_major':0.,'b_minor':0.,'quartic':0.};scales=np.array([.03,.03,.15]);names=['b_major','b_minor','quartic']
grid=np.load('/tmp/agent-toolbar-surface-diagnostic/fine-04-fields.npz');mask=grid['inside'];x=grid['x'][mask];y=grid['y'][mask];targetv=grid['displacement'][mask];rows=[];cache={}
def preset(z):
    q=copy.deepcopy(p)
    for name,v in zip(names,np.asarray(z)*scales):q['back_surface'][name]=float(v)
    return q
def residual(z):
    z=np.asarray(z,float);key=tuple(map(float,z))
    if key not in cache:
        q=preset(z);bound=model.analytic_bounds(q);assert bound['global_subcritical_positive_clearance']
        X,Y,valid,aux=model.rays(x,y,q);assert np.all(valid)
        delta=np.stack([X-x,Y-y],axis=-1)-targetv;flat=delta.ravel();index=len(rows);np.savez_compressed(out/'map-evaluations'/f'{index:04d}.npz',residual=flat)
        row={'index':index,'z':list(key),'parameters':(z*scales).tolist(),'map_vector_RMSE_L':float(np.sqrt(np.mean(np.sum(delta*delta,axis=-1)))),'component_RMSE_L':float(np.sqrt(np.mean(delta*delta))),'analytic_bounds':bound};rows.append(row);cache[key]=(flat,row);(out/'map-evaluations.json').write_text(json.dumps({'grid':'frozen17fine-04','grid_points':len(x),'parameter_names':names,'normalized_scales':scales.tolist(),'target_image_pixels_used':0,'evaluations':rows},indent=2)+'\n')
    return cache[key][0]
results=[]
for i,start in enumerate([[0.,0.,0.],[-.5,.5,-.4666666666666667],[.6666666666666667,.6666666666666667,-.9333333333333333]]):
    fit=least_squares(residual,start,bounds=(-np.ones(3),np.ones(3)),jac='3-point',ftol=1e-11,xtol=1e-11,gtol=1e-11,max_nfev=400)
    r=residual(fit.x);q=preset(fit.x);np.savez_compressed(out/f'start-{i+1}-projection.npz',z=fit.x,parameter_scales=scales,residual=r,jacobian_normalized=fit.jac,x=x,y=y,target_displacement=targetv)
    row={'start':start,'z':fit.x.tolist(),'parameters':(fit.x*scales).tolist(),'success':bool(fit.success),'status':int(fit.status),'message':str(fit.message),'nfev':int(fit.nfev),'optimality':float(fit.optimality),'active_mask':fit.active_mask.tolist(),'cost':float(fit.cost),'map_vector_RMSE_L':float(np.sqrt(np.mean(r*r)*2)),'bounds':model.analytic_bounds(q)};results.append(row);(out/'projection-results.json').write_text(json.dumps(results,indent=2)+'\n');print('MAP_PROJECTION',i+1,json.dumps(row),flush=True)
best_index=min(range(len(results)),key=lambda i:results[i]['cost']);best=results[best_index];q=preset(best['z']);(out/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');np.savez_compressed(out/'best-projection.npz',**dict(np.load(out/f'start-{best_index+1}-projection.npz')))
case=p['case'];x0,y0,x1,y1=case['crop'];source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;target=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');foreground=np.load(package/'derived-foreground.npz');basefg=json.loads((package/'primary-scores.json').read_text())['foreground'];base=np.array([before['observations']['A']['glass']['rmse'],before['observations']['A']['rim']['rmse'],before['observations']['A']['shadow'],basefg['archivebox']['rmse'],basefg['plus']['rmse']])
assert hashlib.sha256((package/'inputs/source.png').read_bytes()).hexdigest()=='6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b'
C,a=model.render(source,case,q);assert np.array_equal(a,np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy'));np.save(out/'material.npy',C);np.save(out/'alpha.npy',a);scores={}
for name in ['glass','rim']:
    D=(C-target)[masks[name]]*255;scores[name]={'rmse':float(np.sqrt(np.mean(D*D))),'pixels':int(masks[name].sum())}
shadow=model.baseline.gaussian_coverage_shadow(case,p);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);scores['shadow']=float(np.sqrt(np.mean(((full-target)[masks['exterior']]*255)**2)))
for layer in p['foreground_layers']:
    aa=foreground[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
fg={}
for layer in p['foreground_layers']:
    aa,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,aa-x0:c-x0]-target[b-y0:d-y0,aa-x0:c-x0])**2))*255)
values=np.array([scores['glass']['rmse'],scores['rim']['rmse'],scores['shadow'],fg['archivebox'],fg['plus']]);measurement={'epoch':before['epoch'],'observations':{'A':scores}};gate=evaluate(before,measurement,visual_review=False,replay_verified=False,source_support_verified=False)
np.save(out/'complete.npy',full);Image.fromarray(np.uint8(np.rint(np.clip(full,0,1)*255))).save(out/'complete-preview.png');(out/'scores.json').write_text(json.dumps(measurement,indent=2)+'\n');crops={}
for name,(aa,b,c,d) in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
    sl=(slice(b-y0,d-y0),slice(aa-x0,c-x0));mask=masks['glass'][sl];crops[name]={'conditional_native_RMSE':float(np.sqrt(np.mean(((C-target)[sl][mask]*255)**2))),'complete_native_RMSE':float(np.sqrt(np.mean(((full-target)[sl][mask]*255)**2)))}
report={'selected_map_start':best_index+1,'projection':best,'native_E':error(scores),'native_foreground':fg,'guard_order':['glass','rim','exterior','archivebox','plus'],'guard_before':base.tolist(),'guard_after':values.tolist(),'all_native_guards':bool(np.all(values<=base)),'gate':gate,'numerical_qualifier':bool(np.all(values<=base) and gate['observations']['A']['passed']),'advisory_crops':crops,'new_native_comparison_renders':1,'target_image_fits':0,'counted_passes':0,'limitations':'Map fitting is a proposal and not a lower bound on best attainable image score. Physical ray geometry only; frozen empirical shading/blur/shadow/foreground. No identified Apple surface, source correction or epoch change.'};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE_COMPARISON',json.dumps(report),flush=True)
