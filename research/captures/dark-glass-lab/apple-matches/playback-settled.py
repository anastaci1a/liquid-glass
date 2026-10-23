"""Settled playback study: full-HD video/GIF, with final icon-color blur.

Reuse the pass06 model. Do not modify past review figures or switch shaders.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import importlib.util,json,subprocess,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image

root=Path('/evidence/apple-matches');out=root/'playback-settled';out.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('pass06',root/'playback-pass06.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.POST_RATIO=1.5/m.DREF
POST_SIGMA=1.5;ICON_SIGMA=3.;SATURATION=.2;TAPER=.5
original_field=m.icon_field
def final_icon(material,output_scale=1.):
    return original_field(material,diameter=m.DREF,output_scale=output_scale,highlight=TAPER,saturation=SATURATION,blur_ratio=ICON_SIGMA/m.DREF)

# Record unambiguous input units and the exact stage ordering.
preset=dict(scope='Owner-selected visual-study calibration; no native-app/default or recovered-Apple-shader claim.',reference_short_dimension_px=m.DREF,geometry=dict(width=4.5,gain=1,inner_endpoint_power=4,amplitude_over_radius=m.prior['parameters']['amplitude'],band_over_radius=m.prior['parameters']['band'],outer_power=m.prior['parameters']['power']),filters=dict(source_sigma_over_short_dimension=.5/m.DREF,glass_post_sigma_over_short_dimension=POST_SIGMA/m.DREF,icon_final_sigma_over_short_dimension=ICON_SIGMA/m.DREF,reference_equivalents_px=dict(source=.5,glass=POST_SIGMA,icon=ICON_SIGMA)),icon=dict(base='Original pass04 independent-channel response',base_parameters=m.params.tolist(),dark_saturation=SATURATION,taper=TAPER,highlight_start=m.HIGHLIGHT_START,dark_span=m.DARK_SPAN,order=['pass04 response','dark-weighted saturation','monotone highlight taper','Gaussian blur of calculated icon color','sharp icon coverage/compositing']),output=dict(width=1920,height=1080,video_fps=30,duration_seconds=6,gif_max_bytes=10_000_000),limits=['Radial inverse-map approximation, not an identified physical Apple solid.','Still exterior context estimated/retained; moving preview omits exterior shadow.','Independent-channel icon response does not guarantee color order on every background.','Offline rendering and GIF frame rate are not Android performance evidence.'])

# Check that the final blur is really after color adjustment, and that the
# downsampled path receives the corresponding output-pixel radius too.
rng=np.random.default_rng(7007);probe=rng.uniform(0,1,(80,90,3))
expected=m.colored_icon(probe,highlight=TAPER,saturation=SATURATION)
tests={}
for scale in [1,.5]:
    ref=cv2.GaussianBlur(expected,(0,0),ICON_SIGMA*scale)
    error=float(np.max(abs(final_icon(probe,scale)-ref)))
    assert error==0;tests[str(scale)]=error
preset['verification']=dict(final_icon_blur_max_error=tests,spatial_ratios='Both blur amounts scale with the same shorter-dimension units as geometry.')
(out/'preset.json').write_text(json.dumps(preset,indent=2)+'\n')

# A final reference-pose still, retaining the already documented exterior.
material=m.still_material();still=m.composite(material,final_icon(material))
Image.fromarray(np.uint8(np.rint(still*255))).save(out/'playback-reference.png')

# Full-native-size preview, no captions or comparison overlays.
N=540;pad=N//2
axis=(np.arange(N*2,dtype=float)+.5)/2-pad
Y,X=np.meshgrid(axis,axis,indexing='ij');R=m.DREF/2;r=np.hypot(X,Y)
a=m.displacement(R-r);ratio=np.divide(r-a,r,out=np.ones_like(r),where=r>1e-12)
lookupX=X*ratio;lookupY=Y*ratio
light=m.light_field(X,Y,m.DREF).astype(np.float32)
coverage=(r<=R).reshape(N,2,N,2).mean((1,3))
mask=cv2.remap(m.alpha,(X+m.cx-m.ix0).astype(np.float32),(Y+m.cy-m.iy0).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT).reshape(N,2,N,2).mean((1,3))
video=out/'playback-final.mp4';log=(out/'video-encode.log').open('w')
encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
background=m.source
for i in range(180):
    u=i/180;center=np.rint([m.cx+340*np.sin(2*np.pi*u),m.cy+120*np.sin(4*np.pi*u)]).astype(int)
    sample=cv2.remap(m.source_for(m.DREF),(lookupX+center[0]).astype(np.float32),(lookupY+center[1]).astype(np.float32),cv2.INTER_LINEAR)
    M=m.shade(sample,light,m.co).reshape(N,2,N,2,3).mean((1,3))
    M=cv2.GaussianBlur(M,(0,0),POST_SIGMA)
    C=final_icon(M);material=M*(1-mask[...,None])+C*mask[...,None]
    frame=background.copy();x,y=center[0]-pad,center[1]-pad
    frame[y:y+N,x:x+N]=material*coverage[...,None]+frame[y:y+N,x:x+N]*(1-coverage[...,None])
    frame=np.uint8(np.rint(np.clip(frame,0,1)*255));encoder.stdin.write(frame.tobytes())
    if i in [0,45,90,135]:Image.fromarray(frame).save(out/f'frame-{i:03}.png')
    if i%30==0:print('Full-HD frame',i,flush=True)
encoder.stdin.close();assert encoder.wait()==0;log.close()

# Keep native dimensions. First try a high-quality global palette at 15fps;
# only reduce palette/frame rate if needed for the strict decimal 10MB cap.
gif=out/'playback-final.gif';attempts=[]
for fps,colors,dither in [(15,192,'bayer:bayer_scale=3'),(15,128,'bayer:bayer_scale=4'),(12,128,'bayer:bayer_scale=4'),(10,96,'none'),(8,64,'none'),(6,48,'none')]:
    palette=out/'palette.png'
    p=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),'-vf',f'fps={fps},palettegen=max_colors={colors}:stats_mode=diff','-frames:v','1',str(palette)],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    assert p.returncode==0,p.stderr
    p=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),'-i',str(palette),'-lavfi',f'fps={fps}[x];[x][1:v]paletteuse=dither={dither}:diff_mode=rectangle','-loop','0','-gifflags','+transdiff',str(gif)],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    assert p.returncode==0,p.stderr
    size=gif.stat().st_size;attempts.append(dict(fps=fps,colors=colors,dither=dither,bytes=size))
    print('GIF attempt',fps,colors,size,flush=True)
    if size<10_000_000:break
assert gif.stat().st_size<10_000_000

probes={}
for file in [video,gif]:
    result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,nb_read_frames,duration,pix_fmt','-of','json',str(file)],check=True,stdout=subprocess.PIPE)
    info=json.loads(result.stdout);probes[file.name]=info
    stream=info['streams'][0];assert stream['width']==1920 and stream['height']==1080
    p=subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert p.returncode==0 and not p.stderr,(file,p.stderr)
with Image.open(gif)as image:
    durations=[]
    for i in range(image.n_frames):image.seek(i);durations.append(image.info.get('duration',0))
    gif_duration=sum(durations)/1000
    assert image.size==(1920,1080)and abs(gif_duration-6)<.1
(out/'media-verification.json').write_text(json.dumps(dict(probes=probes,gif_attempts=attempts,selected_gif_bytes=gif.stat().st_size,gif_duration_seconds=gif_duration,strict_decimal_limit_bytes=10_000_000,final_blur='Calculated icon-color blur is last; sharp alpha coverage follows it.'),indent=2)+'\n')
media=sorted([*out.glob('*.png'),*out.glob('*.mp4'),*out.glob('*.gif'),*out.glob('*.json')])
(out/'media.sha256').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n'for f in media))
print('Final media verified',video.stat().st_size,gif.stat().st_size,flush=True)
