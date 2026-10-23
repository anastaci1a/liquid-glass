from pathlib import Path
import json,hashlib,copy,xml.etree.ElementTree as ET
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from vector_foreground import coverage
from font_vector import export
r=Path('/evidence/extended/music-mini-expanded-vector');s=Study(r);acc=json.loads((r/'accepted.json').read_text());Bfull=s.render(acc['parameters'],np.array(acc['material']));config=s.case;dest=r/'vector-candidates';dest.mkdir(exist_ok=True)
fonts=Path('/evidence/extended/icon-source/fonts/Library/Fonts');records=[];original=json.loads((r.parent/'music-mini-expanded'/'case.json').read_text())
for index,role,weights,glyphs,text in [(1,'title',['Text-Bold','Text-Semibold','Text-Medium','Display-Bold'],[None],'All Of Me'),(2,'artist',['Text-Regular','Text-Medium','Display-Regular'],[None],'Nao'),(3,'play',['Regular','Medium','Semibold'],['play.tag.color','play.tag.color.medium','play.tag.color.large','play.for.badge.color'],None),(4,'forward',['Regular','Medium','Semibold'],['forward.tag.color','forward.tag.color.medium','forward.tag.color.large'],None)]:
 layer=copy.deepcopy(original['foreground_layers'][index]);a,b,c,d=layer['box'];x0,y0,_,_=s.crop;B=Bfull[b-y0:d-y0,a-x0:c-x0];T=s.target[b:d,a:c];seed=T.max(2)<layer['threshold']
 if layer.get('local_contrast'):
  lum=T.mean(2).astype(np.float32);closed=cv2.morphologyEx(lum,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8));seed&=(closed-lum>layer['local_contrast'])
 yy,xx=np.where(seed);cx=a+(xx.min()+xx.max())/2;cy=b+(yy.min()+yy.max())/2;H=float(yy.max()-yy.min()+1)
 candidates=[]
 for weight in weights:
  for glyph in glyphs:
   file=fonts/(f'SF-Pro-{weight}.otf' if '-' in weight else f'SF-Pro-Display-{weight}.otf')
   try:svg,provenance=export(file,glyph,text,17 if role=='title' else 15 if role=='artist' else None)
   except KeyError:continue
   name=f'{role}-{weight}-{glyph or "text"}.svg';(dest/name).write_text(svg);shape=ET.fromstring(svg).get('viewBox').split();ar=float(shape[2])/float(shape[3]);temp={**layer,'vector_asset':'vector-candidates/'+name,'vector_sha256':hashlib.sha256(svg.encode()).hexdigest()}
   max_h=min(d-b-1,(c-a-1)/ar);h0=min(H,max_h-.1)
   def evaluate(v,details=False):
    px,py,h=v;w=ar*h;temp['vector_box']=[px-w/2,py-h/2,px+w/2,py+h/2]
    if px-w/2<a-.5 or px+w/2>c-.5 or py-h/2<b-.5 or py+h/2>d-.5:return (1e6,None,None) if details else 1e6
    A=coverage(r,temp);C=np.clip(np.sum(A[...,None]*(T-B*(1-A[...,None])),(0,1))/max(float(np.sum(A*A)),1e-9),0,1);pred=B*(1-A[...,None])+C*A[...,None];loss=float(np.mean((pred-T)**2))*255**2
    return (loss,C,A) if details else loss
   start=np.array([cx,cy,h0]);bounds=[(cx-2, cx+2),(cy-2,cy+2),(max(1,h0*.85),max_h)]
   fit=minimize(evaluate,start,method='Powell',bounds=bounds,options=dict(maxfev=220,xtol=.02,ftol=1e-6));best=fit.x if fit.fun<evaluate(start) else start;loss,C,A=evaluate(best,True)
   if C is None:continue
   iou=float(np.sum((A>.5)&seed)/max(1,np.sum((A>.5)|seed)));row=dict(role=role,weight=weight,glyph=glyph,text=text,loss=loss,iou_to_thresholded_reference=iou,pose=best.tolist(),vector_box=temp['vector_box'],color=C.tolist(),evaluations=fit.nfev,provenance=provenance,source_svg=name)
   candidates.append(row);print(role,weight,glyph,round(loss,4),round(iou,4),flush=True)
 best=min(candidates,key=lambda x:x['loss']);svg=(dest/best['source_svg']).read_bytes();filename=role+'.svg';(r/filename).write_bytes(svg)
 layer={k:v for k,v in layer.items() if k not in ['threshold','neutral_only','local_contrast']};layer.update(mode='solid',vector_asset=filename,vector_sha256=hashlib.sha256(svg).hexdigest(),vector_box=best['vector_box'],color=best['color'],opacity=1.,vector_provenance=best['provenance']);config['foreground_layers'][index]=layer;records.append(dict(role=role,selected=best,candidates=candidates))
 (r/'vector-calibration-running.json').write_text(json.dumps(records,indent=2)+'\n')
(r/'case.json').write_text(json.dumps(config,indent=2)+'\n');(r/'vector-calibration.json').write_text(json.dumps(records,indent=2)+'\n');s=Study(r);s.comparison(Bfull,r/'vector-baseline.png',acc['parameters']);print('COMPLETE',[(x['role'],x['selected']['loss']) for x in records],flush=True)
