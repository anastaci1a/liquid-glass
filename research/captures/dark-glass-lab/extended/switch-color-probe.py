from pathlib import Path
import json,hashlib
import cv2,numpy as np
from render import geometry
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'chromatic-rim-probe';out.mkdir(exist_ok=True)
reports=[]
for name in ['a','b']:
 c=json.loads((root/name/'case.json').read_text());T=cv2.imread(str(root/name/'target.png'))[:,:,::-1].astype(np.float64)/255
 S=cv2.imread(str(root/name/'source.png'))[:,:,::-1].astype(np.float64)/255
 observed=cv2.imread(str(root/name/'observed.png'),0)>0
 L=min(c['half']);x0,y0,x1,y1=c['crop'];Y,X=np.mgrid[y0:y1,x0:x1]
 sd,*_=geometry((X-c['center'][0])/L,(Y-c['center'][1])/L,np.array(c['half'])/L,c['radius']/L)
 mask=(sd<-2/L)&(sd>-.30);patch=T[y0:y1,x0:x1]
 color=np.array(c['background_estimate']['track_color']);direction=color-color.mean();norm=direction@direction
 def residual(rgb):
  chroma=rgb-rgb.mean(-1,keepdims=True);scale=np.maximum(chroma@direction/norm,0)
  remainder=chroma-scale[...,None]*direction
  return np.sqrt(np.mean(remainder**2,axis=-1))*255
 residuals=residual(patch);smoothed=cv2.GaussianBlur(patch.astype(np.float32),(3,3),.65)
 smooth_residual=residual(smoothed)
 sample_regions=[('upper_left',(X<c['center'][0])&(Y<c['center'][1])),('lower_left',(X<c['center'][0])&(Y>=c['center'][1])),('right',X>=c['center'][0])]
 samples=[]
 for region,where in sample_regions:
  values=np.where(mask&where,smooth_residual,-1);yy,xx=np.unravel_index(np.argmax(values),values.shape)
  rgb=smoothed[yy,xx]*255;samples.append(dict(region=region,position=[int(X[yy,xx]),int(Y[yy,xx])],rgb_3x3_filtered=rgb.tolist(),orthogonal_chroma_rmse=float(smooth_residual[yy,xx])))
 image=(np.clip(residuals/25,0,1)*255).astype(np.uint8);heat=cv2.applyColorMap(image,cv2.COLORMAP_MAGMA);heat[~mask]=np.uint8(np.rint(patch[~mask,::-1]*255))
 cv2.imwrite(str(out/f'{name}-residual.png'),heat)
 reports.append(dict(sample=name,reference=c['reference'],source_sha256=c['source_sha256'],track_rgb=(color*255).tolist(),annulus_pixels=int(mask.sum()),annulus_inner_distance_over_L=[2/L,.30],
  annulus_orthogonal_chroma_rmse_quantiles=dict(zip(['median','p90','p95','p99'],np.quantile(residuals[mask],[.5,.9,.95,.99]).tolist())),
  observed_source_orthogonal_chroma_p95=float(np.quantile(residual(S)[observed],.95)),samples=samples))
report=dict(method='Subtract RGB mean, project onto the nonnegative chroma direction of the estimated track; measure orthogonal RGB residual on a fixed measured-outline annulus. Common achromatic interpolation/blur and scalar brightness changes cannot rotate that chroma direction.',
 assumptions='Uniform estimated hidden track/white background. Channel gains, channel-separated rays, colored reflection/tint, source-estimation error and codec processing can all violate the baseline; this does not identify physical dispersion.',samples=reports)
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
