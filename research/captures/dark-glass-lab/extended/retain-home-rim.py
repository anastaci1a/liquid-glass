"""Retain the independently verified rim trial without altering earlier receipts."""
from pathlib import Path
import sys,json,copy,hashlib
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from PIL import Image
from extended_fit import Study
from paired_fit import permitted,foreground_errors
from source_support import coverage_report,supported
from motion_support import complete

root=Path('/evidence/extended/music-home-vector-corrected/paired')
probe=json.loads((root.parent/'composited-rim-probe/report.json').read_text())
old=json.loads((root/'accepted.json').read_text());assert old==probe['baseline']
assert not (root/'pass-21.json').exists()
trial=next(q for q in probe['verified'] if q['allowed'])
p=copy.deepcopy(old['parameters']);p['grazing_reflection']=dict(strength=trial['strength'],width=trial['width'],angular_power=0.,source_sigma=0.,direction=[0.,1.],environment_rgb=[1.,1.,1.])
co=np.array(old['material']);scores=[];sources=[];composites=[];studies=[]
for i,n in enumerate(['a','b']):
 s=Study(root/n);studies.append(s);s.case['foreground_response']=old['foreground_response']
 pred=s.render(p,co);score=s.scores(pred);scores.append(score)
 assert abs(score['loss']-trial['scores'][i]['loss'])<1e-6
 source=coverage_report(s,p);assert supported(s,source);sources.append(source)
 known=cv2.imread(str(s.folder/'known.png'),0).astype(np.float32)/255
 s.source=complete(s,known);s.cache.clear();display=s.render(p,co)
 file=root/'a'/('rim-final-'+n+'.png');s.comparison(display,file,p,context_completed=True)
 W=s.crop[2]-s.crop[0];H=s.crop[3]-s.crop[1];im=Image.open(file)
 rgb=np.array(im)[im.height-H:,W+2:].astype(np.float32)/255
 *_,(sd,_,_)=s.shape(s.x,s.y,p);mask=(sd<=0)&(sd>-.025)
 mse=float(np.mean(((rgb-s.target_crop)[mask]*255)**2));composites.append(mse)
 assert abs(mse-trial['actual_composite_mse'][i])<.001
 assert mse<=probe['backgrounds'][i]['baseline_composite_mse']
assert permitted(scores,old['scores'])
# Foreground verification uses the unmodified scoring input, not completed display RGB.
native=[Study(root/n) for n in ['a','b']]
fg=foreground_errors(native,p,co,old['foreground_response'])
assert all(a<=b+1e-8 for a,b in zip(fg,old['foreground_scores']['after_mse']))
new=dict(parameters=p,material=old['material'],scores=scores,foreground_response=old['foreground_response'],foreground_scores=dict(before_mse=old['foreground_scores']['after_mse'],after_mse=fg))
code=Path('/workspace/docs/liquid-glass/experiments/reconstruction/grazing_reflection.py').read_bytes()
record=dict(pass_number=21,experiment='Uniform incident rim field with independent composited-contour checks',execution_code_sha256=hashlib.sha256(code).hexdigest(),accepted=True,previous=old,current=new,trials=probe['verified'],evaluations=probe['proposal_count'],proposed_source_support=sources,composite_contour=dict(region=probe['region'],before_mse=[r['baseline_composite_mse'] for r in probe['backgrounds']],after_mse=composites),gate='Both frozen native losses/glass RMSE, shared foreground errors and actual composited contour errors must not increase.',limits='Declared uniform-white incident field is an empirical lighting approximation, not recovered Apple lighting. The source image and native masks remain unchanged.')
(root/'pass-21.json').write_text(json.dumps(record,indent=2)+'\n');(root/'accepted.json').write_text(json.dumps(new,indent=2)+'\n')
print(json.dumps(dict(scores=scores,foreground=fg,composite_contour=record['composite_contour'])))
