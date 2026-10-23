from pathlib import Path
import sys,json,cv2,numpy as np
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from reproduce import *
folder=Path('/evidence/apple-matches/contour-baselines');folder.mkdir(exist_ok=True)
source,target,meta,reg=prepare(folder.parent,'slider',CASES['slider']);case=CASES['slider']
saved=json.load(open(ROOT/'results.json'))['slider']['models'];models={};x0,y0,x1,y1=case['crop']
for i,m in enumerate(['identity','default','field','cap','bounded','spline']):
 print('Fitting contour baseline',m,flush=True)
 f=fit(source,target,case,m,2901+i,saved[m]);f['seed']=2901+i;f['geometry']={k:case[k] for k in ['center','half','radius','oval']};f['sampling']='native-grid, deterministic 6500 subset; outer 4px weight 2.5, other rim 1.3'
 out=render(source,case,f).astype(np.float32);f['scores']=scores(out,target[y0:y1,x0:x1],case)
 (folder/f'slider-{m}.json').write_text(json.dumps(f,indent=2));(folder/f'slider-{m}-{f["seed"]}.json').write_text(json.dumps(f,indent=2))
 cv2.imwrite(str(folder/f'slider-{m}.png'),np.uint8(np.clip(out,0,1)*255)[:,:,::-1]);models[m]=f
 print(m,f['scores']['all_glass']['rmse'],f['scores']['rim']['rmse'],f['scores']['outer_rim']['rmse'],flush=True)
 (folder/'slider-report.json').write_text(json.dumps({'case':case,'frame':meta,'registration':reg,'models':models},indent=2))
