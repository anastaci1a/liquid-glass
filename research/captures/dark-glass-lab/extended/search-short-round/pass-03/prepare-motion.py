import json,sys,os
from pathlib import Path
root=Path('/evidence/extended');out=root/'search-short-round/pass-03/motion';r=json.loads((root/'search-short-round/pass-03/joint-candidate.json').read_text())
for i,n in enumerate(['a','b']):
 d=out/n;d.mkdir(parents=True,exist_ok=True)
 for p in (root/'music-search-vector-paired-replay'/n).iterdir():
  if p.is_file() and p.name!='accepted.json' and not (d/p.name).exists():(d/p.name).symlink_to(p)
 (d/'accepted.json').write_text(json.dumps(dict(parameters=r['parameters'],material=r['candidate']['material'],scores=r['candidate']['scores'][i]),indent=2)+'\n')
