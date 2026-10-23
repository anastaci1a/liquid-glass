import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from PIL import Image,ImageDraw
from vector_foreground import _coverage
root=Path('/evidence/extended');out=root/'toolbar-response-primary-review';folder=Path('/tmp/agent-toolbar-evidence-package/inputs');p=json.loads((root/'helper-toolbar-work/agent-toolbar-response-trials/first-proposal/recipe.json').read_text());a,b,c,d=p['case']['crop']
full=np.load(out/'complete.npy');new=np.load(out/'material.npy');old=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');alpha=np.load(out/'alpha.npy');trans=np.ones_like(alpha)
for layer in p['foreground_layers']:trans*=1-_coverage((folder/layer['asset']).read_bytes(),tuple(p['case']['crop']),tuple(layer['placement']),1)
previous=full-(new-old)*alpha[...,None]*trans[...,None]
reference=np.asarray(Image.open(folder/'target.png'))[b:d,a:c]
W,H=reference.shape[1],reference.shape[0];sheet=Image.new('RGB',(W,3*(H+24)),'#17191e');draw=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate([('Apple',reference),('Accepted revision 2',np.uint8(np.rint(np.clip(previous,0,1)*255))),('Unaccepted shared power candidate',np.uint8(np.rint(np.clip(full,0,1)*255)))]):
 draw.text((8,i*(H+24)+5),name,fill='white');sheet.paste(Image.fromarray(im),(0,i*(H+24)+24))
sheet.save(out/'native-review.png')
