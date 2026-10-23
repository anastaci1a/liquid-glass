"""Original SF symbol outlines, only uniform pose/weight/color fitted."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from scipy.optimize import minimize
from vector_foreground import _coverage
from crowned_tensor import render
from reproduce import CASES
from PIL import Image
root=Path('/tmp/lead-toolbar-input');out=Path('/evidence/extended/toolbar-primary-review/glyphs');out.mkdir(parents=True,exist_ok=True)
fpath=Path('/evidence/extended/icon-source/fallback/Applications/SF Symbols.app/Contents/Resources/Fonts/SFSymbolsFallback.otf');font=TTFont(fpath);recipe=json.loads((root/'candidate-recipe.json').read_text());src=np.asarray(Image.open(root/'source.png'),float)/255;target=np.asarray(Image.open(root/'target.png'),float)/255;case=CASES['regular'];C,A=render(src,case,recipe);cx,cy,_,_=case['crop'];rows=[]
for name,stem,box in [('archivebox','box',[695,462,872,628]),('plus','plus',[1068,470,1215,618])]:
 a,b,c,d=box;B=C[b-cy:d-cy,a-cx:c-cx];T=target[b:d,a:c];best=None;trials=[]
 for glyph in [stem+'.tag.color',stem+'.tag.color.medium',stem+'.tag.color.large']:
  for weight in [400,500,600]:
   gs=font.getGlyphSet(location={'wght':weight});pen=SVGPathPen(gs);bounds=BoundsPen(gs);gs[glyph].draw(pen);gs[glyph].draw(bounds);x0,y0,x1,y1=bounds.bounds;ratio=(x1-x0)/(y1-y0)
   raw=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x1-x0} {y1-y0}"><path fill="#000" transform="translate({-x0} {y1}) scale(1 -1)" d="{pen.getCommands()}"/></svg>\n'.encode()
   def placement(v):
    X,Y,H=v;W=H*ratio;return [X-W/2,Y-H/2,X+W/2,Y+H/2]
   def value(v,detail=False):
    alpha=_coverage(raw,tuple(box),tuple(placement(v)),1);den=max(float((alpha*alpha).sum()),1e-9);color=np.clip(np.sum(alpha[...,None]*(T-B*(1-alpha[...,None])),axis=(0,1))/den,0,1);pred=B*(1-alpha[...,None])+color*alpha[...,None];err=float(np.mean((pred-T)**2)*255**2)
    return (err,color,alpha,pred) if detail else err
   initial=[(a+c)/2,(b+d)/2,(d-b)*.88];fit=minimize(value,initial,method='Powell',bounds=[(a+(c-a)*.4,a+(c-a)*.6),(b+(d-b)*.4,b+(d-b)*.6),((d-b)*.75,(d-b)*.98)],options=dict(maxfev=220,xtol=.01,ftol=1e-7));err,color,alpha,pred=value(fit.x,True)
   record=dict(glyph=glyph,weight=weight,mse=err,color=color.tolist(),box=box,placement=placement(fit.x),uniform_scale=True);trials.append(record)
   if best is None or err<best['mse']:
    best=record;best_raw=raw;best_pred=pred
 chosen=dict(name=name,**best,font_file=fpath.name,font_sha256=hashlib.sha256(fpath.read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(best_raw).hexdigest(),trials=trials,limits='Original SF symbol whole outlines; candidate font style and pose inferred. No per-pixel alpha, outline edits or screenshot texture. Full glyph color constant, not a glass model change.')
 (out/f'{name}.svg').write_bytes(best_raw);(out/f'{name}.json').write_text(json.dumps(chosen,indent=2)+'\n');Image.fromarray(np.uint8(np.clip(best_pred,0,1)*255)).save(out/f'{name}-render.png');Image.fromarray(np.uint8(np.clip(T,0,1)*255)).save(out/f'{name}-reference.png');rows.append(chosen);print(json.dumps({k:chosen[k] for k in ['name','glyph','weight','mse','placement']}),flush=True)
(out/'report.json').write_text(json.dumps(rows,indent=2)+'\n')
