import numpy as np,json,zipfile
from pathlib import Path
R=Path('/research/liquid-glass/research/experiments/miniplayer-split-surface-09');O=Path(__file__).parent
used=0;rows=[]
for member in ['expanded','compact']:
 with np.load(R/f'{member}-paths.npz',allow_pickle=False) as z:
  a=z['regular_entry'];used+=a.nbytes;ix=np.flatnonzero(a.reshape(-1));sel=ix[np.linspace(0,len(ix)-1,64,dtype=int)];data={}
  for f in ['front','back','front_normal','outward_normal','interior_direction','exit_direction','primary_back_clearance','primary_front_clearance','back_bracket_low','back_bracket_high','back_residual','polarization_plane_residual','complete']:
   a=z[f];used+=a.nbytes
   assert used<=536870912
   data[f]=a.reshape((-1,)+a.shape[2:])[sel].tolist()
  rows.append(dict(member=member,flat_indices=sel.tolist(),records=data))
(O/'saved-path-review.json').write_text(json.dumps(dict(decoded_payload_bytes=used,saved_records=128,rows=rows),indent=2)+'\n')
