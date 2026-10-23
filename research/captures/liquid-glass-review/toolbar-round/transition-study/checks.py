import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import toolbar_candidate as base
import toolbar_transition as model
p=json.loads(Path('/tmp/agent-toolbar-run/candidate-with-shadow-recipe.json').read_text());q=copy.deepcopy(p);q['transition']={'family':'coupled_difference','exponent':5.,'band':.48,'normal_delta':[0,0,0]}
rng=np.random.default_rng(222);x=rng.uniform(-1.8,1.8,250);y=rng.uniform(.15,.9,250);h=1e-5
F=lambda x,y:np.array(model.mapping(x,y,q));G=lambda x,y:np.array(base.mapping(x,y,p));D=lambda x,y:F(x,y)-G(x,y)
def curl(fn):return ((fn(x+h,y)[1]-fn(x-h,y)[1])-(fn(x,y+h)[0]-fn(x,y-h)[0]))/(2*h)
c=curl(D);b=curl(G);assert np.max(np.abs(c))<1e-6,float(np.max(np.abs(c)))
report={'coupled_difference_curl_max':float(np.max(np.abs(c))),'baseline_tensor_curl_max':float(np.max(np.abs(b))),'interpretation':'added perturbation integrable; total tensor baseline remains empirical, not a recovered solid','boundary':'m>=4 in coupled family gives at leastC2 added map at inner support; empirical W m>=3 isC2'}
Path('/tmp/agent-toolbar-transition/mathematical-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
