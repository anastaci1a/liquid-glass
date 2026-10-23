"""Only common encoded tone changes; fixed physical geometry/output blur."""
import os,time,json,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from geometric_render import coverage_blur,neutral_color_response
from reproduce import CASES,scores,points,masks
from settled import icon_color
os.umask(2);cv2.setNumThreads(1);START=time.time();DEADLINE=datetime.datetime(2026,10,22,8,5,53,tzinfo=datetime.timezone.utc).timestamp();P=Path('/evidence/extended/playback-pipeline-01');D=P/'color-grading';D.mkdir(exist_ok=True)
def gate():
 if time.time()>DEADLINE:raise RuntimeError('Color original20minute cap reached')
 if (D/'result.json').exists():raise RuntimeError('Completed stage cannot rerun')
A=Path('/evidence/apple-matches/public-settled-replay');R=Path('/evidence/extended/playback-short-round/pass-03');case=CASES['media'];x0,y0,x1,y1=case['crop'];L=245.;p=json.loads((R/'replay-record.json').read_text())['recipe'];M=np.load(P/'blurriness/raw-lens-material.npy');coverage=np.load(P/'blurriness/coverage.npy');clear=np.load(P/'blurriness/clear-premultiplied.npy');old=np.load(P/'blurriness/candidate-complete.npy');ref=np.asarray(Image.open(A/'media-target.png'),np.float32)[y0:y1,x0:x1]/255;oldicon=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L);ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];al=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255;sl=np.s_[ib-y0:id-y0,ia-x0:ic-x0]
ys,xs,dx,dy=points(case);sd,train,held,valid=masks(case,xs,ys,dx,dy);fg=np.zeros(sd.shape,bool)
for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
RECTS=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right',[1025,320,1245,560]),('center-texture',[900,690,1040,755])]
def compose(g,b,k):
 toned,pre=neutral_color_response(M,g,b,k,True);B=coverage_blur(toned,coverage,1.7);C=(coverage[...,None]*B+clear).astype(np.float32);C[sl]=C[sl]*(1-al[...,None])+oldicon[sl]*al[...,None];audit={'applied_after_AA_before_output_blur':True,'covered_pixels':int((coverage>0).sum()),'minimum_preclip':float(pre[coverage>0].min()),'maximum_preclip':float(pre[coverage>0].max()),'clipped_channels':int(((pre<0)|(pre>1))[coverage>0].sum())};return C,B,audit
zero,_,_=compose(1,0,0);assert np.array_equal(zero,old);(D/'zero-control.json').write_text(json.dumps({'max_difference':float(abs(zero-old).max()),'new_geometric_rays':0},indent=2)+'\n')
def measure(C):
 sc=scores(C,ref,case);sc['foreground_MSE']=float(np.mean(((C-ref)[fg]*255)**2));sc['exterior_MSE']=float(np.mean(((C-ref)[sd>0]*255)**2));local={}
 for name,(a,b,c,d) in RECTS:
  v=C[b-y0:d-y0,a-x0:c-x0];rr=ref[b-y0:d-y0,a-x0:c-x0];dif=(v-rr)*255;local[name]={'RGB_RMSE':float(np.sqrt(np.mean(dif**2))),'signed_RGB':dif.mean((0,1)).tolist(),'luma_RMSE':float(np.sqrt(np.mean((dif@np.array([.2126,.7152,.0722]))**2)))}
 return sc,local
base,baselocal=measure(old);(D/'baseline-scores.json').write_text(json.dumps({'scores':base,'local':baselocal},indent=2)+'\n')
# One closed-form two-column least-squares fit on originalTRAIN only.
B0=np.load(P/'blurriness/candidate-material.npy');factor=np.ones(sd.shape);factor[sl]*=1-al;bg=coverage[...,None]*B0*factor[...,None];bb=np.broadcast_to((coverage*factor)[...,None],bg.shape);X=np.stack([bg[train].ravel(),bb[train].ravel()],-1);Y=(ref-old)[train].ravel();step=np.linalg.lstsq(X,Y,rcond=None)[0];g=float(np.clip(1+step[0],.85,1.20));b=float(np.clip(step[1],-.08,.08));proposal={'unbounded_gain':1+float(step[0]),'unbounded_bias':float(step[1]),'bounded_gain':g,'bounded_bias':b,'train_only':True,'basis_condition':float(np.linalg.cond(X))};(D/'affine-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
ledger=[];accepted=None

def evaluate(g,b,k,family):
 global accepted
 gate();C,B,audit=compose(g,b,k);sc,local=measure(C);guards={key:sc[key]['rmse']<=base[key]['rmse'] for key in ['train','held_blocks','all_glass','rim','outer_rim','interior']};guards.update(ssim=sc['ssim']>=base['ssim'],foreground=sc['foreground_MSE']<=base['foreground_MSE'],exterior=sc['exterior_MSE']<=base['exterior_MSE']);row={'trial':len(ledger),'family':family,'gain':g,'bias':b,'highlight_lift':k,'scores':sc,'local':local,'guards':guards,'strict_pass':all(guards.values()),'clipping':audit};ledger.append(row);np.save(D/f'trial-{row["trial"]:02d}-complete.npy',C);np.save(D/f'trial-{row["trial"]:02d}-material.npy',B);(D/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps({'trial':row['trial'],'family':family,'g':g,'b':b,'k':k,'glass':sc['all_glass']['rmse'],'guards':guards,'clip':audit}),flush=True)
 if row['strict_pass'] and sc['all_glass']['rmse']<base['all_glass']['rmse']:accepted=row
 return row
for t in [1.,.5,.25,.125]:
 row=evaluate(1+t*(g-1),t*b,0,'common_affine')
 if accepted:break
if accepted is None:
 for k in [.03,.06,.09,.12]:
  row=evaluate(1,0,k,'source_luminance_highlight_lift')
  if accepted:break
# Final candidate or best rejected diagnostic remains explicitly separated.
selected=accepted or min(ledger,key=lambda z:z['scores']['all_glass']['rmse']);C=np.load(D/f'trial-{selected["trial"]:02d}-complete.npy');B=np.load(D/f'trial-{selected["trial"]:02d}-material.npy');np.save(D/'candidate-complete.npy',C);np.save(D/'candidate-material.npy',B)
result={'status':'STRICT_CANDIDATE_PENDING_VISUAL' if accepted else 'NO_QUALIFIER','selected':selected,'candidates':len(ledger),'original_deadline_utc':datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat(),'wall_seconds':time.time()-START,'new_geometric_rays':0,'geometry_blur_alpha_source_icon_unchanged':True};(D/'result.json').write_text(json.dumps(result,indent=2)+'\n')
canvas=Image.new('RGB',(1324,4*544),'white');dr=ImageDraw.Draw(canvas)
for i,(name,(a,b,c,d)) in enumerate(RECTS):
 for j,(v,label) in enumerate([(ref[b-y0:d-y0,a-x0:c-x0],'Apple'),(old[b-y0:d-y0,a-x0:c-x0],'Accepted geometry+blur'),(C[b-y0:d-y0,a-x0:c-x0],'Tone candidate' if accepted else 'REJECTED tone diagnostic')]):
  im=Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)));im=im.resize((440,int(round(im.height*440/im.width))),Image.Resampling.NEAREST);canvas.paste(im,(442*j,544*i+64));dr.text((442*j+5,544*i+20),name+' / '+label,fill='black')
canvas.save(D/'crops.png');print(json.dumps({'status':result['status'],'selected_trial':selected['trial'],'candidates':len(ledger),'proposal':proposal,'wall_seconds':result['wall_seconds']}))
