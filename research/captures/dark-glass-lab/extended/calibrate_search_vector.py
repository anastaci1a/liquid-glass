from pathlib import Path
import json,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from vector_foreground import coverage
r=Path('/evidence/extended/music-search-vector');s=Study(r);acc=json.loads((r/'accepted.json').read_text());pred=s.render(acc['parameters'],np.array(acc['material']));c=s.case;l=c['foreground_layers'][0];a,b,z,d=l['box'];x0,y0,_,_=s.crop;B=pred[b-y0:d-y0,a-x0:z-x0];T=s.target[b:d,a:z];left,top,right,bottom=l['vector_box'];start=np.array([(left+right)/2,(top+bottom)/2,(right-left+bottom-top)/2])
def evaluate(v,details=False):
 cx,cy,size=v;l['vector_box']=[cx-size/2,cy-size/2,cx+size/2,cy+size/2];alpha=coverage(r,l);D=B*alpha[...,None]
 opacity=float(np.clip(np.sum(D*(B-T))/np.sum(D*D),0,1));P=B*(1-opacity*alpha[...,None]);error=float(np.mean((P-T)**2))*255**2
 return (error,opacity) if details else error
before=evaluate(start);fit=minimize(evaluate,start,method='Powell',bounds=[(start[0]-1.5,start[0]+1.5),(start[1]-1.5,start[1]+1.5),(start[2]-2,start[2]+2)],options=dict(maxfev=350,xtol=.015,ftol=1e-7));best=fit.x if fit.fun<before else start;error,o=evaluate(best,True);l.update(color=[0,0,0],opacity=o)
c['foreground_method']='Solid analytic circular-ring/45-degree capsule SVG, square placement. Black opacity is a separate renderer coefficient; no image-derived matte or baked gray texture.'
(r/'case.json').write_text(json.dumps(c,indent=2)+'\n');(r/'vector-calibration.json').write_text(json.dumps(dict(protocol='Fixed full foreground-box encoded RGB MSE. Clean vector with square pose; one scalar black opacity. Historical photo-matte foreground scores are not directly comparable.',before_mse=before,after_mse=error,placement=l['vector_box'],opacity=o,evaluations=fit.nfev),indent=2)+'\n');s=Study(r);s.comparison(pred,r/'vector-calibrated.png',acc['parameters']);print(error,o,l['vector_box'],flush=True)
