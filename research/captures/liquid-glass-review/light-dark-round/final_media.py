"""Final accepted legacy Light/dark motion. No target-derived display context."""
import os,sys,json,copy,hashlib,subprocess,struct
from pathlib import Path
import cv2,numpy as np
from PIL import Image
R=Path('/evidence/extended/helper-toolbar-work/light-dark-round');sys.path.insert(0,str(R/'code'));sys.path.insert(0,str(R/'publication-pass01/staged/docs/liquid-glass/experiments/reconstruction'))
from reproduce import CASES
from settled import render
from regular_exterior import exterior
from video_color import ENCODING_COLOR_ARGS
O=R/'final-motion-1080';recipe_path=R/'publication-pass03/staged/docs/liquid-glass/experiments/reconstruction/studies/light-dark/review-round/pass-03.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def gif_delays(path):
 data=bytearray(path.read_bytes());assert data[:6] in [b'GIF89a',b'GIF87a'];pos=13
 if data[10]&128:pos+=3*(2**((data[10]&7)+1))
 delays=[];images=0
 while data[pos]!=0x3b:
  tag=data[pos];pos+=1
  if tag==0x21:
   label=data[pos];pos+=1
   if label==0xf9:
    assert data[pos]==4;delays.append(pos+2)
   while True:
    n=data[pos];pos+=1
    if not n:break
    pos+=n
  elif tag==0x2c:
   packed=data[pos+8];pos+=9
   if packed&128:pos+=3*(2**((packed&7)+1))
   pos+=1
   while True:
    n=data[pos];pos+=1
    if not n:break
    pos+=n
   images+=1
  else:raise RuntimeError(('unexpected GIF block',pos,tag))
 assert images==len(delays)==90
 for i,p in enumerate(delays):struct.pack_into('<H',data,p,round((i+1)*100/15)-round(i*100/15))
 path.write_bytes(data)
 return images

def main():
 os.umask(0o002);cv2.setNumThreads(1)
 if O.exists():raise RuntimeError('Inspect immutable partial files before recovery; no restart')
 O.mkdir();record=json.loads(recipe_path.read_text());assert record['accepted'] and record['round_pass']==3
 save(O/'started.json',dict(pid=os.getpid(),recipe=str(recipe_path),recipe_sha256=sha(recipe_path),frames=90,fps=15,width=1080,original_body_samples=4,amplitude_native_x=30,amplitude_native_y=0,no_copied_context=True))
 allrows=[]
 for name in ['regular-light','regular-dark']:
  out=O/name;out.mkdir();c0=CASES[name];p=record['body_recipes'][name];assert p['source_sigma']==0 and not p.get('post_sigma') and p['model']=='field' and p['parameters']['edge']==.4 and p['parameters']['band']==.55 and p['parameters']['rim']==.35 and p['parameters']['core']==.012
  source_path=R/f'{name}-source.png';source=np.asarray(Image.open(source_path).convert('RGB')).astype(np.float64)/255;assert sha(source_path)==record['inputs'][name]['source_sha256'];M0=np.load(R/f'{name}-native-material.npy');expected=np.load(R/f'offset-pass3/{name}-complete.npy');W,H=1080,586
  frames=[];log=(out/'encode.log').open('w');mp4=out/'motion.mp4';enc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','15','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17','-threads','2','-filter_threads','1','-pix_fmt','yuv420p',*ENCODING_COLOR_ARGS,'-movflags','+faststart',str(mp4)],stdin=subprocess.PIPE,stderr=log)
  try:
   for i in range(90):
    dx=30*np.sin(2*np.pi*i/90);c=copy.deepcopy(c0);c['center']=[c0['center'][0]+float(dx),c0['center'][1]]
    material=M0 if i==0 else render(source,c,p,samples=4)
    complete,coverage,sd=exterior(c,source,material,record)
    if i==0:
     assert np.array_equal(complete,expected);np.save(out/'zero-native-complete.npy',complete)
    rgb=np.rint(np.clip(complete,0,1)*255).astype(np.uint8);frame=cv2.resize(rgb,(W,H),interpolation=cv2.INTER_LANCZOS4);enc.stdin.write(frame.tobytes());frames.append(dict(index=i,dx_native=float(dx),native_float_sha256=hashlib.sha256(complete.tobytes()).hexdigest(),export_rgb_sha256=hashlib.sha256(frame.tobytes()).hexdigest()))
    if i in [0,22,45,67]:Image.fromarray(frame).save(out/f'frame-{i:03d}.png')
    if i%10==0:save(out/'progress.json',dict(completed=i+1,total=90));print(name,i+1,flush=True)
  finally:
   enc.stdin.close();assert enc.wait()==0;log.close()
  save(out/'frames.json',frames)
  palette=out/'palette.png';gif=out/'motion.gif'
  for colors in [256,192,128,96]:
   subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_threads','1','-i',str(mp4),'-vf',f'palettegen=max_colors={colors}:stats_mode=diff','-frames:v','1',str(palette)],check=True)
   subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_complex_threads','1','-i',str(mp4),'-i',str(palette),'-lavfi','[0:v][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle','-loop','0','-gifflags','-transdiff',str(gif)],check=True)
   gif_delays(gif)
   if gif.stat().st_size<10_000_000:break
  assert gif.stat().st_size<10_000_000
  file_records=[]
  for f in [mp4,gif]:
   # Full decode and per-frame hashes, not merely container metadata.
   hashes=out/(f.suffix[1:]+'-decoded.framemd5');subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(f),'-f','framemd5','-y',str(hashes)],check=True)
   decoded=[line for line in hashes.read_text().splitlines() if line and not line.startswith('#')];assert len(decoded)==90
   pr=probe(f);st=next(s for s in pr['streams'] if s['codec_type']=='video');assert int(st['nb_read_frames'])==90 and st['width']==W and st['height']==H;assert abs(float(pr['format']['duration'])-6)<1e-6
   file_records.append(dict(file=f.name,bytes=f.stat().st_size,sha256=sha(f),decoded_frames=90,width=W,height=H,duration_seconds=float(pr['format']['duration']),probe=pr))
  # Conservative map-domain proof, valid across every moving center and subpixel phase.
  # Both nonnegative P summands individually <=1 => a<=band*edge*L=23.43px.
  # Inside shape, |map_x|<=245+23.43, |map_y|<=106.5+23.43; outside identity.
  support=dict(kind='analytic conservative finite-domain bound, not observation evidence',body_source_xy_bounds=[[661.57,1258.43],[411.07,670.93]],all_crop_subrays_identity_bounds=[[609.625,1309.375],[349.625,729.375]],underlay_xy_bounds=[[610,1309],[350,729]],image_size=[source.shape[1],source.shape[0]],whole_and_ALL_scored_included=True,bilinear_source_sigma_native=0,light_splice_y739_not_reached=True,dark_copied_top_through_y348_not_reached=True,limits='Estimated/assumed sources; no observed confidence. Finite source-domain proof, not physical optical identification or light-transport reconstruction.')
  row=dict(theme=name,files=file_records,palette_colors=colors,input_sha256=sha(source_path),source_unchanged_after=sha(source_path)==record['inputs'][name]['source_sha256'],zero_native_exact=True,source_support=support,body_samples_per_axis=4,frames=90,fps=15,travel='30sin(2pi*i/90) horizontal nativepx, fixed original output window',context='Only frozen source PNG + existing body renderer + accepted generated operator; no target image read, compose, contact_context or source repair',limits=record['limitations']);save(out/'verification.json',row);allrows.append(row);save(O/'partial-summary.json',allrows)
 save(O/'verification.json',dict(accepted_recipe_sha256=sha(recipe_path),round_pass=3,scope='Illustrative motion over modeled near-uniform sources, NOT optical validation or captured Apple motion',observations=allrows));print('FINAL MEDIA READY',flush=True)
if __name__=='__main__':main()
