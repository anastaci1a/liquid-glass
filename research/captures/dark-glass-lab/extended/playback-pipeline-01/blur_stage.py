"""Fixed real geometry, ordinary source/output filtering only; cached rays."""
import os,time,json,datetime,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from geometric_render import coverage_blur
from reproduce import CASES,scores,points,masks
from settled import icon_color
os.umask(2);cv2.setNumThreads(1);START=time.time();P=Path('/evidence/extended/playback-pipeline-01');D=P/'blurriness';D.mkdir(exist_ok=True)
DEADLINE=datetime.datetime(2026,10,22,7,52,8,tzinfo=datetime.timezone.utc).timestamp()
def gate():
 if time.time()>DEADLINE:raise RuntimeError('Original20minute blur block ended; stop')
 if (D/'result.json').exists():raise RuntimeError('Completed blur study cannot restart')
gate();A=Path('/evidence/apple-matches/public-settled-replay');G=Path('/evidence/extended/geometric-playback-inferred');R=Path('/evidence/extended/playback-short-round/pass-03');case=CASES['media'];x0,y0,x1,y1=case['crop'];W=x1-x0;H=y1-y0;L=245.;p=json.loads((R/'replay-record.json').read_text())['recipe'];source=np.asarray(Image.open(A/'media-source.png'),float)/255;target=np.asarray(Image.open(A/'media-target.png'),np.float32)/255;old=np.load(G/'complete.npy');reference=target[y0:y1,x0:x1];oldicon=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L);ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];icon=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255
inverse=np.linalg.inv(np.vstack([json.loads((A/'settled-scores.json').read_text())['media']['registration']['matrix'],[0,0,1]]));ys,xs,dx,dy=points(case);sd,tr,held,valid=masks(case,xs,ys,dx,dy);fg=np.zeros((H,W),bool)
for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
exterior=sd>0;coverage=np.zeros((H,W),float);tiles=[]
for path in sorted((G/'queries').glob('*.npz')):
 row=int(path.stem);q=np.load(path);X=q['X'];Y=q['Y'];stop=row+X.shape[0]//4;yy,xx=np.mgrid[y0+row:y0+stop:1/4,x0:x1:1/4];inside=(xx-.375-960)**2+(yy-.375-542)**2<=L*L;coverage[row:stop]=inside.reshape(stop-row,4,W,4).mean((1,3));tiles.append((row,stop,X,Y,inside))
# Expanded source filters MUST be proven before a filtered source is sampled.
proof={'new_geometric_rays':0,'cached_query_count':sum(t[2].size for t in tiles),'source_kernel_radii':[0,2,3],'unsupported':0,'output_max_radius':8,'crop_min_lens_padding_native':min(715-x0,297-y0,x1-1205,y1-787),'original_registered_source_proof_sha256':hashlib.sha256((G/'source-proof-FIRST.json').read_bytes()).hexdigest()}
for row,stop,X,Y,inside in tiles:
 gate();i=np.floor(X).astype(int);j=np.floor(Y).astype(int)
 for rad in [2,3]:
  # A Gaussian source lookup needs every expanded bilinear square, not only center.
  for a,b in [(-rad,-rad),(1+rad,-rad),(-rad,1+rad),(1+rad,1+rad)]:
   xx=i+a;yy=j+b;ux=inverse[0,0]*xx+inverse[0,1]*yy+inverse[0,2];uy=inverse[1,0]*xx+inverse[1,1]*yy+inverse[1,2];proof['unsupported']+=int(((xx<0)|(yy<0)|(xx>=1920)|(yy>=1080)|(ux<0)|(uy<0)|(ux>=1919)|(uy>=1079)).sum())
assert proof['unsupported']==0 and proof['crop_min_lens_padding_native']>proof['output_max_radius'];proof['saved_before_candidate_RGB']=True;(D/'finite-filter-source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');np.save(D/'coverage.npy',coverage)
def body(src):
 M=np.zeros((H,W,3),float);clear=np.zeros_like(M)
 for row,stop,X,Y,inside in tiles:
  gate();i=np.floor(X).astype(int);j=np.floor(Y).astype(int);fx=(X-i)[...,None];fy=(Y-j)[...,None];sample=(src[j,i]*(1-fx)+src[j,i+1]*fx)*(1-fy)+(src[j+1,i]*(1-fx)+src[j+1,i+1]*fx)*fy;shape=(stop-row,4,W,4,3)
  numerator=(sample*inside[...,None]).reshape(shape).mean((1,3));M[row:stop]=np.divide(numerator,coverage[row:stop,None],out=np.zeros_like(numerator),where=coverage[row:stop,None]>0) if False else np.divide(numerator,coverage[row:stop,:,None],out=np.zeros_like(numerator),where=coverage[row:stop,:,None]>0)
  clear[row:stop]=(sample*(~inside)[...,None]).reshape(shape).mean((1,3))
 return M,clear
M0,clear=body(source);np.save(D/'raw-lens-material.npy',M0);np.save(D/'clear-premultiplied.npy',clear)
def compose(M):
 C=(coverage[...,None]*M+clear).astype(np.float32);sl=np.s_[ib-y0:id-y0,ia-x0:ic-x0];C[sl]=C[sl]*(1-icon[...,None])+oldicon[sl]*icon[...,None];return C
zero=compose(M0);assert np.array_equal(zero,old),'Native zero must match original G05 exactly'
(D/'zero-control.json').write_text(json.dumps({'maximum_native_difference':float(abs(zero-old).max()),'new_geometric_rays':0,'cached_RGB_integration_reused':7126400,'not_a_new_baseline_fit':True},indent=2)+'\n')
RECTS=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right',[1025,320,1245,560]),('center-texture',[900,690,1040,755])]
def metrics(C):
 s=scores(C,reference,case);s['foreground_fullbox_MSE']=float(np.mean(((C-reference)[fg]*255)**2));s['exterior_MSE']=float(np.mean(((C-reference)[exterior]*255)**2));local={}
 for n,(a,b,c,d) in RECTS:
  v=C[b-y0:d-y0,a-x0:c-x0];t=target[b:d,a:c];delta=(v-t)*255;local[n]={'RGB_RMSE':float(np.sqrt(np.mean(delta**2))),'luma_RMSE':float(np.sqrt(np.mean((delta@np.array([.2126,.7152,.0722]))**2)))}
 return s,local
base,base_local=metrics(old);(D/'baseline-scores.json').write_text(json.dumps({'scores':base,'local':base_local},indent=2)+'\n');ledger=[];best=None;cached={0:(M0,clear)}
for k,(ss,ps) in enumerate([(0,.5),(0,1),(0,1.25),(0,1.5),(0,1.6),(0,1.75),(0,2),(0,2.5),(.5,0),(1.,0),(.5,1.5)]):
 gate()
 if ss not in cached:
  rad=int(np.ceil(3*ss));src=cv2.GaussianBlur(source,(2*rad+1,2*rad+1),ss);cached[ss]=body(src)
 M,cl=cached[ss];assert np.array_equal(cl[coverage==0],clear[coverage==0]) if ss==0 else True
 # Clear backdrop is always the original sharp unfiltered clear premultiplied field.
 B=coverage_blur(M,coverage,ps);C=compose(B);sc,loc=metrics(C);guards={label:sc[label]['rmse']<=base[label]['rmse'] for label in ['train','held_blocks','all_glass','rim','outer_rim','interior']};guards.update(ssim=sc['ssim']>=base['ssim'],foreground=sc['foreground_fullbox_MSE']<=base['foreground_fullbox_MSE'],exterior=sc['exterior_MSE']<=base['exterior_MSE']);ok=all(guards.values());row={'trial':k,'source_sigma_native_px':ss,'output_sigma_native_px':ps,'source_sigma_over_L':ss/L,'output_sigma_over_L':ps/L,'scores':sc,'local':loc,'guards':guards,'qualifies_numerically':ok};ledger.append(row);np.save(D/f'trial-{k:02d}-complete.npy',C);np.save(D/f'trial-{k:02d}-material.npy',B);(D/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps({'trial':k,'source_sigma':ss,'output_sigma':ps,'glass':sc['all_glass']['rmse'],'baseline':base['all_glass']['rmse'],'guards':guards,'center_texture':loc['center-texture']}),flush=True)
 if ok and (best is None or sc['all_glass']['rmse']<best[0]):best=(sc['all_glass']['rmse'],k)
# Evidence sheet uses the best strict numerical candidate, otherwise best rejected diagnostic explicitly labeled.
selected=best[1] if best else min(range(len(ledger)),key=lambda k:ledger[k]['scores']['all_glass']['rmse']);row=ledger[selected];C=np.load(D/f'trial-{selected:02d}-complete.npy')
def pic(v):return Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)))
canvas=Image.new('RGB',(1324,4*544),'white');dr=ImageDraw.Draw(canvas)
for i,(name,(a,b,c,d)) in enumerate(RECTS):
 for j,(v,label) in enumerate([(target[b:d,a:c],'Apple'),(old[b-y0:d-y0,a-x0:c-x0],'G05 zero optical blur'),(C[b-y0:d-y0,a-x0:c-x0],f'Blur source{row["source_sigma_native_px"]}/output{row["output_sigma_native_px"]}')]):canvas.paste(pic(v).resize((440,480),Image.Resampling.NEAREST),(442*j,544*i+64));dr.text((442*j+5,544*i+20),name+' / '+label,fill='black')
canvas.save(D/'crops.png');result={'classification':'NUMERICAL_CANDIDATE_PENDING_VISUAL' if best else 'NO_STRICT_QUALIFIER','selected':selected,'selected_recipe':row,'trials':len(ledger),'new_geometric_rays':0,'wall_seconds':time.time()-START,'fixed_geometry':'G05','fixed_color':'unit body; historical icon separately frozen','proof':proof};(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['classification'],'selected':selected,'wall_seconds':result['wall_seconds']}))
