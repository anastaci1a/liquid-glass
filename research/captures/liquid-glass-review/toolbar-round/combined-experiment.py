import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
import toolbar_candidate as model
from reproduce import CASES,scores
from progress_gate import evaluate,error
out=Path('/tmp/agent-toolbar-run');source=np.asarray(Image.open(out/'source.png')).astype(float)/255;target=np.asarray(Image.open(out/'target.png')).astype(np.float32)/255
case=CASES['regular'];tcrop=target[285:845,475:1445];scrop=source[285:845,475:1445];mask=np.load(out/'frozen-masks.npz')['exterior'];before=json.loads((out/'incumbent.json').read_text());p=json.loads((out/'incumbent-recipe.json').read_text());p['footprint_softness']=.08
rgb,alpha=model.render(source,case,p);trials=[]
for sigma in [.25,.5,.75,1.]:
    q=copy.deepcopy(p);q['post_sigma']=sigma/170
    numerator=cv2.GaussianBlur(rgb*alpha[...,None],(0,0),sigma);den=cv2.GaussianBlur(alpha,(0,0),sigma);C=(numerator/np.maximum(den,1e-12)[...,None]).astype(np.float32)
    full=C*alpha[...,None]+scrop*(1-alpha[...,None]);sc=scores(C,tcrop,case);shadow=float(np.sqrt(np.mean(((full-tcrop)[mask]*255)**2)))
    state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':shadow}}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);native=all(r['passed'] for r in gate['observations'].values())
    trials.append({'post_sigma_native_px':sigma,'scores':state,'gate':gate,'native_gates_passed':native});print(sigma,error(state['observations']['A']),sc['all_glass']['rmse'],shadow,native,flush=True)
    if native:
        (out/'candidate.json').write_text(json.dumps(state,indent=2)+'\n');(out/'candidate-recipe.json').write_text(json.dumps(q,indent=2)+'\n');np.save(out/'candidate-material.npy',C);Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(out/'candidate-clean-exterior.png');break
(out/'combined-experiment.json').write_text(json.dumps({'experiment':4,'review':'review-after-three.md','trials':trials,'qualifying_passes_counted':0},indent=2)+'\n')
