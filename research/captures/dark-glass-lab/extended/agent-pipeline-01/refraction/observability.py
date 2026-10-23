"""Saved four-texel photometric sensitivity, NOT a coordinate model/fit."""
from pathlib import Path
import time,json,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction';out={'rays':0,'new_images':0,'parameter_trials':0,'gradient_units':'RGB normalized per source native px; photometric D derivative per originalL (88.5px)','scope':'Raw fixed source only; frost/grade/lighting can remove information. No fit or source adoption.','cases':{}}
for key in ['a','b']:
 assert time.time()<1792655520.,'Review deadline'
 case=json.loads((P/f'inputs/{key}/case.json').read_text());x0,y0,x1,y1=case['crop'];H=y1-y0;W=x1-x0;source=cv2.imread(str(P/f'inputs/{key}/source.png'))[:,:,::-1].astype(float)/255
 q=np.load(O/'h1'/f'{key}-native-paths.npz');q2=np.load(O/'h2'/f'{key}-native-paths.npz');X=q['X'];Y=q['Y'];support=q['support']&q['complete'];a=np.floor(X[support]).astype(int);b=np.floor(Y[support]).astype(int);fx=(X[support]-a)[:,None];fy=(Y[support]-b)[:,None]
 gx=np.full((*X.shape,3),np.nan);gy=np.full_like(gx,np.nan)
 gx[support]=(source[b,a+1]-source[b,a])*(1-fy)+(source[b+1,a+1]-source[b+1,a])*fy
 gy[support]=(source[b+1,a]-source[b,a])*(1-fx)+(source[b+1,a+1]-source[b,a+1])*fx
 # F_D2-F_D1=(D2-D1)*v exactly for same surface. q native XY already pixels.
 dX=(q['X']-q2['X'])/1.5;dY=(q['Y']-q2['Y'])/1.5
 derivative=(gx*dX[...,None]+gy*dY[...,None]).reshape(H,2,W,2,3).mean((1,3));gx=gx.reshape(H,2,W,2,3).mean((1,3));gy=gy.reshape(H,2,W,2,3).mean((1,3));C=np.load(O/'h1'/f'{key}-material.npy');masks=np.load(P/f'historical-{key}-masks.npz');regions={k:masks[k] for k in ['glass','rim','held']};regions['interior']=masks['glass']&~masks['rim']
 crops=json.loads((O/'h1/protocol.json').read_text())['reference_crops']
 for name,(a,b,c,d) in crops.items():
  m=np.zeros((H,W),bool);m[max(0,b-y0):min(H,d-y0),max(0,a-x0):min(W,c-x0)]=True;regions[name]=m&masks['glass']
 records={}
 for name,m in regions.items():
  if not m.any():continue
  assert np.isfinite(derivative[m]).all()
  x=gx[m].ravel();y=gy[m].ravel();G=np.array([[x@x,x@y],[x@y,y@y]])/x.size;e=np.linalg.eigvalsh(G);mag=np.sqrt((gx[m]**2+gy[m]**2).sum(1))*255
  # Declared dimensionless scales: D1L, neutral gain.1, neutral bias.1.
  A=np.stack([derivative[m].ravel(),.1*C[m].ravel(),np.full(x.size,.1)],axis=1);gram=A.T@A/A.shape[0];norm=np.sqrt(np.diag(gram));corr=np.divide(gram,norm[:,None]*norm[None,:],out=np.zeros_like(gram),where=norm[:,None]*norm[None,:]>0)
  records[name]={'pixels':int(m.sum()),'source_gradient_RMS_levels_per_px_percentiles':np.percentile(mag,[0,10,50,90,100]).tolist(),'fraction_gradient_at_most_1level_per_px':float((mag<=1).mean()),'translation_observation_Gram_eigenvalues':e.tolist(),'D_derivative_RMS_levels_per_L':float(np.sqrt(np.mean(derivative[m]**2))*255),'D_gain_bias_scaled_Gram_eigenvalues':np.linalg.eigvalsh(gram).tolist(),'column_correlation':corr.tolist()}
 out['cases'][key]=records
out['limits']='Gradient threshold is advisory, not source-confidence or scoring mask. Raw rank is not identified Apple optics; finite frost, source registration/photometry, unknown geometry and illumination remain confounds. No failed local model projection is a fit lower bound.'
(O/'observability.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{r:{a:b for a,b in v.items() if a in ['fraction_gradient_at_most_1level_per_px','D_derivative_RMS_levels_per_L']} for r,v in d.items()} for k,d in out['cases'].items()}))
