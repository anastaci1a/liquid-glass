"""Private review crops and white-mask appearance trials. No copied icon RGB."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.optimize import least_squares
from scipy.ndimage import distance_transform_edt
from reproduce import CASES,frame
from publish import read,compose,pair

root=Path('/evidence/apple-matches');fits=root/'curvature-contour';out=root/'review-pass-02';out.mkdir(exist_ok=True)
case=CASES['media'];target=read(fits/'media-target.png');source=read(fits/'media-source.png')
material=read(fits/'media-exponential.png');rendered=compose('media',case,target,material,fits)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

# All three groups on one sheet. The upper-right group includes both crossings.
groups=[('Bottom-left',(690,570,910,810)),('Top-left',(690,290,910,530)),('Upper-right: both crossings',(1025,320,1245,560))]
sheet=Image.new('RGB',(882,3*(480+64)),'#14171e');draw=ImageDraw.Draw(sheet)
for i,(label,box) in enumerate(groups):
 top=i*544;draw.text((12,top+8),label+' | Apple',font=font,fill='#edf0f7');draw.text((454,top+8),'Current reconstruction',font=font,fill='#edf0f7')
 draw.text((12,top+32),str(box)+'; 2x nearest-neighbor enlargement',font=small,fill='#b3becd')
 sheet.paste(Image.fromarray(target).crop(box).resize((440,480),Image.Resampling.NEAREST),(0,top+64))
 sheet.paste(Image.fromarray(rendered).crop(box).resize((440,480),Image.Resampling.NEAREST),(442,top+64))
sheet.save(out/'01-playback-rim-crops.png')

regular=read(fits/'regular-target.png');regular_material=read(fits/'regular-tensor.png')
regular_render=compose('regular',CASES['regular'],regular,regular_material,fits)
box=(1040,370,1210,500)
a=np.array(Image.fromarray(regular).crop(box).resize((680,520),Image.Resampling.NEAREST))
b=np.array(Image.fromarray(regular_render).crop(box).resize((680,520),Image.Resampling.NEAREST))
pair(a,b,('Apple: final d in around','Current image-map reconstruction'),footer='4x nearest-neighbor enlargement; same pass-01 fit, not a new curvature fit.',font_size=18).save(out/'07-toolbar-d-crop.png')

# Expose the actual source baseline; no reference lens or icon in the input.
original,meta=frame(root,'219',180)
Image.fromarray(np.uint8(np.rint(original*255))).save(out/'02-playback-uncovered-frame.png')
Image.fromarray(source).save(out/'03-playback-registered-background.png')
pair(target[220:875,620:1300],source[220:875,620:1300],('Apple lens scene','Registered uncovered background'),font_size=16).save(out/'04-playback-background-comparison.png')

# Reuse the silhouette only; its sampled RGB is discarded. Feather about one
# native pixel with a 0.45px Gaussian, then shade this same white mask per trial.
selected=np.zeros(target.shape[:2],np.uint8);region=target[425:667,870:1089]
selected[425:667,870:1089]=np.uint8((region[:,:,0]>220)&(region[:,:,1]>200)&(region[:,:,2]>160))
count,labels,stats,_=cv2.connectedComponentsWithStats(selected)
mask=(labels==(1+np.argmax(stats[1:,cv2.CC_STAT_AREA]))).astype(np.float32)
interior=cv2.erode(mask,np.ones((7,7),np.uint8))>0
Y,X=np.mgrid[:1080,:1920];held=((X//32+3*(Y//32))%4)==0
train=interior&~held;test=interior&held
expected=target.astype(float)/255
backdrop=source.astype(float)/255
glass=backdrop.copy();glass[220:875,620:1300]=material.astype(float)/255
base=rendered.astype(float)/255
# Remove the copied icon before compositing the replacement white mask.
base[220:875,620:1300]=glass[220:875,620:1300]
# Recover edge coverage only from the reference fringe. Nearest interior RGB is
# used to estimate alpha, never as the trial's icon color. The RGB interior of
# every candidate comes solely from its stated white-mask appearance equation.
nearest=distance_transform_edt(~interior,return_distances=False,return_indices=True)
foreground=expected[nearest[0],nearest[1]]
delta=foreground-glass
alpha=np.clip(np.sum((expected-glass)*delta,axis=2)/np.maximum(np.sum(delta*delta,axis=2),1e-8),0,1)
alpha*=cv2.dilate(mask,np.ones((5,5),np.uint8))
alpha[interior]=1
alpha=cv2.GaussianBlur(alpha,(0,0),.35)
trials=[]

def record(name,prediction,parameters,kind):
 metrics={k:float(np.sqrt(np.mean((prediction[m]-expected[m])**2))*255)for k,m in [('training_rmse',train),('withheld_rmse',test)]}
 trials.append(dict(name=name,parameters=parameters,kind=kind,**metrics))
 color=base*(1-alpha[...,None])+prediction*alpha[...,None]
 return np.uint8(np.clip(color,0,1)*255)

white=record('White mask',np.ones_like(base),{},'constant white')
constant=np.mean(expected[train],axis=0);flat=record('Constant RGB',np.broadcast_to(constant,base.shape),dict(color=constant.tolist()),'constant color control')
variants=[]
for input_name,input_image in [('Uncovered background',backdrop),('Reconstructed glass',glass)]:
 for sigma in [0,3,12,24,48]:
  B=cv2.GaussianBlur(input_image,(0,0),sigma)if sigma else input_image
  bt=B[train];yt=expected[train]
  def predict(p,b):return 1-np.array(p[:3])*(1-b)**p[3]
  result=least_squares(lambda p:(predict(p,bt)-yt).ravel(),[.05,.2,.3,1.],bounds=([0,0,0,.1],[1,1,1,12]),max_nfev=150)
  p=result.x;name=f'{input_name}, sigma {sigma:g}px'
  image=record(name,predict(p,B),dict(strength_RGB=p[:3].tolist(),exponent=float(p[3]),blur_sigma=sigma),input_name)
  variants.append((trials[-1]['training_rmse'],name,image))
variants.sort(key=lambda x:x[0])
# Compare white/constant controls and two best fits. Selection uses training only.
box=(870,420,1095,675);W,H=450,510
tile=Image.new('RGB',(5*W+8,H+78),'#14171e');d=ImageDraw.Draw(tile)
items=[('Apple',target),('White mask',white),('Constant RGB',flat)]+[(name,img)for _,name,img in variants[:2]]
for index,(name,img)in enumerate(items):
 x=index*(W+2);d.text((x+8,8),name.split(',')[0],font=small,fill='#edf0f7')
 if ','in name:d.text((x+8,30),name.split(',')[1].strip(),font=small,fill='#b3becd')
 tile.paste(Image.fromarray(img).crop(box).resize((W,H),Image.Resampling.NEAREST),(x,78))
tile.save(out/'05-white-icon-shading-trials.png')
Image.fromarray(np.uint8(alpha*255)).crop(box).save(out/'06-white-icon-mask.png')
(out/'icon-trials.json').write_text(json.dumps(dict(formula='C=1-strength_RGB*(1-GaussianBlur(B,sigma))**exponent',mask='Reference silhouette and edge coverage only; no copied RGB interior; 0.35px Gaussian opacity feather',selection='Lowest training error; 32px spatial blocks withheld; same frame, not independent validation',limits='Encoded RGB; fitted nuisance color response, not an identified Apple shader. The underlying glass is an imperfect reconstruction.',trials=trials),indent=2)+'\n')
print(json.dumps(sorted(trials,key=lambda t:t['training_rmse']),indent=2),flush=True)
