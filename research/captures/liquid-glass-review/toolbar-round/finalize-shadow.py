import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
import toolbar_candidate as model
from reproduce import CASES,scores
from progress_gate import error,evaluate
out=Path('/tmp/agent-toolbar-run');case=CASES['regular'];source=np.asarray(Image.open(out/'source.png')).astype(float)/255;target=np.asarray(Image.open(out/'target.png')).astype(np.float32)/255
p=json.loads((out/'candidate-with-shadow-recipe.json').read_text());saved=json.loads((out/'candidate-with-shadow.json').read_text());before=json.loads((out/'incumbent.json').read_text());C=np.load(out/'candidate-with-shadow-material.npy');alpha=np.load(out/'candidate-with-shadow-alpha.npy');mask=np.load(out/'frozen-masks.npz');B=source[285:845,475:1445];T=target[285:845,475:1445]
a=model.gaussian_coverage_shadow(case,p);comp=C*alpha[...,None]+B*(1-a[...,None])*(1-alpha[...,None]);shadow=float(np.sqrt(np.mean(((comp-T)[mask['exterior']]*255)**2)));state=copy.deepcopy(saved);state['observations']['A']['shadow']=shadow
report={'experiment':6,'shadow':p['shadow'],'scores':state,'E':error(state['observations']['A']),'shadow_repeat_rmse_difference':shadow-saved['observations']['A']['shadow'],'glass_parameters_preserved_during_shadow_fit':True,'mask_coverage_min':float(alpha[mask['glass']].min()),'actual_composite_glass_scores_advisory':scores(comp.astype(np.float32),T,case),'gate':evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False),'qualifying_passes_counted':0,'limits':'Gaussian width reached .3L bound; source blank estimate and fixed35px exterior constrain this model conditionally. No unique light rig or far-shadow identification. Three initial starts converged to same boundary optimum; incomplete reporting jobs are not extra experiments/passes.'}
(out/'shadow-fit.json').write_text(json.dumps(report,indent=2)+'\n');(out/'candidate-with-shadow.json').write_text(json.dumps(state,indent=2)+'\n');Image.fromarray(np.uint8(np.clip(comp,0,1)*255)).save(out/'candidate-with-shadow-clean.png');np.save(out/'shadow-opacity.npy',a);print(json.dumps(report),flush=True)
