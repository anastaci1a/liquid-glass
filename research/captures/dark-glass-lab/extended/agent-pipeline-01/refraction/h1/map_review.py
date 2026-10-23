"""Saved-map geometry analysis; no new rays and no RGB sampling."""
from pathlib import Path
import json,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h1';q=np.load(O/'a-native-paths.npz');c=json.loads((P/'inputs/a/case.json').read_text());x0,y0,x1,y1=c['crop'];X=q['X'];Y=q['Y'];H,W=X.shape;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];xx-=.25;yy-=.25
Jxx=np.gradient(X,.5,axis=1);Jxy=np.gradient(X,.5,axis=0);Jyx=np.gradient(Y,.5,axis=1);Jyy=np.gradient(Y,.5,axis=0);det=Jxx*Jyy-Jxy*Jyx
safe=cv2.erode((q['inside']&q['complete']).astype(np.uint8),np.ones((5,5),np.uint8))>0
proto=json.loads((O/'protocol.json').read_text());regions=proto['reference_crops']|{'all_regular':c['crop']};out={'rays_added':0,'RGB_samples':0,'method':'Finite differences on saved native 0.5px lattice; exclude 2-subpixel geometry boundary neighborhood. Numerical map evidence, not analytic global determinant bound.','regions':{}}
for name,(a,b,d,e) in regions.items():
 m=safe&(xx>=a)&(xx<d)&(yy>=b)&(yy<e)
 if not m.any():continue
 out['regions'][name]={'samples':int(m.sum()),'negative_det_samples':int((det[m]<0).sum()),'det_percentiles':np.percentile(det[m],[0,1,10,50,90,99,100]).tolist(),'horizontal_map_derivative_percentiles':np.percentile(Jxx[m],[0,10,50,90,100]).tolist(),'vertical_map_derivative_percentiles':np.percentile(Jyy[m],[0,10,50,90,100]).tolist(),'horizontal_displacement_px':np.percentile((X-xx)[m],[0,10,50,90,100]).tolist(),'vertical_displacement_px':np.percentile((Y-yy)[m],[0,10,50,90,100]).tolist()}
np.savez(O/'saved-map-jacobian.npz',Jxx=Jxx,Jxy=Jxy,Jyx=Jyx,Jyy=Jyy,det=det,safe=safe)
(O/'map-review.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
