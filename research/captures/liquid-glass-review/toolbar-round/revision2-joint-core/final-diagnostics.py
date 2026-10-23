"""New final evidence on saved materials only; no rendering or refitting."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
import toolbar_candidate as baseline
root=Path('/tmp/agent-toolbar-joint-core');package=Path('/tmp/agent-toolbar-evidence-package');result=json.loads((root/'result.json').read_text());best=result['best'];p=json.loads((package/'recipe.json').read_text());q=json.loads((root/'best-feasible/recipe.json').read_text())
check=copy.deepcopy(q);check.pop('core_strain')
for i in range(3):check['parameters']['coefficients'][i+4]=p['parameters']['coefficients'][i+4]
assert check==p
case=p['case'];x0,y0,x1,y1=case['crop'];T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;B=source[y0:y1,x0:x1]
C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');C=np.load(root/'best-feasible/material.npy');assert np.array_equal(a,np.load(root/'best-feasible/alpha.npy'))
shadow=baseline.gaussian_coverage_shadow(case,p);masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fm=np.load(package/'derived-foreground.npz')
def complete(C):
    full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None])
    for layer in p['foreground_layers']:
        aa=fm[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    return full
F0=complete(C0);F=complete(C);crops={}
for name,(x,y,z,w) in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
    sl=(slice(y-y0,w-y0),slice(x-x0,z-x0));mask=masks['glass'][sl]
    def rmse(V):return float(np.sqrt(np.mean(((V-T)[sl][mask]*255)**2)))
    crops[name]={'pixels':int(mask.sum()),'before_conditional_native':rmse(C0),'after_conditional_native':rmse(C),'before_complete_native':rmse(F0),'after_complete_native':rmse(F)}
feas=json.loads((root/'feasibility.json').read_text());base=np.sqrt(feas['baseline_MSE']);actual=np.sqrt(best['MSE']);baseE=np.sqrt(.7*base[0]**2+.3*base[1]**2)
report={'best':best,'reduction_percent':100*(1-best['E']/baseE),'required_E':baseE*.995,'guard_order':feas['guard_order'],'native_guard_RMSE_before':base.tolist(),'native_guard_RMSE_after':actual.tolist(),'native_guard_RMSE_slack':(base-actual).tolist(),'recipe_only_changes_inner4_6_and_core_amplitude':True,'same_coverage_exact':True,'crops_advisory':crops,'new_renders':0,'counted_passes':0,'termination':result['termination'],'independent_acceptance':False}
(root/'final-diagnostics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
