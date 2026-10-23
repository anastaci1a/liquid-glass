from pathlib import Path
import copy,hashlib,json
import numpy as np
from extended_fit import Study
from source_support import coverage_report,supported
from paired_fit import permitted
folder=Path('/evidence/extended/active-switch/paired');path=folder/'pass-23.json';assert not path.exists();old=json.loads((folder/'accepted.json').read_text());assert 'grazing_reflection' not in old['parameters'];check=json.loads((folder.parent/'grazing-compact-probe/production-verification.json').read_text());probe=json.loads((folder.parent/'grazing-compact-probe/report.json').read_text());current=copy.deepcopy(old);current['parameters']['grazing_reflection']=check['parameters'];current['scores']=[];support=[];bands=[]
for name in ['a','b']:
 s=Study(folder/name);p=current['parameters'];co=np.array(current['material']);pred=s.render(p,co);base=s.render(old['parameters'],co);current['scores'].append(s.scores(pred));r=coverage_report(s,p);assert supported(s,r);support.append(r)
 # Supplementary contour metric includes the unscored outermost fitted band.
 # It is reported separately and never replaces/changes the frozen masks.
 *_,(sd,nx,ny)=s.shape(s.x,s.y,p);mask=(sd<=0)&(sd>-.025)&(ny>0)
 bands.append(dict(definition='Fitted-footprint inward distance0..0.025L, outward normal ny>0; supplementary, not a native-score mask.',pixels=int(mask.sum()),previous_mse=float(np.mean(((base-s.target_crop)[mask]*255)**2)),current_mse=float(np.mean(((pred-s.target_crop)[mask]*255)**2))))
 s.comparison(pred,folder/f'pass-23-{name}.png',p)
assert permitted(current['scores'],old['scores']);assert all(b['current_mse']<=b['previous_mse'] for b in bands)
record=dict(pass_number=23,experiment='Separate source-derived grazing reflection from transmission scattering',execution_script=Path(__file__).name,execution_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),accepted=True,previous=old,current=current,trials=probe['trials'],evaluations=probe['evaluations'],seconds=probe['seconds'],proposed_source_support=support,supplementary_contour=bands,gate='Frozen per-background native loss/glass plus separately reported lower-contour check; no native masks changed.',limits='Directional incident field is an empirical source proxy. Colored inner rainbow and remaining upper/side rim mismatch are unresolved; not an Apple reflection law.')
path.write_text(json.dumps(record,indent=2)+'\n');(folder/'accepted.json').write_text(json.dumps(current,indent=2)+'\n');print(json.dumps(dict(scores=current['scores'],contours=bands)))
