import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image,ImageDraw
import toolbar_candidate as base
import toolbar_phase_tail as phase
from reproduce import CASES
root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-tangent');source=np.asarray(Image.open(root/'source.png')).astype(float)/255;target=np.asarray(Image.open(root/'target.png')).astype(np.float32)/255
p=json.loads((root/'candidate-with-shadow-recipe.json').read_text());q=json.loads((out/'best-recipe.json').read_text());case=copy.deepcopy(CASES['regular']);case['crop']=[960,450,1120,550]
A,aa=base.render(source,case,p,scale=4);B,ab=phase.render(source,case,q,scale=4);assert float(aa.min())==1 and float(ab.min())==1
ref=cv2.resize(target[450:550,960:1120],(640,400),interpolation=cv2.INTER_NEAREST);sheet=Image.new('RGB',(1920,440),'#202020');d=ImageDraw.Draw(sheet)
for i,(label,C) in enumerate(zip(['Apple native x4; glyph unscored','Pending .10/1.25 baseline, fresh4x','REJECTED phase k-.005/band1, fresh4x'],[ref,A,B])):
    sheet.paste(Image.fromarray(np.uint8(np.clip(C,0,1)*255)),(i*640,40));d.text((i*640+6,8),label,fill='white')
sheet.save(out/'rejected-d-stroke-4x.png');print('saved rejected crop')
