"""Bounded eligibility screen only: valid724 precedes known unrelated726."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image,ImageDraw
from reproduce import frame
root=Path('/tmp/agent-toolbar-A-source-audit');out=root/'late-screen';out.mkdir(exist_ok=True)
video=Path('/evidence/apple-matches/219-hd.mp4')
with video.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest=='3d58f9e843f0b8c22e99d76de6b5201ef5b17de5bb4bf5732862ba7dbf9be60e'
sheet=Image.new('RGB',(1280,396),'#202020');draw=ImageDraw.Draw(sheet);records=[]
for i,t in enumerate([724.5,725.]):
    rgb,meta=frame(video.parent,'219',t);rgb=np.uint8(rgb*255);dest=out/f'frame-{t}.png';Image.fromarray(rgb).save(dest)
    records.append({'requested_seconds':t,**meta,'native_size':[1920,1080],'local_file':str(dest.relative_to(root)),'rgb_sha256':hashlib.sha256(rgb.tobytes()).hexdigest(),'png_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    draw.text((i*640+8,8),f'{t}s | frame{meta["frame_index"]} | PTS{meta["presentation_seconds"]:.6f}',fill='white');sheet.paste(Image.fromarray(rgb).resize((640,360)),(i*640,36))
sheet.save(out/'eligibility-overview.png')
(out/'frame-provenance.json').write_text(json.dumps({'video_path':str(video),'video_sha256':digest,'bounded_extension':[724,725],'reason':'Only final1s after knownsame-page724, beforeknownunrelated726. Visual eligibility required before any registration; never newelement study.','frames':records,'source_or_epoch_changed':False},indent=2)+'\n')
print(json.dumps(records),flush=True)
