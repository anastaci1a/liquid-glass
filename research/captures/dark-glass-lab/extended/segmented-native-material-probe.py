"""Exact native-material refinement without modifying optical/source states."""
from pathlib import Path
import sys,json,numpy as np,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
from paired_fit import Cached
from material_local import trial
root=Path('/evidence/extended/active-segmented-selector');out=root/'native-material-probe';out.mkdir(exist_ok=True);A=Study(root);B=Study(root/'second-observation');rows=[]
for tag,file in [('single20',root/'accepted.json'),('local1',root/'local-settlement-probe/1.json')]:
 raw=json.loads(file.read_text());p=raw['parameters'];co=np.array(raw['material']);old=dict(parameters=p,material=co.tolist(),scores=[A.scores(A.render(p,co))]);cache=Cached(A,p);start=time.time()
 result,scores,calls=trial([cache],old,list(range(23)),iterations=10,progress=lambda row:print(json.dumps(dict(seed=tag,**row)),flush=True));scoreA=A.scores(A.render(p,result));scoreB=B.scores(B.render(p,result));row=dict(seed=tag,parameters=p,material=result.tolist(),scores=[scoreA,scoreB],baseline=old,evaluations=calls,seconds=time.time()-start);rows.append(row);(out/f'{tag}.json').write_text(json.dumps(row,indent=2)+'\n');A.comparison(A.render(p,result),out/f'{tag}.png',p,context_completed=True);print(json.dumps(dict(seed=tag,loss=[scoreA['loss'],scoreB['loss']],glass=[scoreA['glass']['rmse'],scoreB['glass']['rmse']])),flush=True)
(out/'report.json').write_text(json.dumps(dict(rows=rows,limits='Read-only native-pixel material optimization. Both background files remain frozen. No optical/accepted mutation; B observed but not constrained in this single-reference diagnostic.'),indent=2)+'\n')
