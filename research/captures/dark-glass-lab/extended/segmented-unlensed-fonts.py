"""Measure the Month input from an independently unoccluded label."""
from pathlib import Path
import sys,json,hashlib,copy,xml.etree.ElementTree as ET
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import minimize
from font_vector import export
from vector_foreground import coverage
from switch_source import frame
root=Path('/evidence/extended');out=root/'segmented-unlensed-fonts';out.mkdir(exist_ok=True)
cap=cv2.VideoCapture(str(root/'sources/details.mp4'));im,_=frame(cap,17.0);cap.release();records=[]
for text,box in [('Week',[370,500,600,590]),('Month',[820,500,1090,590])]:
 a,b,c,d=box;T=im[b:d,a:c].astype(np.float32)/255;seed=T.mean(2)<.7
 Y,X=np.where(seed);cx=a+(X.min()+X.max())/2;cy=b+(Y.min()+Y.max())/2;h0=Y.max()-Y.min()+1
 stencil=cv2.dilate(seed.astype(np.uint8),np.ones((5,5),np.uint8))*255
 B=cv2.inpaint(np.rint(T[:,:,::-1]*255).astype(np.uint8),stencil,5,cv2.INPAINT_TELEA)[:,:,::-1].astype(np.float32)/255;trials=[]
 for family,weight in ([('Text','Medium')] if text=='Week' else [(f,w) for f in ['Text','Display'] for w in ['Regular','Medium','Semibold']]):
  font=root/f'icon-source/fonts/Library/Fonts/SF-Pro-{family}-{weight}.otf';raw,meta=export(font,text=text,size_pt=17);name=f'{text}-{family}-{weight}.svg';(out/name).write_text(raw)
  vb=list(map(float,ET.fromstring(raw).attrib['viewBox'].split()));ar=vb[2]/vb[3]
  layer=dict(box=box,vector_asset=name,vector_sha256=hashlib.sha256(raw.encode()).hexdigest())
  def evaluate(v,detail=False):
   px,py,h=v;w=h*ar
   if px-w/2<a or px+w/2>c or py-h/2<b or py+h/2>d:return (1e5,None,None) if detail else 1e5
   layer['vector_box']=[px-w/2,py-h/2,px+w/2,py+h/2];A=coverage(out,layer)
   C=np.clip(np.sum(A[...,None]*(T-B*(1-A[...,None])),(0,1))/max(np.sum(A*A),1e-9),0,1)
   loss=float(np.mean((B*(1-A[...,None])+C*A[...,None]-T)**2))*255**2
   return (loss,C,dict(layer)) if detail else loss
  f=minimize(evaluate,[cx,cy,h0],method='Powell',bounds=[(cx-2,cx+2),(cy-2,cy+2),(h0*.92,min(h0*1.08,(c-a-2)/ar))],options=dict(maxfev=180,xtol=.01,ftol=1e-7))
  loss,C,layer=evaluate(f.x,True);trials.append(dict(loss=loss,color=C.tolist(),layer=layer,pose=f.x.tolist(),provenance=meta))
 best=min(trials,key=lambda r:r['loss']);records.append(dict(text=text,selected=best,trials=trials,source_reference=dict(video='details',seconds=17.,lens_occlusion=False)));print(text,best['provenance']['font_file'],best['pose'],best['loss'],flush=True)
old=json.loads((root/'segmented-font-calibration.json').read_text());base=next(r['selected'] for r in old if r['text']=='Week');week=records[0]['selected'];month=copy.deepcopy(records[1]);scale=base['pose'][2]/week['pose'][2]
def point(x,y):return [(x-week['pose'][0])*scale+base['pose'][0],(y-week['pose'][1])*scale+base['pose'][1]]
def normalize(r):
 q=r['layer'];x0,y0,x1,y1=q['vector_box'];q['vector_box']=[*point(x0,y0),*point(x1,y1)];x0,y0,x1,y1=q['vector_box'];q['box']=[int(x0-3),int(y0-3),int(x1+4),int(y1+4)];r['pose']=[*point(*r['pose'][:2]),r['pose'][2]*scale];return r
month['selected']=normalize(month['selected']);month['reference_normalization']=dict(method='Isotropic camera scale/translation from the same unoccluded Week outline in14.6/17.0s; no lensed label is used for source size/pose.',scale=scale,from_week=week['pose'],to_week=base['pose'])
new=[month if r['text']=='Month' else {**r,'source_reference':dict(video='details',seconds=14.6,lens_occlusion=False)} for r in old]
(out/'measurements.json').write_text(json.dumps(records,indent=2)+'\n');(root/'segmented-unlensed-font-calibration.json').write_text(json.dumps(new,indent=2)+'\n');print('Unlensed Month at14.6 camera',month['selected']['pose'],'previous lensed proxy',next(r['selected']['pose'] for r in old if r['text']=='Month'),flush=True)
