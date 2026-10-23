import sys,json,ast,math,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from extended_shadow import shadow
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/compact-mini-round');packet=root/'thin-material-pass1';out=Path('/evidence/extended/compact-pass02-primary-review');r=json.loads((packet/'result.json').read_text());native=json.loads((packet/'candidate-native.json').read_text());p=native['parameters'];co=np.asarray(native['material']);tree=ast.parse((root/'preflight.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='guards');exec(compile(ast.Module(body=[node],type_ignores=[]),'<original frozen guards>','exec'))
rows=[];oldp=json.loads((root/'baseline-native-recipe.json').read_text())['parameters'];assert {k:v for k,v in p.items() if k not in ['rim_width','thin_width']}=={k:v for k,v in oldp.items() if k not in ['rim_width','thin_width']}
for i,n in enumerate(['a','b']):
 s=Study(root/n);M=s.render(p,co);diff=float(np.max(abs(M-np.load(packet/f'trial2-ref{i}-material.npy'))));assert diff==0;score,_,_=guards(s,p,M);expected=r['candidate']['scores'][i];assert score==expected,(score,expected);before=r['baseline'][i];assert score['E']<=before['E'] and score['glass']['rmse']<=before['glass']['rmse'] and score['exterior']['rmse']<=before['exterior']['rmse'] and all(v<=before['foreground_mse'][k] for k,v in score['foreground_mse'].items());rows.append(dict(observation=n,previous=before,candidate=score,native_max_difference=diff));print(n,score['E'],flush=True)
report=dict(native_replay=True,visual_review=False,accepted=False,observations=rows,source_proof='Independent comparison verifies ALL parameters except one lighting-only rim_width unchanged. Material coefficients also change; original whole and all-scored source maps/kernels/emitted grid proofs are reused, with min defined/observed1. No repeated source-ray probe claimed.',code_note='Current optional target-observation-mask constructor defaults to original known.png for these unchanged cases; native pixels and every original guard recover EXACTLY despite source-code digest change.',limits='A improvement tiny; B measurable. Artwork and source assignments remain approximate observations; no Apple parity claim.')
(out/'verification-pending-visual.json').write_text(json.dumps(report,indent=2)+'\n')
