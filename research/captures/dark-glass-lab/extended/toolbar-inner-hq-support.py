import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from crowned_tensor import mapping
p=json.loads(Path('/evidence/extended/toolbar-primary-review/inner-profile/recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];L=min(case['half']);cx,cy=case['center'];margin=3*p['source_sigma']*L+1;low=np.array([np.inf,np.inf]);high=-low;count=0;ok=True
for row in range(y0,y1,4):
 yy,xx=np.mgrid[row:min(row+4,y1):.0625,x0:x1:.0625];X,Y=mapping((xx-.46875-cx)/L,(yy-.46875-cy)/L,p);X=X*L+cx;Y=Y*L+cy
 low=np.minimum(low,[X.min(),Y.min()]);high=np.maximum(high,[X.max(),Y.max()]);count+=X.size
 ok &= bool(np.all((X>=margin)&(X<1920-margin)&(Y>=margin)&(Y<1080-margin)))
report=dict(output_scale=4,samples_per_output_axis=4,emitted_rays=count,bounds=[low.tolist(),high.tolist()],source_dimensions=[1920,1080],source_kernel_margin_native_px=margin,all_defined=ok)
Path('/evidence/extended/toolbar-primary-review/inner-profile/hq-source-support.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert ok
