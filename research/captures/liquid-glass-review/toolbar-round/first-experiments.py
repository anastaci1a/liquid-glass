import sys,json,copy,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
import toolbar_candidate as model
from reproduce import CASES,scores
from progress_gate import evaluate,error
out=Path('/tmp/agent-toolbar-run');source=np.asarray(Image.open(out/'source.png')).astype(float)/255;target=np.asarray(Image.open(out/'target.png')).astype(np.float32)/255
case=CASES['regular'];p=json.loads((out/'incumbent-recipe.json').read_text());tcrop=target[285:845,475:1445];scrop=source[285:845,475:1445]
masks=np.load(out/'frozen-masks.npz');original=np.load(out/'incumbent-material.npy')
base,coverage=model.render(source,case,p);delta=float(np.max(np.abs(base-original)));assert delta==0,delta
# Freeze clean-composite exterior guard before proposing an optical trial. No pasted context.
protocol=json.loads((out/'protocol.json').read_text());protocol['exterior']='fixed original 0<sd<35 band; guard is full-composite RMSE against target, original source composited outside generated shape, no copied shadow; not a claim of a solved shadow'
(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
hashes={f:hashlib.sha256((out/f).read_bytes()).hexdigest() for f in ['source.png','target.png','frozen-masks.npz','protocol.json']};epoch=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
def record(rgb,alpha):
    sc=scores(rgb,tcrop,case);composite=rgb*alpha[...,None]+scrop*(1-alpha[...,None]);shadow=float(np.sqrt(np.mean(((composite-tcrop)[masks['exterior']]*255)**2)))
    return {'epoch':epoch,'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':shadow}}},sc,composite
before,_,_=record(base,coverage);(out/'incumbent.json').write_text(json.dumps(before,indent=2)+'\n');(out/'epoch-input-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('INCUMBENT',error(before['observations']['A']),'shadow',before['observations']['A']['shadow'],flush=True)
experiments=[('ordinary-output-blur',[(v/170,) for v in [.25,.5,.75,1.,1.5]]),('tangential-easing',[(v,) for v in [3.,3.5,4.5,5.]]),('continuous-footprint',[(v,) for v in [.08,.15,.25]])]
log=[];candidate=None
for number,(name,values) in enumerate(experiments,1):
    trials=[]
    for (v,) in values:
        q=copy.deepcopy(p)
        if number==1:q['post_sigma']=v;rgb=cv2.GaussianBlur(base,(0,0),v*170);alpha=coverage
        else:
            q['tangent_exponent' if number==2 else 'footprint_softness']=v;rgb,alpha=model.render(source,case,q)
        state,sc,composite=record(rgb,alpha);r=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
        native=all(x['passed'] for x in r['observations'].values());t={'value':v,'scores':state,'E':error(state['observations']['A']),'native_gates_passed':native,'gate':r};trials.append(t)
        print(name,v,t['E'],sc['all_glass']['rmse'],state['observations']['A']['shadow'],native,flush=True)
        if native and candidate is None:
            candidate=q;np.save(out/'candidate-material.npy',rgb);Image.fromarray(np.uint8(np.clip(composite,0,1)*255)).save(out/'candidate-clean-exterior.png');(out/'candidate.json').write_text(json.dumps(state,indent=2)+'\n');(out/'candidate-recipe.json').write_text(json.dumps(q,indent=2)+'\n')
    log.append({'experiment':number,'name':name,'trials':trials,'incumbent_preserved':True,'candidate_is_unaccepted':candidate is not None})
    (out/'first-experiments.json').write_text(json.dumps(log,indent=2)+'\n')
    if candidate is not None:break
(out/'model-review.json').write_text(json.dumps({'completed_substantive_experiments':len(log),'bounded_evaluations':sum(len(x['trials']) for x in log),'candidate_for_independent_review':candidate is not None,'qualifying_passes_counted':0,'baseline_renderer_max_absolute_difference':delta,'notes':'Each experiment isolates one normalized mechanism; no material refit or source edits. Geometry variants remain empirical image maps. Stop for lead independent acceptance before a next pass.'},indent=2)+'\n')
