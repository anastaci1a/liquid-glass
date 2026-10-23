"""Lead-independent native/material/foreground/source verification; no fitting."""
import sys,json,ast,math,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from extended_shadow import shadow
from source_support import coverage_report,supported
from revision_replay import subpixel_support
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/navigation-round');packet=root/'rim-width-neighborhood';out=Path('/evidence/extended/navigation-pass02-primary-review');r=json.loads((packet/'result.json').read_text());native=json.loads((packet/'candidate-native.json').read_text());p=native['parameters'];co=np.asarray(native['material'])
public=Path('/workspace/docs/liquid-glass/experiments/reconstruction');codechecks={}
for name in ['extended_fit.py','render.py','curvature.py','crowned_footprint.py','chromatic_transmission.py','source_support.py']:
 codechecks[name]=hashlib.sha256((public/name).read_bytes()).hexdigest()==hashlib.sha256((root/'short-outer-profile/code'/name).read_bytes()).hexdigest()
assert all(codechecks.values())
tree=ast.parse((Path('/evidence/extended/navigation-primary-review/retained-protocol.py')).read_text())
# The retained protocol driver is copied into the evidence directory.
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='guards');exec(compile(ast.Module(body=[node],type_ignores=[]),'<frozen guard definitions>','exec'))
rows=[]
for i,name in enumerate(['a','b']):
 s=Study(root/'short-outer-profile'/name);im=s.render(p,co);diff=float(np.max(np.abs(im-np.load(packet/f'trial0-ref{i}-material.npy'))));assert diff==0
 now=guards(s,p,im);old=r['baseline'][i];expected=r['candidate']['scores'][i]
 assert now==expected
 assert now['E']<=old['E'] and now['glass']['rmse']<=old['glass']['rmse'] and now['exterior']['rmse']<=old['exterior']['rmse'] and all(v<=old['foreground_mse'][k] for k,v in now['foreground_mse'].items())
 prior=json.loads(Path('/evidence/extended/navigation-primary-review/accepted-verification.json').read_text()); oldp=json.loads((root/'combined-outer-saved/candidate-native.json').read_text())['parameters']; assert {k:v for k,v in p.items() if k!='rim_width'}=={k:v for k,v in oldp.items() if k!='rim_width'}; center=prior['observations'][i]['center_support'];sub=prior['observations'][i]['emitted_support']; assert sub['passed']
 rows.append(dict(observation=name.upper(),native_pixel_max_difference=diff,previous=old,candidate=now,center_support=center,emitted_support=sub));print(name,now['E'],sub,flush=True)
report=dict(codechecks=codechecks,observations=rows,native_replay=True,source_support_verified=True,visual_review=False,accepted=False,scope='Primary renderer/native all16 foreground and exterior/source verification; baseline arrays and completed agent controls reused, no optimizer or baseline rerender.')
(out/'verification-pending-visual.json').write_text(json.dumps(report,indent=2)+'\n')
