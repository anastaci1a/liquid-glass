import sys,json,os
from pathlib import Path
from fontTools.ttLib import TTFont
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from font_vector import export
D=Path('/evidence/extended/blue-slider-short-round');font=Path('/evidence/extended/icon-source/fonts/Library/Fonts/SF-Pro-Display-Regular.otf');f=TTFont(font);os.umask(0o002)
rows={'tables':f.keys(),'color_layers':{}}
if 'COLR' in f:
 rows['colr_version']=f['COLR'].version
 if hasattr(f['COLR'],'ColorLayers'):
  for name in ['tortoise.tag.color','tortoise.tag.fill.color','hare.tag.color','hare.tag.fill.color']:rows['color_layers'][name]=[(l.name,l.colorID) for l in f['COLR'].ColorLayers.get(name,[])]
for name in ['tortoise.tag.fill.color','hare.tag.fill.color']:
 svg,meta=export(font,glyph=name);(D/(name+'.svg')).write_text(svg)
print(rows,flush=True);(D/'font-layer-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
