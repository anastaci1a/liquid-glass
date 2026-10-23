"""Remaining original authority only: same H, predicted crown coverage may differ."""
from pathlib import Path
import sys,json,time
import numpy as np
from PIL import Image
P=Path('/evidence/extended/geometric-toolbar-round/heldout-navigation-06');sys.path.insert(0,'/evidence/extended/geometric-toolbar-round/harmonic-05/code')
from harmonic_crowned_back import HarmonicCrownedBack
from geometric_optics import trace_flat_front_orthographic
root=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile/b');c=json.loads((root/'case.json').read_text());old=json.loads((P/'input-hash-check.json').read_text());p=old['parameters'];known=np.asarray(Image.open(root/'known.png'))
L=min(c['half']);half=np.array(c['half'])/L+[p['half_x_delta'],p['half_y_delta']];center=np.array(c['center'])+L*np.array([p['shape_dx'],p['shape_dy']]);s=HarmonicCrownedBack(half=tuple(half));x0,y0,x1,y1=c['crop'];H,W=y1-y0,x1-x0
# Original scoring masks remain based on original case, as Study.__init__.
yy,xx=np.mgrid[y0:y1,x0:x1];xx0=(xx-c['center'][0])/L;yy0=(yy-c['center'][1])/L;hh=np.array(c['half'])/L;rad=c['radius']/L
qx=abs(xx0)-hh[0]+rad;qy=abs(yy0)-hh[1]+rad;sd=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-rad
scored=(sd<-1/L)&(known[y0:y1,x0:x1]>0)
for a,b,d,e in c['foreground']:scored|=(xx>=a)&(xx<d)&(yy>=b)&(yy<e)
r={'status':'RUNNING_REMAINING_ORIGINAL_AUTHORITY','deadline':'2026-10-22T04:44:28.894Z','rays':0,'required':0,'images':0,'reference_masks_case_pose_unchanged':True,'predicted_coverage_allowed_to_differ':True,'source_RGB_sampled':False}
for top in range(0,H,12):
 if time.time()>1792644268.894:r['status']='STOP_ORIGINAL_DEADLINE';break
 bot=min(top+12,H);iy,ix=np.mgrid[top*4:bot*4,:W*4];X=x0+(ix+.5)/4-.5;Y=y0+(iy+.5)/4-.5;o=trace_flat_front_orthographic(s,(X-center[0])/L,(Y-center[1])/L,1.5,2.)
 u=o['X']*L+center[0];v=o['Y']*L+center[1];required=o['inside']|np.repeat(np.repeat(scored[top:bot],4,0),4,1);r['rays']+=u.size;r['required']+=int(required.sum())
 bad=required&~o['complete']
 if bad.any():r['status']='STOP_UNRESOLVED_REQUIRED_PATH';r['unsupported']=int(bad.sum());break
 ax=np.floor(u).astype(int);ay=np.floor(v).astype(int);bounds=(ax>=0)&(ay>=0)&(ax+1<known.shape[1])&(ay+1<known.shape[0])
 if (required&~bounds).any():r['status']='STOP_SOURCE_BOUNDS';break
 # No clamping; indices are checked before any confidence lookup.
 if not bounds.all():r['status']='STOP_UNSUPPORTED_CROP_BOUNDS';break
 conf=np.minimum.reduce([known[ay,ax],known[ay,ax+1],known[ay+1,ax],known[ay+1,ax+1]])
 bad=required&(conf!=255)
 if bad.any():
  a,b=np.argwhere(bad)[0];r.update(status='STOP_UNDEFINED_REQUIRED_SOURCE',unsupported_in_first_failing_tile=int(bad.sum()),tile_native_rows=[top,bot],witness={'output_XY':[float(X[a,b]),float(Y[a,b])],'source_XY':[float(u[a,b]),float(v[a,b])],'source_floor':[int(ax[a,b]),int(ay[a,b])],'four_known_values':[int(known[ay[a,b]+dy,ax[a,b]+dx]) for dx,dy in [(0,0),(1,0),(0,1),(1,1)]],'whole_predicted':bool(o['inside'][a,b]),'original_scored':bool(np.repeat(np.repeat(scored[top:bot],4,0),4,1)[a,b])});break
else:r['status']='PREFLIGHT_COMPLETE_NO_SAFE_IMAGE_DRIVER_WITHIN_REMAINING_TIME'
r['finished_unix']=time.time();(P/'remaining-preflight.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
