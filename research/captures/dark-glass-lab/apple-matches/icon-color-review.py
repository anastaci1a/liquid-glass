"""Background-driven icon color refinements; no painted positional gradient."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from scipy.optimize import least_squares
from publish import read,pair,compose,CASES

root=Path('/evidence/apple-matches');p=root/'curvature-contour';out=root/'review-pass-04';out.mkdir(exist_ok=True)
target=read(p/'media-target.png');source=read(p/'media-source.png');material=read(p/'media-exponential.png');case=CASES['media']
full=compose('media',case,target,material,p).astype(float)/255
back=source.astype(float)/255;back[220:875,620:1300]=material.astype(float)/255
full[220:875,620:1300]=material.astype(float)/255
alpha=np.zeros(target.shape[:2]);alpha[420:675,870:1095]=np.array(Image.open(root/'review-pass-02/06-white-icon-mask.png'))/255
region=target[425:667,870:1089];mask=np.zeros(target.shape[:2],np.uint8)
mask[425:667,870:1089]=np.uint8((region[:,:,0]>220)&(region[:,:,1]>200)&(region[:,:,2]>160))
_,labels,stats,_=cv2.connectedComponentsWithStats(mask);mask=np.uint8(labels==(1+np.argmax(stats[1:,cv2.CC_STAT_AREA])))
inside=cv2.erode(mask,np.ones((7,7),np.uint8))>0
Y,X=np.mgrid[:1080,:1920];held=((X//32+3*(Y//32))%4)==0;train=inside&~held;test=inside&held
E=target.astype(float)/255;coeff=np.array([.2126,.7152,.0722]);B=back[train];T=E[train]
original=json.loads((root/'review-pass-02/icon-trials.json').read_text())['trials']
prior=next(t for t in original if t['name']=='Reconstructed glass, sigma 0px')['parameters']
start=prior['strength_RGB']+[prior['exponent']]

def base(v,b):return 1-np.array(v[:3])*(1-b)**v[3]
def saturated(v,b):
 C=base(v,b);Y=C@coeff;dark=(1-b@coeff)**v[5]
 return np.clip(Y[...,None]+(1+v[4]*dark[...,None])*(C-Y[...,None]),0,1)
def channels(v,b):return 1-np.array(v[:3])*(1-b)**np.array(v[3:6])
models=[('Shared channel exponent',base,start,([0,0,0,.1],[1,1,1,12])),('Dark-weighted saturation',saturated,start+[.1,2.],([0,0,0,.1,0,.25],[1,1,1,12,2,6])),('Separate channel exponents',channels,start[:3]+[start[3]]*3,([0,0,0,.1,.1,.1],[1,1,1,12,12,12]))]
results=[];images=[]
dark_threshold=float(np.quantile(back[inside]@coeff,.25));dark=inside&((back@coeff)<=dark_threshold)
for name,fn,initial,bounds in models:
 fit=least_squares(lambda v:(fn(v,B)-T).ravel(),initial,bounds=bounds,max_nfev=300)
 pred=fn(fit.x,back);metrics={key:float(np.sqrt(np.mean((pred[m]-E[m])**2))*255)for key,m in [('training_rmse',train),('withheld_rmse',test),('dark_quartile_rmse',dark)]}
 metrics.update(name=name,parameters=fit.x.tolist(),parameter_count=len(fit.x))
 composite=full*(1-alpha[...,None])+pred*alpha[...,None]
 images.append((name,np.uint8(np.clip(composite,0,1)*255)))
 results.append(metrics)
box=(870,420,1095,675)
def crop(im):return np.array(Image.fromarray(im).crop(box).resize((450,510),Image.Resampling.NEAREST))
for i,(name,image)in enumerate(images,1):pair(crop(target),crop(image),('Apple',name),footer='White mask; calculated icon color. 2x nearest-neighbor view.',font_size=18).save(out/f'0{i}-icon-color.png')
# A second view includes the surrounding lens to judge strength at native scale.
sheet=Image.new('RGB',(680*4+6,695),'#14171e')
from PIL import ImageDraw,ImageFont
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);d=ImageDraw.Draw(sheet)
for i,(name,image)in enumerate([('Apple',target)]+images):
 d.text((i*682+12,10),name,font=font,fill='#edf0f7');sheet.paste(Image.fromarray(image).crop((620,220,1300,875)),(i*682,40))
sheet.save(out/'04-icon-color-context.png')
(out/'icon-color-diagnostics.json').write_text(json.dumps(dict(scope='Same frame and white mask as pass 02; no added blur or positional color gradient',formulas={'shared':'C=1-a_RGB*(1-B)^gamma','saturated':'C0=shared; Y=dot(C0,[.2126,.7152,.0722]); C=clip(Y+(1+s*(1-dot(B,weights))^k)*(C0-Y),0,1)','channels':'C=1-a_RGB*(1-B)^gamma_RGB'},limits='Encoded-RGB response approximations, not radiometric or recovered Apple shaders. More parameters can improve same-scene fit without generalization.',dark_quartile_background_luma_threshold=dark_threshold,trials=results),indent=2)+'\n')
print(json.dumps(results,indent=2),flush=True)
