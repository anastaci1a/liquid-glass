"""One finite scalar-transmission proposal on immutable Mail inputs."""
from pathlib import Path
import argparse,json,copy,numpy as np,cv2
from extended_fit import Study
from vector_revision import composite
from publish import pair
cv2.setNumThreads(1)
ap=argparse.ArgumentParser();ap.add_argument('--number',type=int,required=True);ap.add_argument('--tau',type=float,required=True);a=ap.parse_args();assert 1<=a.number<=3 and 0<=a.tau<=1
R=Path('/evidence/extended/safari-tab-pill-round');O=R/f'pass-{a.number:02d}';assert not O.exists();O.mkdir();s=Study(R/'a-canonical')
if a.number==1:rec=json.loads((R/'canonical-baseline-recipe.json').read_text());old=np.load(R/'canonical-baseline-arrays.npz');baseline=json.loads((R/'canonical-input-acceptance.json').read_text());scores0=baseline['scores'];guards0=baseline['guards']
else:
 pre=R/f'pass-{a.number-1:02d}';assert(pre/'accepted.json').exists();rec=json.loads((pre/'recipe.json').read_text());old=np.load(pre/'native-arrays.npz');previous=json.loads((pre/'proposal.json').read_text());scores0=previous['scores'];guards0=previous['guards']
co=np.zeros(23);co[:3]=co[-3:]=a.tau;co[3:6]=1-a.tau;M=s.render(rec['parameters'],co);C=composite(s,rec['parameters'],M);scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']));guards={};yy,xx=np.mgrid[600:810,1015:1330];fg=np.zeros(s.valid.shape,bool)
for name,layer in zip(['count','plus'],s.case['foreground_layers']):
 x,y,z,w=layer['box'];mask=(xx>=x)&(xx<z)&(yy>=y)&(yy<w);fg|=mask;guards['glyph_'+name]=float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2)))
for name,mask in [('combined_glyph',fg),('near_exterior',(s.sd>0)&(s.sd<=.35)),('full_exterior',s.sd>0)]:guards[name]=float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2)))
checks={k:scores[k]['rmse']<=scores0[k]['rmse']for k in ['glass','rim','held','interior']};checks.update(E=scores['E']<=scores0['E'],SSIM=scores['ssim']>=scores0['ssim']);checks.update({k:guards[k]<=guards0[k]for k in guards});checks['measurable']=scores['E']<scores0['E'];rec['tau']=a.tau;rec['material']=co.tolist();rec['stage']='SCALAR_MATERIAL_CANDIDATE_PENDING_PRIMARY_ACCEPTANCE';(O/'recipe.json').write_text(json.dumps(rec,indent=2)+'\n');np.savez_compressed(O/'native-arrays.npz',material=M,complete=C,alpha=old['alpha']);report={'scope':'Conditional one-channel-shared neutral material only, not refraction/blur calibration','tau':a.tau,'old_E':scores0['E'],'scores':scores,'guards':guards,'checks':checks,'numerical_qualifier':all(checks.values()),'accepted':False,'source_ray_footprint':'Unchanged frozeninput/map/geometry/SVG/AA/blur, original source proof reused','actual_new_native_renders':1};(O/'proposal.json').write_text(json.dumps(report,indent=2)+'\n');T=np.uint8(np.rint(s.target_crop*255));rgb=np.uint8(np.rint(np.clip(C,0,1)*255));pair(cv2.resize(T,(630,420),interpolation=cv2.INTER_LANCZOS4),cv2.resize(rgb,(630,420),interpolation=cv2.INTER_LANCZOS4),('Apple source','Neutral transmission proposal'),font_size=32).save(O/'comparison.png');print(json.dumps(report))
