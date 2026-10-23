import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import toolbar_candidate as base
import toolbar_inner_transition as model
from crowned_footprint import field
p=json.loads(Path('/tmp/agent-toolbar-run/candidate-with-shadow-recipe.json').read_text());q=copy.deepcopy(p);q['inner_transition']={'family':'coupled_difference','exponent':5.,'band':.48,'normal_delta':[0,0,0],'gain':1.}
rng=np.random.default_rng(222);x=rng.uniform(-1.8,1.8,300);y=rng.uniform(.1,.98,300);h=1e-6
F=lambda x,y:np.array(model.mapping(x,y,q));G=lambda x,y:np.array(base.mapping(x,y,p));D=lambda x,y:F(x,y)-G(x,y)
c=((D(x+h,y)[1]-D(x-h,y)[1])-(D(x,y+h)[0]-D(x,y-h)[0]))/(2*h)
assert np.max(np.abs(c))<1e-4,float(np.max(np.abs(c)))
x=np.linspace(-2.35,2.35,500);y=np.full_like(x,.99);T,*_=field(x,y,p['shape']['half'],p['footprint_softness']);d=1-np.sqrt(T);outer=d<=.04
checks={}
for family in ['empirical','coupled_difference']:
    q['inner_transition']={'family':family,'exponent':6.,'band':.7,'normal_delta':[.02,-.01,.02],'gain':1.1}
    delta=np.array(model.mapping(x,y,q))-np.array(base.mapping(x,y,p));checks[family+'_outer_strip_max_delta']=float(np.max(np.abs(delta[:,outer])));assert checks[family+'_outer_strip_max_delta']==0
report={'enveloped_potential_curl_max':float(np.max(np.abs(c))),**checks,'note':'outer-strip map preservation is exact; native postblur/exterior guards still independently required; normal coefficient changes/total baseline empirical'}
Path('/tmp/agent-toolbar-inner-transition/mathematical-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
