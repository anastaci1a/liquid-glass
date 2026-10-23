import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image,ImageDraw
from reproduce import frame
root=Path('/evidence/apple-matches');out=Path('/tmp/agent-toolbar-second-observation');out.mkdir(exist_ok=True)
manifest=json.loads(Path('/tmp/agent-toolbar-code/sources.json').read_text());video=root/'219-hd.mp4'
with video.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest==manifest['219']['sha256']
records=[];sheet=Image.new('RGB',(1920,1188),'#202020');draw=ImageDraw.Draw(sheet)
for i,t in enumerate([706,708,710,712,714,716,718,720,722]):
    rgb,meta=frame(root,'219',t);rgb=np.uint8(rgb*255);dest=out/f'frame-{t}.png';Image.fromarray(rgb).save(dest);r={'requested_seconds':t,**meta,'rgb_sha256':hashlib.sha256(rgb.tobytes()).hexdigest(),'png_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()};records.append(r)
    x=(i%3)*640;y=(i//3)*396;draw.text((x+8,y+8),f'{t}s | frame {meta["frame_index"]} | PTS {meta["presentation_seconds"]:.6f}',fill='white');sheet.paste(Image.fromarray(rgb).resize((640,360)),(x,y+36))
    if t==710:
        original=np.asarray(Image.open('/tmp/agent-toolbar-run/target.png'));r['original_A_max_pixel_difference']=int(np.max(np.abs(rgb.astype(int)-original.astype(int))))
    print('FRAME',t,meta,flush=True)
sheet.save(out/'overview.png');(out/'frame-provenance.json').write_text(json.dumps({'video_path':str(video),'video_sha256':digest,'source_manifest':manifest['219'],'frames':records,'status':'proposal assessment only; no pair stage, no scoring/input epoch changed'},indent=2)+'\n')
