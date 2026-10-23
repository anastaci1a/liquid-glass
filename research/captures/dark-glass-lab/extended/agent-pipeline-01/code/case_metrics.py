"""Private fixed native metric supplement; no renderer/source change."""
import numpy as np
def scores(s,masks,C):
 r=s.scores(C);err=(C-s.target_crop)*255;r['E']=float(np.sqrt(r['loss']));r['exterior']={'pixels':int(masks['exterior'].sum()),'rmse':float(np.sqrt(np.mean(err[masks['exterior']]**2)))};r['foreground_MSE']=[];x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];e=err[b-y0:d-y0,a-x0:c-x0];r['foreground_MSE'].append(float(np.mean(e*e)))
 return r
