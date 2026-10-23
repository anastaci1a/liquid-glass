"""Fresh navigation study. Solid foreground vectors; fixed optical masks."""
from pathlib import Path
import copy,json,hashlib,shutil,xml.etree.ElementTree as ET
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study,initial
from vector_shapes import svg
from vector_foreground import coverage
from font_vector import export
root=Path('/evidence/extended');r=root/'music-navigation';assert not r.exists(),'Do not overwrite a frozen study';r.mkdir()
recovery=root/'music-recovery';names={f:f.replace('.png','-0.0.png') for f in ['source.png','target.png','known.png']}
for dest,src in names.items():shutil.copyfile(recovery/src,r/dest)
for name,shape in [('home','home'),('new','new-grid'),('library','library-stack'),('selection','selected-backing')]: (r/(name+'.svg')).write_text(svg(shape))
raw=(root/'nav-vector-survey/radio-public-export.svg').read_bytes();radio=ET.fromstring(raw);width=radio.attrib.pop('width');height=radio.attrib.pop('height');radio.set('viewBox',f'0 0 {width} {height}');(r/'radio.svg').write_bytes(ET.tostring(radio))
source_url='https://raw.githubusercontent.com/alexzhirkevich/compose-cupertino/f66875aa6f3848b30c38e42a89fc99c9ac24a585/cupertino-icons-extended/svg/outlined/dot.radiowaves.left.and.right.svg'
provenance={'home':dict(method='Existing clean symmetric Home trace, reused without geometry changes.'),'new':dict(method='Clean symmetric four-rounded-square trace; no screenshot alpha.'),'library':dict(method='Clean symmetric stacked-frame trace with a smooth beamed-note cutout; no screenshot alpha. Not claimed to be Apple original geometry.'),'radio':dict(method='Solid-vector public SF-style export; compare against observed contours, do not infer original Apple app implementation.',source_url=source_url,source_sha256=hashlib.sha256(raw).hexdigest(),license='Apache-2.0; Compose Cupertino project,2023')}
font=root/'icon-source/fonts/Library/Fonts/SF-Pro-Text-Regular.otf'
for role,text in [('home-label','Home'),('new-label','New'),('radio-label','Radio'),('library-label','Library')]:
 text_svg,p=export(font,None,text,13);(r/(role+'.svg')).write_text(text_svg);provenance[role]={**p,'source_url':'https://devimages-cdn.apple.com/design/resources/download/SF-Symbols-7.dmg','method':'Original font outlines and normal AAT tracking at13pt; intended app typeface/point size inferred, not read from Apple source.'}
roles=[('home',[420,573,526,675],True),('home-label',[416,683,537,727],True),('new',[665,578,752,672],False),('new-label',[663,683,757,727],False),('radio',[882,582,1006,669],False),('radio-label',[883,683,1009,727],False),('library',[1149,570,1239,679],False),('library-label',[1124,683,1269,727],False)]
selection=dict(mode='solid',box=[332,544,618,748],vector_asset='selection.svg',vector_sha256=hashlib.sha256((r/'selection.svg').read_bytes()).hexdigest(),vector_box=[334,546,615,746],color=[0.,0.,0.],opacity=.14,fit_style=False,vector_provenance=dict(method='Computed rounded selection backing with fixed neutral14% opacity. This reference does not establish independent secondary refraction.'))
case=dict(id=r.name,category='Regular navigation container with separate fixed selection backing',center=[831.5,647.5],half=[511.5,113.5],radius=113.5,crop=[285,495,1365,830],foreground=[[328,540,620,751],*[box for _,box,_ in roles[2:]]],foreground_layers=[selection],reference=dict(video='music',seconds=0.,url='https://www.apple.com/newsroom/videos/2025/autoplay/06/apple-introduces-a-delightful-and-elegant-new-software-design/apple-wwdc25-liquid-glass-apple-music-dynamic-tab-bars/large_2x.mp4'),input_names=names,source_sha256={f:hashlib.sha256((r/f).read_bytes()).hexdigest() for f in names},background='Masked temporal translation mosaic; fixed observed-pixel confidence, not a reconstructed photograph inferred from glass pixels.',exterior_exclusions=[[0,0,1920,512],[1345,0,1920,1080]],foreground_method='Solid icon/font outlines plus a computed fixed selection backing. Main glass scoring excludes foreground; symbols are calibrated against their actual backing.',identifiability='The mostly-white backing weakly constrains optics away from recovered text. Fitted image map/material, not recovered proprietary geometry; fixed selected backing is not an independently calibrated second lens.')
(r/'case.json').write_text(json.dumps(case,indent=2)+'\n');s=Study(r);p=initial();_,co=s.fit(p);Bfull=s.render(p,co);baseline=dict(parameters=p,material=co.tolist(),scores=s.scores(Bfull));(r/'accepted.json').write_text(json.dumps(baseline,indent=2)+'\n');(r/'initial.json').write_text(json.dumps(baseline,indent=2)+'\n')
Bfull=s.apply_foreground(Bfull.copy());records=[]
for role,box,accent in roles:
 a,b,c,d=box;x0,y0,_,_=s.crop;T=s.target[b:d,a:c];B=Bfull[b-y0:d-y0,a-x0:c-x0]
 seed=((T[:,:,0]-T[:,:,1]>.15)&(T[:,:,0]-T[:,:,2]>.08)) if accent else (T.max(2)<.60)
 yy,xx=np.where(seed);assert len(xx)>5,(role,'Empty location seed');cx=a+(xx.min()+xx.max())/2;cy=b+(yy.min()+yy.max())/2;H=float(yy.max()-yy.min()+1)
 filename=role+'.svg';root_svg=ET.parse(r/filename).getroot();v=list(map(float,root_svg.attrib['viewBox'].split()));ar=v[2]/v[3]
 layer=dict(mode='solid',box=box,vector_asset=filename,vector_sha256=hashlib.sha256((r/filename).read_bytes()).hexdigest(),vector_provenance=provenance[role],opacity=1.)
 max_h=min(d-b-1,(c-a-1)/ar);h0=min(H,max_h-.1)
 def evaluate(v,details=False):
  px,py,h=v;w=ar*h;layer['vector_box']=[px-w/2,py-h/2,px+w/2,py+h/2]
  if px-w/2<a-.5 or px+w/2>c-.5 or py-h/2<b-.5 or py+h/2>d-.5:return (1e6,None) if details else 1e6
  A=coverage(r,layer);C=np.clip(np.sum(A[...,None]*(T-B*(1-A[...,None])),(0,1))/max(float(np.sum(A*A)),1e-9),0,1);pred=B*(1-A[...,None])+C*A[...,None]
  loss=float(np.mean((pred-T)**2))*255**2;return (loss,C) if details else loss
 start=np.array([cx,cy,h0]);fit=minimize(evaluate,start,method='Powell',bounds=[(cx-2,cx+2),(cy-2,cy+2),(max(1,h0*.85),max_h)],options=dict(maxfev=300,xtol=.01,ftol=1e-7));best=fit.x if fit.fun<evaluate(start) else start;loss,C=evaluate(best,True);assert C is not None
 layer['color']=C.tolist();case['foreground_layers'].append(layer);records.append(dict(role=role,loss=loss,pose=best.tolist(),vector_box=layer['vector_box'],color=C.tolist(),evaluations=fit.nfev));print(role,loss,layer['vector_box'],flush=True)
(r/'case.json').write_text(json.dumps(case,indent=2)+'\n');(r/'vector-calibration.json').write_text(json.dumps(records,indent=2)+'\n');s=Study(r);s.comparison(s.render(p,co),r/'vector-baseline.png',p);assert s.scores(s.render(p,co))['loss']==baseline['scores']['loss'];print('Navigation baseline',baseline['scores'],flush=True)
