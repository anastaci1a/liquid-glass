import time,json
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from geometric_render import coverage_blur
from reproduce import CASES,scores,points,masks
from settled import icon_color
D=Path('/evidence/extended/playback-pipeline-01/blurriness');P=D.parent;A=Path('/evidence/apple-matches/public-settled-replay');R=Path('/evidence/extended/playback-short-round/pass-03');case=CASES['media'];L=245.;x0,y0,x1,y1=case['crop'];p=json.loads((R/'replay-record.json').read_text())['recipe'];M=np.load(D/'raw-lens-material.npy');coverage=np.load(D/'coverage.npy');clear=np.load(D/'clear-premultiplied.npy');old=np.load('/evidence/extended/geometric-playback-inferred/complete.npy');target=np.asarray(Image.open(A/'media-target.png'),np.float32)/255
B=coverage_blur(M,coverage,1.7);C=(B*coverage[...,None]+clear).astype(np.float32);color=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L);ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];al=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255;sl=np.s_[ib-y0:id-y0,ia-x0:ic-x0];C[sl]=C[sl]*(1-al[...,None])+color[sl]*al[...,None];np.save(D/'candidate-complete.npy',C);np.save(D/'candidate-material.npy',B)
sc=scores(C,target[y0:y1,x0:x1],case);base=json.loads((D/'baseline-scores.json').read_text())['scores'];ys,xs,dx,dy=points(case);sd,_,_,_=masks(case,xs,ys,dx,dy);fg=np.zeros(sd.shape,bool)
for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
sc['foreground_fullbox_MSE']=float(np.mean(((C-target[y0:y1,x0:x1])[fg]*255)**2));sc['exterior_MSE']=float(np.mean(((C-target[y0:y1,x0:x1])[sd>0]*255)**2));guards={label:sc[label]['rmse']<=base[label]['rmse'] for label in ['train','held_blocks','all_glass','rim','outer_rim','interior']};guards.update(ssim=sc['ssim']>=base['ssim'],foreground=sc['foreground_fullbox_MSE']<=base['foreground_fullbox_MSE'],exterior=sc['exterior_MSE']<=base['exterior_MSE']);assert all(guards.values())
result={'status':'STRICT_NUMERICAL_CANDIDATE_PENDING_PEER_VISUAL_REVIEW','source_sigma_over_L':0,'post_sigma_over_L':1.7/L,'post_sigma_native_px':1.7,'finite_radius_native_px':6,'scores':sc,'baseline_scores':base,'guards':guards,'all_candidate_evaluations_total':12,'geometry':'G05 unchanged','output_blur_last_body_color_operation':True,'new_geometric_rays':0,'alpha_changed':False,'reason':'Selected texture fidelity instead of score-minimizing overblur2.5px'}
(D/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
rects=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right',[1025,320,1245,560]),('center-texture',[900,690,1040,755])];canvas=Image.new('RGB',(1324,4*544),'white');draw=ImageDraw.Draw(canvas)
for i,(name,(a,b,c,d)) in enumerate(rects):
 for j,(v,label) in enumerate([(target[b:d,a:c],'Apple'),(old[b-y0:d-y0,a-x0:c-x0],'G05 no optical blur'),(C[b-y0:d-y0,a-x0:c-x0],'Output blur1.7nativepx')]):
  im=Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)));im=im.resize((440,int(round(im.height*440/im.width))),Image.Resampling.NEAREST);canvas.paste(im,(442*j,544*i+64));draw.text((442*j+5,544*i+20),name+' / '+label,fill='black')
canvas.save(D/'candidate-crops.png');print(json.dumps(result))
