"""Canonical unadopted foreground candidates, no screenshot matte or glyph fitting."""
import os,json,re,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
os.umask(0o002)
R=Path('/evidence/extended/helper-toolbar-work/options-popup-round');D=R/'foreground-candidates';D.mkdir();T=np.asarray(Image.open('/evidence/apple-matches/219-240.png').convert('RGB'));g=T.mean(2);yy,xx=np.mgrid[:g.shape[0],:g.shape[1]];rows=[]
sha=lambda x:hashlib.sha256(x).hexdigest()
def placement(bounds,bbox):
 l,b,r,t=bounds;w=r-l;h=t-b;a,c,d,e=bbox;k=min((d-a)/w,(e-c)/h);mx=(a+d-1)/2;my=(c+e-1)/2;return [mx-w*k/2,my-h*k/2,mx+w*k/2,my+h*k/2]
for j,(shape,word,y0,y1) in enumerate([('Circle','One',270,350),('Triangle','Two',420,495),('Square','Three',565,640),('Hexagon','Four',710,800)]):
 roi=(xx>=725)&(xx<814)&(yy>=y0)&(yy<y1)&(g<60);y,x=np.where(roi);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];raw=(R/f'sf{shape}.js').read_bytes();paths=re.findall(r'\{d:"([^"]+)"',raw.decode());assert len(paths)==1 and re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9., +\-Ee]+',paths[0]);bp=BoundsPen(None);parse_path(paths[0],bp);l,b,r,t=bp.bounds;svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {t-b}"><path fill="#000" transform="translate({-l} {-b})" d="{paths[0]}"/></svg>\n';name=shape.lower()+'.svg';(D/name).write_text(svg);rows.append(dict(kind='icon',identity=shape.lower(),asset=name,svg_sha256=sha(svg.encode()),pinned_commit='2a0100e93e11a22ea0ff5e0530efd10e2cf0d243',module=f'dist/module/sf{shape}.js',module_sha256=sha(raw),module_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),source_bounds=list(bp.bounds),native_observed_ink_bbox=bbox,uniform_placement_proposal=placement(bp.bounds,bbox),scoring_status='UNSCORED_UNADOPTED',style='Black1, original pinned outline; exact weight/variant not independently proved. JS not executed.'))
fontp=Path('/evidence/extended/icon-source/fonts/Library/Fonts/SF-Pro-Text-Regular.otf');font=TTFont(fontp);gs=font.getGlyphSet();cmap=font.getBestCmap();fontsha=sha(fontp.read_bytes())
for word,y0,y1 in [('One',270,350),('Two',420,495),('Three',565,640),('Four',710,800)]:
 pen=SVGPathPen(gs);bp=BoundsPen(gs);advance=0
 for char in word:
  name=cmap[ord(char)];tr=(1,0,0,1,advance,0);gs[name].draw(TransformPen(pen,tr));gs[name].draw(TransformPen(bp,tr));advance+=font['hmtx'][name][0]
 l,b,r,t=bp.bounds;svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {t-b}"><path fill="#000" transform="translate({-l} {t}) scale(1 -1)" d="{pen.getCommands()}"/></svg>\n';name='text-'+word.lower()+'.svg';(D/name).write_text(svg);roi=(xx>=840)&(xx<1070)&(yy>=y0)&(yy<y1)&(g<60);y,x=np.where(roi);bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];rows.append(dict(kind='visible_text',text=word,asset=name,svg_sha256=sha(svg.encode()),font=str(fontp),font_sha256=fontsha,glyph_names=[cmap[ord(c)] for c in word],source_bounds=list(bp.bounds),native_observed_ink_bbox=bbox,uniform_placement_proposal=placement(bp.bounds,bbox),scoring_status='UNSCORED_UNADOPTED',limitations='ONE original SF Pro Text Regular candidate, default hmtx advances only: GPOS/optical kerning/size/weight not identified, no shaping or per-letter fitting. All words fully visible; no invented hidden content. Fixed black1/solidfontpaths, no screenshot matte.'))
font.close();out=dict(status='CANONICAL_CANDIDATES_ONLY_SOURCE_UNSUPPORTED_NO_ADOPTION',assets=rows,glyph_fits=0,optical_renders=0,source='Pinned icon literal path data plus ONE independently available originalSFtextfont. Glyph identity/layout uncertainty explicit; no font search/optimizer.',count=0);(R/'foreground-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(assets=len(rows),font_sha256=fontsha,all_unscored=True)))
