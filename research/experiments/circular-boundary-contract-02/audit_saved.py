from pathlib import Path
import json,datetime,hashlib
import numpy as np
P=Path(__file__).resolve().parent
F=Path('/helper/research/experiments/agent-circle-radius-parity-11/config-00.npz')
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
assert not (P/'result.json').exists();assert datetime.datetime.now(datetime.timezone.utc)<end
sha=lambda:hashlib.sha256(F.read_bytes()).hexdigest()
first=sha();z=np.load(F);points=z['points'];assert len(points)==33
observations=sum(z[k].size for k in z.files);assert observations<=p['caps']['scalar_array_observations']
status={}
for key in ['inside','boundary_unresolved','complete']:
 a=z['flat_'+key];b=z['closed_'+key]
 status[key]={'equal':bool(np.array_equal(a,b)),'different_indices':np.flatnonzero(a!=b).tolist()}
regular=z['flat_inside']&~z['flat_boundary_unresolved'];boundary=z['flat_boundary_unresolved'];clear=~z['flat_inside']
groups={}
for name,mask in [('regular',regular),('boundary',boundary),('clear',clear)]:
 groups[name]={'count':int(mask.sum()),'flat_inside':z['flat_inside'][mask].tolist(),'closed_inside':z['closed_inside'][mask].tolist(),'flat_complete':z['flat_complete'][mask].tolist(),'closed_complete':z['closed_complete'][mask].tolist()}
for name,a,b in [('X','X','X'),('Y','Y','Y'),('exit','back','exit'),('normal','outward_normal','exit_normal'),('direction','exit_direction','exit_direction')]:
 av=z['flat_'+a];bv=z['closed_'+b]
 groups['regular'][name]={'NaN_pattern_exact':bool(np.array_equal(np.isnan(av[regular]),np.isnan(bv[regular]))),'max_absolute_difference':float(np.max(abs(av[regular]-bv[regular])))}
 if name in ['X','Y']:
  groups['boundary'][name+'_both_NaN']=bool(np.isnan(av[boundary]).all() and np.isnan(bv[boundary]).all())
  groups['clear'][name+'_exact_identity']=bool(np.array_equal(av[clear],points[clear,0 if name=='X' else 1]) and np.array_equal(bv[clear],points[clear,0 if name=='X' else 1]))
projected=z['closed_inside']|z['closed_boundary_unresolved']
assert sha()==first
assert datetime.datetime.now(datetime.timezone.utc)<end
out=dict(status='SAVED_FIRST_CONFIGURATION_CONTRACT_DIAGNOSIS_ONLY',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=first,status_fields=status,groups=groups,closed_strict_plus_boundary_matches_flat_inside=bool(np.array_equal(projected,z['flat_inside'])),regular_membership_matches=bool(np.array_equal(regular,z['closed_inside']&~z['closed_boundary_unresolved'])),saved_ray_records=len(points),scalar_array_observations=observations,new_optical_evaluations=0,remaining_configurations_reviewed=0,original_failed_checkpoint_remains_failed=True)
(P/'result.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps(out))
