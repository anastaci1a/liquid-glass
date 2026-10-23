from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,numpy as np,argparse
ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);a=ap.parse_args();r=a.folder
report=json.loads((r/'verification.json').read_text());im=Image.open(r/'motion.gif');assert im.size==tuple(report['gif']['output_size'])
assert hashlib.sha256((r/'motion.gif').read_bytes()).hexdigest()==report['files']['motion.gif']['sha256']
im.seek(0);B=np.array(im.convert('RGB')).astype(np.float32);W,H=im.size
raw=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-i',str(r/'motion.mp4'),'-vf',f'scale={W}:{H}:flags=lanczos','-frames:v','3','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);frames=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)
errors=[float(np.sqrt(np.mean((A.astype(np.float32)-B)**2))) for A in frames];dur=[]
for i in range(im.n_frames):
 im.seek(i);dur.append(im.info.get('duration',0))
 if i==im.n_frames//4:im.convert('RGB').save(r/'gif-peak.png')
qa=dict(size=im.size,frames=im.n_frames,duration_ms=sum(dur),minimum_duration_ms=min(dur),maximum_duration_ms=max(dur),first_gif_frame_rgb_rmse_to_video_frames_0_1_2=errors,nearest_video_frame=int(np.argmin(errors)),limits='Palette/encode diagnostic, separate from native glass score. Nearest early video frame accounts for GIF frame-rate resampling phase.')
(r/'gif-qa.json').write_text(json.dumps(qa,indent=2)+'\n');print(qa,flush=True)
assert im.n_frames==round(report['frames']*report['gif']['fps']/report['fps'])
assert min(dur)>0 and abs(sum(dur)-1000*report['frames']/report['fps'])<=20
if min(errors)>=4:print('REVIEW palette diagnostic above4RGB; inspect and record decision, not a native glass regression gate',flush=True)
