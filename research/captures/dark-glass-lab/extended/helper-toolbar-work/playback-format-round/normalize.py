"""Formatting/export only: preserve accepted playback model, inputs and trajectory."""
import sys,os,json,hashlib,subprocess,copy,struct
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
R=Path('/evidence/extended/helper-toolbar-work/playback-format-round');sys.path.insert(0,str(R/'code'))
from settled import mapping,lighting,icon_color,ROOT
from playback_replay import composite
from reproduce import CASES
from render import shade
from video_color import ENCODING_COLOR_ARGS
P=Path('/evidence/extended/playback-short-round/pass-03');I=Path('/evidence/apple-matches/public-settled-replay');O=R/'normalized'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def exact_gif_delays(path):
 data=bytearray(path.read_bytes());assert data[:6] in [b'GIF89a',b'GIF87a'];pos=13
 if data[10]&128:pos+=3*2**((data[10]&7)+1)
 offsets=[];images=0
 while data[pos]!=0x3b:
  tag=data[pos];pos+=1
  if tag==0x21:
   label=data[pos];pos+=1
   if label==0xf9:assert data[pos]==4;offsets.append(pos+2)
   while True:
    n=data[pos];pos+=1
    if not n:break
    pos+=n
  elif tag==0x2c:
   packed=data[pos+8];pos+=9
   if packed&128:pos+=3*2**((packed&7)+1)
   pos+=1
   while True:
    n=data[pos];pos+=1
    if not n:break
    pos+=n
   images+=1
  else:raise RuntimeError(('unexpectedGIFblock',pos,tag))
 assert len(offsets)==images==90
 for i,p in enumerate(offsets):struct.pack_into('<H',data,p,round((i+1)*100/15)-round(i*100/15))
 path.write_bytes(data)

def main():
 os.umask(0o002);cv2.setNumThreads(1)
 if O.exists():raise RuntimeError('Inspect outputs before recovery; no repeat')
 O.mkdir();record=json.loads((R/'pass-03.json').read_text());p=record['recipe'];assert record==json.loads((P/'replay-record.json').read_text())
 for n,digest in record['input_sha256'].items():assert sha(I/n)==digest
 source=np.asarray(Image.open(I/'media-source.png'),np.float64)/255;case=CASES['media'];a,b,c,d=case['crop'];m0=np.load(P/'candidate-material.npy');oldhq=np.asarray(Image.open(P/'hq/render.png').convert('RGB'));oldpair=np.asarray(Image.open(P/'hq/comparison.png').convert('RGB'))
 assert oldpair.shape==(2784,5442,3);assert np.array_equal(oldpair[164:,2722:],oldhq)
 # Lossless saved panels only: no body or icon rerender for the still.
 lhs=Image.fromarray(oldpair[164:,:2720]);rhs=Image.fromarray(oldhq);width=1080;height=round(lhs.height*width/lhs.width);sheet=Image.new('RGB',(width*2+2,height+64),'white');draw=ImageDraw.Draw(sheet)
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
 except OSError:font=ImageFont.load_default()
 for x,im,label in [(0,lhs,'Apple reference'),(1082,rhs,'Accepted playback reconstruction')]:sheet.paste(im.resize((width,height),Image.Resampling.LANCZOS),(x,64));draw.text((x+14,20),label,font=font,fill='black')
 sheet.save(O/'playback-round-current.png');rhs.resize((width,height),Image.Resampling.LANCZOS).save(O/'recreation-1080.png');lhs.resize((width,height),Image.Resampling.LANCZOS).save(O/'apple-1080.png')
 zero=composite(source,case,p,m0,1);np.save(O/'native-zero-complete.npy',zero)
 original=json.loads((R/'pass-03-verification.json').read_text());still=dict(image='playback-round-current.png',width=2162,height=height+64,side_width=1080,caption_height=64,gutter=2,body_height=height,lossless_source_hq_sha256=sha(P/'hq/render.png'),lossless_comparison_sha256=sha(P/'hq/comparison.png'),old_reference_bounds=[0,164,2720,2784],old_recreation_bounds=[2722,164,5442,2784],native_scene_crop=[a,b,c,d],original_body_fully_inside_crop=True,native_lens_bounds=[715,297,1205,787],native_material_sha256=sha(P/'candidate-material.npy'),native_zero_complete_sha256=sha(O/'native-zero-complete.npy'),native_material_unchanged=True,native_original_verified_metrics=original['candidate'],new_optical_still_renders=0,still_resampling_only=True,source_and_icon_pipeline='Existing public playback_replay.composite, registered clean photograph and independently calculated icon color; reference-derived triangular coverage retained, no new glyph or copied colored target')
 save(O/'still-verification.json',still);print('STILL READY',flush=True)
 # Original motion model/path and2x2 integration, exactly everyother original180-frame pose.
 source_blur=cv2.GaussianBlur(source,(0,0),p['source_sigma']*p['reference_length']);mask=np.asarray(Image.open(ROOT/p['icon']['coverage']))/255;L=p['reference_length'];N=540;axis=(np.arange(N*2)+.5)/2-N/2;Y,X=np.meshgrid(axis,axis,indexing='ij');x,y=X/L,Y/L;A,B=mapping(x,y,p);light=lighting(x,y,p);coverage=(np.hypot(x,y)<=1).reshape(N,2,N,2).mean((1,3));box=np.asarray(p['icon']['box_over_L'])*L;alpha=cv2.remap(mask,(X-box[0]).astype(np.float32),(Y-box[1]).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT).reshape(N,2,N,2).mean((1,3));frames=[];observed_bounds=[np.array([np.inf,np.inf]),np.array([-np.inf,-np.inf])]
 outW,outH=1080,608;log=(O/'encode.log').open('w');video=O/'playback-settled.mp4';proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{outW}x{outH}','-framerate','15','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17','-threads','2','-filter_threads','1','-pix_fmt','yuv420p',*ENCODING_COLOR_ARGS,'-movflags','+faststart',str(video)],stdin=subprocess.PIPE,stderr=log)
 try:
  for i in range(90):
   t=i/90;cx,cy=np.rint([960+340*np.sin(2*np.pi*t),542+120*np.sin(4*np.pi*t)]).astype(int);sx=(A*L+cx).astype(np.float32);sy=(B*L+cy).astype(np.float32)
   observed_bounds[0]=np.minimum(observed_bounds[0],[sx.min(),sy.min()]);observed_bounds[1]=np.maximum(observed_bounds[1],[sx.max(),sy.max()]);assert sx.min()>3 and sx.max()<source.shape[1]-4 and sy.min()>3 and sy.max()<source.shape[0]-4
   sample=cv2.remap(source_blur,sx,sy,cv2.INTER_LINEAR);material=shade(sample,light,np.asarray(p['material'])).reshape(N,2,N,2,3).mean((1,3));material=cv2.GaussianBlur(material,(0,0),p['post_sigma']*L);color=icon_color(material,p['icon'],L);material=material*(1-alpha[...,None])+color*alpha[...,None];result=source.copy();result[cy-N//2:cy+N//2,cx-N//2:cx+N//2]=material*coverage[...,None]+result[cy-N//2:cy+N//2,cx-N//2:cx+N//2]*(1-coverage[...,None]);rgb=np.rint(np.clip(result,0,1)*255).astype(np.uint8);frame=cv2.resize(rgb,(outW,outH),interpolation=cv2.INTER_LANCZOS4);proc.stdin.write(frame.tobytes());frames.append(dict(index=i,original_frame_index=2*i,center=[int(cx),int(cy)],rgb_sha256=hashlib.sha256(frame.tobytes()).hexdigest()))
   if i==0:np.save(O/'motion-zero-material-with-icon.npy',material)
   if i in [0,22,45,67]:Image.fromarray(frame).save(O/f'frame-{i:03d}.png')
   if i%15==0:save(O/'motion-progress.json',dict(completed=i+1,total=90));print('MOTION',i+1,flush=True)
 finally:proc.stdin.close();assert proc.wait()==0;log.close()
 save(O/'frames.json',frames)
 palette=O/'palette.png';gif=O/'playback-settled.gif'
 for colors in [256,192,128,96]:
  subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_threads','1','-i',str(video),'-vf',f'palettegen=max_colors={colors}:stats_mode=diff','-frames:v','1',str(palette)],check=True)
  subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_complex_threads','1','-i',str(video),'-i',str(palette),'-lavfi','[0:v][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle','-loop','0','-gifflags','-transdiff',str(gif)],check=True);exact_gif_delays(gif)
  if gif.stat().st_size<10_000_000:break
 assert gif.stat().st_size<10_000_000
 files=[]
 for file in [video,gif]:
  decoded=O/(file.suffix[1:]+'-decoded.framemd5');subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(file),'-f','framemd5','-y',str(decoded)],check=True);count=len([s for s in decoded.read_text().splitlines() if s and not s.startswith('#')]);assert count==90;probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(file)]));st=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(st['nb_read_frames'])==90 and st['width']==outW and st['height']==outH;assert float(probe['format']['duration'])==6
  files.append(dict(file=file.name,bytes=file.stat().st_size,sha256=sha(file),decoded_frames=count,width=outW,height=outH,duration_seconds=6,probe=probe))
 source_margin=min(observed_bounds[0][0],observed_bounds[0][1],source.shape[1]-1-observed_bounds[1][0],source.shape[0]-1-observed_bounds[1][1])-3;assert source_margin>0
 motion=dict(files=files,frames=90,fps=15,palette_colors=colors,sampling='UNCHANGED existingmotion2x2; original4x4native scoring and savedmaterial unchanged; motionzero is NOT asserted bitexact to4x4native',trajectory='Original cx=round(960+340sin(2pi*t)),cy=round(542+120sin(4pi*t)); t=i/90 =originalframe2i/180',source_bounds_min=observed_bounds[0].tolist(),source_bounds_max=observed_bounds[1].tolist(),whole_and_ALL_scored_domain='ALL1080x1080 subpixel source coordinates in moving540x540patch checked for everyframe, including unscored exterior; all scored rays subset. Gaussian source finite radius2 +bilinear1 included.',source_margin_after_kernel_bilinear_native_px=float(source_margin),native_source_proof_inherited=original['domain'],source_limits='Finite-domain support does NOT certify independently observed reconstructed photograph/registration or Apple generalization. Near-equivalent resized exports are not a scientific pass.',source_hashes_unchanged=all(sha(I/n)==v for n,v in record['input_sha256'].items()),old_target_context_used=False)
 save(O/'motion-verification.json',motion);save(O/'verification.json',dict(scope='Playback formatting/export ONLY. Completed3pass model unchanged; no new accepted pass.',recipe_sha256=sha(R/'pass-03.json'),input_hashes=record['input_sha256'],native_scoring_unchanged=True,new_fits=0,new_optical_still_renders=0,new_motion_frames=90,still=still,motion=motion));print('NORMALIZATION READY',flush=True)
if __name__=='__main__':main()
