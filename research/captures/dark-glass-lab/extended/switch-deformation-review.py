import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from switch_deformation_model import DeformationStudy,depth_coordinate
root=Path('/evidence/extended/active-switch');out=root/'deformation-review';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text());S=[DeformationStudy(root/'paired'/n) for n in ['a','b']];co=np.array(old['material']);p=old['parameters'];anchor=depth_coordinate(S[0],p)[0];rows=[]
for coupling in [0.,.5,1.]:
    q=copy.deepcopy(p);q['deformation_response']=dict(reference_depth_coordinate=anchor,coupling=coupling)
    sc=[s.scores(s.render(q,co),include_ssim=False) for s in S];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,old['scores'])]
    row=dict(parameters=q,material=co.tolist(),scores=sc,ratios=ratios,depth_coordinates=[depth_coordinate(s,p) for s in S],accepted=False);rows.append(row)
    print('DEFORMATION',coupling,ratios,row['depth_coordinates'],flush=True)
    (out/'review.json').write_text(json.dumps(dict(trials=rows,limits='Measured track geometry normalizes video scale. Constant-volume/self-similar height and weak displacement scaling are hypotheses. No source colors, target pixels or per-reference fitting enter the law. Native frozen scores unchanged.'),indent=2)+'\n')
