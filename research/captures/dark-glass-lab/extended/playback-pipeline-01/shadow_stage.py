from pathlib import Path
import os,time,json,datetime
import numpy as np,cv2
from PIL import Image,ImageDraw
from crowned_tensor import gaussian_coverage_shadow
from reproduce import CASES,scores,points,masks
from settled import icon_color
os.umask(2);cv2.setNumThreads(1);START=time.time();DEADLINE=datetime.datetime(2026,10,22,8,48,36,tzinfo=datetime.timezone.utc).timestamp();P=Path('/evidence/extended/playback-pipeline-01');D=P/'shadow';D.mkdir(exist_ok=True)
def gate():
 if time.time()>DEADLINE:raise RuntimeError('Original15minute shadow cap')
 if (D/'result.json').exists():raise RuntimeError('Completed shadow family cannot repeat')
case=CASES['media'];x0,y0,x1,y1=case['crop'];L=245.;A=np.load(P/'blurriness/coverage.npy');M=np.load(P/'blurriness/candidate-material.npy');clear=np.load(P/'blurriness/clear-premultiplied.npy');old=np.load(P/'blurriness/candidate-complete.npy');T=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)[y0:y1,x0:x1]/255;R=Path('/evidence/extended/playback-short-round/pass-03');p=json.loads((R/'replay-record.json').read_text())['recipe'];iconcol=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L);ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];al=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255;sl=np.s_[ib-y0:id-y0,ia-x0:ic-x0]
ys,xs,dx,dy=points(case);sd,_,_,_=masks(case,xs,ys,dx,dy);ext=sd>0;near=ext&(sd<.15*L);far=sd>.15*L;fg=np.zeros(A.shape,bool)
for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
def compose(K,o):
 C=(A[...,None]*M+clear*(1-o*K[...,None])).astype(np.float32);C[sl]=C[sl]*(1-al[...,None])+iconcol[sl]*al[...,None];return C
assert np.array_equal(compose(np.zeros(A.shape),0),old)
def measure(C):
 s=scores(C,T,case);err=(C-T)*255;s['foreground_MSE']=float(np.mean(err[fg]**2));s['exterior_MSE']=float(np.mean(err[ext]**2));s['near_exterior_RMSE']=float(np.sqrt(np.mean(err[near]**2)));s['far_exterior_RMSE']=float(np.sqrt(np.mean(err[far]**2)));return s
base=measure(old);ledger=[];best=None
for sig in [.015,.03,.06]:
 for oy in [.01,.025]:
  gate();pp={'shape':{'half':[1,1],'radius':1},'shadow':{'opacity':1.,'sigma':sig,'offset':[0,oy]}};K=gaussian_coverage_shadow(case,pp,1,4);factor=np.ones(A.shape);factor[sl]*=1-al;B=clear*K[...,None]*factor[...,None];delta=old-T;o=float(np.clip(np.sum(B[ext]*delta[ext])/np.sum(B[ext]**2),0,.15));C=compose(K,o);s=measure(C);guards={k:s[k]['rmse']<=base[k]['rmse'] for k in ['train','held_blocks','all_glass','rim','outer_rim','interior']};guards.update(ssim=s['ssim']>=base['ssim'],foreground=s['foreground_MSE']<=base['foreground_MSE'],exterior=s['exterior_MSE']<=base['exterior_MSE']);row={'trial':len(ledger),'sigma_over_L':sig,'offset_over_L':[0,oy],'opacity':o,'scores':s,'guards':guards,'strict':all(guards.values()),'maximum_visible_RGB_change_levels':float(abs((C-old)[ext]*255).max())};ledger.append(row);np.save(D/f'trial-{row["trial"]}-complete.npy',C);np.save(D/f'trial-{row["trial"]}-kernel.npy',K);(D/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps(row),flush=True)
  if row['strict'] and s['exterior_MSE']<base['exterior_MSE'] and (best is None or s['exterior_MSE']<best[0]):best=(s['exterior_MSE'],row['trial'])
chosen=best[1] if best else None;result={'status':'NUMERICAL_EXTERIOR_CANDIDATE_PENDING_VISIBLE_IDENTIFICATION' if best else 'NO_QUALIFIER','selected':chosen,'baseline_scores':base,'trials':len(ledger),'new_optical_rays':0,'source_input_changes':False,'geometry_blur_tone_icon_alpha_frozen':True,'wall_seconds':time.time()-START,'deadline':datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat()};(D/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if chosen is not None:
 C=np.load(D/f'trial-{chosen}-complete.npy');canvas=Image.new('RGB',(2044,719),'white');dr=ImageDraw.Draw(canvas)
 for j,(v,label) in enumerate([(T,'Apple'),(old,'Accepted zero generated shadow'),(C,'Generated neutral shadow candidate')]):canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255))),(682*j,64));dr.text((682*j+8,20),label,fill='black')
 canvas.save(D/'comparison.png')
print(json.dumps(result))
