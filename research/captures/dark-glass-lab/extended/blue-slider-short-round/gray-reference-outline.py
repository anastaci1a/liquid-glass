"""Observation-only minimum-state outline. No source/optical calibration."""
import os,json,sys
from pathlib import Path
import cv2,numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from shapes import oval_minimum_radius
os.umask(0o002);D=Path('/evidence/extended/blue-slider-short-round');b=cv2.imread(str(D/'sequence/frame-07.png'))[:,:,::-1].astype(float)/255;lum=b.mean(2)
row=lum[530:570,1000:1200].mean(1);lo,hi=row.min(),row.max();ys=np.where(row<(lo+hi)/2)[0]+530;track_y=float((ys[0]+ys[-1])/2)
original=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/contour.json').read_text())['geometry'];cy=track_y+(original['center'][1]-549.5)
xs=np.arange(502,689,2);ys=[];curvature=[]
for x in xs:
 line=lum[478:531,x];k=int(np.argmin(line));assert 0<k<len(line)-1
 den=line[k-1]-2*line[k]+line[k+1];delta=.5*(line[k-1]-line[k+1])/den
 ys.append(478+k+np.clip(delta,-.5,.5));curvature.append(float(den))
ys=np.array(ys);train=np.arange(len(xs))%3!=0;oval=original['oval']
def curve(v):
 cx,a,b=v;u=(xs-cx)/a;return cy-b*np.sqrt(np.maximum(1-u*u,0))*(1+oval[0]*u*u+oval[1]*u**4)
opt=least_squares(lambda v:(curve(v)-ys)[train],[595,109,64],bounds=([590,103,55],[600,118,75]),loss='soft_l1',f_scale=.4,max_nfev=120)
err=curve(opt.x)-ys;cx,a,h=opt.x;result=dict(status='OBSERVATION_ONLY not adopted paired input',target='sequence/frame-07.png',frame=json.loads((D/'sequence/frames.json').read_text())['rows'][7],method='Original subpixel mean-RGB upper-dark-ridge proxy; original A polynomial-oval coefficients held fixed. Center-track offset transferred from A; train2/3 columns, held1/3. No lensed track endpoint or optical image fit.',geometry=dict(center=[float(cx),cy],half=[float(a),float(h)],oval=oval,radius=float(oval_minimum_radius([a,h],oval))),track_y=track_y,train_rmse=float(np.sqrt(np.mean(err[train]**2))),held_rmse=float(np.sqrt(np.mean(err[~train]**2))),all_rmse=float(np.sqrt(np.mean(err**2))),samples=dict(x=xs.tolist(),ridge=ys.tolist(),fit=curve(opt.x).tolist(),train=train.tolist(),ridge_curvature=curvature),aspect_ratio_vs_A=float((a/h)/(original['half'][0]/original['half'][1])),limits='Clamped interaction changes silhouette/possibly depth and track layout; same-element observation, not automatically matched-state validation. Upper ridge and transferred center offset are geometric proxies; bottom/right symmetry not independently established. Source remains pending, no optical trial/count.')
(D/'gray-outline.json').write_text(json.dumps(result,indent=2)+'\n');im=Image.fromarray(np.rint(b*255).astype(np.uint8));draw=ImageDraw.Draw(im);draw.line(list(zip(xs.tolist(),curve(opt.x).tolist())),fill='#ff00ff',width=1);im.crop((375,445,805,680)).resize((860,470)).save(D/'gray-outline-overlay.png');print({k:v for k,v in result.items() if k not in ['samples','frame']},flush=True)
