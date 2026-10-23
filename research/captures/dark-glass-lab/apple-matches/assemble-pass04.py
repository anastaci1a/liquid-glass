"""Complete private review set; earlier passes remain immutable."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.optimize import least_squares
from publish import read,pair,compose,coverage,CASES

root=Path('/evidence/apple-matches');fits=root/'curvature-contour';candidates=root/'pass04-candidates';out=root/'review-pass04-complete';out.mkdir(exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=ImageFont.truetype(font,17);S=ImageFont.truetype(font,13)
def crop(im,box,scale=1):return np.array(Image.fromarray(im).crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.NEAREST))
def multi(items,footer=''):
 w=items[0][1].shape[1];h=items[0][1].shape[0];im=Image.new('RGB',(len(items)*(w+2)-2,h+76),'#14171e');d=ImageDraw.Draw(im)
 for i,(title,photo)in enumerate(items):d.text((i*(w+2)+12,9),title,font=F,fill='#edf0f7');im.paste(Image.fromarray(photo),(i*(w+2),40))
 if footer:d.text((12,h+49),footer,font=S,fill='#b7c2d2')
 return im

regular=read(fits/'regular-target.png');regnew=compose('regular',CASES['regular'],regular,read(candidates/'regular-profile-3301.png'),fits)
box=CASES['regular']['crop'];pair(crop(regular,box),crop(regnew,box),('Apple','Refined stretch band and blur'),font_size=16).save(out/'01-toolbar-current.png')
pair(crop(regular,(650,369,1270,435)),crop(regnew,(650,369,1270,435)),('Apple upper rim','Refined upper rim'),font_size=16).save(out/'02-toolbar-upper-rim.png')
box=(1040,370,1210,500);pair(crop(regular,box,4),crop(regnew,box,4),('Apple: d in around','Refined stretch band; sigma 11px'),footer='4x nearest-neighbor view; encoded source blur, not a post-capture blur.',font_size=18).save(out/'07-toolbar-d-crop.png')

# Use the same newly generated exterior on both slider variants, isolating the
# interior comparison from a swap between retained/generated outer shadows.
slider=read(fits/'slider-target.png');exterior=read(candidates/'slider-generated-exterior.png')
case=CASES['slider'];x0,y0,x1,y1=case['crop'];cov=coverage('slider');sliders=[]
for name,file in [('Previous map; corrected input',candidates/'slider-original-map-corrected.png'),('New: crown 0.6, curved rear',candidates/'slider-transverse-3662-corrected.png')]:
 full=exterior.astype(float).copy();full[y0:y1,x0:x1]=read(file)*cov+full[y0:y1,x0:x1]*(1-cov);sliders.append((name,np.uint8(full)))
multi([('Apple',crop(slider,case['crop']))]+[(name,crop(im,case['crop']))for name,im in sliders],footer='Same input, scale, zero blur and computed exterior on both reconstructions; interior material fits differ.').save(out/'03-slider-comparison.png')

# Quantified blue span: a reproducible color threshold, not an exact boundary.
profiles={};columns=[647,650,655,660,665,675,685,695,705]
for name,im in [('Apple',slider)]+sliders:
 rows=[]
 for X in columns:
  col=im[480:625,X].astype(float)/255;mask=(col[:,2]-col[:,0]>.4)&(col[:,2]-col[:,1]>.15);Y=np.flatnonzero(mask)+480
  rows.append(dict(x=X,distance_from_left_tip_px=float(X-(case['center'][0]-case['half'][0])),blue_span_px=int(Y.max()-Y.min()+1)if len(Y)else None,blue_center_y=float(Y.mean())if len(Y)else None))
 profiles[name]=rows
(out/'slider-line-height.json').write_text(json.dumps(dict(method='Blue span across y480..624 at each column; B-R>0.4 and B-G>0.15 in encoded RGB. Same thresholds for all images. Small blue branches can affect the total span; this is not a physical caustic measurement.',profiles=profiles),indent=2)+'\n')
table=Image.new('RGB',(1100,420),'#14171e');d=ImageDraw.Draw(table);d.text((18,12),'Blue-line span near the left rim (pixels)',font=F,fill='#edf0f7')
headers=['From left tip','Apple','Previous reconstruction','New shape candidate']
for X,title in zip([18,220,440,760],headers):d.text((X,52),title,font=F,fill='#c2cfdf')
for row in range(len(columns)):
 y=94+row*32;d.text((18,y),f"{profiles['Apple'][row]['distance_from_left_tip_px']:g} px",font=F,fill='#edf0f7')
 for X,name in zip([220,440,760],profiles):d.text((X,y),str(profiles[name][row]['blue_span_px']),font=F,fill='#edf0f7')
d.text((18,390),'Identical blue-color threshold; all measurements use native pixels.',font=S,fill='#adb9c9');table.save(out/'08-slider-line-height.png')

# New playback control removes the outer-return branch in a radial phase map.
# It is explicitly an image-map hypothesis, not disguised closed-body tracing.
media=read(fits/'media-target.png');material=read(candidates/'media-singlefold-3461.png');new=compose('media',CASES['media'],media,material,fits).astype(float)/255
B=new.copy();B[220:875,620:1300]=material.astype(float)/255
alpha=np.zeros(media.shape[:2]);alpha[420:675,870:1095]=np.array(Image.open(root/'review-pass-02/06-white-icon-mask.png'))/255
region=media[425:667,870:1089];mask=np.zeros(media.shape[:2],np.uint8);mask[425:667,870:1089]=np.uint8((region[:,:,0]>220)&(region[:,:,1]>200)&(region[:,:,2]>160));_,labels,stats,_=cv2.connectedComponentsWithStats(mask);inside=cv2.erode(np.uint8(labels==1+np.argmax(stats[1:,cv2.CC_STAT_AREA])),np.ones((7,7),np.uint8))>0
Y,X=np.mgrid[:1080,:1920];held=((X//32+3*(Y//32))%4)==0;train=inside&~held;test=inside&held;target=media.astype(float)/255
fn=lambda p,b:1-np.array(p[:3])*(1-b)**np.array(p[3:6])
fit=least_squares(lambda p:(fn(p,B[train])-target[train]).ravel(),[.9,.9,.5,11,8,5],bounds=([0,0,0,.1,.1,.1],[1,1,1,12,12,12]),max_nfev=300)
icon=fn(fit.x,B)
# Clear the entire symbol neighborhood before compositing, including any old
# reference AA fringe that lies just outside the reused opacity mask.
new[420:675,870:1095]=B[420:675,870:1095]
new=new*(1-alpha[...,None])+icon*alpha[...,None]
new=np.uint8(np.clip(new,0,1)*255)
pair(crop(media,CASES['media']['crop']),crop(new,CASES['media']['crop']),('Apple','Single-turn phase map; calculated icon'),font_size=16).save(out/'04-playback-current.png')
box=(870,420,1095,675);pair(crop(media,box,2),crop(new,box,2),('Apple icon','White mask; channel-response shader'),footer='Calculated color from underlying reconstruction; no copied interior icon RGB.',font_size=18).save(out/'05-play-icon-color.png')
groups=[('Bottom-left',(690,570,910,810)),('Top-left',(690,290,910,530)),('Upper-right: both crossings',(1025,320,1245,560))]
sheet=Image.new('RGB',(882,3*544),'#14171e');d=ImageDraw.Draw(sheet)
for i,(title,box)in enumerate(groups):
 top=i*544;d.text((12,top+8),title+' | Apple',font=F,fill='#edf0f7');d.text((454,top+8),'New phase-map reconstruction',font=F,fill='#edf0f7');d.text((12,top+32),'2x nearest-neighbor enlargement',font=S,fill='#adb9c9');sheet.paste(Image.fromarray(crop(media,box,2)),(0,top+64));sheet.paste(Image.fromarray(crop(new,box,2)),(442,top+64))
sheet.save(out/'06-playback-rim-crops.png')
diagnostics=dict(icon_parameters=fit.x.tolist(),icon_training_rmse=float(np.sqrt(np.mean((icon[train]-target[train])**2))*255),icon_withheld_rmse=float(np.sqrt(np.mean((icon[test]-target[test])**2))*255),toolbar=json.loads((candidates/'regular-profile-3301.json').read_text()),slider_new=json.loads((candidates/'slider-transverse-3662-corrected.json').read_text()),slider_exterior=json.loads((candidates/'slider-generated-exterior.json').read_text()),playback=json.loads((candidates/'media-singlefold-3461.json').read_text()))
(out/'diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
print('Prepared eight complete-pass review figures and reproducible diagnostics',flush=True)
