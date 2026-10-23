import os,json,hashlib,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
R=Path('/evidence/extended/helper-toolbar-work/flower-previous-round');os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (R/'frame-provenance.json').exists();start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'));(R/'frames').mkdir();sheet=Image.new('RGB',(4*480,3*292),'#222');draw=ImageDraw.Draw(sheet);rows=[]
for i,t in enumerate(start['times']):
 cap=cv2.VideoCapture('/evidence/apple-matches/219-hd.mp4');cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok and bgr.shape[:2]==(1080,1920);rgb=bgr[:,:,::-1];name=f'{t:g}.png';Image.fromarray(rgb).save(R/'frames'/name);row=dict(seconds=t,presentation_seconds=cap.get(cv2.CAP_PROP_POS_MSEC)/1000,frame_index=int(cap.get(cv2.CAP_PROP_POS_FRAMES))-1,sha256=sha(R/'frames'/name),native_size=[1920,1080]);cap.release()
 if t==170:row['cached170_pixel_exact']=bool(np.array_equal(rgb,np.asarray(Image.open('/evidence/apple-matches/219-170.png').convert('RGB'))));assert row['cached170_pixel_exact']
 rows.append(row);x=(i%4)*480;y=(i//4)*292;sheet.paste(Image.fromarray(rgb).resize((480,270),Image.Resampling.LANCZOS),(x,y+22));draw.text((x+8,y+5),f'Original219 {t}s',fill='white');save('frame-provenance-partial.json',rows);print(t,row['presentation_seconds'],flush=True)
sheet.save(R/'contact.png');save('frame-provenance.json',rows)
fontp=Path('/evidence/extended/icon-source/fallback/Applications/SF Symbols.app/Contents/Resources/Fonts/SFSymbolsFallback.otf');font=TTFont(fontp);names=font.getGlyphOrder();candidate=[n for n in names if 'backward.end' in n and 'fill' in n];save('known-font-glyph-names.json',dict(font=str(fontp),font_sha256=sha(fontp),backward_end_fill_names=candidate));print('KNOWN glyphnames',candidate,flush=True)
