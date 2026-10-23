"""One joint existing material/monotone foreground-response proposal."""
import sys,json,ast,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from extended_shadow import shadow
from vector_foreground import coverage
from foreground_response import fit_blended
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'home-short-round/boundary-epoch/joint-response';out.mkdir(exist_ok=True);assert not (out/'result.json').exists()
old=json.loads((root/'home-short-round/boundary-epoch/pass-01/joint-candidate.json').read_text());rejected=json.loads((root/'home-short-round/boundary-epoch/pass-02/joint-candidate.json').read_text());trial=rejected['trials'][0];p=trial['parameters'] if 'parameters' in trial else rejected['parameters'];co=np.asarray(trial['material']);S=[Study(root/'home-short-round/input-boundary-replay-proposal'/n) for n in ['a','b']];images=[];samples=[]
for i,s in enumerate(S):
 M=np.load(root/f'home-short-round/boundary-epoch/pass-02/joint-candidate-{i}.npy') if trial.get('allowed') else s.render(p,co);images.append(M);layer=s.case['foreground_layers'][0];a,b,c,d=layer['box'];x0,y0,_,_=s.crop;A=coverage(s.folder,layer);samples.append((M[b-y0:d-y0,a-x0:c-x0],s.target[b:d,a:c],A))
style,fit=fit_blended(samples,{'response':S[0].case['foreground_response']})
# Retain original inputs; this is ONE model coefficient vector shared by BOTH backgrounds.
for s in S:s.case={**s.case,'foreground_response':style['response']}
tree=ast.parse((root/'search-short-round/propose.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='metrics');node=ast.parse(ast.unparse(node).replace(" and layer['mode'] != 'transmission'",'').replace("s.folder / 'known.png'","s.folder / s.case.get('target_observation_mask','known.png')")).body[0];exec(compile(ast.Module(body=[node],type_ignores=[]),'<retained native guards>','exec'))
scores=[metrics(s,M) for s,M in zip(S,images)];base=old['candidate']['scores'];allowed=all(a['E']<=b['E'] and a['glass']['rmse']<=b['glass']['rmse'] and all(a[k]<=b[k] for k in ['foreground','shadow']) for a,b in zip(scores,base))
for i,M in enumerate(images):np.save(out/f'candidate-{i}.npy',M)
report=dict(parameters=p,material=co.tolist(),foreground_response=style['response'],baseline=base,scores=scores,allowed=allowed,accepted=False,response_fit=fit,scope='ONE shared existing bounded monotone response, fixed SVG/inputs; combines the already declared full material step with foreground response settlement. Prior material-only proposals remain rejected. No per-image coefficients, target-matte changes, source/geometry/blur/shadow changes or optical credit for input extension.')
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print([(a['E'],a['foreground'],b['foreground']) for a,b in zip(scores,base)],allowed,flush=True)
