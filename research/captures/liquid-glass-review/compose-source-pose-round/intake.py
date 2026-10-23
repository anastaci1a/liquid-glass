"""Bounded native same-example source/pose intake; no image model or input fitting."""
import os,json,hashlib,sys,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
R=Path('/evidence/extended/helper-toolbar-work/compose-source-pose-round');V=Path('/evidence/apple-matches/219-hd.mp4');F=Path('/evidence/extended/icon-source/SF-Pro.ttf')
os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
if (R/'frame-provenance.json').exists():raise RuntimeError('Existing intake frames; no duplicate')
start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'))
assert sha(V)==start['video_expected_sha256'];(R/'frames').mkdir();rows=[];thumbs=[]
for t in [388,390,392,394,396,398,400,402,404,406,408,410,412,414]:
 cap=cv2.VideoCapture(str(V));cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read();assert ok and im.shape[:2]==(1080,1920);rgb=im[:,:,::-1];p=R/f'frames/{t:03d}.png';Image.fromarray(rgb).save(p);row=dict(requested_seconds=t,presentation_seconds=cap.get(cv2.CAP_PROP_POS_MSEC)/1000,frame_index=int(cap.get(cv2.CAP_PROP_POS_FRAMES))-1,native_size=[1920,1080],sha256=sha(p),decoder='OpenCV VideoCapture encoded RGB8, no rescale/interpolation/registration',original_video_sha256=start['video_expected_sha256']);cap.release()
 old=Path(f'/evidence/apple-matches/219-{t}.png')
 if old.exists():row['existing_cache_pixel_exact']=bool(np.array_equal(rgb,np.asarray(Image.open(old).convert('RGB'))));row['existing_cache_sha256']=sha(old)
 rows.append(row);crop=Image.fromarray(rgb).crop((780,340,1160,720));thumbs.append((t,crop));print('NATIVE',t,row['presentation_seconds'],flush=True)
 save('frame-provenance-partial.json',rows)
sheet=Image.new('RGB',(380*4,408*4),'#202020');d=ImageDraw.Draw(sheet)
for i,(t,im) in enumerate(thumbs):x=(i%4)*380;y=(i//4)*408;d.text((x+8,y+8),f'219 {t}s native ROI',fill='white');sheet.paste(im,(x,y+28))
sheet.save(R/'same-example-button-contact.png');save('frame-provenance.json',rows)
font=TTFont(F);matches=[n for n in font.getGlyphOrder() if any(s in n.lower() for s in ['compose','pencil','square.and'])];axes=[dict(tag=a.axisTag,minimum=a.minValue,default=a.defaultValue,maximum=a.maxValue) for a in font['fvar'].axes] if 'fvar' in font else []
save('original-vector-catalog.json',dict(font_file=str(F),font_sha256=sha(F),axes=axes,glyphs=matches,classification='Original font glyph candidates only; none selected/fitted or adopted, no target-derived alpha'))
print('FONT',matches[:35],len(matches),flush=True)
