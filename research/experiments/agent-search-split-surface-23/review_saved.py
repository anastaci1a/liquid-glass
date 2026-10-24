"""Saved-path and candidate reductions only; no numerical model imports."""
from pathlib import Path
import json,numpy as np
O=Path(__file__).parent
q=np.load(O/'native-paths.npz',allow_pickle=False);inside=q['inside'];d=q['front_reflection_direction'][inside];N=len(d)
angle=np.rad2deg(np.arccos(np.clip(d[:,2],-1,1)));summary={'scope':'Reductions of retained directions and existing candidate arrays only; zero emitter, direction, Fresnel, ray or source evaluations.','saved_direction_records':N,'min_polar_degrees':float(angle.min()),'max_polar_degrees':float(angle.max()),'emitter_inner_support_degrees':30,'all_directions_below_support':bool((angle<30).all()),'min_outgoing_clearance':float(q['outgoing_back_clearance'][inside].min()),'min_front_reflection_clearance':float(q['reflection_front_clearance'][inside].min()),'max_back_residual':float(abs(q['back_residual'][inside]).max()),'max_bracket_width':float((q['back_bracket_high'][inside]-q['back_bracket_low'][inside]).max()),'max_polarization_plane_residual':float(q['polarization_plane_residual'][inside].max()),'all_regular_complete':bool(q['complete'][inside].all()),'references':[]}
for k in ['a','b']:
 a=np.load(O/f'{k}-light1.npz',allow_pickle=False);b=np.load(O/f'{k}-light4.npz',allow_pickle=False)
 summary['references'].append({'reference':k,'encoded_samples_exact_between_amplitudes':bool(np.array_equal(a['sample_after_response'],b['sample_after_response'],equal_nan=True)),'complete_exact_between_amplitudes':bool(np.array_equal(a['complete'],b['complete'],equal_nan=True))})
(O/'saved-direction-review.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary),flush=True)
