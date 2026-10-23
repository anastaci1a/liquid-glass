import json,sys,numpy as np
from pathlib import Path
P=Path('/evidence/extended/agent-pipeline-01');sys.path.insert(0,str(P/'code'))
from extended_fit import Study
D=Path('/evidence/extended/playback-pipeline-01/peer-expanded');verified=json.loads((D/'verification.json').read_text());ledger=json.loads((P/'blurriness/ledger.json').read_text());selected=next(r for r in ledger if r['sigma_native_px']==6.75);out={}
for key in ['a','b']:
 s=Study(P/f'inputs/{key}');masks=np.load(P/f'historical-{key}-masks.npz');C=np.load(P/'refraction/h1'/f'{key}-complete.npy');before=s.scores(C);before['E']=float(np.sqrt(before['loss']));err=(C-s.target_crop)*255;before['exterior']={'rmse':float(np.sqrt(np.mean(err[masks['exterior']]**2)))};before['foreground_MSE']=[];x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];before['foreground_MSE'].append(float(np.mean(err[b-y0:d-y0,a-x0:c-x0]**2)))
 after=selected['cases'][key]['scores'];guards={n:after[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};guards.update(E=after['E']<=before['E'],ssim=after['ssim']>=before['ssim']);guards.update({f'foreground{i}':a<=b for i,(a,b) in enumerate(zip(after['foreground_MSE'],before['foreground_MSE']))});assert all(guards.values());out[key]={'guards':guards,'E':[before['E'],after['E']]}
(D/'blur-guards.json').write_text(json.dumps({'status':'PRIMARY_BLUR_GUARDS_PASS','cases':out,'native_material_replay':'Baseline6.75pixel equality and scores already independently verified inverification.json','new_rays':0,'new_source_samples':0,'new_material_renders':0},indent=2)+'\n');print(json.dumps(out))
