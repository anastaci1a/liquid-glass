from pathlib import Path
import json,time,numpy as np
from extended_fit import Study
from paired_fit import Cached,scores,permitted
from material_local import trial
from material_context import matrix
from source_support import coverage_report,supported
root=Path('/evidence/extended/music-home-vector');out=root/'context-bridge-probe';out.mkdir(exist_ok=True)
a=json.loads((root/'accepted.json').read_text());b=json.loads((root/'paired/accepted.json').read_text());studies=[Study(root/'paired'/n) for n in ['a','b']];target=[a['scores'],b['scores'][1]];results=[]
for sensitivity in [2.,3.,4.]:
 p={**a['parameters'],'material_chroma_sensitivity':sensitivity,'material_chroma_floor':0.};co=np.linalg.solve(matrix(studies[0],p),np.array(a['material']));caches=[Cached(s,p) for s in studies];actual=scores(caches,co);old=dict(parameters=p,material=co.tolist(),scores=actual)
 start=time.time();v,metric,calls=trial(caches,old,list(range(23)),iterations=20)
 full=[s.scores(s.render(p,v)) for s in studies];footprints=[coverage_report(s,p) for s in studies]
 row=dict(sensitivity=sensitivity,baseline=old,parameters=p,material=v.tolist(),scores=full,source_support=footprints,permitted=permitted(full,target) and all(supported(s,r) for s,r in zip(studies,footprints)),seconds=time.time()-start,evaluations=calls);results.append(row)
 (out/'report.json').write_text(json.dumps(dict(scope='Private use of the existing shared source-color material function; actual baseline metrics and stricter desired thresholds remain separate. No accepted writes/pass count.',targets=target,results=results),indent=2)+'\n')
 for n,s in zip(['a','b'],studies):s.comparison(s.render(p,v),out/(str(sensitivity)+'-'+n+'.png'),p)
 print(json.dumps(dict(sensitivity=sensitivity,loss=[r['loss'] for r in full],permitted=row['permitted'])),flush=True)
