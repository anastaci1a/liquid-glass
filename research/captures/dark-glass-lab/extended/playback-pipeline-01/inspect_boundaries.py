import json,os,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from scipy.signal import find_peaks
os.umask(2);cv2.setNumThreads(1)
D=Path('/evidence/extended/playback-pipeline-01');A=Path('/evidence/apple-matches/public-settled-replay');G=Path('/evidence/extended/geometric-playback-inferred')
target=np.asarray(Image.open(A/'media-target.png'),np.float32)/255;base=np.load(G/'complete.npy');source=np.asarray(Image.open(A/'media-source.png'),np.float32)/255
# Analysis-only smoothing does not alter any render or proposed optical material.
L=245.;cx=960.;cy=542.;angles=np.arange(-180,180,10.);r=np.linspace(.65,.98,325);x=cx+L*np.cos(np.deg2rad(angles))[:,None]*r;y=cy+L*np.sin(np.deg2rad(angles))[:,None]*r
profiles={};rows=[]
for name,img,origin in [('Apple',target,(0,0)),('G05',base,(620,220))]:
 lum=img@np.array([.2126,.7152,.0722],np.float32);lum=cv2.GaussianBlur(lum,(0,0),1.0)
 values=cv2.remap(lum,(x-origin[0]).astype(np.float32),(y-origin[1]).astype(np.float32),cv2.INTER_LINEAR);deriv=np.gradient(values,r,axis=1)/L*255
 profiles[name]=(values,deriv)
for j,a in enumerate(angles):
 row={'angle_degrees':float(a),'Apple_peaks':[],'G05_peaks':[]}
 for name in ['Apple','G05']:
  g=profiles[name][1][j];idx,prop=find_peaks(abs(g),prominence=.35,distance=10)
  row[name+'_peaks']=[{'r':float(r[k]),'x':float(x[j,k]),'y':float(y[j,k]),'signed_levels_per_px':float(g[k]),'prominence':float(p)} for k,p in zip(idx,prop['prominences'])]
 rows.append(row)
# Fixed inspection cohort, not a fit/scoring-mask change: keep all angles and all peaks.
np.savez(D/'inspection-profiles.npz',r=r,angles=angles,x=x,y=y,Apple=profiles['Apple'][0],G05=profiles['G05'][0],Apple_derivative=profiles['Apple'][1],G05_derivative=profiles['G05'][1])
(D/'inspection.json').write_text(json.dumps({'analysis_sigma_native':1.,'r_interval':[.65,.98],'all_angles_retained':True,'not_an_optical_blur':True,'rows':rows},indent=2)+'\n')
canvas=Image.new('RGB',(1300,36*65+50),'white');d=ImageDraw.Draw(canvas)
for j,a in enumerate(angles):
 oy=50+j*65;d.text((2,oy),str(int(a)),fill='black')
 for name,col in [('Apple','red'),('G05','blue')]:
  yy=profiles[name][1][j];pts=[(70+k*3.5,oy+30-float(np.clip(v,-5,5))*5) for k,v in enumerate(yy)];d.line(pts,fill=col,width=1)
canvas.save(D/'inspection-profile-gradients.png')
print(json.dumps({'angle_count':len(angles),'peak_counts':{n:sum(len(z[n+'_peaks']) for z in rows) for n in ['Apple','G05']},'purpose':'Identify distinguishable signed boundary features; no fitted shape or new body render.'}))
