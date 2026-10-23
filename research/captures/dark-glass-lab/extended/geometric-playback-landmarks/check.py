from pathlib import Path
import json,time
import numpy as np,cv2
from PIL import Image,ImageDraw
started=time.time();D=Path('/evidence/extended/geometric-playback-landmarks');x0,y0,x1,y1=620,220,1300,875
ref=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),float)/255;C=np.load('/evidence/extended/geometric-playback-inferred/complete.npy');X=np.arange(1090,1151);Y=np.arange(390,451);yy,xx=np.meshgrid(Y,X,indexing='ij');allowed=np.hypot(xx-960,yy-542)<245-8;rows=[]
for sigma in [.5,1,1.5]:
 traces={}
 for name,im in [('reference',ref[y0:y1,x0:x1]),('geometric',C)]:
  L=im@np.array([.2126,.7152,.0722]);L=cv2.GaussianBlur(L,(0,0),sigma);g=-np.gradient(L,axis=0);roi=g[np.ix_(Y-y0,X-x0)];masked=np.where(allowed,roi,-np.inf);idx=np.argmax(masked,axis=0);positions=[];margins=[];boundary=[]
  for j,k in enumerate(idx):
   boundary.append(bool(k==0 or k==len(Y)-1 or (k>0 and not allowed[k-1,j]) or (k<len(Y)-1 and not allowed[k+1,j])))
   step=0
   if 0<k<len(Y)-1 and not boundary[-1]:
    a,b,c=roi[k-1:k+2,j];den=a-2*b+c
    if den!=0:step=float(np.clip(.5*(a-c)/den,-.5,.5))
   positions.append(float(Y[k]+step));other=masked[:,j].copy();other[max(0,k-3):min(len(Y),k+4)]=-np.inf;margins.append(float(roi[k,j]-np.max(other)))
  traces[name]=dict(y=positions,boundary=boundary,derivative_prominence=margins)
 diff=np.array(traces['geometric']['y'])-traces['reference']['y'];rows.append(dict(sigma=sigma,columns=X.tolist(),traces=traces,delta_y=diff.tolist(),RMS_pixels=float(np.sqrt(np.mean(diff**2))),median_abs_pixels=float(np.median(abs(diff))),max_abs_pixels=float(abs(diff).max())))
result=dict(ROI=[1090,390,1151,451],rows=rows,wall_seconds=time.time()-started,new_rays=0,new_candidates=0,fits=0,limits='Strongest derivative may be a competing image/illumination edge; all columns and ambiguity/boundary flags retained. Analysis smoothing is not render blur.')
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps([dict(sigma=r['sigma'],RMS=r['RMS_pixels'],median=r['median_abs_pixels'],max=r['max_abs_pixels'],boundary_ref=sum(r['traces']['reference']['boundary']),boundary_new=sum(r['traces']['geometric']['boundary'])) for r in rows]))
