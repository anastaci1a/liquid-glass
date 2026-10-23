"""Offline 30fps motion previews over the unchanged registered source image.

Uses EXACTLY the still-study displacement and color functions, extracted without
running the fitting script. Not an Android/GPU frame-time or Apple-motion test.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import ast,sys,json,subprocess,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.interpolate import PchipInterpolator
from PIL import Image,ImageDraw,ImageFont
from publish import read,CASES
from render import case_geometry,illumination,shade

root=Path('/evidence/apple-matches');out=root/'review-pass05-playback'
diag=json.loads((out/'diagnostics.json').read_text());prior=json.loads((root/'pass04-candidates/media-singlefold-3461.json').read_text())
oldicon=np.array(json.loads((root/'review-pass04-complete/diagnostics.json').read_text())['icon_parameters'])
case=CASES['media'];R=245.;P=prior['parameters'];A=P['amplitude']*R;b=P['band']*R;p=P['power']
LUMA=np.array([.2126,.7152,.0722])
text=(root/'playback-pass05.py').read_text();tree=ast.parse(text)
functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['smooth5','displacement','response','ordered_response','shared_curve_response']],type_ignores=[])
exec(compile(functions,'playback-pass05.py:selected-functions','exec'))
source=read(root/'curvature-contour/media-source.png')/255.
src=cv2.GaussianBlur(source,(0,0),prior['sigma'])
background=cv2.resize(source,(960,540),interpolation=cv2.INTER_AREA)
alpha=np.array(Image.open(root/'review-pass-02/06-white-icon-mask.png'))/255.
# A 540-native-pixel patch becomes 270 output pixels. Two subpixels per
# output axis integrate both shape coverage and native source sampling.
N=270;pad=N//2;axis=np.arange(N*2,dtype=float)-N+.5
Y,X=np.meshgrid(axis,axis,indexing='ij');rr=np.hypot(X,Y);depth=R-rr
light=illumination(X,Y,case['half'],R,prior['rim_width'],case_geometry(case,X,Y))
co=np.array(prior['material']);cov=(rr<=R).reshape(N,2,N,2).mean((1,3))
mask=cv2.remap(alpha,(X+960-870).astype(np.float32),(Y+542-420).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT).reshape(N,2,N,2).mean((1,3))
vnew=np.array(diag['combined']['icon_parameters']);post=diag['combined']['post_sigma_px'];extra=diag['combined']['icon_color_input_sigma_px']
maps={}
selected=next(t for t in diag['geometry_trials']if t['key']==diag['combined']['geometry'])
for name,width,gain,q in [('before',1.,1.,p),('after',selected['width_factor'],selected['shoulder_gain'],4.)]:
    a=displacement(depth,width,gain,q)
    ratio=np.divide(rr-a,rr,out=np.ones_like(rr),where=rr>1e-12)
    maps[name]=(X*ratio,Y*ratio)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def render(center,name):
    ox,oy=maps[name]
    sample=cv2.remap(src,(ox+center[0]*2).astype(np.float32),(oy+center[1]*2).astype(np.float32),cv2.INTER_LINEAR)
    C=shade(sample,light,co).reshape(N,2,N,2,3).mean((1,3))
    if name=='after' and post:C=cv2.GaussianBlur(C,(0,0),post/2)
    if name=='before':icon=1-oldicon[:3]*(1-C)**oldicon[3:6]
    else:
        field=cv2.GaussianBlur(C,(0,0),extra/2)if extra else C
        icon=shared_curve_response(vnew,field)
    C=C*(1-mask[...,None])+icon*mask[...,None]
    frame=background.copy();x,y=center[0]-pad,center[1]-pad
    frame[y:y+N,x:x+N]=C*cov[...,None]+frame[y:y+N,x:x+N]*(1-cov[...,None])
    return np.uint8(np.rint(np.clip(frame,0,1)*255))

logs=[]
def encoder(path,size):
    log=(out/(path+'.encode.log')).open('w');logs.append(log)
    args=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',size,'-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out/(path+'.mp4'))]
    return subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
one=encoder('09-playback-motion','960x540');both=encoder('10-playback-motion-comparison','1920x540')
captured=[];centers=[]
for i in range(180):
    u=i/180;center=np.rint([480+170*np.sin(2*np.pi*u),270+60*np.sin(4*np.pi*u)]).astype(int)
    before=render(center,'before');after=render(center,'after')
    labelled=[]
    for label,im in [('Pass04',before),(f"Updated: {selected['width_factor']:g}x tail / blur / icon",after)]:
        im=Image.fromarray(im);draw=ImageDraw.Draw(im);draw.rounded_rectangle((12,12,380,44),radius=8,fill='#14171e');draw.text((22,19),label,font=font,fill='#edf0f7');labelled.append(np.array(im))
    one.stdin.write(labelled[1].tobytes());pair=np.concatenate(labelled,axis=1);both.stdin.write(pair.tobytes())
    if i in [0,45,90,135]:captured.append(Image.fromarray(pair))
    centers.append(center.tolist())
    if i%30==0:print('frame',i,flush=True)
for proc in [one,both]:
    proc.stdin.close()
    if proc.wait():raise RuntimeError('Video encoding failed; inspect encode log')
for f in logs:f.close()
sheet=Image.new('RGB',(1920,540*len(captured)))
for i,frame in enumerate(captured):sheet.paste(frame,(0,i*540))
sheet.save(out/'11-motion-contact-sheet.png')
probes={}
for name in ['09-playback-motion.mp4','10-playback-motion-comparison.mp4']:
    result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration,pix_fmt','-of','json',str(out/name)],check=True,stdout=subprocess.PIPE)
    probes[name]=json.loads(result.stdout)
    check=subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(out/name),'-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert check.returncode==0 and not check.stderr,(name,check.stderr)
report=dict(source='Same registered uncovered source image as the still study; no background repair for motion.',source_sha256=hashlib.sha256((root/'curvature-contour/media-source.png').read_bytes()).hexdigest(),study_script_sha256=hashlib.sha256(text.encode()).hexdigest(),render=dict(frame_rate=30,frames=180,duration_seconds=6,output='960x540 (comparison 1920x540)',subpixels_per_output_axis=2,source_sigma_native_px=prior['sigma'],updated_tail_width_factor=selected['width_factor'],updated_shoulder_gain=selected['shoulder_gain'],updated_tail_inner_power=4,post_refraction_sigma_native_px=post,icon_color_input_sigma_native_px=extra),centers_output_pixels=centers,probes=probes,limits=['Offline CPU-rendered frames; playback fps is not render throughput or Android device evidence.','No deformation/morphing in this translation-only preview.','Narrow exterior shadow and old reference-context treatment omitted, so the original fixed reference lens is not retained in the background.','Lighting/material/icon response calibrated on one reference pose; movement is an extrapolation, not measured Apple-motion parity.'])
(out/'motion-diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
print('Complete: both 6-second MP4 clips decode cleanly',flush=True)
