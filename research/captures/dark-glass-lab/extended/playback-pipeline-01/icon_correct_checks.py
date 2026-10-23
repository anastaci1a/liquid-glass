import json
from pathlib import Path
import numpy as np
from PIL import Image
from reproduce import CASES,points,masks,scores
P=Path('/evidence/extended/playback-pipeline-01');D=P/'icon';case=CASES['media'];x0,y0,x1,y1=case['crop'];ref=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)[y0:y1,x0:x1]/255
xs,ys,dx,dy=points(case);sd,_,_,_=masks(case,xs,ys,dx,dy);fg=np.zeros(sd.shape,bool)
for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
def m(C):return {'foreground_pixels':int(fg.sum()),'foreground_MSE':float(np.mean(((C-ref)[fg]*255)**2)),'exterior_pixels':int((sd>0).sum()),'exterior_MSE':float(np.mean(((C-ref)[sd>0]*255)**2))}
base=np.load(P/'blurriness/candidate-complete.npy');out={'cause':'Supplemental checks reversed points() xs,ys. Original scores() uses correct grid and is unchanged. Old supplemental reports preserved but superseded.','baseline':m(base),'shape':m(np.load(D/'original-vector-complete.npy')),'material':[m(np.load(D/f'material-{i}-complete.npy')) for i in range(6)]}
for label,path in [('raw-G05',Path('/evidence/extended/geometric-playback-inferred/complete.npy')),('shadow-rejected',P/'shadow/candidate-complete.npy')]:
 if path.exists():out[label]=m(np.load(path))
(D/'corrected-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
