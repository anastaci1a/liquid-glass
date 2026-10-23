import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
cv2.setNumThreads(1)
r=Path('/evidence/extended/home-short-round');rows=[]
for i,n in enumerate(['a','b']):
 s=Study(r/'input-boundary-replay-proposal'/n);old=np.load(r/f'boundary-epoch/joint-response/candidate-{i}.npy');new=np.load(r/f'boundary-epoch/pass-03/joint-candidate-{i}.npy')
 def E(M):
  q=(M.astype(np.float64)-s.target_crop.astype(np.float64))*255;g=np.mean(q[s.valid]**2);rim=np.mean(q[s.rim]**2);return float(np.sqrt(.7*g+.3*rim))
 delta=(new-old)[s.valid]*255;rows.append(dict(observation=n,previous_float64_reduction_E=E(old),candidate_float64_reduction_E=E(new),difference=E(new)-E(old),changed_scored_rgb=int(np.count_nonzero(delta)),changed_pixel_rms=float(np.sqrt(np.mean(delta**2)))))
assert all(x['difference']<=0 for x in rows) and any(x['difference']<0 for x in rows)
(r/'boundary-epoch/pass-03/precision-advisory.json').write_text(json.dumps(dict(protocol='Advisory double-precision reduction of unchanged native float32 arrays; original float32 gate remains authoritative. No raster/sampler/color/source/mask change.',observations=rows),indent=2)+'\n');print(rows)
