from pathlib import Path
import copy,hashlib,json
import numpy as np
from extended_fit import Study
from paired_fit import permitted
from source_support import coverage_report,supported
folder=Path('/evidence/extended/active-switch/paired');path=folder/'pass-24.json';assert not path.exists()
probe=json.loads((folder.parent/'transmission-dispersion-probe/report.json').read_text());verified=json.loads((folder.parent/'transmission-dispersion-probe/production-verification.json').read_text());old=json.loads((folder/'accepted.json').read_text());assert old==json.loads((folder/'pass-23.json').read_text())['current']
current=copy.deepcopy(old);current['parameters']['directional_transmission']=verified['parameters'];current['scores']=[];support=[]
for name in ['a','b']:
 s=Study(folder/name);p=current['parameters'];prediction=s.render(p,np.array(current['material']));score=s.scores(prediction);current['scores'].append(score);r=coverage_report(s,p);assert supported(s,r);support.append(r);s.comparison(prediction,folder/f'pass-24-{name}.png',p)
assert permitted(current['scores'],old['scores'])
assert np.max(abs(np.array([s['loss'] for s in current['scores']])-np.array([r['scores']['loss'] for r in verified['records']])))<1e-6
record=dict(pass_number=24,experiment='Directional channel separation before fixed material lighting',execution_script=Path(__file__).name,execution_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),accepted=True,previous=old,current=current,trials=probe['trials'],evaluations=probe['calls'],seconds=probe['seconds'],proposed_source_support=support,gate='Both frozen native per-reference losses and whole-glass RMSE hold; analytic field verified independently of half-pixel proposal atlas.',limits='Fixed-direction RGB offsets and horizontally fading contribution are empirical lateral-chromatic hypotheses. Apple upper rim and spectral detail remain imperfect. Hidden source is estimated, not directly observed.')
path.write_text(json.dumps(record,indent=2)+'\n');(folder/'accepted.json').write_text(json.dumps(current,indent=2)+'\n');print(json.dumps(dict(scores=current['scores'])))
