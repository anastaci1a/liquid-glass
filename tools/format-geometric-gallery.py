"""Format saved geometric models for the gallery; zero optical evaluation."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'.evidence-working/geometric-gallery'
ASSETS=ROOT/'guide/assets';records=[]
font=ImageFont.load_default(size=18)
def display(a):
 a=np.asarray(a);valid=np.isfinite(a).all(2)
 yy,xx=np.indices(valid.shape);checker=np.where(((xx//6+yy//6)%2)[...,None],.72,.9)
 a=np.where(valid[...,None],a,checker)
 return Image.fromarray(np.uint8(np.rint(np.clip(a,0,1)*255)))
def pair(name,target,calculated,label,max_width=1080):
 reference=target.convert('RGB');predicted=display(calculated)
 assert predicted.size==reference.size
 original=reference.size;w=min(original[0],max_width);h=round(original[1]*w/original[0])
 if (w,h)!=original:
  reference=reference.resize((w,h),Image.Resampling.LANCZOS);predicted=predicted.resize((w,h),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(2*w+2,h+64),'white');draw=ImageDraw.Draw(canvas)
 canvas.paste(reference,(0,64));canvas.paste(predicted,(w+2,64))
 draw.text((12,20),'Apple reference',font=font,fill='black');draw.text((w+14,20),label,font=font,fill='black')
 dest=ASSETS/name;canvas.save(dest)
 records.append({'asset':'assets/'+name,'width':canvas.width,'height':canvas.height,'top':64,'bottom':0,'gutter':2,'native_panel_size':list(original),'shown_panel_size':[w,h],'unavailable_pixels':int((~np.isfinite(calculated).all(2)).sum()),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
pair('geometric-playback-primary.png',Image.open(WORK/'play-target.png').crop((620,220,1300,875)),np.load(ROOT/'research/experiments/clear-play-02/candidate.npz')['complete'],'Incident blur 1.7 px; incomplete model')
pair('geometric-toolbar-primary.png',Image.open(WORK/'toolbar-target-sha.png').crop((475,285,1445,845)),np.asarray(Image.open(WORK/'toolbar.png').convert('RGB'))/255,'Primary geometric baseline')
for k in ['a','b']:
 target=Image.open(WORK/f'music-{k}-target.png')
 pair(f'geometric-expanded-primary-{k}.png',target.crop((280,290,1640,540)),np.load(ROOT/f'research/experiments/expanded-geometry-02/h1-{k}.npz')['complete'],'Incident blur 6.75 px; incomplete model')
 raw=np.load(ROOT/f'research/experiments/navigation-geometry-01/{k}-raw.npz')
 pair(f'geometric-navigation-primary-{k}.png',target.crop((285,495,1365,830)),raw['complete'],'Primary geometric baseline')
metadata=json.loads((ROOT/'guide/comparison-panels.json').read_text())
for r in records:metadata[r['asset']]={key:r[key] for key in ['width','height','top','bottom','gutter']}
(ROOT/'guide/comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n')
(ROOT/'research/presentation/geometric-gallery-verification.json').write_text(json.dumps({'operation':'Saved-array presentation only','new_rays':0,'optical_renders':0,'fits':0,'scores_changed':False,'unsupported_presentation':'Checkerboard marks unavailable unscored exterior; no source completion.','records':records},indent=2)+'\n')
print(json.dumps(records),flush=True)
