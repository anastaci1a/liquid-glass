"""One native source/pose intake. No refraction fit, mask promotion or glyph matte."""
from pathlib import Path
import os,json,hashlib,sys
import cv2,numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/mail-toolbar-round');assert not(R/'source-review.json').exists();target=Path('/evidence/apple-matches/219-100.png');T=np.asarray(Image.open(target).convert('RGB'));H,W=T.shape[:2];y,x=np.mgrid[:H,:W]
# Fixed uncovered bands: above pill, right of pill, below pill and inside parent boundary; excludes compose button.
upper=(x>=360)&(x<=1240)&(y>=480)&(y<=550);right=(x>=1040)&(x<=1240)&(y>=570)&(y<=840);lower=(x>=590)&(x<=1240)&(y>=845)&(y<=855);controls=upper|right|lower;held=((x//16+3*(y//16))%4)==0;train=controls&~held;test=controls&held
X=(x-653.5)/300;Y=(y-701.5)/82.5
basis=[np.ones_like(X),X,Y];design=np.stack(basis,-1);co=np.linalg.lstsq(design[train],T[train]/255,rcond=None)[0];field=design@co
rows=[]
for name,m in [('held_all',test),('held_upper',test&upper),('held_right',test&right),('held_lower',test&lower),('independent_near_upper',(x>=440)&(x<=900)&(y>=575)&(y<=585)),('independent_near_lower',(x>=590)&(x<=940)&(y>=815)&(y<=825))]:
 e=(field-T/255)[m]*255;rows.append({'name':name,'pixels':int(m.sum()),'rmse':float(np.sqrt(np.mean(e**2))),'signed_rgb':e.mean(0).tolist(),'p95':float(np.percentile(abs(e),95))})
# Vertical ridge landmarks on the nearly horizontal body. No optical/body fitting.
g=T.mean(2).astype('float32');gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)/8
landmarks=[]
for kind,lo,hi in [('upper',610,635),('lower',770,795)]:
 for xx in np.arange(450,861,5):
  vals=abs(gy[lo:hi,xx]);j=int(vals.argmax());landmarks.append([float(xx),float(lo+j),kind,float(vals[j])])
# Provisional exposed glyph rectangles; no extracting screenshot alpha.
boxes={'trash':[400,645,496,751],'folder':[600,655,702,743],'reply':[800,650,906,744]};glyph=[]
for name,(a,b,c,d)in boxes.items():
 roi=T[b:d,a:c];ink=roi.max(2)<50;yy,xx=np.where(ink);bbox=[int(a+xx.min()),int(b+yy.min()),int(a+xx.max()+1),int(b+yy.max()+1)];glyph.append({'name':name,'dark_bbox':bbox,'median_ink_rgb':np.median(roi[ink],axis=0).tolist(),'limits':'Pure dark exposed bounds only; no alpha/stroke reconstruction or target-matte calibration'})
fontpath=Path('/evidence/extended/icon-source/fallback/Applications/SF Symbols.app/Contents/Resources/Fonts/SFSymbolsFallback.otf');font=TTFont(fontpath);names=[n for n in font.getGlyphOrder()if n.startswith(('trash.','folder.','arrowshape.turn.up'))and n.endswith('color.large')and 'fill'not in n]
np.savez_compressed(R/'source-control-evidence.npz',train=train,held=test,field=field.astype('float32'));Image.fromarray(T).crop((300,580,1010,825)).save(R/'native-target.png');Image.fromarray(np.uint8(np.rint(np.clip(field,0,1)*255))).crop((300,580,1010,825)).save(R/'source-plane-preview.png')
report={'status':'Input-only proposal, not adopted; zero optical fits/passes','target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'native_size':[W,H],'reference':'OriginalApple219/100s','pose_seed':{'center':[653.5,701.5],'half':[301,82.5],'radius':82.5,'limits':'Approximate image landmark seed; crown/physical coverage not measured yet'},'source_basis':['1','(x-653.5)/300','(y-701.5)/82.5'],'source_coefficients_rgb':co.tolist(),'controls':rows,'training_pixels':int(train.sum()),'hidden_source_observed_fraction':0,'source_limit':'Affine extrapolation from uncovered panel. Parent gradient/lighting/shadows confounded; smooth input cannot identify refraction or blur. No reference shadow or target residual pasted','body_gradient_landmarks':landmarks,'glyph_bounds':glyph,'available_original_font_names':names,'font_sha256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'fits':0,'passes':0};(R/'source-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='body_gradient_landmarks'}))
