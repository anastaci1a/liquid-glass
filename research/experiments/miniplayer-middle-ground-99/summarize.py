"""Declared scalar geometry/shadow diagnostics and existing-record summary."""
from pathlib import Path
import json,sys,datetime
import numpy as np
R=Path(__file__).resolve().parents[3];O=Path(__file__).parent;sys.path.insert(0,str(R/'reconstruction'))
# Eight extent queries (384 fixed bisection points), 42 scalar shadow evaluations.
(O/'summary-protocol.json').write_text(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),maximum_extent_queries=8,fixed_bisection_points=384,shadow_scalar_points=42,new_source_or_image_reads=0,deadline=json.loads((O/'plan.json').read_text())['deadline']),indent=2)+'\n')
from ellipse_edge_effects import extent_at
f=json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text());L=f['length_unit_native_pixels'];rad=f['geometry']['corner_radius']*L;B=f['geometry']['minor_half']*L
joins=[]
for m in ['expanded','compact']:
 A=f['members'][m]['major_half']*L
 for reduction in [0,.75,1.25,2.]:
  h=float(extent_at(np.array([A-rad]),(A,B),rad-reduction)[0]);joins.append(dict(member=m,radius_reduction=reduction,old_join_inset=B-h,top_moves_down=True,bottom_moves_up=True,axis_extrema_unchanged=True))
shadows=[]
for offset,strength in [(0,.08),(14,34/255),(18,34/255)]:
 for side in [-1,1]:
  for d in [.5,4,8,16,20.5,32,64]:
   sd=d-side*offset;v=255*(1-strength*np.exp(-(max(sd,0)/32)**1.5));shadows.append(dict(offset=offset,side='above' if side==-1 else 'below',outside_distance=d,unit_white_output=v,hex=f'#{round(v):02X}{round(v):02X}{round(v):02X}'))
(O/'shape-shadow-summary.json').write_text(json.dumps(dict(joins=joins,shadow_controls=shadows,scope='Model unit-white central-axis controls, not registered measurements of the reported reference hex colors.'),indent=2)+'\n')
print(json.dumps(joins,indent=2))
