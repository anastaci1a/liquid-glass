import os,json,hashlib,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
R=Path('/evidence/extended/helper-toolbar-work/photos-actions-source-round');V=Path('/evidence/apple-matches/219-hd.mp4');os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
if (R/'frame-provenance.json').exists():raise RuntimeError('Existing batch, no repeat')
start=json.loads((R/'started.json').read_text());assert sha(V)==start['video_sha256'];(R/'frames').mkdir();rows=[];sheet=Image.new('RGB',(750*4,198*4),'#202020');d=ImageDraw.Draw(sheet)
for i,t in enumerate(start['times']):
 cap=cv2.VideoCapture(str(V));cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read();assert ok and im.shape[:2]==(1080,1920);rgb=im[:,:,::-1];name=f'{t:05.1f}.png';p=R/'frames'/name;Image.fromarray(rgb).save(p);row=dict(requested_seconds=t,presentation_seconds=cap.get(cv2.CAP_PROP_POS_MSEC)/1000,frame_index=int(cap.get(cv2.CAP_PROP_POS_FRAMES))-1,native_size=[1920,1080],sha256=sha(p),decoder='Originalnative OpenCV RGB8; no upsample/recolor/registration');cap.release()
 old=Path(f'/evidence/apple-matches/219-{t:g}.png')
 if old.exists():row['cache_pixel_exact']=bool(np.array_equal(rgb,np.asarray(Image.open(old).convert('RGB'))))
 rows.append(row);crop=Image.fromarray(rgb).crop((570,550,1320,720));x=(i%4)*750;y=(i//4)*198;d.text((x+8,y+8),f'219 {t}s native ROI',fill='white');sheet.paste(crop,(x,y+28));save('frame-provenance-partial.json',rows);print(t,row['presentation_seconds'],flush=True)
sheet.save(R/'same-example-contact.png');save('frame-provenance.json',rows)
fontpath=Path('/evidence/extended/icon-source/SF-Pro.ttf');font=TTFont(fontpath);names=font.getGlyphOrder();candidates={key:[n for n in names if key in n and ('.tag.color' in n or '.tag.fill.color' in n)] for key in ['person','lightbulb']};save('original-vector-catalog.json',dict(font_file=str(fontpath),font_sha256=sha(fontpath),candidates=candidates));print('FONT CANDIDATES',candidates,flush=True)
