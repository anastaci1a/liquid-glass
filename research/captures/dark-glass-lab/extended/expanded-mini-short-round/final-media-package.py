import os,sys,json,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from extended_fit import Study
from publish import pair
ROOT=Path('/evidence/extended/expanded-mini-short-round');D=ROOT/'final-1080';rows=[];os.umask(0o002)
for n in ['a','b']:
 folder=D/n/'final';report=json.loads((folder/'render.json').read_text());check=json.loads((folder/'verification.json').read_text());files={}
 for name in ['motion.mp4','motion.gif']:
  b=(folder/name).read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha==check['files'][name]['sha256'];files[name]=dict(bytes=len(b),sha256=sha)
 assert files['motion.gif']['bytes']<10_000_000 and report['output_size']==[1080,200] and report['frames']==90
 image=Image.open(folder/'motion.gif');duration=0
 for i in range(image.n_frames):image.seek(i);duration+=image.info.get('duration',0)
 assert image.n_frames==90
 frame=np.array(Image.open(folder/'frame-000.png').convert('RGB'));assert frame.shape==(200,1080,3);frame=frame[:199]
 s=Study(ROOT/n);target=cv2.resize(np.rint(s.target_crop*255).astype(np.uint8),(1080,199),interpolation=cv2.INTER_LANCZOS4);pair(target,frame,('Apple source','Reconstruction'),font_size=24).save(D/(n+'-comparison.png'))
 rows.append(dict(reference=n,render=report,existing_decode_verification=check,files=files,gif_duration_ms=duration,gif_frames=image.n_frames,presentation='1080wide final still uses zero-shift lossless frame000, drops one codec-padding row. Original target upsample/downsample only; native scores unchanged.'))
(D/'motion.json').write_text(json.dumps(dict(exports=rows,limits='Illustrative recovered-backdrop scroll, not captured Apple motion or Android performance. Finite motion source sample checks are not continuous full moving-subray proof. Frozen stationary optical proofs and native guards are separate.'),indent=2)+'\n');print([(r['reference'],r['gif_duration_ms'],r['files']['motion.gif']['bytes']) for r in rows],flush=True)
