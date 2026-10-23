"""Playback-only owner review: independent rim, fine blur and icon experiments.

No source/reference edits. No native-app or deployment changes. Optical trials
are C2 radial inverse maps, NOT identified physical Apple surface curvature.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.optimize import least_squares
from scipy.interpolate import PchipInterpolator
from publish import read,compose,coverage,CASES
from render import illumination,case_geometry,shade
from reproduce import scores

root=Path('/evidence/apple-matches');fits=root/'curvature-contour'
out=root/'review-pass05-playback';out.mkdir(exist_ok=True)
raw=out/'renders';raw.mkdir(exist_ok=True)
FONTP='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F=ImageFont.truetype(FONTP,17);S=ImageFont.truetype(FONTP,13)
case=CASES['media'];x0,y0,x1,y1=case['crop'];cx,cy=case['center'];R=245.
target=read(fits/'media-target.png');source=read(fits/'media-source.png')/255.
prior=json.loads((root/'pass04-candidates/media-singlefold-3461.json').read_text())
P=prior['parameters'];A=P['amplitude']*R;b=P['band']*R;p=P['power']
co=np.array(prior['material']);src=cv2.GaussianBlur(source,(0,0),prior['sigma'])
base=read(root/'pass04-candidates/media-singlefold-3461.png')/255.
alpha=np.array(Image.open(root/'review-pass-02/06-white-icon-mask.png'))/255.
IB=(870,420,1095,675);ix0,iy0,ix1,iy1=IB
alpha_full=np.zeros(target.shape[:2]);alpha_full[iy0:iy1,ix0:ix1]=alpha
yy,xx=np.mgrid[y0:y1,x0:x1];d=R-np.hypot(xx-cx,yy-cy)
cov=coverage('media')
context=compose('media',case,target,np.uint8(base*255),fits)/255.

def smooth5(t):
    t=np.clip(t,0,1);return t*t*t*(10+t*(-15+6*t))

def displacement(depth,width=1.,gain=1.,end_power=4.):
    """Exact baseline at (1,1,p); C2 splice preserves the outer map.

    d_a=b/4, d_s=b/2; gain ramps with S5 between these depths. The
    tail from d_s to d_s+width*(b-d_s) has identical value/first/second
    derivative at its entry. The tail's endpoint exponent is independent of
    the original profile: >2 gives C2; >3 also gives C3 at the inner endpoint.
    """
    initial=A*np.clip(1-depth/b,0,1)**p
    start=b/2;w0=b-start;w=width*w0
    ramp=1+(gain-1)*smooth5((depth-b/4)/(start-b/4))
    t=np.clip((depth-start)/w,0,1-1e-12)
    q=end_power
    logtail=q*np.log1p(-t)+(q-p*width)*t+.5*(q-p*width*width)*t*t
    tail=gain*A*(1-start/b)**p*np.exp(logtail)
    return np.where(depth<=start,initial*ramp,np.where(depth<start+w,tail,0.))

def render(width,gain,end_power=4.):
    result=np.zeros_like(base)
    for top in range(y0,y1,24):
        bottom=min(top+24,y1)
        Y,X=np.mgrid[top:bottom:.25,x0:x1:.25];X=X-.375-cx;Y=Y-.375-cy
        radius=np.hypot(X,Y);a=displacement(R-radius,width,gain,end_power)
        ratio=np.divide(radius-a,radius,out=np.ones_like(radius),where=radius>1e-12)
        sample=cv2.remap(src,(X*ratio+cx).astype(np.float32),(Y*ratio+cy).astype(np.float32),cv2.INTER_LINEAR)
        light=illumination(X,Y,case['half'],R,prior['rim_width'],case_geometry(case,X,Y))
        result[top-y0:bottom-y0]=shade(sample,light,co).reshape(bottom-top,4,x1-x0,4,3).mean((1,3))
    return result

def crop(im,box,scale=1):
    if np.issubdtype(im.dtype,np.floating):im=np.uint8(np.rint(np.clip(im,0,1)*255))
    im=Image.fromarray(im).crop(box)
    return im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)

def sheet(path,rows,footer=''):
    """Each row: [(label,PIL image),...]. Supports different cell heights."""
    W=max(sum(im.width+12 for _,im in row) for row in rows)+12
    H=sum(max(im.height for _,im in row)+44 for row in rows)+12+(42 if footer else 0)
    canvas=Image.new('RGB',(W,H),'#14171e');dr=ImageDraw.Draw(canvas);Y=8
    for row in rows:
        X=12;h=max(im.height for _,im in row)
        for label,im in row:
            dr.text((X,Y),label,font=F,fill='#edf0f7');canvas.paste(im,(X,Y+30));X+=im.width+12
        Y+=h+44
    if footer:dr.text((12,Y+5),footer,font=S,fill='#b7c2d2')
    canvas.save(out/path)

def full(material,icon):
    result=context.copy()
    result[y0:y1,x0:x1]=material*cov+result[y0:y1,x0:x1]*(1-cov)
    # No retained original icon or AA fringe in the symbol neighborhood.
    result[iy0:iy1,ix0:ix1]=material[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
    result[iy0:iy1,ix0:ix1]=result[iy0:iy1,ix0:ix1]*(1-alpha[...,None])+icon*alpha[...,None]
    return result

# Keep the pass04 white-mask response as an exact comparison control.
old_params=np.array(json.loads((root/'review-pass04-complete/diagnostics.json').read_text())['icon_parameters'])
old_response=lambda B:1-old_params[:3]*(1-B)**old_params[3:6]
base_icon_field=base[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
base_full=full(base,old_response(base_icon_field))
T=target[iy0:iy1,ix0:ix1]/255.
inside=cv2.erode(np.uint8(alpha>.99),np.ones((7,7),np.uint8))>0
YI,XI=np.mgrid[iy0:iy1,ix0:ix1];held=((XI//32+3*(YI//32))%4)==0
train=inside&~held;test=inside&held
LUMA=np.array([.2126,.7152,.0722])

def response(v,B):
    # A clipped background threshold produces a real white plateau rather
    # than merely approaching white asymptotically.
    C=1-v[:3]*np.maximum(1-B/v[6],0)**v[3:6]
    if len(v)>7:
        l=C@LUMA
        C=l[...,None]+(1+v[7]*(1-l[...,None]))*(C-l[...,None])
    return np.clip(C,0,1)

def ordered_response(v,B):
    # Common strength, ordered channel exponents. For warm inputs R>=G>=B,
    # the output remains warm: each step preserves that component ordering.
    a,gblue,dgreen,dred,t=v[:5]
    gamma=np.array([gblue+dgreen+dred,gblue+dgreen,gblue])
    C=1-a*np.maximum(1-B/t,0)**gamma
    L=C@LUMA
    return np.clip(L[...,None]+(1+v[5]*(1-L[...,None]))*(C-L[...,None]),0,1)

def fit_ordered_icon(B):
    best=None
    for t in [.45,.7]:
        fit=least_squares(lambda v:(ordered_response(v,B[train])-T[train]).ravel(),[.45,1.5,1.5,1,t,.1],bounds=([0,.1,0,0,.3,0],[.5,12,12,12,1,3]),max_nfev=400)
        if best is None or fit.cost<best.cost:best=fit
    return best.x

def shared_curve_response(v,B):
    increments=np.r_[v[1:4],1.]
    cumulative=np.r_[0,np.cumsum(increments)/increments.sum()]
    values=np.r_[v[0]+(1-v[0])*cumulative,1.]
    knots=np.r_[v[4]*np.array([0,.3,.55,.8,1]),1.]
    return PchipInterpolator(knots,values)(np.clip(B,0,1))

def fit_shared_icon(B):
    best=None
    for t in [.4,.5,.7]:
        f=least_squares(lambda v:(shared_curve_response(v,B[train])-T[train]).ravel(),[.6,.1,.8,1,t],bounds=([.5,.001,.001,.001,.3],[.9,8,8,8,.9]),max_nfev=300)
        if best is None or f.cost<best.cost:best=f
    return best.x

def fit_icon(B,saturated=False):
    start=list(old_params)+[.7]+([.15] if saturated else [])
    bounds=([0,0,0,.1,.1,.1,.3]+([0] if saturated else []),[1,1,1,16,16,16,1]+([3] if saturated else []))
    best=None
    # Fit against eroded interiors; edges and white-mask shape never optimized.
    for white in [.65,.9]:
        v=start.copy();v[6]=white
        f=least_squares(lambda v:(response(v,B[train])-T[train]).ravel(),v,bounds=bounds,max_nfev=250)
        if best is None or f.cost<best.cost:best=f
    return best.x

def icon_metrics(pred):
    result={key:float(np.sqrt(np.mean((pred[mask]-T[mask])**2))*255) for key,mask in [('train_rmse',train),('held_rmse',test)]}
    result['RGB_percentiles']={str(q):[float(v) for v in np.quantile(pred[inside],q/100,axis=0)*255] for q in [5,50,95,99,100]}
    result['near_white_fraction']=float(np.mean((pred[inside]*255>=253).all(-1)))
    return result

report=dict(scope='Play button only; no slider or toolbar changes.',geometry=dict(model='C2 radial inverse-map splice; C3 at inner endpoint, not recovered surface curvature',radius=R,amplitude_px=A,original_band_px=b,original_power=p,inner_endpoint_power=4.,tail_start_depth_px=b/2,baseline_tail_width_px=b/2,outer_gain_ramp_start_px=b/4,material='Fixed pass04 coefficients and source sigma; no per-candidate nuisance refit'),geometry_trials=[],blur_trials=[],icon_trials=[])

# First render the full requested two-axis grid. Fixed material/no icon refits.
widths=[1,1.5,2,2.5,3,3.5,4];gains=[.75,1,1.25];rendered={}
radial=np.linspace(0,R,30001)
for gain in gains:
    for width in widths:
        key=f'q4-w{width:g}-g{gain:g}'
        cache=raw/f'{key}.npy'
        im=np.load(cache)if cache.exists()else render(width,gain)
        np.save(cache,im);rendered[(width,gain)]=im
        Image.fromarray(np.uint8(np.rint(im*255))).save(raw/f'{key}.png')
        a=displacement(radial,width,gain);D=1+np.gradient(a,radial)
        signs=np.sign(D);folds=int(np.count_nonzero(signs[1:]!=signs[:-1]))
        assert np.isfinite(im).all() and (a>=0).all()
        assert folds==1,(key,folds)
        stat=scores(im.astype(np.float32),(target[y0:y1,x0:x1]/255.).astype(np.float32),case)
        report['geometry_trials'].append(dict(key=key,width_factor=width,shoulder_gain=gain,tail_width_px=width*b/2,quiet_center_starts_at_depth_px=(1+width)*b/2,shoulder_displacement_px=gain*A*.5**p,radial_derivative_sign_changes=folds,scores=stat))
        print(key,stat['all_glass']['rmse'],flush=True)
reference=A*np.maximum(1-radial/b,0)**p
report['geometry']['baseline_max_displacement_error_px']=float(np.max(np.abs(reference-displacement(radial,1,1,p))))
assert report['geometry']['baseline_max_displacement_error_px']<1e-10
baseline_render=render(1,1,p)
report['geometry']['baseline_rerender_RGB_max_error_255']=float(np.max(np.abs(baseline_render-base))*255)
report['geometry']['baseline_rerender_rounded_uint8_max_error']=float(np.max(np.abs(np.rint(baseline_render*255)-base*255)))
assert report['geometry']['baseline_rerender_rounded_uint8_max_error']<=1

# Select by the same training-pixel loss as the established comparison. Held
# blocks are reported, never used for selection. This is still one image.
bestgeo=min(report['geometry_trials'],key=lambda f:f['scores']['selection_loss'])
chosen=rendered[(bestgeo['width_factor'],bestgeo['shoulder_gain'])]
report['geometry_selected']=bestgeo['key']
rows=[]
for gain in gains:
    row=[('Apple',crop(target,case['crop']).resize((340,328),Image.Resampling.LANCZOS))]
    for width in widths:
        im=rendered[(width,gain)];B=im[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
        row.append((f'{width:g}x / gain {gain:g}',crop(full(im,old_response(B)),case['crop']).resize((340,328),Image.Resampling.LANCZOS)))
    rows.append(row)
sheet('01-lens-transition-grid.png',rows,'Columns: tail width. Rows: inner-shoulder displacement. Same outer refraction, lighting and old icon response.')
box=(710,625,870,775)
rows=[]
for gain in gains:
    row=[('Apple / 2x',crop(target,box,2))]
    for width in widths:
        im=rendered[(width,gain)]
        row.append((f'{width:g}x / gain {gain:g}',crop(full(im,old_response(im[iy0-y0:iy1-y0,ix0-x0:ix1-x0])),box,2)))
    rows.append(row)
sheet('02-lens-rim-detail-grid.png',rows,'Same bottom-left crop, 2x nearest-neighbor. These are image-map controls, not measured surface-curvature values.')

# Fine POST-refraction blur, independent of geometry: pass04 map held fixed.
# The sample is >40px inside the rim and clear of the icon, so contact shading
# and symbol coverage cannot bias the fine-dune measurement.
dunebox=(920,680,1040,728);dx0,dy0,dx1,dy1=dunebox
expected=target[dy0:dy1,dx0:dx1]/255.
hp=lambda C:C-cv2.GaussianBlur(C,(0,0),1.)
sigmas=[0,.25,.5,.75,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,4,4.5,5]
blurred={}
for sigma in sigmas:
    im=cv2.GaussianBlur(base,(0,0),sigma) if sigma else base.copy();blurred[sigma]=im
    patch=im[dy0-y0:dy1-y0,dx0-x0:dx1-x0]
    residual=hp(patch)-hp(expected)
    report['blur_trials'].append(dict(post_refraction_sigma_px=sigma,detail_highpass_rmse_255=float(np.sqrt(np.mean(residual**2))*255),detail_highpass_rms_255=float(np.sqrt(np.mean(hp(patch)**2))*255),detail_RGB_rmse_255=float(np.sqrt(np.mean((patch-expected)**2))*255)))
report['blur_reference']=dict(crop=list(dunebox),highpass_sigma_px=1,reference_highpass_rms_255=float(np.sqrt(np.mean(hp(expected)**2))*255),limits='Single-frame detail diagnostic. Source registration, video compression and material errors confound blur identification; no recovered Apple blur-stage claim.')
bestblur=min(report['blur_trials'],key=lambda f:f['detail_highpass_rmse_255'])['post_refraction_sigma_px']
report['blur_selected_by_detail_diagnostic']=bestblur
rows=[]
for group in [sigmas[:6],sigmas[6:12],sigmas[12:]]:
    row=[('Apple / 4x',crop(target,dunebox,4))]
    for sigma in group:
        im=blurred[sigma]
        row.append((f'Added sigma {sigma:g}px',crop(full(im,old_response(im[iy0-y0:iy1-y0,ix0-x0:ix1-x0])),dunebox,4)))
    rows.append(row)
sheet('03-dune-blur-options.png',rows,'Pass04 geometry fixed; additional image-space glass blur only. Nearest-neighbor enlargement; icon not blurred.')

# Independently compare new icon response against the identical pass04 glass.
vplain=fit_icon(base_icon_field,False);vsat=fit_icon(base_icon_field,True)
icon_trials=[('Pass04 response',old_response(base_icon_field)),('White plateau',response(vplain,base_icon_field)),('Plateau + chroma',response(vsat,base_icon_field))]
illumination_trials=[]
for radius in [0,1,2,3,4,6,8]:
    # Smooth the full glass field before extracting icon input. Never filter
    # the icon mask or fill from beyond its own cropped neighborhood.
    B=cv2.GaussianBlur(base,(0,0),radius)if radius else base
    B=B[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
    v=vsat if not radius else fit_icon(B,True)
    pred=response(v,B)
    illumination_trials.append(dict(sigma_px=radius,parameters=v.tolist(),metrics=icon_metrics(pred)))
illumination_best=min(illumination_trials,key=lambda t:t['metrics']['train_rmse'])
radius=illumination_best['sigma_px'];field=cv2.GaussianBlur(base,(0,0),radius)if radius else base
if radius:icon_trials.append((f'Color input sigma {radius:g}px',response(np.array(illumination_best['parameters']),field[iy0-y0:iy1-y0,ix0-x0:ix1-x0])))
ordered=fit_ordered_icon(base_icon_field)
icon_trials.append(('Ordered response',ordered_response(ordered,base_icon_field)))
report['icon_ordered_model']=dict(parameters=ordered.tolist(),formula='gamma=[gB+dG+dR,gB+dG,gB]; C0=1-a*max(1-B/t,0)^gamma; C=clip(L+(1+s*(1-L))*(C0-L),0,1)',bounds=dict(strength=[0,.5],gblue=[.1,12],delta_green=[0,12],delta_red=[0,12],white_threshold=[.3,1],chroma=[0,3]),reason='Moving the unconstrained response over other dunes exposed pink reversals. Common strength and ordered exponents preserve R>=G>=B for warm RGB inputs. This is a constraint of this scene/control response, not a universal Apple material law.')
shared=fit_shared_icon(base_icon_field)
icon_trials.append(('Shared monotone curve',shared_curve_response(shared,base_icon_field)))
report['icon_shared_model']=dict(parameters=shared.tolist(),formula='w=[w1,w2,w3,1]; cumulative=[0,cumsum(w)/sum(w)]; values=[floor+(1-floor)*cumulative,1]; knots=[threshold*[0,.3,.55,.8,1],1]; apply same monotone PCHIP to each RGB component.',notes='Five parameters; shared scalar function preserves component order and neutral grays for every RGB input. White plateau and C1 transitions. Still an empirical encoded-RGB response, not recovered Apple shading.')
report['icon_illumination_trials']=illumination_trials
report['icon_illumination_selected_by_training_loss']=radius
for name,pred in icon_trials:
    report['icon_trials'].append(dict(name=name,**icon_metrics(pred)))
report['icon_reference']=icon_metrics(T)
report['icon_models']=dict(white_plateau=dict(parameters=vplain.tolist(),formula='C=1-a_RGB*max(1-B/t,0)^gamma_RGB'),plateau_chroma=dict(parameters=vsat.tolist(),formula='C0=plateau; L=dot(C0,luma); C=clip(L+(1+s*(1-L))*(C0-L),0,1)'),notes='Encoded-RGB empirical responses of the refracted background; no positional gradient or copied interior colors. Same mask and feather. Two optimizer starts; block-withheld check on the same scene.')
sheet('04-icon-color-options.png',[[('Apple',crop(target,IB,2))]+[(name,crop(full(base,pred),IB,2))for name,pred in icon_trials]],'Same glass in every reconstruction. Ordered response removes warm-background hue reversals; white silhouette stays sharp.')
# Close comparison of the diagonal upper-right edge and lower highlight.
iconbox=(995,465,1092,595)
sheet('05-icon-diagonal-detail.png',[[('Apple',crop(target,iconbox,4))]+[(name,crop(full(base,pred),iconbox,4))for name,pred in icon_trials]],'4x nearest-neighbor. White silhouette/AA unchanged; compare near-white highlights and faint warm saturation.')

# A wider-tail comparison stays separate from the training-loss choice. Pixel
# loss may favor the original map; do not call an arbitrary wider tail a winner.
# Compare two combined versions with identical icon PARAMETERS so their
# remaining differences come from glass geometry/blur and its color input.
combined=cv2.GaussianBlur(chosen,(0,0),bestblur)if bestblur else chosen
color_field=cv2.GaussianBlur(combined,(0,0),radius)if radius else combined
B=color_field[iy0-y0:iy1-y0,ix0-x0:ix1-x0]
vcombined=fit_shared_icon(B);combined_full=full(combined,shared_curve_response(vcombined,B))
wider=rendered[(2,1)];wider=cv2.GaussianBlur(wider,(0,0),bestblur)if bestblur else wider
wider_color=cv2.GaussianBlur(wider,(0,0),radius)if radius else wider
wider_full=full(wider,shared_curve_response(vcombined,wider_color[iy0-y0:iy1-y0,ix0-x0:ix1-x0]))
report['combined']=dict(geometry=bestgeo['key'],post_sigma_px=bestblur,icon_model='shared_curve_response',icon_color_input_sigma_px=radius,icon_parameters=vcombined.tolist(),icon_metrics=icon_metrics(shared_curve_response(vcombined,B)),additional_geometry_control='q4-w2-g1, same icon parameters and blur')
sheet('06-playback-combined.png',[[('Apple',crop(target,case['crop'])),('Pass04',crop(base_full,case['crop'])),('Combined / lowest map loss',crop(combined_full,case['crop'])),('Combined / 2x tail',crop(wider_full,case['crop']))]],'Same scale. Wider-tail control is an option, not an asserted improvement. Both combined icons use the same parameters.')
groups=[('Bottom-left',(690,570,910,810)),('Top-left',(690,290,910,530)),('Upper-right crossings',(1025,320,1245,560))]
sheet('07-playback-combined-rim.png',[[('Apple / '+title,crop(target,box,2)),('Pass04',crop(base_full,box,2)),('Combined / lowest loss',crop(combined_full,box,2)),('Combined / 2x tail',crop(wider_full,box,2))]for title,box in groups],'2x nearest-neighbor; exterior context remains the pass04 estimate/retained reference context.')
# Full native renders for zoom/crops and review reproducibility.
Image.fromarray(np.uint8(np.rint(combined_full*255))).save(raw/'combined-full.png')
Image.fromarray(np.uint8(np.rint(wider_full*255))).save(raw/'combined-wider-full.png')
Image.fromarray(np.uint8(np.rint(base_full*255))).save(raw/'pass04-control-full.png')
Image.fromarray(target).save(raw/'apple-full.png')
(out/'diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'images.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'for p in sorted(out.glob('*.png'))))
print('Complete',out,report['geometry_selected'],'blur',bestblur,flush=True)
