"""Saved coordinate-unit correction only; no tracing or image modification."""
from pathlib import Path
import numpy as np,json,datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P=json.loads((OUT/'map-unit-review-protocol.json').read_text())
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'))
assert not (OUT/'map-unit-correction.json').exists()
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']
count=0;decoded=0;rows=[]
for member in ['expanded','compact']:
 q=np.load(OUT/f'{member}-paths.npz');old=np.load(ROOT/('research/experiments/expanded-spline-observation-01/native-paths.npz' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06/compact-paths.npz'))
 inside=q['inside'];decoded+=inside.nbytes;error=[]
 for axis,key in enumerate(['X','Y']):
  current=q[key];prior=old[key];decoded+=current.nbytes+prior.nbytes
  assert decoded<=P['caps']['decoded_array_bytes']
  count+=2*int(inside.sum());assert count<=P['caps']['saved_coordinate_observations']
  if member=='expanded':prior=(prior-scene['center'][axis])/scene['L']
  error.append(current[inside]-prior[inside])
 maximum=max(float(np.max(abs(v))) for v in error)
 rows.append(dict(member=member,old_cache_units='nativepixels' if member=='expanded' else 'normalizedL',comparison_units='normalizedL',maximum_coordinate_error_L=maximum,maximum_coordinate_error_native_pixels=maximum*88.5))
result=dict(status='DIAGNOSTIC_UNIT_CORRECTION_ONLY',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,saved_coordinate_observations=count,decoded_array_bytes=decoded,original_diagnostic_preserved=True,actual_coordinates_changed=False,actual_images_changed=False,note='Initial expanded diagnostic subtracted pixel units from normalized units. The as-run value remains; no sample was ever taken from the diagnostic.',administrative_note='An initial one-line Python metadata snippet failed syntax before execution; no array read or optical call.')
(OUT/'map-unit-correction.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
