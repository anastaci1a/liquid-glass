"""Two actual raw frames only; stop before frame2 or encoding. No native4x4 render."""
import os,sys,json,hashlib,importlib.util,shutil
from pathlib import Path
from PIL import Image
R=Path('/evidence/extended/helper-toolbar-work/playback-format-round');P=R/'portable-motion-patch';sys.path.insert(0,str(R/'code'));spec=importlib.util.spec_from_file_location('portable_motion',P/'staged/docs/liquid-glass/experiments/reconstruction/motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
os.umask(0o002);expected=json.loads((R/'normalized/frames.json').read_text());seen=[];calls=[]
class Complete(BaseException):pass
class Pipe:
 def write(self,data):
  i=len(seen);digest=hashlib.sha256(data).hexdigest();assert digest==expected[i]['rgb_sha256'];seen.append(dict(frame=i,sha256=digest,exact_to_accepted_normalization=True));assert len(data)==1080*608*3
  if len(seen)==2:raise Complete()
 def close(self):pass
class Proc:
 def __init__(self,argv,**kwargs):
  assert argv[argv.index('-video_size')+1]=='1080x608' and argv[argv.index('-framerate')+1]=='15';self.stdin=Pipe();calls.append(argv)
 def wait(self):return 0
m.subprocess.Popen=Proc
sys.argv=['motion.py','/evidence/apple-matches/public-settled-replay',str(P/'first-frame-check'),'--frames','90','--fps','15','--width','1080','--record',str(R/'pass-03.json')]
try:m.main()
except Complete:pass
assert len(seen)==2
old=R/'normalized/playback-settled.gif';copy=P/'timing-check.gif';shutil.copyfile(old,copy);before=hashlib.sha256(copy.read_bytes()).hexdigest();n,ms=m.set_gif_timing(copy,6);assert n==90 and ms==6000 and before==hashlib.sha256(copy.read_bytes()).hexdigest()
with Image.open(copy) as im:
 assert im.n_frames==90
 duration=0
 for i in range(im.n_frames):im.seek(i);duration+=im.info['duration']
 assert duration==6000
(P/'verification.json').write_text(json.dumps(dict(raw_frames=seen,encoder_args=calls[0],new_generated_motion_frames=2,native4x4_tests=0,full90frame_rerender=False,new_encodes=0,timing_control=dict(real_existing_gif_frames=n,duration_ms=ms,byte_exact_after_timing_pass=True),source_and_record='main hashed original source/target inputs and used unchanged final pass03 recipe',scope='Private portable export patch only; no scientific pass'),indent=2)+'\n');print('PASS first2rawframes exact; existingGIF90frames6s remains byteexact; no encoding/native4x4 test')
