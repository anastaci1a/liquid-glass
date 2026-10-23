"""Pipeline01 R1: one physical two-parameter family, bounded native patch search."""
import os,time,json,hashlib,sys,datetime
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from geometric_optics import RadialCurvatureBack,trace_flat_front_orthographic
from reproduce import CASES,points,masks,scores
from settled import icon_color
os.umask(2);cv2.setNumThreads(1)
ROOT=Path('/evidence/extended/playback-pipeline-01');OUT=ROOT/'refraction-01';OUT.mkdir(exist_ok=True)
SCHEDULE=json.loads(Path('/evidence/../liquid-glass-review/pipeline-01/schedule.json').read_text()) if False else None
NOT_BEFORE=datetime.datetime(2026,10,22,7,1,50,tzinfo=datetime.timezone.utc).timestamp();HARD_END=datetime.datetime(2026,10,22,9,1,50,tzinfo=datetime.timezone.utc).timestamp()
if time.time()<NOT_BEFORE:raise RuntimeError('Inspection block has not ended; no shape evaluation yet')
if (OUT/'result.json').exists():raise RuntimeError('Completed R1 cannot restart')
START=time.time();DEADLINE=min(START+35*60,HARD_END)
def gate():
 if time.time()>DEADLINE:raise RuntimeError('R1 deadline; preserve partial results and stop')
A=Path('/evidence/apple-matches/public-settled-replay');G=Path('/evidence/extended/geometric-playback-inferred');R=Path('/evidence/extended/playback-short-round/pass-03');record=json.loads((R/'replay-record.json').read_text());p=record['recipe'];case=CASES['media'];L=245.;cx,cy=case['center'];x0,y0,x1,y1=case['crop'];W=x1-x0;H=y1-y0
for name,digest in record['input_sha256'].items():assert hashlib.sha256((A/name).read_bytes()).hexdigest()==digest
source=np.asarray(Image.open(A/'media-source.png'),float)/255;target=np.asarray(Image.open(A/'media-target.png'),np.float32)/255;old=np.load(G/'complete.npy');reg=json.loads((A/'settled-scores.json').read_text())['media']['registration'];inverse=np.linalg.inv(np.vstack([reg['matrix'],[0,0,1]]));profile=np.load('/evidence/extended/geometric-playback-inverse/geometry-513.npz');nodes=profile['nodes'];curv=profile['curvature'];c0=float(nodes[0]);oldicon=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L)
icon_box=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];ia,ib,ic,id=icon_box;icon_alpha=np.asarray(Image.open(ROOT/'code'/p['icon']['coverage']),float)/255
RECTS=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right',[1025,320,1245,560])]
ys,xs=np.mgrid[y0:y1,x0:x1];_,_,_,valid=masks(case,xs.astype(np.float32),ys.astype(np.float32),(xs-cx).astype(np.float32),(ys-cy).astype(np.float32))
def surface(dc,amp):
 c=c0+dc;ratio=(1-c)/(1-c0);kk=c+(nodes-c0)*ratio;kk[-1]=1.;return RadialCurvatureBack(kk,amp*curv/ratio**2)
def qtiles(s,rects):
 proof=dict(rays=0,scored_subrays=0,incomplete=0,unsupported=0,source_bounds=[1e10,1e10,-1e10,-1e10],max_height=s.maximum_height,slope_bound=s.slope_bound,model_source_not_truth=True);tiles=[]
 for name,(a,b,c,d) in rects:
  for row in range(b,d,24):
   gate();stop=min(row+24,d);yy,xx=np.mgrid[row:stop:1/4,a:c:1/4];q=trace_flat_front_orthographic(s,(xx-.375-cx)/L,(yy-.375-cy)/L,1.5,2.);X=q['X']*L+cx;Y=q['Y']*L+cy
   proof['rays']+=X.size;proof['scored_subrays']+=int(valid[row-y0:stop-y0,a-x0:c-x0].sum())*16;proof['incomplete']+=int((~q['complete']).sum());assert q['complete'].all()
   ii=np.floor(X).astype(np.int32);jj=np.floor(Y).astype(np.int32);bad=(ii<0)|(jj<0)|(ii+1>=1920)|(jj+1>=1080)
   for u,v in [(0,0),(1,0),(0,1),(1,1)]:
    ux=inverse[0,0]*(ii+u)+inverse[0,1]*(jj+v)+inverse[0,2];uy=inverse[1,0]*(ii+u)+inverse[1,1]*(jj+v)+inverse[1,2];bad|=(ux<0)|(uy<0)|(ux>=1919)|(uy>=1079)
   proof['unsupported']+=int(bad.sum());bb=proof['source_bounds'];proof['source_bounds']=[min(bb[0],float(X.min())),min(bb[1],float(Y.min())),max(bb[2],float(X.max())),max(bb[3],float(Y.max()))]
   tiles.append((name,a,row,c,stop,X,Y))
 assert proof['incomplete']==proof['unsupported']==0
 return tiles,proof

def render_tiles(tiles,rects):
 outputs={name:np.empty((d-b,c-a,3),np.float32) for name,(a,b,c,d) in rects};boxes=dict(rects)
 for name,a,b,c,d,X,Y in tiles:
  gate();i=np.floor(X).astype(int);j=np.floor(Y).astype(int);fx=(X-i)[...,None];fy=(Y-j)[...,None];C=(source[j,i]*(1-fx)+source[j,i+1]*fx)*(1-fy)+(source[j+1,i]*(1-fx)+source[j+1,i+1]*fx)*fy
  ox,oy,_,_=boxes[name];outputs[name][b-oy:d-oy]=C.reshape(d-b,4,c-a,4,3).mean((1,3))
 for name,(a,b,c,d) in rects:
  left=max(a,ia);top=max(b,ib);right=min(c,ic);bottom=min(d,id)
  if left<right and top<bottom:
   al=icon_alpha[top-ib:bottom-ib,left-ia:right-ia,None];sl=np.s_[top-b:bottom-b,left-a:right-a];outputs[name][sl]=outputs[name][sl]*(1-al)+oldicon[top-y0:bottom-y0,left-x0:right-x0]*al
 return outputs

def gradient(im):
 lum=cv2.GaussianBlur((im@np.array([.2126,.7152,.0722],np.float32)).astype(np.float32),(0,0),1.)
 return np.stack([cv2.Sobel(lum,cv2.CV_32F,1,0,ksize=3)/8,cv2.Sobel(lum,cv2.CV_32F,0,1,ksize=3)/8],-1)
features={}
for name,(a,b,c,d) in RECTS:
 yy,xx=np.mgrid[b:d,a:c];r=np.hypot(xx-cx,yy-cy)/L;mask=valid[b-y0:d-y0,a-x0:c-x0]&(r>.70)&(r<.94)
 for aa,bb,cc,dd in case['foreground']:mask&=~((xx>=aa-10)&(xx<=cc+10)&(yy>=bb-10)&(yy<=dd+10))
 # Suppress patch boundaries where derivative uses different contextual pixels.
 mask[:5]=False;mask[-5:]=False;mask[:,:5]=False;mask[:,-5:]=False
 ref=target[b:d,a:c];gr=gradient(ref);norm=np.sum(gr*gr,-1);weight=np.sqrt(norm)/(np.sqrt(norm)+.004);features[name]=(ref,gr,norm,mask,weight)

def measure(images):
 out={};total=[]
 for name,box in RECTS:
  ref,gr,norm,mask,weight=features[name];im=images[name];gg=gradient(im);eps=.005**2;cos=(np.sum(gr*gg,-1)+eps)/np.sqrt((norm+eps)*(np.sum(gg*gg,-1)+eps));loss=float(np.sum((1-cos)[mask]*weight[mask])/weight[mask].sum());diff=(im-ref)*255
  out[name]={'signed_gradient_loss':loss,'analysis_pixels':int(mask.sum()),'RGB_RMSE':float(np.sqrt(np.mean(diff**2))),'luma_RMSE':float(np.sqrt(np.mean((diff@np.array([.2126,.7152,.0722]))**2)))};total.append(loss)
 return float(np.mean(total)),out
ledger=[];best=None
# Baseline is one declared grid member. Its frozen image is reused, no baseline ray/render repeat.
baseimages={n:old[b-y0:d-y0,a-x0:c-x0] for n,(a,b,c,d) in RECTS};base_loss,base_metrics=measure(baseimages)
(OUT/'baseline-analysis.json').write_text(json.dumps({'loss':base_loss,'local':base_metrics,'baseline_render_reused':True,'analysis_sigma_only':1.},indent=2)+'\n')
for dc in [-.02,-.01,0.,.01,.02]:
 for amp in [.94,.97,1.,1.03,1.06]:
  gate();k=len(ledger);s=surface(dc,amp)
  if dc==0 and amp==1:
   row={'dc':dc,'amplitude':amp,'loss':base_loss,'local':base_metrics,'status':'BASELINE_REUSED','rays':0};imgs=baseimages
  else:
   tiles,proof=qtiles(s,RECTS);(OUT/f'trial-{k:02d}-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');imgs=render_tiles(tiles,RECTS);loss,local=measure(imgs);row={'dc':dc,'amplitude':amp,'loss':loss,'local':local,'status':'PATCH_EVALUATED','rays':proof['rays'],'max_height':s.maximum_height,'slope_bound':s.slope_bound};np.savez(OUT/f'trial-{k:02d}-patches.npz',**imgs);del tiles
  ledger.append(row);(OUT/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps({'trial':k,'dc':dc,'amplitude':amp,'loss':row['loss'],'baseline':base_loss}),flush=True)
  if best is None or row['loss']<best[0]:best=(row['loss'],k,dc,amp)
  if len(ledger)%5==0:(OUT/'checkpoint.json').write_text(json.dumps({'evaluations':len(ledger),'best':best,'wall_seconds':time.time()-START},indent=2)+'\n')
# One full actual native candidate, if its analysis loss improves by a visible-scale fraction.
full=None
if best[0]<base_loss*.98:
 _,k,dc,amp=best;s=surface(dc,amp);rects=[('full',case['crop'])];tiles,proof=qtiles(s,rects);(OUT/'candidate-source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');C=render_tiles(tiles,rects)['full'];np.save(OUT/'candidate-complete.npy',C);np.savez(OUT/'candidate-surface.npz',nodes=s.knots,curvature=s.curvature);full={'best_grid_index':k,'dc':dc,'amplitude':amp,'surface_kind':'curvature','index':1.5,'distance':2.,'scores':scores(C,target[y0:y1,x0:x1],case),'baseline_scores':scores(old,target[y0:y1,x0:x1],case),'source':proof}
 (OUT/'candidate.json').write_text(json.dumps(full,indent=2)+'\n')
 def pic(v):return Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)))
 sheet=Image.new('RGB',(2044,H+64),'white');draw=ImageDraw.Draw(sheet)
 for j,(v,label) in enumerate([(target[y0:y1,x0:x1],'Apple'),(old,'G05 raw starting surface'),(C,f'R1 physical core/sag {dc:+.2f}/{amp:.2f}')]):sheet.paste(pic(v),(682*j,64));draw.text((682*j+8,20),label,fill='black')
 sheet.save(OUT/'comparison.png');crop=Image.new('RGB',(1324,1632),'white');dr=ImageDraw.Draw(crop)
 for i,(name,(a,b,c,d)) in enumerate(RECTS):
  for j,(v,label) in enumerate([(target[b:d,a:c],'Apple'),(old[b-y0:d-y0,a-x0:c-x0],'G05'),(C[b-y0:d-y0,a-x0:c-x0],'R1')]):crop.paste(pic(v).resize((440,480),Image.Resampling.NEAREST),(442*j,544*i+64));dr.text((442*j+5,544*i+20),name+' / '+label,fill='black')
 crop.save(OUT/'crops.png')
result={'status':'COMPLETE_PENDING_VISUAL_REVIEW' if full else 'NO_FEATURE_CANDIDATE','baseline_loss':base_loss,'best':best,'evaluations':len(ledger),'full_native_candidates':int(full is not None),'patch_ray_queries':sum(x['rays'] for x in ledger),'wall_seconds':time.time()-START,'start_utc':datetime.datetime.fromtimestamp(START,datetime.timezone.utc).isoformat(),'original_deadline_utc':datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat(),'actual_shapes_only':True,'no_color_blur_outline_changes':True}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
