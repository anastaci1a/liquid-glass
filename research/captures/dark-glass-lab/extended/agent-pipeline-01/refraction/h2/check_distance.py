from pathlib import Path
import sys,time,json,numpy as np
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h2';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
from geometric_optics import trace_flat_front_orthographic
assert 1792653600.<=time.time()<1792655400.,'Declared H2 window'
g=json.loads((O/'geometry-checkpoint.json').read_text());p=g['scene'];s=ExpandedHarmonicBack(tuple(p['surface_half']),p['surface_radius']);x,y=np.meshgrid(np.linspace(-s.half[0],s.half[0],101),np.linspace(-s.half[1],s.half[1],41));q=trace_flat_front_orthographic(s,x,y,1.5,.5);m=q['inside']&~q['boundary_unresolved'];assert np.all(q['complete'][m]);assert .5>s.maximum_height
np.savez(O/'checkpoint-paths.npz',x=x,y=y,**q);g['status']='PASS_H2_DISTANCE_CHECK';g['H2_checkpoint_rays']=x.size;g['H1_surface_invariants_repeated']=False;g['D']=.5;g['finished_unix']=time.time();(O/'geometry-checkpoint.json').write_text(json.dumps(g,indent=2));print(g['status'],x.size)
