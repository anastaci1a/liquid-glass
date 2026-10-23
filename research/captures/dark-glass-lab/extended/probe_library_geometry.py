"""Uncounted clean trace refinement: translate/scale only the note cutout."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET,numpy as np
from scipy.optimize import minimize
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from extended_fit import Study
from vector_foreground import _coverage,coverage
r=Path('/evidence/extended/music-navigation/paired');old=json.loads((r/'accepted.json').read_text());samples=[]
base=(r/'a/library.svg').read_bytes();root=ET.fromstring(base);target=next(n for n in root.iter() if n.get('fill-rule')=='evenodd');outer,note=target.get('d').split(' M69.5',1);note='M69.5'+note
for name in ['a','b']:
 s=Study(r/name);s.case['foreground_styles']=old['foreground_styles'];G=s.render(old['parameters'],np.array(old['material']));l=next(l for l in s.case['foreground_layers'] if l.get('vector_asset')=='library.svg');B=s.apply_foreground(G.copy(),stop_before=l['box']);a,b,c,d=l['box'];x0,y0,_,_=s.crop;samples.append((B[b-y0:d-y0,a-x0:c-x0],s.target[b:d,a:c],l))
style=old['foreground_styles']['library.svg'];C=np.asarray(style['color'],np.float32)
def make(v):
 dx,dy,scale=v;pen=SVGPathPen(None);parse_path(note,TransformPen(pen,(scale,0,0,scale,dx+46.45*(1-scale),dy+86.35*(1-scale))));root=ET.fromstring(base);node=next(n for n in root.iter() if n.get('fill-rule')=='evenodd');node.set('d',outer+' '+pen.getCommands());return ET.tostring(root)
def errors(v):
 raw=make(v);out=[]
 for B,T,l in samples:
  A=_coverage(raw,tuple(l['box']),tuple(l['vector_box']),1)*style['opacity'];pred=B*(1-A[...,None])+C*A[...,None];out.append(float(np.mean((pred-T)**2))*255**2)
 return np.array(out)
start=np.array([0.,0.,1.]);before=errors(start);fit=minimize(lambda v:errors(v).mean(),start,method='Powell',bounds=[(-8,8),(-8,8),(.8,1.2)],options=dict(maxfev=600,xtol=.002,ftol=1e-8));best=start;after=before
for t in [1,.5,.25,.125,.0625]:
 v=start+t*(fit.x-start);e=errors(v)
 if np.all(e<=before+1e-8) and e.sum()<after.sum():best=v;after=e
report=dict(scope='Exploratory fixed clean primitives: uniform scale and translation of beamed-note cutout only. Same geometry on both backgrounds; no photo alpha.',transform=best.tolist(),before_mse=before.tolist(),after_mse=after.tolist(),evaluations=fit.nfev,previous_sha256=hashlib.sha256(base).hexdigest())
(r/'library-geometry-probe.json').write_text(json.dumps(report,indent=2)+'\n');(r/'library-geometry-candidate.svg').write_bytes(make(best));print(report,flush=True)
