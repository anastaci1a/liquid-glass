from pathlib import Path
import json,hashlib,cv2,numpy as np
from PIL import Image
from publish import pair
from video_color import ENCODING_COLOR_ARGS,rgb_digest
import subprocess
R=Path('/evidence/extended/helper-toolbar-work/flower-next-round');D=R/'final-media';O=Path('/evidence/extended/flower-next-primary-final');v=json.loads((D/'verification.json').read_text());support=json.loads((D/'source-support.json').read_text());assert all(v['native_zero_exact']['checks'].values()) and support['passed'];assert v['candidate_recipe_sha256']==hashlib.sha256((R/'neutral-additive-round3/candidate-native.json').read_bytes()).hexdigest()
for name,q in v['files'].items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==q['sha256'],name
from extended_fit import Study
s=Study(R/'neutral-playback-baseline/inputs/a');T=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(1080,1073),interpolation=cv2.INTER_LANCZOS4);A=np.array(Image.open(D/'original.png'));B=np.array(Image.open(D/'reconstruction.png'));assert np.array_equal(T,A) and np.array_equal(B,np.array(Image.open(D/'frames/000.png')));pair(A,B,('Apple source','Neutral material reconstruction'),font_size=32).save(O/'comparison.png')
known=cv2.imread(str(R/'neutral-playback-baseline/inputs/a/known.png'),0)>0
for key in ['all_90_pose_source_enclosure_including_bilinear_and_source_kernel','all_90_pose_exterior_enclosure','independent_all_pose_enclosure']:
 x,y,z,w=support[key];assert known[y:w+1,x:z+1].all(),key
# Source frames are unchanged; add explicit video color metadata on this new encode.
f=O/'motion.mp4';subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-framerate','15','-i',str(D/'frames/%03d.png'),'-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2,'+ENCODING_COLOR_ARGS[1],'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',*ENCODING_COLOR_ARGS[2:],'-movflags','+faststart',str(f)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]));assert int(probe['streams'][0]['nb_read_frames'])==90;decoded=rgb_digest(f);record={'accepted_primary_media':True,'underlying_pass':3,'target_direct_native_crop_resize_exact':True,'reconstruction_equals_first_frame':True,'all_agent_media_hashes_exact':True,'source_rectangles_independently_verified':True,'native_control_reused':'Agent scale1 byte-exact settled/public clean compositor; source unchanged, no fitting/repeated baseline score.','metadata_change':'New MP4 encode from unchanged PNG frames with existing explicit color arguments; GIF unchanged and original full decode/timing evidence reused. Comparison captions normalized only.','mp4':{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'probe':probe,'decoded_rgb_digest':decoded},'gif_bytes':(D/'motion.gif').stat().st_size,'limitations':v['limitations']};(O/'verification.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS FINAL MEDIA',f.stat().st_size)
