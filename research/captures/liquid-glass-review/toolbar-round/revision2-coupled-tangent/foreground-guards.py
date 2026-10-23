import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
import toolbar_candidate as base
package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());case=p['case'];source=np.asarray(Image.open(package/'inputs/source.png')).astype(float)/255;target=np.asarray(Image.open(package/'inputs/target.png')).astype(np.float32)/255;x0,y0,x1,y1=case['crop'];B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1];shadow=base.gaussian_coverage_shadow(case,p);fm=np.load(package/'derived-foreground.npz')
def measure(C,a):
    full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None])
    for layer in p['foreground_layers']:
        alpha=fm[layer['name']][...,None];full=full*(1-alpha)+np.array(layer['color'])*alpha
    r={}
    for layer in p['foreground_layers']:
        A,b,c,d=layer['box'];r[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,A-x0:c-x0]-T[b-y0:d-y0,A-x0:c-x0])**2))*255)
    return r
before=measure(np.load('/tmp/agent-toolbar-inner-settlement/material.npy'),np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy'));public=json.loads((package/'primary-scores.json').read_text())['foreground']
assert all(abs(v-public[k]['rmse'])<1e-9 for k,v in before.items()),(before,public)
for name in ['revision2-tangent','revision2-coupled']:
    root=Path('/tmp/agent-toolbar-'+name);rows=[]
    for i in [1,2]:
        d=root/f'seed-{i}';after=measure(np.load(d/'material.npy'),np.load(d/'alpha.npy'));checks={k:after[k]<=before[k] for k in before};rows.append({'seed':i,'before':before,'after':after,'per_foreground_nonregression':checks,'all_foreground_guards_pass':all(checks.values())})
    (root/'foreground-guards.json').write_text(json.dumps({'frozen_baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','exact_baseline_foreground_recovery':True,'rows':rows,'note':'Canonical assets/colors/placements unchanged. Separate native guards in addition to E/glass/exterior; no scores/epochs reset.'},indent=2)+'\n');print(name,rows,flush=True)
