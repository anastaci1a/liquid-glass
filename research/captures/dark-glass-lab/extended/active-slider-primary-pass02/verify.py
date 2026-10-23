import os,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
from revision_replay import clean_composite
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');sys.path.insert(0,str(ROOT));from intake import score
D=ROOT/'pass07-recentered-saved';OUT=Path('/evidence/extended/active-slider-primary-pass02');os.umask(0o002)
r=json.loads((D/'candidate-native.json').read_text());old=json.loads((ROOT/'strength-postblur-joint/candidate-native.json').read_text());support=json.loads((D/'fresh-source-proof.json').read_text());rows=[]
for i,n in enumerate(['a','b']):
 s=Study(ROOT/n);a=s.render(r['parameters'],np.array(r['material']));saved=np.load(D/f'trial1-ref{i}-material.npy');assert np.array_equal(a,saved)
 sc,full,ext=score(s,r['parameters'],a);assert sc==r['scores'][i]
 b=old['scores'][i];assert sc['E']<=b['E'] and sc['glass']['rmse']<=b['glass']['rmse'] and sc['shadow']['rmse']<=b['shadow']['rmse'];assert not s.foreground_layers and not s.transmission_layers
 assert support[i]['passed'];rows.append(dict(reference=n,previous=b,candidate=sc,native_max_difference=0,source_proof=support[i]))
(OUT/'verification.json').write_text(json.dumps(dict(native_replay=True,visual_review=True,accepted=True,round_pass=2,observations=rows,limits='Both approved-size saved candidates inspected; existing dispersion/color/shape approximations remain. Native public-code replay exact. Original explicitly modeled hidden-track input retained; defined support1 does NOT mean observed RGB, observed minimum0. Rim alone is advisory and worsensA; original pairedE/glass/fixedexterior gates hold.'),indent=2)+'\n');print('Active green second new pass accepted',flush=True)
