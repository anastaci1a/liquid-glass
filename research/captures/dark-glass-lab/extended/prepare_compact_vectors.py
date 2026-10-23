"""Reuse frozen expanded-player vectors; calibrate compact pose/color only."""
from pathlib import Path
import json,hashlib,copy,xml.etree.ElementTree as ET,shutil
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from vector_foreground import coverage
root=Path('/evidence/extended');r=root/'music-mini-compact-vector'
assert not r.exists(),'Do not overwrite completed experiments'
r.mkdir();prior=root/'music-mini-compact';expanded=root/'music-mini-expanded-vector'
for name in ['source.png','target.png','known.png']:shutil.copyfile(prior/name,r/name)
old=json.loads((prior/'accepted.json').read_text());(r/'accepted.json').write_text(json.dumps(old,indent=2)+'\n')
config=json.loads((prior/'case.json').read_text());config['id']=r.name
config['continuation']=dict(baseline='music-mini-compact',additional_single_pass_minimum=10,paired_pass_minimum=20)
shadow_reference=json.loads((prior/'pass-12/record.json').read_text())['current']['parameters']
config['exterior_reference_shape']={k:shadow_reference.get(k,0) for k in ['shape_dx','shape_dy','half_x_delta','half_y_delta','radius_delta','cap_join_width']}
(r/'case.json').write_text(json.dumps(config,indent=2)+'\n');s=Study(r);Bfull=s.render(old['parameters'],np.array(old['material']))
from extended_shadow import shadow
*_,(sd,_,_)=s.shape(s.x,s.y,config['exterior_reference_shape'])
x0,y0,x1,y1=s.crop;known=cv2.imread(str(r/'known.png'),0)[y0:y1,x0:x1]>0;mask=(sd>1.5/s.L)&(sd<.20)&known
X=s.x*s.L+s.case['center'][0];Y=s.y*s.L+s.case['center'][1]
for a,b,c,d in config.get('exterior_exclusions',[]):mask&=~((X>=a)&(X<=c)&(Y>=b)&(Y<=d))
alpha=shadow(s,old['parameters'],s.x[mask],s.y[mask]);error=s.source[y0:y1,x0:x1][mask]*(1-alpha[...,None])-s.target_crop[mask]
exterior=float(np.sqrt(np.mean(error**2))*255);assert int(mask.sum())==old['scores']['exterior']['pixels']
assert abs(exterior-old['scores']['exterior']['rmse'])<1e-6,('Stale exterior baseline',exterior)
print('PASS original fixed exterior region',mask.sum(),exterior,flush=True)
shared=json.loads((expanded/'case.json').read_text());shutil.copyfile(expanded/'jupiter.jpg',r/'jupiter.jpg')
for key in ['artwork_asset','artwork_sha256','source_url']:config['foreground_layers'][0][key]=shared['foreground_layers'][0][key]
records=[]
for index,role in enumerate(['title','artist','play','forward'],1):
 layer=copy.deepcopy(config['foreground_layers'][index]);a,b,c,d=layer['box'];x0,y0,_,_=s.crop
 B=Bfull[b-y0:d-y0,a-x0:c-x0];T=s.target[b:d,a:c];seed=T.max(2)<layer['threshold']
 if layer.get('local_contrast'):
  lum=T.mean(2).astype(np.float32);closed=cv2.morphologyEx(lum,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8));seed&=(closed-lum>layer['local_contrast'])
 yy,xx=np.where(seed);cx=a+(xx.min()+xx.max())/2;cy=b+(yy.min()+yy.max())/2;H=float(yy.max()-yy.min()+1)
 source=shared['foreground_layers'][index];asset=source['vector_asset'];shutil.copyfile(expanded/asset,r/asset)
 ar=float(ET.parse(r/asset).getroot().get('viewBox').split()[2])/float(ET.parse(r/asset).getroot().get('viewBox').split()[3])
 layer={k:v for k,v in layer.items() if k not in ['threshold','neutral_only','local_contrast']}
 layer.update(mode='solid',vector_asset=asset,vector_sha256=source['vector_sha256'],vector_provenance=source['vector_provenance'],opacity=1.)
 max_h=min(d-b-1,(c-a-1)/ar);h0=min(H,max_h-.1)
 def evaluate(v,details=False):
  px,py,h=v;w=ar*h;layer['vector_box']=[px-w/2,py-h/2,px+w/2,py+h/2]
  if px-w/2<a-.5 or px+w/2>c-.5 or py-h/2<b-.5 or py+h/2>d-.5:return (1e6,None) if details else 1e6
  A=coverage(r,layer);C=np.clip(np.sum(A[...,None]*(T-B*(1-A[...,None])),(0,1))/max(float(np.sum(A*A)),1e-9),0,1)
  pred=B*(1-A[...,None])+C*A[...,None];loss=float(np.mean((pred-T)**2))*255**2
  return (loss,C) if details else loss
 start=np.array([cx,cy,h0]);fit=minimize(evaluate,start,method='Powell',bounds=[(cx-2,cx+2),(cy-2,cy+2),(max(1,h0*.85),max_h)],options=dict(maxfev=300,xtol=.01,ftol=1e-7))
 best=fit.x if fit.fun<evaluate(start) else start;loss,C=evaluate(best,True);assert C is not None
 layer['color']=C.tolist();config['foreground_layers'][index]=layer
 records.append(dict(role=role,pose=best.tolist(),vector_box=layer['vector_box'],color=C.tolist(),loss=loss,evaluations=fit.nfev,source='Frozen expanded-player vector, same label/symbol, new compact placement only'))
 print(role,loss,layer['vector_box'],flush=True)
config['foreground_method']='Same solid vector font/icon outlines as expanded mini-player, separately measured placement/color, original high-resolution catalogue artwork; original glass exclusion mask is unchanged.'
(r/'case.json').write_text(json.dumps(config,indent=2)+'\n');(r/'vector-calibration.json').write_text(json.dumps(records,indent=2)+'\n')
s=Study(r);pred=s.render(old['parameters'],np.array(old['material']));assert s.scores(pred)['loss']==old['scores']['loss']
s.comparison(pred,r/'vector-baseline.png',old['parameters']);print('PASS compact vector baseline; optics unchanged',old['scores']['loss'],flush=True)
