from pathlib import Path
import numpy as np,json,datetime
P=Path(__file__).resolve().parent;z=np.load(P/'geometry-arrays.npz');records=[]
for key in ['a','b']:
 u=z[key+'_exit_direction'][:,6];v=np.linspace(-.93,.93,13);inner=(abs(v)>0.01)&(abs(v)<.4);outer=abs(v)>.8
 assert np.all(u[inner,1]*v[inner]>0) and np.all(u[outer,1]*v[outer]<0)
 assert np.all(u[:,2]<0)
 records.append(dict(case=key,inner_outward_transmitted=True,outer_inward_transmitted=True,all_downward=True))
(P/'cached-direction-check.json').write_text(json.dumps(dict(records=records,new_rays=0,new_height_evaluations=0,RGB_queries=0,images=0,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
