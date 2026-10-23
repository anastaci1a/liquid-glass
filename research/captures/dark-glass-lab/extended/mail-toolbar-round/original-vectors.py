"""Safely extract three pinned data paths, never execute JavaScript."""
from pathlib import Path
import re,json,hashlib
from PIL import Image,ImageDraw
import numpy as np,cv2,cairosvg
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
R=Path('/evidence/extended/mail-toolbar-round');assert not(R/'original-vector-review.json').exists();refs=json.loads((R/'source-review.json').read_text());T=Image.open('/evidence/apple-matches/219-100.png').convert('RGB');rows=[];sheet=Image.new('RGB',(900,230),'white');d=ImageDraw.Draw(sheet)
for i,(name,stem,expected)in enumerate([('trash','sfTrash','b78e88c31780b25c2dba4b6dc8272481fe4fc149'),('folder','sfFolder','4524bc4d03e72ac6b5d79c4ea7299d5c61416ffd'),('reply','sfArrowshapeTurnUpBackward','a2427d4db56e1a00f61ba2638587171477ba0a94')]):
 raw=(R/(stem+'.js')).read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==expected;paths=re.findall(r'\{d:"([^"]+)"',raw.decode());assert paths and all(re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9., +\-Ee]+',p)for p in paths);pen=BoundsPen(None)
 for p in paths:parse_path(p,pen)
 l,b,r,t=pen.bounds;svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {t-b}"><g fill="#000" transform="translate({-l} {-b})">'+''.join(f'<path d="{p}"/>'for p in paths)+'</g></svg>\n';(R/(name+'-outline.svg')).write_text(svg);bb=next(g['dark_bbox']for g in refs['glyph_bounds']if g['name']==name);sx=(bb[2]-bb[0])/(r-l);sy=(bb[3]-bb[1])/(t-b);s=min(sx,sy);w,h=(r-l)*s,(t-b)*s;cx=(bb[0]+bb[2])/2-.5;cy=(bb[1]+bb[3])/2-.5;placement=[cx-w/2,cy-h/2,cx+w/2,cy+h/2]
 # Independent clean vector beside original native ink crop, preserve aspect in diagnostic.
 ref=T.crop(bb);ref.thumbnail((130,150));sheet.paste(ref,(i*300+8,50));ww=120;hh=round(ww*(t-b)/(r-l));png=cairosvg.svg2png(bytestring=svg.encode(),output_width=ww,output_height=hh);q=cv2.imdecode(np.frombuffer(png,'uint8'),cv2.IMREAD_UNCHANGED);im=Image.fromarray(cv2.cvtColor(q,cv2.COLOR_BGRA2RGBA));sheet.paste(im,(i*300+150,50),im);d.text((i*300+8,12),name+' Apple / pinned outline',fill='black');rows.append({'name':name,'source_url':f'https://raw.githubusercontent.com/bradleyhodges/sfsymbols/2a0100e93e11a22ea0ff5e0530efd10e2cf0d243/dist/module/{stem}.js','blob_sha1':blob,'module_sha256':hashlib.sha256(raw).hexdigest(),'svg_sha256':hashlib.sha256(svg.encode()).hexdigest(),'raw_bounds':[l,b,r,t],'placement':placement,'shape':'Original literal path, ink bounding trim, no aspect deformation, no target-matte pixels','opacity':'Fixed black1, independent of package .85 style','limits':'Identity to pinned SF export verified; official Apple origin and exact UI weight not independently proven; no weight/pose fit'})
sheet.save(R/'outline-glyph-comparison.png');(R/'original-vector-review.json').write_text(json.dumps({'candidates':rows,'js_executed':False,'lens_fits':0,'passes':0},indent=2)+'\n');print(json.dumps(rows))
