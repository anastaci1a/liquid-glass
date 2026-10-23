"""ONE unfitted circular-material transfer. Input proposal only, no paired pass."""
import os,sys,json,copy,shutil,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image
os.umask(0o002);cv2.setNumThreads(1)
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
from vector_revision import composite
from source_support import masks,kernel_safe,confidence_at
from publish import pair
R=Path('/evidence/extended/safari-plus-source-round');A=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');assert not (R/'unfitted-transfer.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
info=json.loads((R/'source-pose.json').read_text());case=copy.deepcopy(json.loads((A/'foreground-control/proposed-a/case.json').read_text()));rec=json.loads((A/'foreground-control/proposed-baseline-recipe.json').read_text());folder=R/'b-proposed';folder.mkdir()
shutil.copyfile(Path(info['target']),folder/'target.png');shutil.copyfile(R/'plus.svg',folder/'plus.svg');fields=np.load(R/'source-proposal.npz');source=np.nan_to_num(fields['field']);defined=fields['defined'];Image.fromarray(np.uint8(np.rint(np.clip(source,0,1)*255))).save(folder/'source.png');Image.fromarray(np.uint8(defined)*255).save(folder/'known.png');Image.fromarray(np.zeros_like(defined,dtype='uint8')).save(folder/'observed.png');Image.fromarray(np.ones_like(defined,dtype='uint8')*255).save(folder/'target-visible.png')
L=round(info['pose']['radius'],3);cx,cy=[round(t,3) for t in info['pose']['center']];ink=info['glyph']['bbox'];x0,y0,x1,y1=ink;box=[x0-6,y0-6,x1+6,y1+6]
# Uniform size, bounding-square placement from exposed ink only, no geometry/weight fit.
side=max(x1-x0,y1-y0);mx=(x0+x1)/2-.5;my=(y0+y1)/2-.5
layer=dict(mode='mask',box=box,color=[0,0,0],threshold=.33,vector_asset='plus.svg',vector_box=[mx-side/2,my-side/2,mx+side/2,my+side/2],vector_sha256=sha(folder/'plus.svg'),opacity=1.)
case.update(id='safari-isolated-plus-transfer-proposal',category='Safari isolated plus — unfitted transfer',center=[cx,cy],half=[L,L],radius=L,crop=[1295,595,1520,815],foreground=[box],foreground_layers=[layer],background_estimate=dict(kind='Affine RGB plane from uncovered upper/left controls; not recovered hidden content',basis=info['source_basis'],coefficient_rgb=info['source_coefficients'],source_defined_domain=info['defined_domain'],controls=info['controls'],observed_hidden_fraction=0,uncertainty='Estimated field does not reproduce curved parent boundary visible in lower-right crop; exterior errors retained, no target shadow'),foreground_provenance=info['glyph']);case['source_sha256']={n:sha(folder/n) for n in ['source.png','target.png','known.png','observed.png','target-visible.png']};(folder/'case.json').write_text(json.dumps(case,indent=2)+'\n')
p=copy.deepcopy(rec['parameters']);scale=L/72.894
for k in ['sigma','post_sigma']:p[k]*=scale
co=np.asarray(rec['material']);s=Study(folder);M=s.render(p,co);C=composite(s,p,M);alpha=s.shape_coverage(p);scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']));yy,xx=np.mgrid[595:815,1295:1520];fg=(xx>=box[0])&(xx<box[2])&(yy>=box[1])&(yy<box[3]);ext=(s.sd>0)&(s.sd<=.35);full=s.sd>0
for name,m in [('glyph',fg),('exterior',ext),('full_visible_exterior',full)]:scores[name]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
defd,observed=masks(s);safe,k=kernel_safe(defd,s,p);counts=dict(whole=0,scored=0,whole_bad=0,scored_bad=0);bounds=[1e9,1e9,-1e9,-1e9]
for row,bottom,W,x,y in s.raster_tiles():
 X,Y,d,J=s.geometry_field(x,y,p);rx=(X*L+cx).astype('float32');ry=(Y*L+cy).astype('float32');q=confidence_at(safe,rx,ry);whole=s.shape(x,y,p)[-1][0]<=0;scored=np.repeat(np.repeat(s.valid[row:bottom],2,0),2,1)
 for name,m in [('whole',whole),('scored',scored)]:counts[name]+=int(m.sum());counts[name+'_bad']+=int((q[m]<.999999).sum())
 m=whole|scored
 if m.any():bounds=[min(bounds[0],float(rx[m].min())),min(bounds[1],float(ry[m].min())),max(bounds[2],float(rx[m].max())),max(bounds[3],float(ry[m].max()))]
np.savez_compressed(R/'unfitted-native-arrays.npz',material=M,complete=C,alpha=alpha,glass_mask=s.valid,rim_mask=s.rim,glyph_mask=fg,exterior_mask=ext)
U=np.uint8(np.rint(np.clip(C,0,1)*255));T=np.uint8(np.rint(np.clip(s.target_crop,0,1)*255));pair(T,U,('Apple source','Unfitted shared material'),font_size=16).save(R/'unfitted-native-comparison.png');pair(cv2.resize(T,(450,440),interpolation=cv2.INTER_LANCZOS4),cv2.resize(U,(450,440),interpolation=cv2.INTER_LANCZOS4),('Apple source','Unfitted shared material'),font_size=24).save(R/'unfitted-comparison.png')
record=dict(parameters=p,material=co.tolist(),case_sha256={'b-proposed':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()},vector_sha256={'b-proposed':{'plus.svg':sha(folder/'plus.svg')}},stage='UNACCEPTED_INPUT_TRANSFER_NO_FIT_OR_PAIR_COUNT',kernel_scaling='Only source/post ordinary sigma by measured radius ratio; all dimensionless geometry,lighting,material same as A',scale_ratio=scale,source_epoch_not_activated=True)
(R/'transfer-recipe.json').write_text(json.dumps(record,indent=2)+'\n');result=dict(status='SOURCE_PROPOSAL_UNFITTED_TRANSFER_NOT_ACTIVE_B',scores=scores,source_support=dict(counts=counts,bounds=bounds,finite_gaussian_radius=k,observed_fraction=0),optical_fits=0,passes=0,warning='Low-frequency input cannot identify refraction; parent panel boundary omitted by source plane. Scored errors retained; no optical or paired validation credit.');(R/'unfitted-transfer.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
