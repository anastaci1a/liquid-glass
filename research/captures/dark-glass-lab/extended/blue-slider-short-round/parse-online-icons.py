"""Read literal SVG path data only; never execute downloaded JavaScript."""
import os,json,re,hashlib
from pathlib import Path
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
D=Path('/evidence/extended/blue-slider-short-round');os.umask(0o002)
for name in ['Tortoise','Hare']:
 text=(D/('sf'+name+'-online.js.txt')).read_text();paths=[];pen=BoundsPen(None)
 for m in re.finditer(r'\{d:("(?:\\.|[^"\\])*")',text):
  d=json.loads(m[1]);assert re.fullmatch(r'[A-Za-z0-9eE.+,\s-]+',d);parse_path(d,pen);paths.append(d)
 assert paths and pen.bounds is not None;x0,y0,x1,y1=pen.bounds
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}">'+''.join(f'<path fill="#000" d="{d}"/>' for d in paths)+'</svg>\n';(D/(name.lower()+'-online-outline.svg')).write_text(svg);meta=json.loads((D/('sf'+name+'-online.provenance.json')).read_text());meta.update(svg_sha256=hashlib.sha256(svg.encode()).hexdigest(),bounds=pen.bounds,path_count=len(paths),geometry='Original literal path data unchanged. ViewBox trimmed to analytic ink bounds only; no trace, stroke/filter or geometric edits. External asset identity must still pass exposed-reference checks.');(D/(name.lower()+'-online-outline.json')).write_text(json.dumps(meta,indent=2)+'\n');print(name,pen.bounds,len(paths),flush=True)
