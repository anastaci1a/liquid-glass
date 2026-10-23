"""Read-only decomposition of current switch rim residual; no score/mask change."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
root=Path('/evidence/extended/active-switch');out=root/'rev3-rim-components';out.mkdir(exist_ok=True)
r=json.loads((root/'joint-native-review/candidate.json').read_text());p=r['parameters'];co=np.array(r['material']);rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);q=copy.deepcopy(p);q.pop('grazing_reflection');identity=np.zeros(23);identity[:3]=identity[-3:]=1
 full=s.render(p,co);unreflected=s.render(q,co);transmission=s.render(q,identity)
 *_,(sd,nx,ny)=s.shape(s.x,s.y,p);angle=np.arctan2(ny,nx);depth=-sd
 fields={'target':s.target_crop,'transmission_before_material':transmission,'material_before_reflection':unreflected,'final':full}
 sectors={};bins=[0,.01,.02,.04,.06,.10,.15,.20]
 for title,a in [('right',0.),('lower-right',np.pi/4),('bottom',np.pi/2),('lower-left',3*np.pi/4),('upper-right',-np.pi/4),('upper-left',-3*np.pi/4)]:
  delta=np.arctan2(np.sin(angle-a),np.cos(angle-a));records=[]
  for lo,hi in zip(bins,bins[1:]):
   mask=(abs(delta)<np.pi/12)&(depth>=lo)&(depth<hi)&s.valid
   if not mask.any():continue
   records.append(dict(depth_over_L=[lo,hi],pixels=int(mask.sum()),rgb255={key:(v[mask].mean(0)*255).tolist() for key,v in fields.items()},rmse255={key:float(np.sqrt(np.mean(((v-s.target_crop)[mask]*255)**2))) for key,v in fields.items() if key!='target'}))
  sectors[title]=records
 rows.append(dict(observation=name.upper(),sectors=sectors))
(out/'profiles.json').write_text(json.dumps(dict(advisory_only=True,limits='Fixed current source/shape/material/epoch. Native-center geometric bins are diagnostic subsets, not new score masks. Unshaded transmission retains input gamma, normal filtering and existing directional RGB map. No fit or pixel correction.',observations=rows),indent=2)+'\n')
for row in rows:
 for k in ['right','lower-right','upper-left']:
  print(row['observation'],k,[(v['depth_over_L'],{key:[round(c,1) for c in rgb] for key,rgb in v['rgb255'].items()}) for v in row['sectors'][k][:4]],flush=True)
