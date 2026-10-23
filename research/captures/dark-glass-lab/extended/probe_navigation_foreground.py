"""Uncounted check of a shared monotone response through the clean Home SVG."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from vector_foreground import coverage
from foreground_response import response
r=Path('/evidence/extended/music-navigation/paired');old=json.loads((r/'accepted.json').read_text());p=old['parameters'];co=np.array(old['material']);samples=[];studies=[];preds=[]
for name in ['a','b']:
 s=Study(r/name);s.case['foreground_styles']=old['foreground_styles'];G=s.render(p,co);layer=next(l for l in s.case['foreground_layers'] if l.get('vector_asset')=='home.svg');B=s.apply_foreground(G.copy(),stop_before=layer['box']);a,b,c,d=layer['box'];x0,y0,_,_=s.crop;samples.append((B[b-y0:d-y0,a-x0:c-x0],s.target[b:d,a:c],coverage(s.folder,layer)));studies.append(s);preds.append(G)
style=old['foreground_styles']['home.svg'];opacity=style['opacity'];v=1-opacity;q=np.array(style['color'])*opacity;t=q+v;strength=np.divide(v,t,out=np.zeros_like(t),where=t>0);start=np.stack([t,strength,np.ones(3)],1).ravel()
def errors(v):return np.array([float(np.mean(((1-A[...,None])*B+A[...,None]*response(B,v.reshape(3,3))-T)**2))*255**2 for B,T,A in samples])
before=errors(start);scale=max(1,before.mean());fit=minimize(lambda v:errors(v).mean()/scale,start,method='SLSQP',bounds=[b for _ in range(3) for b in [(0,1),(0,1),(.2,12)]],constraints=[dict(type='ineq',fun=lambda v:(before-errors(v))/scale)],options=dict(maxiter=200,ftol=1e-12,eps=2e-5));best=start;after=before
for t in [1,.5,.25,.125,.0625,.03125]:
 v=start+t*(fit.x-start);e=errors(v)
 if np.all(e<=before+1e-8) and e.sum()<after.sum():best=v;after=e
report=dict(scope='Exploratory only. Same9-parameter monotone response on both observed backgrounds, clean SVG alpha unchanged.',start=start.reshape(3,3).tolist(),response=best.reshape(3,3).tolist(),before_mse=before.tolist(),after_mse=after.tolist(),evaluations=fit.nfev)
(r/'foreground-response-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
