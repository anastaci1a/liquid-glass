import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-evidence-package/code');sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
from background import paper
import toolbar_candidate as model
root=Path('/tmp/agent-toolbar-second-observation');out=Path('/tmp/agent-toolbar-B-background-proposal');out.mkdir(exist_ok=True)
B=np.asarray(Image.open(root/'frame-714.png')).astype(np.float32)/255;donor=np.asarray(Image.open(root/'frame-724.png')).astype(np.float32)/255
record=json.loads((root/'later-donors.json').read_text())['records'][0];M=np.asarray(record['matrix']);excluded=np.zeros((1080,1920),bool);excluded[280:960,440:1480]=True
source_paper,source_fit=paper(donor,excluded);target_paper,target_fit=paper(B,excluded)
ink=np.clip(donor/np.maximum(source_paper,1e-4),0,1)
registered_ink=cv2.warpAffine(ink,M,(1920,1080),flags=cv2.INTER_LINEAR,borderValue=(1,1,1))
weight=cv2.warpAffine((~excluded).astype(np.float32),M,(1920,1080),flags=cv2.INTER_LINEAR,borderValue=0)
known=(weight>1-1e-6);known=cv2.erode(known.astype(np.uint8),np.ones((3,3),np.uint8))>0
proposal=target_paper*np.where(known[...,None],registered_ink,1)
# Estimated pixels retain an unresolved-content marker; they are never called observed.
rgba=np.dstack((np.uint8(np.clip(proposal,0,1)*255),np.uint8(known)*255))
Image.fromarray(rgba).save(out/'observed-content-transfer-RGBA.png')
Image.fromarray(np.uint8(np.clip(target_paper,0,1)*255)).save(out/'estimated-paper-field.png')
Image.fromarray(np.uint8(np.clip(proposal,0,1)*255)).save(out/'proposal-preview-NOT-ACTIVE.png')
for name,mask in [('observed-scene-content',known),('estimated-paper',~known),('unresolved-content',~known)]:Image.fromarray(np.uint8(mask)*255).save(out/f'{name}-mask.png')
np.save(out/'proposal-encoded-RGB-float.npy',proposal)
# Feasibility only: pose/shape not accepted, no B glass score or paired fitting.
p=json.loads(Path('/tmp/agent-toolbar-evidence-package/recipe.json').read_text());L=172.5;cx,cy=959.,546.5
Y,X=np.mgrid[270:870,440:1480].astype(np.float64);x=(X-cx)/L;y=(Y-cy)/L;sd,*_=model.boundary(x,y,p);inside=sd<-.75/L
U,V=model.mapping(x,y,p);U=(U*L+cx).astype(np.float32);V=(V*L+cy).astype(np.float32)
blur_radius=int(np.ceil(3*p['source_sigma']*L))+1;safe=cv2.erode(known.astype(np.uint8),np.ones((2*blur_radius+1,2*blur_radius+1),np.uint8))>0
center_support=cv2.remap(known.astype(np.float32),U,V,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)>1-1e-6
kernel_support=cv2.remap(safe.astype(np.float32),U,V,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)>1-1e-6
footknown=known[270:870,440:1480];foot_excluded=excluded[270:870,440:1480]
allowed=(~excluded)&(B.min(2)>.65);assert int((allowed[270:870,440:1480]&inside).sum())==0
outside=(~excluded)&known
exterior_diff=float(np.sqrt(np.mean(((proposal-B)[outside]*255)**2)))
report={'status':'partial clean-background RECOVERY PROPOSAL, NOT ACTIVE INPUT','B_target':'frame-714.png','donor':'frame-724.png','donor_to_B':record,'method':'registered unoccluded scene ink normalized by robust source paper, transferred onto independently estimated B paper; unknown regions shown as estimated paper ONLY, not asserted blank observation','paper_source_evidence':source_fit,'paper_B_evidence':target_fit,'B_glass_pixels_used_in_paper_fit':0,'raw_donor_RGB_retained_as_exact':False,'observed_content_is_not_exact_RGB':True,'provisional_pose':{'center':[cx,cy],'L':L,'shape':'last accepted normalized shape, pose NOT frozen; independent B contour/state review required'},'coverage':{'provisional_footprint_pixels':int(inside.sum()),'observed_scene_content_fraction':float(footknown[inside].mean()),'estimated_unresolved_fraction':float((~footknown)[inside].mean()),'refracted_center_lookup_observed_fraction':float(center_support[inside].mean()),'source_3sigma_plus_bilinear_radius_native_px':blur_radius,'refracted_source_kernel_observed_fraction':float(kernel_support[inside].mean())},'exposed_non_glass_transfer_rmse_255':exterior_diff,'limits':['Donor/source shadows beyond exclusion and paper-field extrapolation remain uncertain','Photometric transfer changes RGB, even where scene content is observed','Estimated paper previews do NOT prove missing content is blank','No B optical score, optimization, model calibration or paired epoch was created','Never remove unknown-score pixels to inflate future results; source assumptions require independent lead review','A source/target/registration/masks and accepted revision2 stay immutable']}
report['files_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()}
(out/'proposal.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','B_glass_pixels_used_in_paper_fit','coverage','exposed_non_glass_transfer_rmse_255']}),flush=True)
