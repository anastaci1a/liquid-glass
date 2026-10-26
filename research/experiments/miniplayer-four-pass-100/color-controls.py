from pathlib import Path
import numpy as np,json,datetime
from miniplayer_refinement_effects import saturated_rim
P=Path(__file__).parent
colors=np.array([[0.,0.,0.],[1.,1.,1.],[.95,.89,.38],[.98,.94,.52],[.4,.2,.01]])
rows=[]
for chroma in [1.,1.35,1.7]:
 for alpha in [0.,.5,1.]:
  v=saturated_rim(colors,colors,np.full(len(colors),alpha),chroma=chroma)
  assert np.isfinite(v).all() and v.min()>=0 and v.max()<=1 and np.array_equal(v[1],colors[1])
  if alpha==0:assert np.array_equal(v,colors)
  rows.append(dict(chroma=chroma,alpha=alpha,output=v.tolist()))
(P/'color-controls.json').write_text(json.dumps({'passed':True,'color_inputs':45,'maximum_inputs':45,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'recovery':'Initial zero-alpha response lacked early return; fixed and tested separately. Prior quadrature controls were not repeated. Initial failed five color inputs remain charged separately.'},indent=2)+'\n')
print('COLOR CONTROLS PASS')
