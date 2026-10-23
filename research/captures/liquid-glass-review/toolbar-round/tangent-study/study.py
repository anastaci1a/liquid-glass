import sys,json,copy,hashlib,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
import toolbar_candidate as base
import toolbar_phase_tail as model
from reproduce import CASES,scores
from progress_gate import error,evaluate
root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-tangent');out.mkdir(exist_ok=True)
case=CASES['regular'];p=json.loads((root/'candidate-with-shadow-recipe.json').read_text());before=json.loads((root/'candidate-with-shadow.json').read_text());source=np.asarray(Image.open(root/'source.png')).astype(float)/255;target=np.asarray(Image.open(root/'target.png')).astype(np.float32)/255
B=source[285:845,475:1445];T=target[285:845,475:1445];masks=np.load(root/'frozen-masks.npz');shadow=base.gaussian_coverage_shadow(case,p);C0=np.load(root/'candidate-with-shadow-material.npy')
# Zero-strength raster identity and phase Jacobian symmetry, independent of images.
zero=copy.deepcopy(p);zero['phase_tail']={'strength':0,'band':.8};C,a=model.render(source,case,zero);delta=float(np.max(np.abs(C-C0)));assert delta==0,delta
rng=np.random.default_rng(222);x=rng.uniform(-1.6,1.6,200);y=rng.uniform(.2,.85,200);q=copy.deepcopy(p);q['phase_tail']={'strength':.01,'band':.8};h=1e-5
axp,ayp=model.perturbation(x+h,y,q);axm,aym=model.perturbation(x-h,y,q);bxp,byp=model.perturbation(x,y+h,q);bxm,bym=model.perturbation(x,y-h,q)
curl=(ayp-aym)/(2*h)-(bxp-bxm)/(2*h);assert np.max(np.abs(curl))<1e-7,float(np.max(np.abs(curl)))
checks={'zero_strength_native_max_abs':delta,'perturbation_curl_max':float(np.max(np.abs(curl))),'total_field_integrability':'NOT asserted; inherited tensor field remains empirical','qualifying_passes_counted':0}
(out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');print('CHECKS',checks,flush=True)
rows=[];bestE=1e10;best=None
for band in [.65,.8,1.]:
    for strength in [-.01,-.005,.005,.01]:
        q=copy.deepcopy(p);q['phase_tail']={'strength':strength,'band':band};C,a=model.render(source,case,q);sc=scores(C,T,case);full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);ext=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)));state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':ext}}};E=error(state['observations']['A']);gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ok=all(r['passed'] for r in gate['observations'].values())
        row={'band':band,'strength':strength,'E':E,'scores':state,'gate':gate,'native_pass':ok};rows.append(row);print('TRIAL',band,strength,E,sc['all_glass']['rmse'],ext,ok,flush=True)
        if E<bestE:bestE=E;best=(q,C,a,full,state,ok)
        (out/'study.json').write_text(json.dumps({'experiment':7,'one_hypothesis':'compact C2 phase tail','before':before,'trials':rows,'qualifying_passes_counted':0},indent=2)+'\n')
q,C,a,full,state,ok=best;(out/'best-recipe.json').write_text(json.dumps(q,indent=2)+'\n');(out/'best-score.json').write_text(json.dumps(state,indent=2)+'\n');np.save(out/'best-material.npy',C);np.save(out/'best-alpha.npy',a);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(out/'best-clean-preview.png');(out/'result.json').write_text(json.dumps({'best_E':bestE,'best_numerical_gate_pass':ok,'counted_passes':0,'prerequisite':'pending first candidate not yet accepted by primary','unchanged':['source','mask','registration','footprint','material','ordinary blur','shadow']},indent=2)+'\n');print('RESULT',bestE,ok,flush=True)
