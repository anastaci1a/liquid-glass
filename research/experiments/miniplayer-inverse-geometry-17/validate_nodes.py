"""Same-height nodal Snell validation, without repeating the design solve."""
from pathlib import Path
import json,sys,datetime
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'));sys.path.insert(0,str(OUT))
from geometric_optics import refract
from hermite_height_profile import HermiteProfile
P=json.loads((OUT/'protocol.json').read_text());end=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'))
assert datetime.datetime.now(datetime.timezone.utc)<end and not (OUT/'nodal-validation.json').exists()
profile=json.loads((OUT/'back-profile.json').read_text());nodes=json.loads((OUT/'design-nodes.json').read_text())['nodes'];N=len(nodes)
old=json.loads((OUT/'result.json').read_text())['ledger']
totals=dict(old)
# The first run made two vectorized Hermite endpoint checks not charged by
# its old-spline query hook. Preserve that ledger and include this supplement.
totals['profile_scalar_queries']+=2*N+2*N
totals['shared_Snell_points']+=N
assert all(totals[k]<=P['caps'][k] for k in totals)
h=HermiteProfile(profile['radius_nodes'],profile['heights'],profile['derivatives'])
r=np.array([q['back_radius'] for q in nodes]);B=h.evaluate(r);gradient=h.evaluate(r,True)
normal=np.stack([-gradient,np.zeros(N),-np.ones(N)],-1);normal/=np.linalg.norm(normal,axis=-1)[:,None]
incident=np.array([q['inside_direction'] for q in nodes]);expected=np.array([q['direction'] for q in nodes])
out,blocked,_=refract(incident,-normal,P['fixed']['index'],1.)
assert not blocked.any()
direction_error=float(np.max(abs(out-expected)))
source=r+(-P['fixed']['background_distance']+B)*out[:,0]/out[:,2]
source_error=float(np.max(abs(source-np.array([q['target_source'] for q in nodes]))))
assert direction_error<P['tolerances']['Snell_residual'] and source_error<P['tolerances']['height_residual']
result=dict(status='ACTUAL_HERMITE_HEIGHT_AND_SNELL_NODES_PASS',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),nodes=N,maximum_direction_error=direction_error,maximum_source_plane_error=source_error,initial_Hermite_query_supplement=2*N,new_Hermite_validation_queries=2*N,new_shared_Snell_points=N,conservative_total_ledger=totals,native_images=0,source_RGB_queries=0,limits='Nodal consistency only; dense forward tracing and whole/all-guard source support still required.')
(OUT/'nodal-validation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result),flush=True)
