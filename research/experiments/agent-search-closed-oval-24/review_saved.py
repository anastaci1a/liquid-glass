"""Retained path reductions only; no optical model functions imported."""
from pathlib import Path
import numpy as np,json
O=Path(__file__).parent;B=O.parent/'agent-music-search-baseline-01';p=json.loads((O/'protocol.json').read_text());R=p['surface']['R'];c=np.array(p['surface']['center']);L=p['surface']['L'];q=np.load(O/'native-paths.npz',allow_pickle=False);blocked=q['blocked'];regular=q['regular_entry'];e=q['entry'][blocked];k=q['discriminant'][blocked];rad=np.linalg.norm(e[:,:2],axis=1)/R
cohorts=[]
for ref in ['a','b']:
 m=np.load(B/f'{ref}-masks.npz',allow_pickle=False)
 row={'reference':ref}
 for name in ['glass','rim','held','foreground','exterior']:
  cohort=np.repeat(np.repeat(m[name],2,0),2,1);row[name+'_blocked_subrays']=int((cohort&blocked).sum())
 cohorts.append(row)
all_k=q['discriminant'][regular];front=q['entry_normal'][regular];angles=np.rad2deg(np.arccos(np.clip(front[:,2],-1,1)))
summary={'scope':'Saved path metadata only, no new ray, direction, normal, height or Fresnel evaluation.','saved_native_records':int(regular.sum()),'strict_TIR':int((k<0).sum()),'critical_k_zero':int((k==0).sum()),'blocked_discriminant_min':float(k.min()),'blocked_discriminant_max':float(k.max()),'blocked_launch_radius_over_R':[float(rad.min()),float(rad.max())],'blocked_launch_native_bounds':[(e[:,:2]*L+c).min(0).tolist(),(e[:,:2]*L+c).max(0).tolist()],'entry_normal_tilt_degrees':[float(angles.min()),float(angles.max())],'max_bracket_width':float(q['intersection_bracket'][regular].max()),'max_exit_level_residual':float(abs(q['exit_level_residual'][regular]).max()),'cohorts':cohorts,'no_source_support_claim_for_complete_primary':True}
(O/'saved-path-review.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
