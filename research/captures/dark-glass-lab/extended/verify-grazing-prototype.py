from pathlib import Path
import copy,json
import numpy as np
from extended_fit import Study
from paired_fit import Cached,permitted
from prepared import Prepared
from source_support import coverage_report,supported
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-22.json').read_text())['current'];probe=json.loads((root.parent/'grazing-compact-probe/report.json').read_text());a,w,power=probe['best']['parameters'];p={**old['parameters'],'grazing_reflection':dict(strength=a,width=w,angular_power=power,source_sigma=.007,direction=[0,1])};co=np.array(old['material']);records=[]
for n in ['a','b']:
 s=Study(root/n);pred=s.render(p,co);metric=s.scores(pred);index=0 if n=='a' else 1;assert abs(metric['loss']-probe['best']['scores'][index]['loss'])<1e-6,(metric,probe['best']['scores'][index]);assert np.max(abs(Cached(s,p).render(co)-pred))<2e-6
 motion=Prepared(s,p,co,1);assert np.max(abs(motion.render()-pred))<2e-6;s.backdrop_shift=[0.,7.25];shifted=s.render(p,co);assert np.max(abs(motion.render()-shifted))<2e-6;s.backdrop_shift=[0.,0.];del motion
 report=coverage_report(s,p);assert supported(s,report);records.append(dict(sample=n,scores=metric,support=report));s.comparison(pred,root.parent/'grazing-compact-probe'/f'production-{n}.png',p)
assert permitted([r['scores'] for r in records],old['scores']);print(json.dumps(dict(parameters=p['grazing_reflection'],records=records)),flush=True)
(root.parent/'grazing-compact-probe/production-verification.json').write_text(json.dumps(dict(parameters=p['grazing_reflection'],records=records),indent=2)+'\n')
