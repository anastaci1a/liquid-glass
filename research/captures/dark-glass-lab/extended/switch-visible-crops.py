"""Advisory crop metrics of the visible composite, with frozen crop positions."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from revision_replay import clean_composite
from crop_diagnostics import diagnostics
root=Path('/evidence/extended/active-switch');states=[json.loads((root/path).read_text()) for path in ['paired/accepted.json','crown-material-review/candidate.json','rim-width-review/minimax.json']]
crops={'upper-left':[.12,.06,.40,.31],'lower-left':[.12,.64,.42,.87],'right-rim':[.72,.28,.91,.70],'center':[.35,.35,.65,.65]};summary=[]
keys=['bounds_normalized','bounds_pixels','rgb_rmse_255','channel_rmse_255','luma_rmse_255','chroma_rmse_255','mean_signed_rgb_255','pixel_error_p95_255']
for n in ['a','b']:
 s=Study(root/'paired'/n);row=dict(observation=n.upper(),scope='Visible clean composite, including generated exterior. Corrects earlier conditional-material-only crop measurements; core glass/rim acceptance masks unchanged.',states=[])
 for model in states:
  p=model['parameters'];v=clean_composite(s,p,s.render(p,np.asarray(model['material'])));detail=diagnostics(s.target_crop,v,crops);row['states'].append({k:{a:b for a,b in item.items() if a in keys} for k,item in detail.items()})
 summary.append(row)
(root/'rim-width-review/visible-crops.json').write_text(json.dumps(summary,indent=2)+'\n');print('Visible-composite crop summaries written',flush=True)
