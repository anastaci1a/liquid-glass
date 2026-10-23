"""Bounded image-landmark geometry and two fixed uncovered-source hypotheses."""
from pathlib import Path
import json,os,sys,hashlib
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
import cairosvg
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from crowned_footprint import field
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/mail-toolbar-round');assert not(R/'geometry-source-review.json').exists();source=json.loads((R/'source-review.json').read_text());T=np.asarray(Image.open('/evidence/apple-matches/219-100.png').convert('RGB'));H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];saved=np.load(R/'source-control-evidence.npz');train=saved['train'];held=saved['held'];X=(xx-653.5)/300;Y=(yy-701.5)/82.5;D=np.stack([np.ones_like(X),X,Y,X*X,X*Y,Y*Y],-1);co=np.linalg.lstsq(D[train],T[train]/255,rcond=None)[0];model=D@co
masks=[('upper',held&(yy<=550)),('right',held&(xx>=1040)&(yy>=570)&(yy<=840)),('lower',held&(yy>=845)),('independent_upper',(xx>=440)&(xx<=900)&(yy>=575)&(yy<=585)),('independent_lower',(xx>=590)&(xx<=940)&(yy>=815)&(yy<=825))];comp=[]
for name,m in masks:
 old=float(np.sqrt(np.mean(((saved['field'][m]-T[m]/255)*255)**2)));new=float(np.sqrt(np.mean(((model[m]-T[m]/255)*255)**2)));comp.append({'region':name,'affine':old,'quadratic':new})
# Require >=20% improvement on both fixed independent bands, no held-region regression. Input comparison only.
adopt=all(v['quadratic']<=v['affine']for v in comp[:3])and all(v['quadratic']<=.8*v['affine']for v in comp[3:])
# Same provisional capsule normal coordinates, absolute-gradient ridge ±12px. Save all peaks including weak ones.
g=T.mean(2).astype('float32');a=np.linspace(-np.pi/2,np.pi/2,180);offset=np.arange(-12,12.001,.125);pts=[]
for side,xc,angles in [('left',435,a+np.pi),('right',872,a)]:
 for theta in angles:
  nx,ny=np.cos(theta),np.sin(theta);px=(xc+nx*(82.5+offset))[None].astype('float32');py=(701.5+ny*(82.5+offset))[None].astype('float32');v=cv2.remap(g,px,py,cv2.INTER_LINEAR)[0];dv=abs(np.gradient(v,.125));j=int(dv.argmax());pts.append([float(px[0,j]),float(py[0,j]),float(dv[j])])
for side,sign in [('top',-1),('bottom',1)]:
 for x in np.arange(435,873,4):
  py=(701.5+sign*(82.5+offset))[None].astype('float32');px=np.full_like(py,x);v=cv2.remap(g,px,py,cv2.INTER_LINEAR)[0];dv=abs(np.gradient(v,.125));j=int(dv.argmax());pts.append([float(x),float(py[0,j]),float(dv[j])])
pts=np.asarray(pts);valid=pts[:,2]>=.5;indices=np.arange(len(pts));fitmask=valid&(indices%4!=0);testmask=valid&(indices%4==0)
def residual(v,p,crown):
 cx,cy,a,b=v[:4];x=p[:,0]-cx;y=p[:,1]-cy
 if not crown:return np.hypot(np.maximum(abs(x)-(a-b),0),y)-b
 t,gx,gy=field(x,y,[a,b],v[4]);return(t-1)/np.maximum(np.hypot(gx,gy),1e-10)
base=least_squares(lambda v:residual(v,pts[fitmask],False),[653.5,701.5,301,82.5],bounds=([650,698,296,79.5],[657,705,306,85.5]),loss='soft_l1',f_scale=.5,max_nfev=100);fits=[]
for softness in [.08,.2]:
 z=least_squares(lambda v:residual(v,pts[fitmask],True),[*base.x,softness],bounds=([650,698,296,79.5,.002],[657,705,306,85.5,.4]),loss='soft_l1',f_scale=.5,max_nfev=100);fits.append(z)
best=min(fits,key=lambda z:np.mean(residual(z.x,pts[fitmask],True)**2));geometry={'capsule':{'parameters':base.x.tolist(),'held_normal_rmse':float(np.sqrt(np.mean(residual(base.x,pts[testmask],False)**2)))},'crown':{'parameters':best.x.tolist(),'held_normal_rmse':float(np.sqrt(np.mean(residual(best.x,pts[testmask],True)**2)))},'total_landmarks':len(pts),'strong_train':int(fitmask.sum()),'strong_held':int(testmask.sum()),'selection':'Strength>=.5 predeclared; full peaks retained; every4th held','limits':'Absolute image gradient, not known physical coverage. Crown residual first-order normal projection, not exact Euclidean distance; comparable only near boundary. No optical fit/count.'}
np.savez_compressed(R/'contour-landmarks.npz',points=pts,train=fitmask,held=testmask);fontpath=Path('/evidence/extended/icon-source/fallback/Applications/SF Symbols.app/Contents/Resources/Fonts/SFSymbolsFallback.otf');font=TTFont(fontpath);gs=font.getGlyphSet(location={'wght':400});glyphs=[];sheet=Image.new('RGB',(768,230),'white');draw=ImageDraw.Draw(sheet)
for i,(name,glyph)in enumerate([('trash','trash.tag.color.large'),('folder','folder.tag.color.large'),('reply','arrowshape.turn.up.backward.crop.color.large')]):
 bp=BoundsPen(gs);gs[glyph].draw(bp);l,b,r,t=bp.bounds;pen=SVGPathPen(gs);gs[glyph].draw(pen);raw=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {r-l} {t-b}"><path fill="#000" transform="translate({-l} {t}) scale(1 -1)" d="{pen.getCommands()}"/></svg>\n';(R/(name+'-original.svg')).write_text(raw);png=cairosvg.svg2png(bytestring=raw.encode(),output_width=120,output_height=140);q=cv2.imdecode(np.frombuffer(png,'uint8'),cv2.IMREAD_UNCHANGED);rgba=Image.fromarray(cv2.cvtColor(q,cv2.COLOR_BGRA2RGBA));sheet.paste(rgba,(i*256+128,50),rgba);bb=next(v['dark_bbox']for v in source['glyph_bounds']if v['name']==name);crop=Image.fromarray(T).crop(bb);crop.thumbnail((110,140));sheet.paste(crop,(i*256+6,50));draw.text((i*256+4,12),name+' Apple / default font',fill='black');glyphs.append({'name':name,'glyph':glyph,'weight':400,'bounds':list(bp.bounds),'svg_sha256':hashlib.sha256(raw.encode()).hexdigest(),'status':'Original font candidate, no fitted weight/pose; exact reference identity pending visual check'})
sheet.save(R/'glyph-comparison.png');out={'source_models':comp,'quadratic_conditionally_preferred':adopt,'quadratic_coefficients_rgb':co.tolist(),'geometry':geometry,'glyphs':glyphs,'optical_fits':0,'passes':0};(R/'geometry-source-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
