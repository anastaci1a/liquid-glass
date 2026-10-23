from pathlib import Path
import os,json,sys
from fontTools.ttLib import TTFont
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from font_vector import export
D=Path('/evidence/extended/blue-slider-short-round');font=Path('/evidence/extended/icon-source/fonts/Library/Fonts/SF-Pro-Display-Regular.otf');os.umask(0o002)
f=TTFont(font);names=[n for n in f.getGlyphOrder() if n.startswith('tortoise') or n.startswith('hare')];(D/'font-candidates.json').write_text(json.dumps(dict(font=str(font),glyph_names=names,limits='Original vector candidates; exact icon/weight assignment not yet verified against exposed source. Not inferred from lensed pixels.'),indent=2)+'\n');print(names,flush=True)
for base in ['tortoise','hare']:
 for glyph in [base,base+'.tag.color']:
  if glyph in names:
   svg,meta=export(font,glyph=glyph);(D/(base+'-'+glyph.replace('.','-')+'.svg')).write_text(svg);(D/(base+'-'+glyph.replace('.','-')+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
