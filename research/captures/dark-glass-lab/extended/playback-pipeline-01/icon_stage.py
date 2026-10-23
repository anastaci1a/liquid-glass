import os,time,json,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import minimize
from vector_foreground import _coverage
from settled import icon_color
from reproduce import CASES,scores,points,masks
os.umask(2);cv2.setNumThreads(1)
P=Path('/evidence/extended/playback-pipeline-01');D=P/'icon';assert not (D/'result.json').exists()
START=time.time();DEADLINE=datetime.datetime(2026,10,22,9,12,57,tzinfo=datetime.timezone.utc).timestamp()
case=CASES['media'];x0,y0,x1,y1=case['crop'];L=245.;R=Path('/evidence/extended/playback-short-round/pass-03');p=json.loads((R/'replay-record.json').read_text())['recipe'];M=np.load(P/'blurriness/raw-lens-material.npy');B=np.load(P/'blurriness/candidate-material.npy');A=np.load(P/'blurriness/coverage.npy');clear=np.load(P/'blurriness/clear-premultiplied.npy');old=np.load(P/'blurriness/candidate-complete.npy');ref=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)[y0:y1,x0:x1]/255
box=tuple(int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L']));a,b,c,d=box;sl=np.s_[b-y0:d-y0,a-x0:c-x0];alpha=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255
body=(B*A[...,None]+clear).astype(np.float32);oldcolor=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L)
def comp(al,col):
 C=body.copy();C[sl]=C[sl]*(1-al[...,None])+col[sl]*al[...,None];return C
assert np.array_equal(comp(alpha,oldcolor),old)
ys,xs,dx,dy=points(case);sd,_,_,_=masks(case,xs,ys,dx,dy);fg=np.zeros(sd.shape,bool)
for aa,bb,cc,dd in case['foreground']:fg|=(xs>=aa)&(xs<=cc)&(ys>=bb)&(ys<=dd)
def measure(C):
 s=scores(C,ref,case);s['foreground_MSE']=float(np.mean(((C-ref)[fg]*255)**2));s['exterior_MSE']=float(np.mean(((C-ref)[sd>0]*255)**2));return s
base=measure(old)
def guards(s):
 g={k:s[k]['rmse']<=base[k]['rmse'] for k in ['train','held_blocks','all_glass','rim','outer_rim','interior']};g.update(ssim=s['ssim']>=base['ssim'],foreground=s['foreground_MSE']<=base['foreground_MSE'],exterior=s['exterior_MSE']<=base['exterior_MSE']);return g
raw=(D/'original-play.svg').read_bytes();ratio=536.0062488430746/610.058892827182;count=0;best=None
shape_deadline=min(time.time()+420,DEADLINE)
def fun(v):
 global count,best
 if count>=48 or time.time()>shape_deadline:raise RuntimeError('SHAPE_BUDGET')
 h,cx,cy=v;w=h*ratio;placement=(cx-w/2,cy-h/2,cx+w/2,cy+h/2);al=_coverage(raw,box,placement,1).astype(float);loss=float(np.mean((al-alpha)**2));count+=1
 if best is None or loss<best['loss']:best={'loss':loss,'parameters':list(map(float,v)),'placement':placement,'alpha':al}
 return loss
try:minimize(fun,[214,979,544.5],method='Powell',bounds=[(208,220),(975,983),(541,548)],options={'maxfev':48,'xtol':.01,'ftol':1e-9})
except RuntimeError as e:assert str(e)=='SHAPE_BUDGET'
shapeC=comp(best['alpha'],oldcolor);shapeS=measure(shapeC);shapeG=guards(shapeS);shapeok=all(shapeG.values());np.save(D/'original-vector-alpha.npy',best.pop('alpha'));np.save(D/'original-vector-complete.npy',shapeC)
shape={'source':'Existing original SF play.tag.color, exact UI weight unestablished','evaluations':count,**best,'scores':shapeS,'guards':shapeG,'accepted':shapeok,'input_revision_not_optical_gain':True}
(D/'shape-result.json').write_text(json.dumps(shape,indent=2)+'\n')
# Shape selection remains isolated from response. Retain old shape if original fails.
selected_alpha=np.load(D/'original-vector-alpha.npy') if shapeok else alpha
ledger=[];chosen=None
for name,src,mult in [('raw-current-background',M,1.),('postblur-current-background',B,1.)]+[(f'raw-current-gamma-{m}',M,m) for m in [.9,.95,1.05,1.1]]:
 if time.time()>DEADLINE:break
 ip=dict(p['icon']);ip['gamma']=(np.array(ip['gamma'])*mult).tolist();col=icon_color(src,ip,L);C=comp(selected_alpha,col);s=measure(C);g=guards(s);row={'trial':len(ledger),'input':name,'gamma_multiplier':mult,'scores':s,'guards':g,'accepted':all(g.values())};ledger.append(row);np.save(D/f'material-{row["trial"]}-complete.npy',C)
 if row['accepted'] and s['foreground_MSE']<base['foreground_MSE']:chosen=row;break
selected=comp(selected_alpha,oldcolor) if shapeok else old
if chosen:selected=np.load(D/f'material-{chosen["trial"]}-complete.npy')
np.save(D/'selected-complete.npy',selected)
result={'shape':shape,'material_trials':ledger,'accepted_material':chosen,'baseline_scores':base,'selected_scores':measure(selected),'zero_control_exact':True,'legacy_empirical_icon_background_dependency':chosen is None,'new_optical_rays':0,'wall_seconds':time.time()-START,'dispersion':'SKIPPED by user','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(D/'result.json').write_text(json.dumps(result,indent=2)+'\n')
# Exactly two fixed sheets; nearest neighbour 2x native crop.
for name,candidate in [('shape',shapeC),('material',np.load(D/f'material-{(chosen or ledger[0])["trial"]}-complete.npy'))]:
 rect=(865,415,1100,680);aa,bb,cc,dd=rect;canvas=Image.new('RGB',(1414,594),'white');dr=ImageDraw.Draw(canvas)
 for j,(arr,label) in enumerate([(ref,'Apple'),(old,'Accepted stage 2'),(candidate,name+(' candidate' if (shapeok if name=='shape' else chosen is not None) else ' REJECTED'))]):
  im=Image.fromarray(np.uint8(np.rint(np.clip(arr[bb-y0:dd-y0,aa-x0:cc-x0],0,1)*255))).resize((470,530),Image.Resampling.NEAREST);canvas.paste(im,(j*472,64));dr.text((j*472+4,20),label,fill='black')
 canvas.save(D/f'{name}-comparison.png')
print(json.dumps(result))
