from pathlib import Path
source=Path('/evidence/extended/switch-grazing-compact-probe.py').read_text();exec(source.split('for width in')[0]);v=[1.,.0390105138992314,1.5538792812814484]
for n,s,c in zip(['a','b'],studies,caches):s.comparison(c.render(v),out/f'peek-{n}.png',old['parameters'])
