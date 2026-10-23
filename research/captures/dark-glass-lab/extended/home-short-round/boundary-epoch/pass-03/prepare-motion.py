import json
from pathlib import Path
r=Path('/evidence/extended/home-short-round');out=r/'boundary-epoch/pass-03/motion';state=json.loads((r/'boundary-epoch/pass-03/joint-candidate.json').read_text());response=json.loads((r/'boundary-epoch/joint-response/result.json').read_text())['foreground_response']
for i,n in enumerate(['a','b']):
 s=r/'input-boundary-replay-proposal'/n;d=out/n;d.mkdir(parents=True,exist_ok=True)
 for p in s.iterdir():
  if p.is_file() and p.name not in ['case.json','accepted.json'] and not (d/p.name).exists():(d/p.name).symlink_to(p.resolve())
 case=json.loads((s/'case.json').read_text());case['foreground_response']=response;(d/'case.json').write_text(json.dumps(case,indent=2)+'\n');(d/'accepted.json').write_text(json.dumps(dict(parameters=state['parameters'],material=state['candidate']['material'],scores=state['candidate']['scores'][i]),indent=2)+'\n')
