import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from PIL import Image
from tensor_replay import composite
from publish import pair
root=Path('/evidence/extended/toolbar-primary-review');out=root/'inner-profile';inputs=Path('/tmp/lead-toolbar-input');assets=Path('/workspace/docs/liquid-glass/assets')
source=np.asarray(Image.open(inputs/'source.png'),float)/255;target=np.asarray(Image.open(inputs/'target.png'),np.float32)/255
old=json.loads((root/'final/recipe.json').read_text());new=json.loads((out/'recipe.json').read_text());case=new['case'];x0,y0,x1,y1=case['crop'];T=target[y0:y1,x0:x1]
A,_,_=composite(source,case,old,inputs);B,_,_=composite(source,case,new,inputs);masks=np.load(inputs/'frozen-masks.npz')
hi=np.asarray(Image.open(out/'hq/render.png'));hiT=cv2.resize(np.uint8(np.rint(T*255)),(hi.shape[1],hi.shape[0]),interpolation=cv2.INTER_LANCZOS4)
rows=[]
for name,box,asset in [('upper rim',[650,369,1270,435],'match-regular-rim.png'),('d-stroke',[960,450,1120,550],'toolbar-d-stroke-current.png')]:
 a,b,c,d=box;a-=x0;c-=x0;b-=y0;d-=y0;roi=np.zeros(T.shape[:2],bool);roi[b:d,a:c]=True;mask=roi&masks['glass']
 row=dict(name=name,box_native=box,visible_rmse=[float(np.sqrt(np.mean(((im-T)[roi]*255)**2))) for im in [A,B]],glass_rmse=[float(np.sqrt(np.mean(((im-T)[mask]*255)**2))) for im in [A,B]],glass_pixels=int(mask.sum()));rows.append(row)
 pair(hiT[b*4:d*4,a*4:c*4],hi[b*4:d*4,a*4:c*4],('Apple source','Revision 2 (4×)'),font_size=32).save(assets/asset)
(out/'crop-diagnostics.json').write_text(json.dumps(dict(crops=rows,order=['revision1','revision2'],purpose='Fixed local advisory diagnostics, not additional gates; crop positions unchanged'),indent=2)+'\n');print(json.dumps(rows))
