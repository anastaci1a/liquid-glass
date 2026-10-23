"""Independent source typography feasibility: unoccluded720 only for fitting.

Train font/size/PSF/opacity on 'and depend on'. Align separate line using only
'the'; score 'world around us.' and frozen outside-glass A controls untouched.
No glass pixels, donor registration, hidden-word invention or optical fit.
"""
import sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont
from scipy.optimize import least_squares
cv2.setNumThreads(1)
out=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-A-typography');protocol=json.loads((out/'protocol.json').read_text());raw=np.load(out/'observed-opacity.npz');ink=raw['ink'];paper=raw['paper'];fonts=Path('/evidence/extended/icon-source/fonts/Library/Fonts');pbase=136;pad=20.;baseline=150.;results=[];cache={};trials=[]
trainbox=protocol['geometry_boxes']['train_and_depend_on']['box'];alignbox=protocol['geometry_boxes']['align_the_only']['box'];holdbox=protocol['geometry_boxes']['heldout_world_around_us']['box']
def crop(A,b):
    x,y,z,w=b;return A[y:w,x:z]
def template(font,text):
    f=ImageFont.truetype(str(font),pbase*4);width=int(np.ceil(f.getlength(text)/4+2*pad));image=Image.new('L',(width*4,200*4));ImageDraw.Draw(image).text((pad*4,baseline*4),text,font=f,fill=255,anchor='ls');a=cv2.resize(np.asarray(image,np.float32)/255,(width,200),interpolation=cv2.INTER_AREA);return a
def render(A,params,box):
    ox,by,scale,sigma,amplitude=params;x,y,z,w=box;M=np.array([[scale,0,ox-x-scale*pad],[0,scale,by-y-scale*baseline]],float);a=cv2.warpAffine(A,M,(z-x,w-y),flags=cv2.INTER_LINEAR)
    if sigma>1e-7:a=cv2.GaussianBlur(a,(0,0),sigma)
    return a*amplitude
def fit_template(A,box,initial,lower,upper,steps,mode):
    obs=crop(ink,box).astype(float);used={};calls=0
    def fun(v):
        nonlocal calls
        key=tuple(map(float,v))
        if key not in used:
            pred=render(A,v,box);res=(pred-obs)[::2,::2].ravel();used[key]=res;calls+=1
        return used[key]
    def jac(v):
        cols=[]
        for i,h in enumerate(steps):
            plus=np.array(v);minus=np.array(v);plus[i]=min(upper[i],v[i]+h);minus[i]=max(lower[i],v[i]-h);cols.append((fun(plus)-fun(minus))/(plus[i]-minus[i]))
        return np.stack(cols,axis=1)
    fit=least_squares(fun,np.clip(initial,lower,upper),jac=jac,bounds=(lower,upper),ftol=1e-8,xtol=1e-7,gtol=1e-7,max_nfev=45,x_scale=np.array([2,2,.02,.5,.05]))
    return fit,render(A,fit.x,box),calls
for index,filename in enumerate(protocol['candidates']):
    font=fonts/filename;A=template(font,'and depend on');B=template(font,'the world around us.');yy,xx=np.where(A>.25);observed=protocol['geometry_boxes']['train_and_depend_on']['observed_ink_bbox_xyxy'];scale0=(observed[3]-observed[1])/(yy.max()-yy.min()+1);xinit=observed[0]-scale0*(xx.min()-pad);yinit=observed[3]-scale0*(yy.max()+1-baseline)
    initial=np.array([xinit,yinit,scale0,1.,.99]);lower=np.array([xinit-12,yinit-10,scale0-.07,0.,.75]);upper=np.array([xinit+12,yinit+10,scale0+.07,5.,1.05]);fit,pred,calls=fit_template(A,trainbox,initial,lower,upper,[.125,.125,.0008,.05,.004],'train');np.savez_compressed(out/f'{index}-train-template.npz',alpha=A,heldout_template=B);params=fit.x
    # Only pose of 'the' is calibrated; font/size/PSF/opacity stay frozen.
    f=ImageFont.truetype(str(font),pbase);width_the=f.getlength('the ');prefix_mask=B.copy();prefix_mask[:,int(np.ceil(pad+width_the)):]=0;yy,xx=np.where(prefix_mask>.25);observed=protocol['geometry_boxes']['align_the_only']['observed_ink_bbox_xyxy'];pose0=np.array([observed[0]-params[2]*(xx.min()-pad),observed[3]-params[2]*(yy.max()+1-baseline)])
    obsalign=crop(ink,alignbox).astype(float);pose_cache={}
    def alignfun(v):
        key=tuple(map(float,v))
        if key not in pose_cache:pose_cache[key]=(render(prefix_mask,[*v,*params[2:]],alignbox)-obsalign)[::2,::2].ravel()
        return pose_cache[key]
    def alignjac(v):
        cols=[]
        for i in range(2):
            u=v.copy();w=v.copy();u[i]+=.125;w[i]-=.125;cols.append((alignfun(u)-alignfun(w))/.25)
        return np.stack(cols,axis=1)
    pose=least_squares(alignfun,pose0,jac=alignjac,bounds=(pose0-10,pose0+10),ftol=1e-8,xtol=1e-7,gtol=1e-7,max_nfev=35)
    holdparams=np.r_[pose.x,params[2:]];predhold=render(B,holdparams,holdbox);obshold=crop(ink,holdbox);trainobs=crop(ink,trainbox);trainerr=(pred-trainobs);holderr=predhold-obshold
    full_line=render(B,holdparams,[0,0,1920,1080]);np.save(out/f'{index}-predicted-lastline-opacity.npy',full_line);Image.fromarray(np.uint8(np.clip(full_line,0,1)*255)).save(out/f'{index}-predicted-lastline-opacity.png');ys,xs=np.where(full_line>.01)
    row={'font':filename,'font_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'train_parameters':params.tolist(),'font_size_native_px':float(params[2]*pbase),'train_success':bool(fit.success),'train_status':int(fit.status),'train_message':str(fit.message),'train_optimality':float(fit.optimality),'train_nfev':int(fit.nfev),'train_unique_parameter_evals':calls,'train_opacity_RMSE':float(np.sqrt(np.mean(trainerr**2))),'heldout_pose_the_only':pose.x.tolist(),'heldout_pose_success':bool(pose.success),'heldout_pose_message':str(pose.message),'heldout_world_run_opacity_RMSE':float(np.sqrt(np.mean(holderr**2))),'heldout_relative_error_increase':float(np.sqrt(np.mean(holderr**2))/max(np.sqrt(np.mean(trainerr**2)),1e-20)),'predicted_lastline_ink_bbox_raw720':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'train_bounds':[lower.tolist(),upper.tolist()]};results.append(row);(out/'font-results.json').write_text(json.dumps(results,indent=2)+'\n');print('FONT23',json.dumps(row),flush=True)
best_index=min(range(len(results)),key=lambda i:results[i]['train_opacity_RMSE']);best=results[best_index];alpha=np.load(out/f'{best_index}-predicted-lastline-opacity.npy');M=np.array([[.9578697054607762,.00018082755364204328,40.514486622923656],[-.00018082755364204328,.9578697054607762,210.46202215716735]]);alphaA=cv2.warpAffine(alpha,M,(1920,1080));ys,xs=np.where(alphaA>.01);estimated=np.ones((1080,1920),np.float32);estimated[350:790,490:1420]=0;estimated=cv2.warpAffine(estimated,M,(1920,1080),flags=cv2.INTER_LINEAR)<.999;overlap=int(((alphaA>.01)&estimated).sum())
# Shared existing paper coefficients, no A-glyph/color fit. ONLY validation on
# explicit exterior control rectangles, no source image is replaced here.
Aref=np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png'),float)/255;oldsource=np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/source.png'),float)/255;audit=json.loads(Path('/tmp/agent-toolbar-input-audit.json').read_text());co=np.array(audit['registration']['page_field']['background_coefficients']);yy,xx=np.mgrid[:1080,:1920];X=(xx-960)/960;Y=(yy-540)/540;paperA=np.clip(np.stack([X**i*Y**j for i in range(5) for j in range(5-i)],axis=-1)@co,0,1);newlast=paperA*(1-alphaA[...,None]);validation={}
for name,(a,b,c,d) in {'A_left_lastline_heldout':[60,425,480,555]}.items():
    mask=np.zeros((1080,1920),bool);mask[b:d,a:c]=True;inkmask=mask&(Aref.min(2)<.4);papermask=mask&(Aref.min(2)>.75)
    def score(I,mask):return {'pixels':int(mask.sum()),'RGB_RMSE_255':float(np.sqrt(np.mean(((I-Aref)[mask]*255)**2)))}
    validation[name]={'oldsource_all':score(oldsource,mask),'font_model_all':score(newlast,mask),'oldsource_ink':score(oldsource,inkmask),'font_model_ink':score(newlast,inkmask),'oldsource_paper':score(oldsource,papermask),'font_model_paper':score(newlast,papermask)}
report={'selected_by_TRAIN_only_index':best_index,'selected':best,'all_font_results':results,'estimated_rectangle_new_predicted_ink_pixels':overlap,'registered_predicted_lastline_ink_bbox_A':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'outside_A_controls_never_used_to_fit':validation,'paper_RGB_reused_unchanged':True,'no_new_donor_registration':True,'no_source_pixels_promoted_or_epoch_changed':True,'native_optical_fits_renders':0,'limits':['One font/PSF model does not identify source RGB truth or unknown words','All source fitting uses unoccluded720glyphs and paper, Aexteriorheldout only validates','Existing720registration reused with historical covariance unknown; no source adoption or optical gain claimed']};(out/'feasibility.json').write_text(json.dumps(report,indent=2)+'\n');np.save(out/'selected-proposed-lastline-opacity-A.npy',alphaA);print('TYPOGRAPHY23_COMPLETE',json.dumps({'selected_font':best['font'],'train_RMSE':best['train_opacity_RMSE'],'heldout_RMSE':best['heldout_world_run_opacity_RMSE'],'new_estimated_ink':overlap,'A_exterior_validation':validation}),flush=True)
