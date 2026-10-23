"""Build explicitly estimated selected/unselected content from vector text.

No photographed lens pixel enters the incident texture. Selected-text color,
hidden track symmetry and font choice are assumptions recorded with the input.
"""
from pathlib import Path
import sys,json,hashlib,shutil
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import minimize,least_squares
from font_vector import export
from vector_foreground import coverage
from render import geometry
from switch_source import frame,track_coverage,VIDEO_SHA
from extended_fit import Study,initial

root=Path('/evidence/extended');out=root/'segmented-matched-state-preparation'
assert not out.exists(),'Preserve existing preparation';out.mkdir()
video=root/'sources/details.mp4';assert hashlib.sha256(video.read_bytes()).hexdigest()==VIDEO_SHA
cap=cv2.VideoCapture(str(video));reference,_=frame(cap,14.6)
fontroot=root/'icon-source/fonts/Library/Fonts';font_records=[];labels={}
cache=root/'segmented-unlensed-font-calibration.json'
if cache.exists():
 font_records=json.loads(cache.read_text());labels={r['text']:r['selected'] for r in font_records}
 for file in (root/'segmented-first-preparation').glob('*.svg'):shutil.copyfile(file,out/file.name)
for text,box,accent in ([] if cache.exists() else [('Week',[290,495,550,595],False),('Month',[780,495,1120,595],True),('Year',[1360,495,1600,595],False)]):
 a,b,c,d=box;T=reference[b:d,a:c].astype(np.float32)/255
 seed=(T[:,:,0]-T[:,:,1]>.2) if accent else (T.mean(2)<.7)
 Y,X=np.where(seed);cx=a+(X.min()+X.max())/2;cy=b+(Y.min()+Y.max())/2;h0=Y.max()-Y.min()+1
 stencil=cv2.dilate(seed.astype(np.uint8),np.ones((5,5),np.uint8))*255
 B=cv2.inpaint(np.rint(T[:,:,::-1]*255).astype(np.uint8),stencil,5,cv2.INPAINT_TELEA)[:,:,::-1].astype(np.float32)/255
 trials=[]
 for family in ['Text','Display']:
  for weight in ['Regular','Medium','Semibold']:
   font=fontroot/f'SF-Pro-{family}-{weight}.otf';raw,meta=export(font,text=text,size_pt=17)
   name=f'{text}-{family}-{weight}.svg';(out/name).write_text(raw)
   import xml.etree.ElementTree as ET
   vb=list(map(float,ET.fromstring(raw).attrib['viewBox'].split()));ar=vb[2]/vb[3]
   layer=dict(box=box,vector_asset=name,vector_sha256=hashlib.sha256(raw.encode()).hexdigest())
   def evaluate(v,detail=False):
    px,py,h=v;w=h*ar
    if px-w/2<a or px+w/2>c or py-h/2<b or py+h/2>d:return (1e5,None,None) if detail else 1e5
    layer['vector_box']=[px-w/2,py-h/2,px+w/2,py+h/2]
    A=coverage(out,layer);C=np.clip(np.sum(A[...,None]*(T-B*(1-A[...,None])),(0,1))/max(np.sum(A*A),1e-9),0,1)
    pred=B*(1-A[...,None])+C*A[...,None];loss=float(np.mean((pred-T)**2))*255**2
    return (loss,C,dict(layer)) if detail else loss
   fit=minimize(evaluate,[cx,cy,h0],method='Powell',bounds=[(cx-2,cx+2),(cy-2,cy+2),(h0*.92,min(h0*1.08,(c-a-2)/ar))],options=dict(maxfev=140,xtol=.015,ftol=1e-6))
   loss,C,layer=evaluate(fit.x,True);assert C is not None
   trials.append(dict(loss=loss,color=C.tolist(),layer=layer,pose=fit.x.tolist(),provenance=meta))
  
 best=min(trials,key=lambda t:t['loss']);labels[text]=best;font_records.append(dict(text=text,selected=best,trials=trials))
 print('Font',text,best['provenance']['font_file'],best['loss'],flush=True)

cache.write_text(json.dumps(font_records,indent=2)+'\n')
Y,X=np.mgrid[:1080,:1920];records=[]
for index,(seconds,guess) in enumerate([(16.4,[1137,546,362,145]),(16.35,[1053,546,352,143])]):
 target,time=frame(cap,seconds);rgb=target.astype(np.float32)/255
 # Trace the thin outer white ridge rather than thresholding the bright
 # interior, which misses the top edge and shrinks the frozen optical mask.
 gx,gy,ghx,ghy=guess;theta=np.linspace(-np.pi/2,np.pi/2,128)
 right=np.column_stack((gx+ghx-ghy+ghy*np.cos(theta),gy+ghy*np.sin(theta)))
 left=np.column_stack((gx-ghx+ghy-ghy*np.cos(theta),gy+ghy*np.sin(theta)))
 nx=np.cos(theta);ny=np.sin(theta);xs=np.linspace(gx-ghx+ghy,gx+ghx-ghy,128)
 pp=np.vstack([right,left,np.column_stack((xs,np.full(128,gy-ghy))),np.column_stack((xs,np.full(128,gy+ghy)))])
 nn=np.vstack([np.column_stack((nx,ny)),np.column_stack((-nx,ny)),np.tile([0,-1],(128,1)),np.tile([0,1],(128,1))])
 offsets=np.linspace(-16,16,129);search=pp[:,None,:]+nn[:,None,:]*offsets[None,:,None]
 values=cv2.remap(target.mean(2).astype(np.float32),search[:,:,0].astype(np.float32),search[:,:,1].astype(np.float32),cv2.INTER_LINEAR)
 chosen=np.argmax(values-.04*offsets[None,:]**2,axis=1);pts=search[np.arange(len(pp)),chosen]
 pts=pts[(values.max(1)>248)&(np.ptp(values,axis=1)>2)]
 def shape_res(v):
  cx,cy,hx,hy,ratio=v;return geometry(pts[:,0]-cx,pts[:,1]-cy,[hx,hy],hy*ratio)[0]
 g=np.array([*guess,.9]);fit=least_squares(shape_res,g,bounds=([g[0]-25,g[1]-15,g[2]-25,g[3]-20,.45],[g[0]+25,g[1]+15,g[2]+25,g[3]+20,1.]),loss='soft_l1',f_scale=1.)
 cx,cy,hx,hy,ratio=fit.x;pose=dict(center=[cx,cy],half=[hx,hy],radius=hy*ratio)
 bg=np.median(rgb[100:250,200:500],axis=(0,1));track=np.median(rgb[480:505,320:420],axis=(0,1))
 dark=(rgb.mean(2)<float((bg.mean()+track.mean())/2)).astype(np.uint8);dark[:350]=0;dark[740:]=0;dark[:,:150]=0;dark[:,1780:]=0
 contours,_=cv2.findContours(dark,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE);parts=[c.reshape(-1,2) for c in contours if cv2.contourArea(c)>1000];tp=np.concatenate(parts).astype(float)
 sd=geometry(tp[:,0]-cx,tp[:,1]-cy,[hx,hy],pose['radius'])[0];tp=tp[sd>.6*hy]
 def track_res(v):return geometry(tp[:,0]-v[0],tp[:,1]-v[1],[v[2],v[3]],v[3])[0]
 tf=least_squares(track_res,[958,548,754,112],bounds=([940,535,720,95],[975,560,790,130]),loss='soft_l1',f_scale=.75)
 track_error=float(np.sqrt(np.mean(track_res(tf.x)**2)))
 assert track_error<1.5,'Shadow-biased or unsupported track contour; do not freeze this source'
 assert tp[:,0].min()<tf.x[0]-tf.x[2]+20 and tp[:,0].max()>tf.x[0]+tf.x[2]-20,'Both exposed ends must constrain track width/center'
 A=track_coverage(tf.x,1080,1920);base=(bg+(track-bg)*A[...,None]).astype(np.float32)
 source=base.copy();exterior=base.copy();scale=tf.x[2]/823.5
 for text,item in labels.items():
  layer=dict(item['layer']);a,b,c,d=layer['vector_box'];box=np.array([a,b,c,d],float)
  box[[0,2]]=(box[[0,2]]-957.5)*scale+tf.x[0];box[[1,3]]=(box[[1,3]]-547.5)*scale+tf.x[1]
  layer['vector_box']=box.tolist();layer['box']=[max(0,int(box[0]-3)),max(0,int(box[1]-3)),min(1920,int(box[2]+4)),min(1080,int(box[3]+4))]
  aa,bb,cc,dd=layer['box'];alpha=coverage(out,layer)[...,None]
  source[bb:dd,aa:cc]=source[bb:dd,aa:cc]*(1-alpha)+np.array([1.,.35,.4])*alpha
  gray=np.array(item['color']);exterior[bb:dd,aa:cc]=exterior[bb:dd,aa:cc]*(1-alpha)+gray*alpha
 # Copy only distant exterior RGB; selected-color incident labels remain
 # explicitly modeled, even where the unselected label is photographed.
 sd=geometry(X-cx,Y-cy,[hx,hy],pose['radius'])[0];observed=sd>max(140,.8*hy)
 label_region=(Y>470)&(Y<620)&(X>300)&(X<1620);observed&=~label_region
 source=np.where(observed[...,None],rgb,source);exterior=np.where(observed[...,None],rgb,exterior)
 dest=out if index==0 else out/'second-observation';dest.mkdir(exist_ok=True)
 files={'source.png':source,'exterior.png':exterior,'target.png':rgb,'known.png':np.ones((1080,1920),np.float32),'observed.png':observed.astype(np.float32)}
 hashes={}
 for name,array in files.items():
  BGR=array[:,:,::-1] if array.ndim==3 else array;assert cv2.imwrite(str(dest/name),np.rint(np.clip(BGR,0,1)*255).astype(np.uint8));hashes[name]=hashlib.sha256((dest/name).read_bytes()).hexdigest()
 estimate=dict(method='Symmetric capsule from both exposed end contours, excluding a0.6L lens neighborhood. Caption geometry fits only unoccluded labels: Week/Year14.6s and Month17.0s, registered by the common Week outline. Solid SF outlines are recolored for the incident layer; a separate exterior retains gray text.',limits='Hidden track, pre-refraction recoloring, unchanged selected/unselected glyph geometry and layout transfer are assumptions. Nominal selected RGB is a fixed input convention; fitted photometric response is not an independently recovered Apple ink color. Scores remain conditional on these inputs, not proof of Apple geometry or compositing.',video_sha256=VIDEO_SHA,selected_rgb=[1.,.35,.4],track_exclusion_over_L=.6,track_pose=tf.x.tolist(),track_contour_rmse=track_error,lens_contour_rmse=float(np.sqrt(np.mean(shape_res(fit.x)**2))),font_calibration=font_records)
 case=dict(id='active-segmented-selector'+('' if index==0 else '-b'),category='Active selection lens crossing vector text',**pose,parameter_length_reference=hy if index==0 else records[0]['pose']['half'][1],crop=[max(0,int(cx-hx-75)),350,min(1920,int(cx+hx+75)),800],foreground=[],foreground_layers=[],reference=dict(**time,video='details',seconds=seconds,url='https://www.apple.com/newsroom/videos/2025/autoplay/06/apple-introduces-a-delightful-and-elegant-new-software-design/apple-wwdc25-liquid-glass-details/large_2x.mp4'),input_names={n:n.replace('.png',f'-{seconds:.3f}.png') for n in files},source_sha256=hashes,exterior_source='exterior.png',source_observation_mask='observed.png',allow_estimated_background=True,background_estimate=estimate,signed_normal_profile=True,allow_center_reduction=True)
 (dest/'case.json').write_text(json.dumps(case,indent=2)+'\n');s=Study(dest);p=initial();_,co=s.fit(p);state=dict(parameters=p,material=co.tolist(),scores=s.scores(s.render(p,co)));(dest/'initial.json').write_text(json.dumps(state,indent=2)+'\n');(dest/'accepted.json').write_text(json.dumps(state,indent=2)+'\n');s.comparison(s.render(p,co),dest/'baseline.png',p,context_completed=True)
 records.append(dict(seconds=seconds,pose=pose,baseline=state['scores'],estimate=estimate));print('Baseline',seconds,pose,state['scores'],flush=True)
cap.release();(out/'construction.json').write_text(json.dumps(records,indent=2)+'\n')
