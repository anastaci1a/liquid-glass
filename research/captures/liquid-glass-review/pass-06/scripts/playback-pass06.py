"""Owner-selected playback optics; independent highlight, chroma and icon blur.

Private offline study. Everything spatial is expressed relative to lens size;
reference-pixel values in captions are only a calibration at diameter 490px.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,hashlib,subprocess,argparse
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from publish import read,compose,coverage,CASES
from render import illumination,case_geometry,shade

root=Path('/evidence/apple-matches');out=root/'review-pass06-playback';out.mkdir(exist_ok=True)
raw=out/'renders';raw.mkdir(exist_ok=True)
case=CASES['media'];x0,y0,x1,y1=case['crop'];cx,cy=case['center']
DREF=490.;WIDTH=4.5;GAIN=1.;Q=4.
POST_RATIO=1.6/DREF;SOURCE_RATIO=.5/DREF;ICON_RATIO=2/DREF
HIGHLIGHT=.5;SATURATION=.2;HIGHLIGHT_START=.9;DARK_SPAN=.15
prior=json.loads((root/'pass04-candidates/media-singlefold-3461.json').read_text())
params=np.array(json.loads((root/'review-pass04-complete/diagnostics.json').read_text())['icon_parameters'])
co=np.array(prior['material']);LUMA=np.array([.2126,.7152,.0722])
target=read(root/'curvature-contour/media-target.png');source=read(root/'curvature-contour/media-source.png')/255.
base=read(root/'pass04-candidates/media-singlefold-3461.png')/255.
alpha=np.array(Image.open(root/'review-pass-02/06-white-icon-mask.png'))/255.
IB=(870,420,1095,675);ix0,iy0,ix1,iy1=IB
FONTP='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT=ImageFont.truetype(FONTP,17);SMALL=ImageFont.truetype(FONTP,13)
blurs={}

def displacement(depth,diameter=DREF,width=WIDTH):
    radius=diameter/2;A=prior['parameters']['amplitude']*radius
    b=prior['parameters']['band']*radius;p=prior['parameters']['power']
    start=b/2;w=width*b/2;t=np.clip((depth-start)/w,0,1-1e-12)
    tail=A*.5**p*np.exp(Q*np.log1p(-t)+(Q-p*width)*t+.5*(Q-p*width*width)*t*t)
    initial=A*np.clip(1-depth/b,0,1)**p
    return np.where(depth<=start,initial,np.where(depth<start+w,tail,0.))

def old_response(B):return 1-params[:3]*(1-np.clip(B,0,1))**params[3:6]

def highlight_taper(C,strength):
    # A single monotone scalar function of each component, with identity below
    # .9 and no new white plateau. For k in [0,4], derivative is nonnegative:
    # 1-k*u^2*(3-4u), whose subtractive factor has maximum 1/4.
    u=np.clip((C-HIGHLIGHT_START)/(1-HIGHLIGHT_START),0,1)
    return C-strength*u**3*(1-C)

def colored_icon(B,highlight=HIGHLIGHT,saturation=SATURATION):
    C=old_response(B);L=C@LUMA
    weight=np.clip((1-L)/DARK_SPAN,0,1)**2
    C=np.clip(L[...,None]+(1+saturation*weight[...,None])*(C-L[...,None]),0,1)
    return np.clip(highlight_taper(C,highlight),0,1)

def icon_field(material,diameter=DREF,output_scale=1.,highlight=HIGHLIGHT,saturation=SATURATION,blur_ratio=ICON_RATIO):
    # Blur the calculated icon COLOR field, not its silhouette/coverage, and
    # not the underlying glass. This differs from earlier input-blur trials.
    C=colored_icon(material,highlight,saturation)
    sigma=blur_ratio*diameter*output_scale
    return cv2.GaussianBlur(C,(0,0),sigma)if sigma else C

def source_for(diameter):
    sigma=SOURCE_RATIO*diameter
    if sigma not in blurs:blurs[sigma]=cv2.GaussianBlur(source,(0,0),sigma)
    return blurs[sigma]

def light_field(X,Y,diameter):
    # Evaluate every lighting length (including the helper's thin-rim basis)
    # in reference-normalized coordinates, so no hidden fixed-pixel rim remains.
    scale=DREF/diameter;X=X*scale;Y=Y*scale
    return illumination(X,Y,case['half'],DREF/2,prior['rim_width'],case_geometry(case,X,Y))

def sample_material(X,Y,center,diameter=DREF):
    R=diameter/2;r=np.hypot(X,Y);a=displacement(R-r,diameter)
    ratio=np.divide(r-a,r,out=np.ones_like(r),where=r>1e-12)
    sample=cv2.remap(source_for(diameter),(X*ratio+center[0]).astype(np.float32),(Y*ratio+center[1]).astype(np.float32),cv2.INTER_LINEAR)
    return shade(sample,light_field(X,Y,diameter),co)

def still_material():
    result=np.zeros_like(base)
    for top in range(y0,y1,24):
        bottom=min(top+24,y1);Y,X=np.mgrid[top:bottom:.25,x0:x1:.25]
        C=sample_material(X-.375-cx,Y-.375-cy,(cx,cy))
        result[top-y0:bottom-y0]=C.reshape(bottom-top,4,x1-x0,4,3).mean((1,3))
    return cv2.GaussianBlur(result,(0,0),POST_RATIO*DREF)

context=compose('media',case,target,np.uint8(base*255),root/'curvature-contour')/255.
cov=coverage('media')
def composite(material,color):
    result=context.copy();result[y0:y1,x0:x1]=material*cov+result[y0:y1,x0:x1]*(1-cov)
    # Replace the original icon rectangle completely, including its AA fringe.
    B=material[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
    C=color[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
    result[iy0:iy1,ix0:ix1]=B*(1-alpha[...,None])+C*alpha[...,None]
    return result

def crop(C,box,scale=1):
    if np.issubdtype(C.dtype,np.floating):C=np.uint8(np.rint(np.clip(C,0,1)*255))
    im=Image.fromarray(C).crop(box)
    return im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)

def sheet(name,rows,footer=''):
    W=max(sum(im.width+12 for _,im in row)for row in rows)+12
    H=sum(max(im.height for _,im in row)+44 for row in rows)+12+(40 if footer else 0)
    im=Image.new('RGB',(W,H),'#14171e');d=ImageDraw.Draw(im);Y=8
    for row in rows:
        X=12
        for label,C in row:d.text((X,Y),label,font=FONT,fill='#edf0f7');im.paste(C,(X,Y+30));X+=C.width+12
        Y+=max(C.height for _,C in row)+44
    if footer:d.text((12,Y+5),footer,font=SMALL,fill='#b7c2d2')
    im.save(out/name)

def controls():
    check={};d=np.linspace(0,245,30001);a=displacement(d)
    assert (a>=0).all() and np.isfinite(a).all()
    derivative=1+np.gradient(a,d)
    check['radial_fold_count']=int(np.count_nonzero(np.diff(np.sign(derivative))))
    assert check['radial_fold_count']==1
    checks=[];lighting_checks=[]
    for scale in [.25,.5,1,2,4]:
        checks.append(float(np.max(abs(displacement(d*scale,DREF*scale)-scale*a))))
        assert abs(POST_RATIO*(DREF*scale)/scale-1.6)<1e-12
        assert abs(ICON_RATIO*(DREF*scale)/scale-2)<1e-12
        X=np.array([0.,30.,140.,240.]);Y=np.array([180.,-120.,80.,20.])
        lighting_checks.append(float(np.max(abs(light_field(X*scale,Y*scale,DREF*scale)-light_field(X,Y,DREF)))))
    check['scale_covariance_max_error_px']=max(checks);assert max(checks)<1e-9
    check['lighting_scale_max_error']=max(lighting_checks);assert max(lighting_checks)<1e-12
    q=np.linspace(0,1,100001);m=np.repeat(q[:,None],3,axis=-1)
    for k in [0,.5,1,2,3,4]:
        C=highlight_taper(m,k)
        assert np.diff(C[:,0]).min()>=-1e-12 and np.max(abs(C[:,0]-C[:,1]))==0
        assert np.max(abs(C[q<=HIGHLIGHT_START]-m[q<=HIGHLIGHT_START]))==0
        assert (C[0]==0).all() and (C[-1]==1).all()
    check['highlight_monotonicity']='100001 samples per strength; k=0,.5,1,2,3,4; neutral grays and black/white endpoints; unchanged below .9'
    L=np.array([.8,.9,.95,.99,1]);weight=np.clip((1-L)/DARK_SPAN,0,1)**2
    assert np.diff(weight).max()<=0 and weight[-1]==0
    check['dark_saturation_weight']={str(l):float(w)for l,w in zip(L,weight)}
    # Empirical original channel response is not globally color-order-safe.
    # Retain that limitation rather than silently imposing another shader.
    rng=np.random.default_rng(6006);B=rng.uniform(0,1,(10000,3));C=colored_icon(B)
    assert np.isfinite(C).all()and C.min()>=0 and C.max()<=1
    check['icon_response_limits']='Original independent-channel response retained by owner choice; global hue-order preservation is not claimed.'
    (out/'verification.json').write_text(json.dumps(check,indent=2)+'\n')
    return check

def stills():
    cache=raw/'material.npy'
    M=np.load(cache)if cache.exists()else still_material();np.save(cache,M)
    T=target[iy0:iy1,ix0:ix1]/255.;inside=cv2.erode(np.uint8(alpha>.99),np.ones((7,7),np.uint8))>0
    def metrics(color):
        C=color[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
        return dict(RGB_rmse_255=float(np.sqrt(np.mean((C[inside]-T[inside])**2))*255),near_white_fraction=float(np.mean((C[inside]*255>=253).all(-1))),peak_RGB=(C[inside].max(0)*255).tolist())
    original=composite(base,old_response(base));control=composite(M,old_response(M))
    primary_color=icon_field(M);primary=composite(M,primary_color)
    Image.fromarray(np.uint8(np.rint(primary*255))).save(raw/'selected-full.png')
    Image.fromarray(np.uint8(np.rint(control*255))).save(raw/'same-lens-original-icon-full.png')
    sheet('01-playback-comparison.png',[[('Apple',crop(target,case['crop'])),('Pass04',crop(original,case['crop'])),('4.5x / original icon',crop(control,case['crop'])),('4.5x / revised icon',crop(primary,case['crop']))]],'Selected optics: gain1, post-blur1.6px per490px diameter. Example icon: highlight0.5, dark saturation0.2, color blur2px per490px.')
    results=dict(scope='Playback only. Width4.5/gain1 and proportional1.6px glass blur chosen by reviewer; icon strength remains for review.',normalized=dict(reference_diameter_px=DREF,post_sigma_over_short_dimension=POST_RATIO,source_sigma_over_short_dimension=SOURCE_RATIO,icon_sigma_over_short_dimension=ICON_RATIO,spatial_rule='sigma = ratio * min(width,height), in the same units as the geometry; convert to output pixels only when rasterizing.'),geometry=dict(width=WIDTH,gain=GAIN,inner_power=Q,quiet_center_starts_at_depth_px=prior['parameters']['band']*DREF/2*(1+WIDTH)/2),icon=dict(base_parameters=params.tolist(),highlight_start=HIGHLIGHT_START,dark_span=DARK_SPAN,default_highlight=HIGHLIGHT,default_saturation=SATURATION,default_color_sigma_px=ICON_RATIO*DREF,order='Pass04 response -> dark-weighted chroma -> componentwise monotone highlight taper -> blur calculated color field -> composite sharp icon coverage',formulas=dict(highlight='u=clamp((C-.9)/.1,0,1); C_out=C-k*u^3*(1-C), 0<=k<=4',saturation='L=dot(C,luma); w=clamp((1-L)/.15,0,1)^2; C_out=clip(L+(1+s*w)*(C-L),0,1)')),highlight_trials=[],blur_trials=[],saturation_trials=[],primary=metrics(primary_color))
    box=(870,420,1095,675)
    rows=[]
    for sigma in [0,2,4]:
        high=[('Apple / blur row '+str(sigma),crop(target,box,2))]
        for k in [0,.25,.5,1,2]:
            C=icon_field(M,highlight=k,blur_ratio=sigma/DREF);high.append((f'Taper {k:g} / blur {sigma:g}px',crop(composite(M,C),box,2)));results['highlight_trials'].append(dict(strength=k,icon_color_sigma_at_reference_px=sigma,**metrics(C)))
        rows.append(high)
    sheet('02-highlight-options.png',rows,'Columns: larger taper means LESS highlight. Rows: calculated icon-color blur. Fixed lens, dark saturation0.2, sharp silhouette.')
    blur=[]
    for sigma in [0,1,2,4,6]:
        C=icon_field(M,blur_ratio=sigma/DREF);blur.append((f'Icon blur {sigma:g}px',crop(composite(M,C),box,2)));results['blur_trials'].append(dict(sigma_over_diameter=sigma/DREF,sigma_at_reference_px=sigma,**metrics(C)))
    sheet('03-icon-internal-blur.png',[[('Apple',crop(target,box,2))]+blur],'Same highlight0.5 and saturation0.2. Filter applies to icon COLOR only; silhouette, feather and glass remain unchanged.')
    sat=[];detail=(995,465,1092,595)
    for amount in [0,.1,.2,.3]:
        C=icon_field(M,saturation=amount);sat.append((f'Dark saturation {amount:g}',crop(composite(M,C),detail,4)));results['saturation_trials'].append(dict(amount=amount,**metrics(C)))
    sheet('04-dark-saturation.png',[[('Apple',crop(target,detail,4))]+sat],'Same highlight0.5 and color blur2px. Saturation boost fades with brightness and vanishes at white.')
    groups=[('Bottom-left',(690,570,910,810)),('Top-left',(690,290,910,530)),('Upper-right',(1025,320,1245,560))]
    sheet('05-rim-crops.png',[[('Apple / '+label,crop(target,box,2)),('Pass04',crop(original,box,2)),('4.5x / 1.6px blur',crop(primary,box,2))]for label,box in groups],'2x nearest-neighbor. Still exterior remains the prior estimated/retained reference context; optical model remains an inverse-map approximation.')
    dune=(920,680,1040,728)
    sheet('06-dune-detail.png',[[('Apple',crop(target,dune,4)),('Pass04',crop(original,dune,4)),('Selected 1.6px / 490px',crop(primary,dune,4))]],'4x nearest-neighbor; glass blur scales with lens shorter dimension, not a fixed raster-pixel count.')
    results['reference_near_white_fraction']=float(np.mean((T[inside]*255>=253).all(-1)))
    (out/'diagnostics.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Stills complete; highlight coverage',[(r['strength'],r['near_white_fraction'])for r in results['highlight_trials']],flush=True)

def motion():
    N=270;pad=N//2;axis=np.arange(2*N,dtype=float)-N+.5;Y,X=np.meshgrid(axis,axis,indexing='ij')
    R=DREF/2;r=np.hypot(X,Y);a=displacement(R-r);ratio=np.divide(r-a,r,out=np.ones_like(r),where=r>1e-12)
    lookupX=X*ratio;lookupY=Y*ratio
    light=light_field(X,Y,DREF)
    coverage=(r<=R).reshape(N,2,N,2).mean((1,3))
    mask=cv2.remap(alpha,(X+cx-ix0).astype(np.float32),(Y+cy-iy0).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT).reshape(N,2,N,2).mean((1,3))
    background=cv2.resize(source,(960,540),interpolation=cv2.INTER_AREA)
    streams=[];logs=[]
    for name,size in [('07-playback-motion','960x540'),('08-icon-motion-comparison','1920x540')]:
        log=(out/(name+'.encode.log')).open('w');logs.append(log)
        streams.append(subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',size,'-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out/(name+'.mp4'))],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log))
    frames=[]
    for i in range(180):
        u=i/180;center=np.rint([480+170*np.sin(2*np.pi*u),270+60*np.sin(4*np.pi*u)]).astype(int)
        sample=cv2.remap(source_for(DREF),(lookupX+2*center[0]).astype(np.float32),(lookupY+2*center[1]).astype(np.float32),cv2.INTER_LINEAR)
        M=shade(sample,light,co).reshape(N,2,N,2,3).mean((1,3));M=cv2.GaussianBlur(M,(0,0),POST_RATIO*DREF/2)
        colors=[old_response(M),icon_field(M,output_scale=.5)];pair=[]
        for label,C in zip(['Original pass04 response / same lens','Revised icon / same lens'],colors):
            material=M*(1-mask[...,None])+C*mask[...,None]
            frame=background.copy();x,y=center[0]-pad,center[1]-pad
            frame[y:y+N,x:x+N]=material*coverage[...,None]+frame[y:y+N,x:x+N]*(1-coverage[...,None])
            im=Image.fromarray(np.uint8(np.rint(np.clip(frame,0,1)*255)));draw=ImageDraw.Draw(im)
            draw.rounded_rectangle((12,12,418,44),radius=8,fill='#14171e');draw.text((22,19),label,font=FONT,fill='#edf0f7');pair.append(np.array(im))
        streams[0].stdin.write(pair[1].tobytes());comparison=np.concatenate(pair,axis=1);streams[1].stdin.write(comparison.tobytes())
        if i in [0,45,90,135]:frames.append(Image.fromarray(comparison))
        if i%30==0:print('Motion frame',i,flush=True)
    for process in streams:
        process.stdin.close();assert process.wait()==0,'Encoding failure'
    for log in logs:log.close()
    canvas=Image.new('RGB',(1920,2160))
    for i,frame in enumerate(frames):canvas.paste(frame,(0,540*i))
    canvas.save(out/'09-motion-frames.png')
    probes={}
    for file in out.glob('*.mp4'):
        result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration,pix_fmt','-of','json',str(file)],stdout=subprocess.PIPE,check=True)
        probes[file.name]=json.loads(result.stdout)
        decode=subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        assert decode.returncode==0 and not decode.stderr
    (out/'motion-diagnostics.json').write_text(json.dumps(dict(probes=probes,frames=180,duration_seconds=6,frame_rate=30,same_model='Both clips use width4.5, gain1, scaled1.6px post-blur. Comparison changes only icon rendering.',limits=['Offline CPU rendering; playback fps is not rendering speed or Android performance.','Pure translation; no deformation. Exterior shadow omitted.','Original pass04 independent-channel response retained; global hue-order preservation is not claimed.']),indent=2)+'\n')
    print('Both motion clips decode cleanly',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--motion-only',action='store_true');args=parser.parse_args()
    if not args.motion_only:controls();stills()
    motion()
    files=sorted([*out.glob('*.png'),*out.glob('*.mp4'),*out.glob('*.json')])
    (out/'media.sha256').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n'for f in files))
