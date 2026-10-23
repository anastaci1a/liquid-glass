import os,json,hashlib,sys,datetime,shutil
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (R/'source-pose.json').exists(),'Do not repeat completed intake'
start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'))
rows=[];sheet=Image.new('RGB',(720,560),'#222');draw=ImageDraw.Draw(sheet)
for j,t in enumerate([300,290]):
 T=np.asarray(Image.open(f'/evidence/apple-matches/219-{t}.png').convert('RGB'));H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];g=T.mean(2);cx,cy=509.,705.;r=np.hypot(xx-cx,yy-cy)
 # Predeclared local affine field from uncovered panel only, excludes lens and conservative generated-shadow neighborhood.
 domain=(xx>=400)&(xx<=740)&(yy>=490)&(yy<=840);controls=domain&(r>=110)&(r<=205)&(xx>=415)&(yy<=830)
 held=((xx//16+3*(yy//16))%4)==0;train=controls&~held;test=controls&held
 X=np.stack([np.ones_like(xx),(xx-cx)/100,(yy-cy)/100],-1);co=np.linalg.lstsq(X[train],T[train]/255,rcond=None)[0];field=X@co
 result=[]
 for name,m in [('spatial_heldout',test),('upper',test&(yy<620)),('right',test&(xx>610)),('lower',test&(yy>795)),('left',test&(xx<435))]:
  e=(field-T/255)[m]*255
  result.append(dict(name=name,pixels=int(m.sum()),rgb_rmse=float(np.sqrt(np.mean(e**2))),signed_rgb=e.mean(0).tolist(),p95_absolute=float(np.percentile(abs(e),95))))
 # Contour diagnostic: radial largest positive inward-to-outward intensity gradient. Glyph excluded by radial interval.
 angles=np.linspace(0,2*np.pi,720,endpoint=False);rr=np.arange(64,81,.125);px=(cx+np.cos(angles)[:,None]*rr).astype(np.float32);py=(cy+np.sin(angles)[:,None]*rr).astype(np.float32)
 v=cv2.remap(g.astype(np.float32),px,py,cv2.INTER_LINEAR);dv=np.gradient(v,.125,axis=1);idx=dv.argmax(1);ridge=rr[idx];points=np.c_[cx+np.cos(angles)*ridge,cy+np.sin(angles)*ridge]
 pose=least_squares(lambda q:np.linalg.norm(points-q[:2],axis=1)-q[2],[cx,cy,72],loss='soft_l1',f_scale=.5).x
 # Canonical vector placement from independently exposed dark glyph bounding box only; no matte retained.
 glyphroi=(xx>=466)&(xx<=550)&(yy>=663)&(yy<=748);ink=glyphroi&(g<85);gy,gx=np.where(ink);bbox=[int(gx.min()),int(gy.min()),int(gx.max()+1),int(gy.max()+1)]
 rec=dict(seconds=t,original_png=f'/evidence/apple-matches/219-{t}.png',png_sha256=sha(Path(f'/evidence/apple-matches/219-{t}.png')),size=[W,H],source_basis=['1','(x-509)/100','(y-705)/100'],source_coefficients_rgb=co.tolist(),controls=result,training_pixels=int(train.sum()),source_domain=[400,490,741,841],excluded_radius=110,pose_diagnostic=dict(fit_circle_center=pose[:2].tolist(),bright_gradient_radius=float(pose[2]),radius_p10_p50_p90=np.percentile(ridge,[10,50,90]).tolist(),residual_p95=float(np.percentile(abs(np.linalg.norm(points-pose[:2],axis=1)-pose[2]),95)),limitation='Bright ridge is an empirical image landmark, not known physical alpha. Fixed geometry proposal follows it; do not optimize pose against optical target.'),glyph_dark_bbox=bbox,glyph_pixels=int(ink.sum()),glyph_ink_rgb_median=np.median(T[ink],axis=0).tolist())
 rows.append(rec);out=R/f'frame-{t}';out.mkdir();Image.fromarray(T).save(out/'target.png');np.savez_compressed(out/'source-controls.npz',train=train,held=test,modeled_domain=domain,field_rgb=np.where(domain[...,None],field,np.nan).astype(np.float32));crop=Image.fromarray(T).crop((400,570,680,850));sheet.paste(crop,(j*360,28));draw.text((j*360+8,8),f'219 {t}s original native crop',fill='white');print(json.dumps(rec),flush=True)
sheet.save(R/'native-contact.png');save('source-pose.json',dict(observations=rows,stage='SINGLE_A proposal, A300; B290 NOT adopted',background_diversity='Same gray panel, similar pose. Not independently distinct paired backgrounds.',source_kind='Estimated affine gray field fitted ONLY uncovered controls; hidden source observed fraction0. Not ground truth.',optical_fits=0,glyph='Reuse canonical symmetric ring/capsule MusicSearch SVG; no screenshot alpha/codec contours'))
