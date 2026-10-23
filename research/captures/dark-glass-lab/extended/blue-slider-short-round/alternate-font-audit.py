from pathlib import Path
import os,json
from fontTools.ttLib import TTFont
D=Path('/evidence/extended/blue-slider-short-round');os.umask(0o002);rows=[]
for p in [Path('/evidence/extended/icon-source/SF-Pro.ttf'),*Path('/evidence/extended/icon-source/fonts/Library/Fonts').glob('*Text-Regular*')]:
 try:
  f=TTFont(p);names=[n for n in f.getGlyphOrder() if 'tortoise' in n or 'hare' in n];rows.append(dict(file=str(p),tables=f.keys(),version=[str(n.toUnicode()) for n in f['name'].names if n.nameID==5][:2],names=names))
 except Exception as e:rows.append(dict(file=str(p),error=str(e)))
print(rows,flush=True);(D/'alternate-font-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
