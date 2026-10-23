from pathlib import Path
import copy,json,numpy as np
from extended_fit import Study
from material_context import mean_source,LUMA
from source_support import coverage_report,supported
from paired_fit import permitted
root=Path('/evidence/extended/music-home-vector');old=json.loads((root/'ambient-optics-slack/report.json').read_text())['best'];new=copy.deepcopy(old);new['parameters']['material_context_inset']=.08;studies=[Study(root/'paired'/n) for n in ['a','b']];means=[float(mean_source(s,new['parameters'])@LUMA) for s in studies];response=np.array(old['ambient_rim_response'])*(old['source_luma'][1]-old['source_luma'][0])/(means[1]-means[0]);co=np.array(old['material']);co[[6,9,12]]+=(old['source_luma'][0]-.5)*np.array(old['ambient_rim_response'])-(means[0]-.5)*response;new['material']=co.tolist();new['ambient_rim_response']=response.tolist();new['source_luma']=means;new['parameters'].update(ambient_rim_response=response.tolist(),ambient_rim_luma_range=means);new['scores']=[];support=[]
for s in studies:
 pred=s.render(new['parameters'],co);new['scores'].append(s.scores(pred));r=coverage_report(s,new['parameters']);assert supported(s,r);support.append(r)
targets=json.loads((root/'ambient-optics-slack/report.json').read_text())['targets'];assert permitted(new['scores'],targets)
r=dict(best=new,targets=targets,source_support=support,model='One shared radial map and23 material coefficients, plus three neutral rim responses to unrefracted source brightness measured in a0.08L inset footprint. C2 clamped interpolation between observed brightness endpoints; source-mean domain independently confidence-checked. Not an Apple model.',history='The earlier full-footprint candidate read87 unknown source pixels and failed the new context-source gate. It is not accepted. This explicit geometric inset avoids that unsupported boundary; affine recalibration preserves the measured lighting endpoints, with one common source response and no RGB per-scene recipes.',limits='Only two observed source contexts. Bounded interpolation outside their brightness endpoints is a safety rule, not validated Apple adaptation.')
(root/'inset-context-bridge.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(scores=new['scores'],source_support=support)),flush=True)
