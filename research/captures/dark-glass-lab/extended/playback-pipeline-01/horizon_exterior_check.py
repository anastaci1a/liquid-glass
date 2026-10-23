from pathlib import Path
import json,numpy as np,cv2
from PIL import Image
D=Path('/evidence/extended/playback-pipeline-01/horizon-audit');A=Path('/evidence/apple-matches/public-settled-replay');rows=[]
for left,right in [(620,700),(1240,1300)]:
 xs=np.arange(left,right+1);ys=np.arange(360,461);values={}
 for name in ['source','target']:
  im=np.asarray(Image.open(A/f'media-{name}.png'),float)/255;lum=cv2.GaussianBlur(im@np.array([.2126,.7152,.0722]),(0,0),1.);g=np.gradient(lum[360:461,left:right+1],axis=0);i=np.argmin(g,axis=0);values[name]=ys[i]
 # Exposed only: independent geometric disk clearance over every selected peak.
 clear=np.minimum(np.hypot(xs-960,values['source']-542),np.hypot(xs-960,values['target']-542))-245;assert clear.min()>20
 delta=values['target']-values['source'];rows.append(dict(x=[left,right],count=len(xs),minimum_circle_clearance=float(clear.min()),target_minus_source_y_mean=float(delta.mean()),RMS_px=float(np.sqrt(np.mean(delta**2))),min_max=[int(delta.min()),int(delta.max())],source_y=values['source'].tolist(),target_y=values['target'].tolist()))
(D/'unlensed-control.json').write_text(json.dumps(dict(rows=rows,rays=0,new_source_fit=0,no_registration_change=True,scope='Analysis-only integer-grid luma-gradient maxima with same1px analysis filter; pixel phase/PSF/codec uncertainty not separated.'),indent=2)+'\n');print(json.dumps(rows))
