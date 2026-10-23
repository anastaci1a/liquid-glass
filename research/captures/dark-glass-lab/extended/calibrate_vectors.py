from pathlib import Path
import json,numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from vector_foreground import coverage
from foreground_response import fit_response,response
for id in ['music-home-vector','music-search-vector']:
 folder=Path('/evidence/extended')/id;s=Study(folder);acc=json.loads((folder/'accepted.json').read_text());B=s.render(acc['parameters'],np.array(acc['material']));x0,y0,_,_=s.crop
 case=s.case;layer=case['foreground_layers'][0];a,b,c,d=layer['box'];base=B[b-y0:d-y0,a-x0:c-x0];T=s.target[b:d,a:c];old=np.array(layer['vector_box'])
 def evaluate(v,details=False):
  layer['vector_box']=v.tolist();alpha=coverage(folder,layer);inside=cv2.erode((alpha>.995).astype(np.uint8),np.ones((3,3),np.uint8))>0
  if layer['mode']=='transmission':
   params=fit_response(base[inside],T[inside]);ink=response(base,params)
  else:
   params=np.clip(np.sum(alpha[...,None]*(T-base*(1-alpha[...,None])),(0,1))/np.sum(alpha*alpha),0,1);ink=params
  pred=base*(1-alpha[...,None])+ink*alpha[...,None];error=float(np.mean((pred-T)**2))*255**2
  return (error,params,alpha,pred) if details else error
 before=evaluate(old);result=minimize(evaluate,old,method='Powell',bounds=[(v-1.5,v+1.5) for v in old],options=dict(maxfev=120,xtol=.03,ftol=1e-5));best=result.x if result.fun<before else old
 error,params,alpha,pred=evaluate(best,True)
 if layer['mode']=='transmission':case['foreground_response']=params.tolist()
 else:layer['color']=params.tolist()
 (folder/'case.json').write_text(json.dumps(case,indent=2)+'\n')
 (folder/'vector-calibration.json').write_text(json.dumps(dict(protocol='Full fixed foreground box MSE; analytic clean SVG coverage, effects separate. Historical photo-matte foreground scores are not directly comparable.',before_mse=before,after_mse=error,placement=best.tolist(),response=params.tolist(),evaluations=result.nfev),indent=2)+'\n')
 s=Study(folder);s.comparison(B,folder/'vector-calibrated.png',acc['parameters']);print(id,before,error,best.tolist(),flush=True)
