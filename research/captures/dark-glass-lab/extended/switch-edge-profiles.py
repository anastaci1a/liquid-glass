"""Vertical RGB transition measurements; not an identified optical PSF."""
from pathlib import Path
import json
import cv2,numpy as np
from scipy.optimize import least_squares
from scipy.special import ndtr
from PIL import Image,ImageDraw,ImageFont
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'edge-diffusion-analysis';out.mkdir(exist_ok=True);records=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);canvas=Image.new('RGB',(1500,1060),'#14171e');draw=ImageDraw.Draw(canvas)
for column,name in enumerate(['a','b']):
 case=json.loads((root/name/'case.json').read_text());T=cv2.imread(str(root/name/'target.png'))[:,:,::-1].astype(float)/255;cx,cy=case['center'];hx,hy=case['half'];L=min(case['half'])
 for row,fraction in enumerate([.25,.45]):
  x=round(cx-hx+2*hx*fraction);ys=np.arange(round(cy+.48*hy),round(cy+.90*hy)+1);profile=T[ys,x-1:x+2].mean(1);fits=[]
  for c in range(3):
   values=profile[:,c];a=float(values[:5].mean());upper=float(values[-5:].mean());middle=float(ys[np.argmin(abs(values-(a+upper)*.5))]);v0=[np.clip(a,.001,.999),np.clip((upper-a)/max(1-a,1e-3),.001,.999),middle,5.]
   def f(v):return v[0]+(1-v[0])*v[1]*ndtr((ys-v[2])/v[3])
   fit=least_squares(lambda v:f(v)-values,v0,bounds=([0,0,ys[0],.35],[1,1,ys[-1],35]),loss='soft_l1',f_scale=.02);pred=f(fit.x);fits.append(dict(channel='RGB'[c],center_native_px=float(fit.x[2]),sigma_native_px=float(fit.x[3]),center_over_L=float((fit.x[2]-cy)/L),sigma_over_L=float(fit.x[3]/L),rmse_native_rgb=float(np.sqrt(np.mean((pred-values)**2))*255),endpoint_span_native_rgb=float((1-fit.x[0])*fit.x[1]*255),curve=pred.tolist()))
  record=dict(sample=name,position_from_left_fraction=fraction,x_native=x,y_native=ys.tolist(),rgb_native=(profile*255).tolist(),fits=fits);records.append(record)
  left=column*750+70;top=row*530+80;W=620;H=330;draw.text((column*750+20,row*530+12),f'{name.upper()} · vertical profile at {fraction:.0%} of lens width',font=font,fill='#f0f2f7');draw.text((column*750+20,row*530+40),'Solid: source pixels   Dotted: monotone step fit',font=font,fill='#adb4c0')
  for val in [0,64,128,192,255]:
   y=top+H-val/255*H;draw.line((left,y,left+W,y),fill='#333743');draw.text((left-42,y-10),str(val),font=font,fill='#adb4c0')
  for c,color in enumerate(['#fc6b79','#75d493','#6aaeff']):
   points=[(left+(i/(len(ys)-1))*W,top+H-profile[i,c]*H) for i in range(len(ys))];draw.line(points,fill=color,width=3)
   pred=fits[c]['curve'];points=[(left+(i/(len(ys)-1))*W,top+H-pred[i]*H) for i in range(len(ys))]
   for k in range(0,len(points)-1,3):draw.line(points[k:k+2],fill=color,width=2)
  for i in [0,len(ys)//2,len(ys)-1]:draw.text((left+i/(len(ys)-1)*W-20,top+H+8),str(ys[i]),font=font,fill='#adb4c0')
  draw.text((left,top+H+38),'Vertical coordinate in native reference pixels',font=font,fill='#adb4c0')
  draw.text((left,top+H+66),'R/G/B fitted widths: '+', '.join(f"{z['sigma_native_px']:.2f}px" for z in fits),font=font,fill='#adb4c0')
canvas.save(out/'vertical-rgb-profiles.png');report=dict(method='Three-column mean of unmodified native RGB. Independent bounded monotone Gaussian-step fits, soft-L1 residual; no interpretation as recovered PSF.',records=records,limits='Curved/multiple refracted edges, colored lighting, source estimates and video sampling confound widths/centroids. Small endpoint span or large fit residual invalidates a clean blur-width reading. One vertical profile cannot establish a two-dimensional dispersion direction.')
(out/'vertical-rgb-profiles.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([dict(sample=r['sample'],fraction=r['position_from_left_fraction'],fits=[{k:z[k] for k in ['channel','center_native_px','sigma_native_px','rmse_native_rgb','endpoint_span_native_rgb']} for z in r['fits']]) for r in records]))
