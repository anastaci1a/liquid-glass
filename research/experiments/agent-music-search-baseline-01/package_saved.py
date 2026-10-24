"""Saved-path sections only. No geometry calls, source queries or composites."""
from pathlib import Path
import json,csv
import numpy as np
P=Path(__file__).resolve().parent;q=np.load(P/'native-paths.npz');rows=[]
for name,axis,value in [('horizontal_center','y',0.),('horizontal_upper','y',-.65),('horizontal_lower','y',.65),('vertical_center','x',0.)]:
 if axis=='y':
  at=int(np.argmin(abs(q['y'][:,0]-value)));inds=[(at,j) for j in range(q['x'].shape[1])]
 else:
  at=int(np.argmin(abs(q['x'][0]-value)));inds=[(i,at) for i in range(q['x'].shape[0])]
 for i,j in inds:
  if not (q['inside'][i,j] and q['complete'][i,j]):continue
  b=q['back'][i,j];n=q['outward_normal'][i,j];d=q['exit_direction'][i,j]
  rows.append([name,i,j,float(q['x'][i,j]),float(q['y'][i,j]),float(b[2]),*map(float,n),*map(float,d),float(q['source_X'][i,j]),float(q['source_Y'][i,j])])
with (P/'cached-sections.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['section','subray_row','subray_column','x_original_L','y_original_L','back_z_original_L','normal_x','normal_y','normal_z','exit_dx','exit_dy','exit_dz','source_X_native','source_Y_native']);w.writerows(rows)
(P/'cached-sections.json').write_text(json.dumps(dict(status='EXACT_RETAINED_NATIVE_PATH_SUBSETS',rows=len(rows),new_rays=0,height_calls=0,RGB_queries=0,images=0,scope='Nearest actual AA lattice sections; not interpolated center-line surface or additional height evaluation.'),indent=2)+'\n')
