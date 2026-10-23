import os,time,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.signal import find_peaks
cv2.setNumThreads(1);os.umask(2);started=time.time();P=Path('/evidence/extended/playback-pipeline-01');D=P/'horizon-audit';D.mkdir(exist_ok=True);A=Path('/evidence/apple-matches/public-settled-replay');source=np.asarray(Image.open(A/'media-source.png'),float)/255;target=np.asarray(Image.open(A/'media-target.png'),float)/255;base=np.load('/evidence/extended/geometric-playback-inferred/complete.npy')
def luma(a):return cv2.GaussianBlur(a@np.array([.2126,.7152,.0722]),(0,0),1.)
S=luma(source);T=luma(target);B=luma(base);xs=np.arange(680,1241,2);ys=np.arange(360,461);g=np.gradient(S[360:461,680:1241:2],axis=0);idx=np.argmin(g,axis=0);edges=ys[idx];strength=-g[idx,np.arange(len(xs))]*255
# Single declared source line, no robust-outlier rejection or hidden point removal.
co=np.polyfit(xs,edges,1);pred=np.polyval(co,xs);fit_error=edges-pred
angles=np.array([-145,-140,-135,-130,-125,-120,-115,-110,-105,-60,-55,-50,-45]);r=np.linspace(.70,.994,589);X=960+245*np.cos(np.deg2rad(angles))[:,None]*r;Y=542+245*np.sin(np.deg2rad(angles))[:,None]*r
rows=[];images=[('Apple',T,(0,0)),('G05',B,(620,220))];profiles={}
for name,img,(ox,oy) in images:
 vals=cv2.remap(img.astype(np.float32),(X-ox).astype(np.float32),(Y-oy).astype(np.float32),cv2.INTER_LINEAR);gg=np.gradient(vals,r,axis=1)*255/245;profiles[name]=dict(values=vals,gradients=gg)
for j,a in enumerate(angles):
 row=dict(angle=float(a),branches={})
 for name in ['Apple','G05']:
  gg=profiles[name]['gradients'][j];lst=[]
  for sign in [1,-1]:
   ii,props=find_peaks(sign*gg,prominence=.6,distance=8)
   for k,p in zip(ii,props['prominences']):lst.append(dict(r=float(r[k]),sign=sign,prominence=float(p),gradient=float(gg[k]),x=float(X[j,k]),y=float(Y[j,k])))
  row['branches'][name]=sorted(lst,key=lambda v:v['r'])
 rows.append(row)
result=dict(source_line_coefficients=co.tolist(),source_control_x=[680,1240],source_control_y=[360,460],source_fit_RMS_native_px=float(np.sqrt(np.mean(fit_error**2))),source_worst_native_px=float(abs(fit_error).max()),source_peak_min_strength=float(strength.min()),fit_all_controls_retained=True,source_curve_not_source_change=True,analysis_sigma_only=1.,all_peak_candidates=rows,wall_seconds=time.time()-started,rays=0,optical_images=0)
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');np.savez(D/'profiles.npz',x=X,y=Y,r=r,angles=angles,source_edge_x=xs,source_edge_y=edges,**{f'{n}_{k}':v for n,d in profiles.items() for k,v in d.items()})
canvas=Image.new('RGB',(1300,13*110+50),'white');draw=ImageDraw.Draw(canvas)
for j,a in enumerate(angles):
 oy=50+j*110;draw.text((2,oy),str(a),fill='black')
 for name,color in [('Apple','red'),('G05','blue')]:
  gg=profiles[name]['gradients'][j];draw.line([(60+k*2.,oy+50-float(np.clip(v,-8,8))*5) for k,v in enumerate(gg)],fill=color,width=1)
canvas.save(D/'all-branch-gradients.png');print(json.dumps({k:v for k,v in result.items() if k!='all_peak_candidates'}))
