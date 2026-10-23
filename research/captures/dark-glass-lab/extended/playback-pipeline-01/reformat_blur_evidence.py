from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
P=Path('/evidence/extended/playback-pipeline-01');D=P/'blurriness';C=np.load(D/'candidate-complete.npy');old=np.load('/evidence/extended/geometric-playback-inferred/complete.npy');target=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)/255
rects=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right',[1025,320,1245,560]),('center-texture',[900,690,1040,755])];canvas=Image.new('RGB',(1324,1826),'white');draw=ImageDraw.Draw(canvas);metadata=[]
for i,(name,(a,b,c,d)) in enumerate(rects):
 w=min(2*(c-a),max(c-a,720));h=round((d-b)*w/(c-a));metadata.append({'name':name,'source_box':[a,b,c,d],'native_size':[c-a,d-b],'display_size':[w,h],'rule':'min(2W,max(W,720)) with aspect preserved'})
 for j,(v,label) in enumerate([(target[b:d,a:c],'Apple'),(old[b-220:d-220,a-620:c-620],'G05 no optical blur'),(C[b-220:d-220,a-620:c-620],'Output blur 1.7 native pixels')]):
  im=Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255))).resize((w,h),Image.Resampling.NEAREST);canvas.paste(im,(442*j,544*i+64));draw.text((442*j+5,544*i+20),name+' / '+label,fill='black')
canvas.save(D/'candidate-crops-width-rule.png');(D/'preview-width-rule.json').write_text(json.dumps({'regions':metadata,'new_optical_renders':0,'native_arrays_unchanged':True,'original_oversized_and_distorted_sheets_preserved_not_preferred':True},indent=2)+'\n')
