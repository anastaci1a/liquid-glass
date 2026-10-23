"""Source-only Safari plus intake; no optical fitting or source adoption."""
import os,json,hashlib,shutil
from pathlib import Path
import numpy as np,cv2
from PIL import Image
from scipy.optimize import least_squares
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/safari-plus-source-round');Tpath=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round/a/target.png')
assert not (R/'source-pose.json').exists(),'Preserve completed intake'
T=np.asarray(Image.open(Tpath).convert('RGB'));H,W=T.shape[:2];y,x=np.mgrid[:H,:W];cx,cy=1408.,705.;rad=np.hypot(x-cx,y-cy);g=T.mean(2)
# Upper and left uncovered panel. Exclude lens plus conservative neighborhood and curved/right boundary.
upper=(x>=1200)&(x<=1490)&(y>=530)&(y<=590)
left=(x>=1180)&(x<=1290)&(y>=610)&(y<=790)
controls=(upper|left)&(rad>=110)
held=((x//16+3*(y//16))%4)==0;train=controls&~held;test=controls&held
X=np.stack([np.ones_like(x),(x-cx)/100,(y-cy)/100],-1);co=np.linalg.lstsq(X[train],T[train]/255,rcond=None)[0];field=X@co
rows=[]
checks=[('held_train_domains',test),('upper',test&upper),('left',test&left),('independent_right',(x>=1520)&(x<=1540)&(y>=620)&(y<=735)),('independent_lower',(x>=1330)&(x<=1430)&(y>=810)&(y<=825))]
for name,m in checks:
 e=(field-T/255)[m]*255;rows.append(dict(name=name,pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(e**2))),signed_rgb=e.mean(0).tolist(),p95=float(np.percentile(abs(e),95))))
# Full-gradient landmarks, not an optical pose optimization.
a=np.linspace(0,2*np.pi,720,endpoint=False);rr=np.arange(66,82,.125);px=(cx+np.cos(a)[:,None]*rr).astype('float32');py=(cy+np.sin(a)[:,None]*rr).astype('float32');v=cv2.remap(g.astype('float32'),px,py,cv2.INTER_LINEAR);dv=np.gradient(v,.125,axis=1);ridges=rr[abs(dv).argmax(1)];p=np.c_[cx+np.cos(a)*ridges,cy+np.sin(a)*ridges];pose=least_squares(lambda q:np.linalg.norm(p-q[:2],axis=1)-q[2],[cx,cy,73],loss='soft_l1',f_scale=.5).x
ink=(x>=1365)&(x<=1445)&(y>=660)&(y<=749)&(g<40);iy,ix=np.where(ink);box=[int(ix.min()),int(iy.min()),int(ix.max()+1),int(iy.max()+1)]
svg=Path('/evidence/extended/toolbar-primary-review/glyphs/plus.svg');out=R/'plus.svg';shutil.copyfile(svg,out)
domain=(x>=1180)&(x<=1540)&(y>=525)&(y<=830)
# Values are modeled, never claimed recovered RGB; NaNs beyond declared domain.
np.savez_compressed(R/'source-proposal.npz',field=np.where(domain[...,None],field,np.nan).astype('float32'),defined=domain,observed=np.zeros_like(domain),train=train,held=test)
Image.fromarray(np.uint8(np.rint(np.clip(field,0,1)*255))).crop((1260,580,1550,840)).save(R/'modeled-source-preview.png')
result=dict(status='INPUT_PROPOSAL_ONLY_NOT_ADOPTED',target=str(Tpath),target_sha256=hashlib.sha256(Tpath.read_bytes()).hexdigest(),seconds=300,same_frame_as_search=True,potential='Darker-background witness for same circular material; not active pair',source_basis=['1','(x-1408)/100','(y-705)/100'],source_coefficients=co.tolist(),source_rgb_at_center=(np.array([1,(pose[0]-cx)/100,(pose[1]-cy)/100])@co).tolist(),controls=rows,training_pixels=int(train.sum()),defined_domain=[1180,525,1541,831],observed_hidden_fraction=0,limitations=['Hidden source extrapolated from uncovered controls; no target shadow or glass pixels included','Parent panel curved boundary not modeled; source domain excludes its visible dark boundary','Low-frequency background cannot constrain refraction; no optical fit or pass','Circle gradient landmark is not known physical coverage'],pose=dict(center=pose[:2].tolist(),radius=float(pose[2]),ridge_quantiles=np.percentile(ridges,[10,50,90]).tolist(),residual_p95=float(np.percentile(abs(np.linalg.norm(p-pose[:2],axis=1)-pose[2]),95))),glyph=dict(bbox=box,ink_median=np.median(T[ink],axis=0).tolist(),svg_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),provenance='Existing canonical original SF plus.tag.color.large outline; this Safari weight remains unverified',placement='Independently exposed ink bounding box; no vector geometry/weight fitted'),optical_fits=0,passes=0)
(R/'source-pose.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
