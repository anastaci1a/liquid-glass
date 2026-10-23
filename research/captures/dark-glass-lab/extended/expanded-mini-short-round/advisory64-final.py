import json,sys
from pathlib import Path
import numpy as np
ROOT=Path('/evidence/extended/expanded-mini-short-round');sys.path.insert(0,str(ROOT));from preflight import Study
rows=[]
for i,n in enumerate(['a','b']):
 s=Study(ROOT/n);arr=[np.load(ROOT/f'ref{i}-baseline-material.npy'),np.load(ROOT/f'pass-01/ref{i}-material.npy'),np.load(ROOT/f'pass-02/ref{i}-material.npy'),np.load(ROOT/f'pass-03/ref{i}-material.npy')];vals=[]
 for a in arr:
  e=(a.astype(float)-s.target_crop)*255;vals.append(float(np.sqrt(.7*np.mean(e[s.valid]**2)+.3*np.mean(e[s.rim]**2))))
 rows.append(dict(reference=n,baseline_pass1_pass2_pass3=vals,deltas=np.diff(vals).tolist(),nonregressive=bool(np.all(np.diff(vals)<=0))))
print(json.dumps(rows,indent=2));(ROOT/'advisory-double-reduction.json').write_text(json.dumps(rows,indent=2)+'\n')
