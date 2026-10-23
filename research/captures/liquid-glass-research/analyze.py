"""Private Apple asset analysis; Python 3 + numpy + opencv-python-headless.
No input timing inference. Coordinates and displacement are decoded image pixels.
Run after extracting native frames with ffmpeg -vsync 0 (see report).
"""
from pathlib import Path
import json, math
import cv2
import numpy as np
P=Path(__file__).resolve().parent

def read(n): return cv2.imread(str(P/'morph'/f'{n+1:04d}.png')).astype(np.float32)
a=read(0); h,w=a.shape[:2]; yy,xx=np.mgrid[:h,:w]
# Exclude union of possible material footprints and their shadows.
exterior=np.ones((h,w),np.uint8)
exterior[15:215,75:530]=0; exterior[240:360,205:410]=0
# Frame-0 central glass must not enter any source patch, including search margin.
source_clear=np.hypot(xx-305,yy-114)>102
records=[]; registration=[]
for n in [65,80,95,225,240,255]:
 b=read(n); ag=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY); bg=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
 warp=np.eye(2,3,dtype=np.float32)
 cc,warp=cv2.findTransformECC(ag,bg,warp,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,100,1e-6),exterior,5)
 # ECC maps source reference coordinates to target; pull target into reference.
 b=cv2.warpAffine(b,warp,(w,h),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
 bg=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
 registration.append(dict(frame=n,translation=warp[:,2].tolist(),ecc=cc,exterior_mae=float(np.abs(a-b)[exterior>0].mean())))
 sigmas=[0,.5,1,1.5,2,3,4,6]
 sources=[ag if s==0 else cv2.GaussianBlur(ag,(0,0),s) for s in sigmas]
 # 21px target patches and ±8px inverse-coordinate search; compare same grid on repeats.
 half=10; search=8
 for cx in [181,429]:
  for y in range(48,187,12):
   for x in range(cx-66,cx+67,12):
    r=math.hypot(x-cx,y-114)
    if r>65: continue
    ys=slice(y-half,y+half+1); xs=slice(x-half,x+half+1)
    # Entire patch and search aperture must be outside original glass.
    if not source_clear[y-half-search:y+half+search+1,x-half-search:x+half+search+1].all(): continue
    patch=bg[ys,xs]
    if patch.min()<65 or patch.std()<2: continue # glyph/flat rejection
    grad=cv2.cornerMinEigenVal(patch,5,3)
    eig=float(np.mean(grad))
    if eig<.3: continue
    best=None
    for sigma,src in zip(sigmas,sources):
     area=src[y-half-search:y+half+search+1,x-half-search:x+half+search+1]
     corr=cv2.matchTemplate(area,patch,cv2.TM_CCOEFF_NORMED)
     _,score,_,(ix,iy)=cv2.minMaxLoc(corr)
     if ix==0 or iy==0 or ix==search*2 or iy==search*2: continue
     offsets=[]
     for fm,f0,fp in [(corr[iy,ix-1],corr[iy,ix],corr[iy,ix+1]),(corr[iy-1,ix],corr[iy,ix],corr[iy+1,ix])]:
      den=fm-2*f0+fp; offsets.append(float(.5*(fm-fp)/den) if abs(den)>1e-8 else 0.)
     dx=ix-search+offsets[0];dy=iy-search+offsets[1]
     if best is None or score>best['correlation']:
      best=dict(frame=n,center=[cx,114],point=[x,y],radius=r,inset=83-r,sigma=sigma,dx=dx,dy=dy,correlation=score,eigenvalue=eig,identity_correlation=float(corr[search,search]))
    if best and best['correlation']>.92: records.append(best)
(P/'measurements.json').write_text(json.dumps(dict(registration=registration,patches=records),indent=2))
print('REGISTRATION',json.dumps(registration))
print('PATCHES',len(records))
for n in [65,80,95,225,240,255]:
 rows=[r for r in records if r['frame']==n];print(n,[(r['point'],round(r['sigma'],2),round(r['dx'],2),round(r['dy'],2),round(r['correlation'],3)) for r in rows])
# Draw all tested patches and inverse-coordinate displacement arrows for inspection.
out=read(80).astype(np.uint8)
for r in records:
 if r['frame']!=80:continue
 x,y=r['point'];cv2.rectangle(out,(x-10,y-10),(x+10,y+10),(0,0,255),1);cv2.arrowedLine(out,(x,y),(round(x+5*r['dx']),round(y+5*r['dy'])),(0,0,255),1)
cv2.imwrite(str(P/'patches.png'),out)
