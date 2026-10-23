"""Source-only exposed-icon calibration: unchanged vectors, shared tint/PSF.
No lensed target pixels, B halo, per-pixel residual, or altered icon geometry.
"""
import os,json,hashlib
from pathlib import Path
from io import BytesIO
import cv2,numpy as np,cairosvg
from PIL import Image,ImageDraw
from scipy.optimize import minimize
os.umask(0o002);cv2.setNumThreads(1)
D=Path('/evidence/extended/blue-slider-short-round');O=D/'unlensed-vector-calibration';O.mkdir(exist_ok=False)
A=np.asarray(Image.open(D/'sequence/frame-00.png').convert('RGB')).astype(float)/255
P=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/slider-source.png').convert('RGB')).astype(float)/255
previous=json.loads((D/'icon-background-online/result.json').read_text());cases=[]
for row,roi in zip(previous['icons'],[(420,510,530,590),(1420,510,1540,590)]):
 name=row['icon'];svg=(D/f'{name}-online-outline.svg').read_bytes();alpha=np.asarray(Image.open(BytesIO(cairosvg.svg2png(bytestring=svg,output_width=1000))).convert('RGBA'))[:,:,3].astype(np.float32)/255
 x0,y0,x1,y1=roi;Y,X=np.mgrid[y0:y1:.25,x0:x1:.25];X=X-.375;Y=Y-.375;yy,xx=np.mgrid[y0:y1,x0:x1];train=(xx//4+3*(yy//4))%3!=0
 p=row['A_identity_check']['placement'];cases.append(dict(name=name,roi=roi,alpha=alpha,ratio=alpha.shape[0]/alpha.shape[1],X=X,Y=Y,train=train,target=A[y0:y1,x0:x1],bg=P[y0:y1,x0:x1],pose=[p[0],p[1],p[2]-p[0]],svg_sha256=hashlib.sha256(svg).hexdigest()))
def coverage(c,v,sigma):
 left,top,w=v;h=w*c['ratio'];a=c['alpha'];u=((c['X']-left+.5)*a.shape[1]/w-.5).astype(np.float32);z=((c['Y']-top+.5)*a.shape[0]/h-.5).astype(np.float32)
 fine=cv2.remap(a,u,z,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
 if sigma>1e-5:
  r=int(np.ceil(3*sigma*4));fine=cv2.GaussianBlur(fine,(2*r+1,2*r+1),sigma*4,borderType=cv2.BORDER_CONSTANT)
 x0,y0,x1,y1=c['roi'];return fine.reshape(y1-y0,4,x1-x0,4).mean((1,3))
ledger=[]
def evaluate(v,record=True):
 alphas=[coverage(c,v[i*3:i*3+3],v[-1]) for i,c in enumerate(cases)]
 # Ordinary shared RGB glyph tint, linear least squares from TRAIN exposed pixels only.
 num=np.zeros(3);den=0.
 for c,a in zip(cases,alphas):
  m=c['train'];num+=np.sum(a[m,None]*(c['target'][m]-c['bg'][m]*(1-a[m,None])),axis=0);den+=np.sum(a[m]**2)
 color=np.clip(num/den,0,1);pred=[c['bg']*(1-a[...,None])+color*a[...,None] for c,a in zip(cases,alphas)]
 loss=sum(np.sum(((p-c['target'])[c['train']])**2) for p,c in zip(pred,cases))/sum(3*c['train'].sum() for c in cases)
 if record:ledger.append(dict(parameters=np.asarray(v).tolist(),color_rgb=color.tolist(),train_mse=float(loss)))
 return loss,color,pred,alphas
initial=np.array([q for c in cases for q in c['pose']]+[.5]);bounds=[]
for c in cases:
 x,y,w=c['pose'];bounds.extend([(x-1.5,x+1.5),(y-1.5,y+1.5),(w-2,w+2)])
bounds.append((0,1.5))
opt=minimize(lambda v:evaluate(v)[0],initial,method='Powell',bounds=bounds,options=dict(maxfev=360,xtol=.001,ftol=1e-8))
loss,color,pred,aa=evaluate(opt.x,False);rows=[];canvas=Image.new('RGB',(960,690),'white');draw=ImageDraw.Draw(canvas)
for i,(c,p,a) in enumerate(zip(cases,pred,aa)):
 row=dict(icon=c['name'],pose=opt.x[i*3:i*3+3].tolist(),vector_sha256=c['svg_sha256'],train_rgb_rmse=float(np.sqrt(np.mean(((p-c['target'])[c['train']])**2))*255),held_rgb_rmse=float(np.sqrt(np.mean(((p-c['target'])[~c['train']])**2))*255));rows.append(row)
 draw.text((5,i*345+5),'Unlensed Apple / unchanged vector + shared tint and source PSF',fill='black')
 for j,image in enumerate([c['target'],p]):canvas.paste(Image.fromarray(np.rint(np.clip(image,0,1)*255).astype(np.uint8)).resize((480,320)),(j*480,i*345+25))
 np.save(O/f'{c["name"]}-coverage.npy',a)
canvas.save(O/'identity-comparison.png')
result=dict(status='Source proposal only, no B source or optical epoch adoption',color_rgb=color.tolist(),source_psf_sigma_native_px=float(opt.x[-1]),parameters=opt.x.tolist(),bounds=bounds,observations=rows,evaluations=int(opt.nfev),solver_success=bool(opt.success),solver_message=str(opt.message),limits='Shared RGB tint and ordinary isotropic source PSF calibrated ONLY against unlensed A training blocks. Held-out blocks not used for pose/color/PSF. Unknown camera encoding/PSF/background model remain; no claim of exact Apple font configuration. B halo excluded entirely. Vectors unchanged, only uniformscale/translation; not an optical pass.')
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n');(O/'evaluations.json').write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps(result),flush=True)
