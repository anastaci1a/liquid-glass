import sys,json,ast,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from extended_fit import Study
from extended_shadow import shadow
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'home-short-round/pass-01';r=json.loads((out/'joint-candidate.json').read_text());p=copy.deepcopy(r['parameters']);tree=ast.parse((root/'search-short-round/propose.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='metrics');node=ast.parse(ast.unparse(node).replace(" and layer['mode'] != 'transmission'",'')).body[0];exec(compile(ast.Module(body=[node],type_ignores=[]),'<original named exterior guard>','exec'))
p['shadow']['opacity']*=.9
scores=[metrics(Study(root/'music-home-vector-corrected/paired'/n),np.load(out/f'joint-candidate-{i}.npy')) for i,n in enumerate(['a','b'])]
allowed=all(a['shadow']<=b['shadow'] for a,b in zip(scores,r['baseline']))
proposal=dict(parameters=p,material=r['candidate']['material'],scores=scores,allowed=allowed,scope='ONE existing neutral shadow opacity neighbor,10percent reduction. No optical rerender or source correction. Actual native material arrays reused; named exterior mask fixed before this comparison.')
(out/'shadow-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n');print([(a['shadow'],b['shadow']) for a,b in zip(scores,r['baseline'])],allowed)
