"""One two-neighbor source-filter family; fixed accepted pass1 baseline."""
import sys,json,ast,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from extended_shadow import shadow
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'home-short-round/boundary-epoch/source-kernel';out.mkdir(exist_ok=True);assert not (out/'result.json').exists()
r=json.loads((root/'home-short-round/boundary-epoch/pass-01/joint-candidate.json').read_text());original=r['parameters'];p=original;co=np.asarray(r['candidate']['material']);base=r['candidate']['scores'];S=[Study(root/'home-short-round/input-boundary-replay-proposal'/n) for n in ['a','b']]
tree=ast.parse((root/'search-short-round/propose.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='metrics');node=ast.parse(ast.unparse(node).replace(" and layer['mode'] != 'transmission'",'').replace("s.folder / 'known.png'","s.folder / s.case.get('target_observation_mask','known.png')")).body[0];exec(compile(ast.Module(body=[node],type_ignores=[]),'<retained fixed guards>','exec'))
rows=[];best=None
for j,delta in enumerate([.25,-.25]):
 p=copy.deepcopy(original);p['sigma']+=delta;images=[s.render(p,co) for s in S];scores=[metrics(s,m) for s,m in zip(S,images)];allowed=all(a['E']<=b['E'] and a['glass']['rmse']<=b['glass']['rmse'] and all(a[k]<=b[k] for k in ['foreground','shadow']) for a,b in zip(scores,base));row=dict(delta_native_sigma=delta,parameters=p,material=co.tolist(),scores=scores,allowed=allowed);rows.append(row);print(delta,[a['E']/b['E'] for a,b in zip(scores,base)],allowed,flush=True)
 for i,m in enumerate(images):np.save(out/f'trial{j}-ref{i}.npy',m)
 if allowed:best=row;break
(out/'result.json').write_text(json.dumps(dict(baseline=base,trials=rows,candidate=best,accepted=False,scope='One existing source Gaussian bin neighborhood; native input epoch, masks, foreground, geometry, shadow and material frozen. No dispersion claim.'),indent=2)+'\n')
