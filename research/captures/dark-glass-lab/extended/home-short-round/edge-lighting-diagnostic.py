"""Target-independent pre-clamp edge-lighting audit, not a fit."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from material_context import effective
cv2.setNumThreads(1)
root=Path('/evidence/extended/home-short-round');r=json.loads((root/'boundary-epoch/pass-03/joint-candidate.json').read_text());p=r['parameters'];rows=[]
for n in ['a','b']:
 s=Study(root/'input-boundary-replay-proposal'/n);co=effective(s,p,np.asarray(r['candidate']['material']));points=[]
 for direction in ['top','left','bottom','right']:
  for d in [.001,.003,.006,.012,.025,.05]:
   x=p['shape_dx'];y=p['shape_dy'];R=s.radius+p.get('radius_delta',0)
   if direction=='top':y-=R-d
   if direction=='bottom':y+=R-d
   if direction=='left':x-=s.half[0]+p.get('half_x_delta',0)-d
   if direction=='right':x+=s.half[0]+p.get('half_x_delta',0)-d
   C,J=s.field(np.array([x]),np.array([y]),p);core=J[0,-1];gain=(1-core)*co[:3]+core*co[-3:];terms=J[0,:-1]*co[6:-3];raw=C[0]*gain+co[3:6]+terms.sum();points.append(dict(direction=direction,inward_over_L=d,incident_rgb=C[0].tolist(),unclipped_rgb=raw.tolist(),thin_contribution=float(terms[0]),thin_directional_contribution=terms[1:3].tolist(),negative_before_clamp=bool((raw<0).any())))
 rows.append(dict(observation=n,points=points));print(n,sum(q['negative_before_clamp'] for q in points),'of',len(points),'negative edge probes',flush=True)
(root/'edge-lighting-diagnostic.json').write_text(json.dumps(dict(status='DIAGNOSTIC ONLY; no material/model change or verified pass',interpretation='Signed thin-rim basis can drive encoded RGB negative before the existing final clamp. This is distinct from the generated external shadow and must not be corrected by target-pixel painting. The coverage-integration probe did not remove the visible dark ring and failed strict native nonregression, so it is not adopted.',observations=rows),indent=2)+'\n')
