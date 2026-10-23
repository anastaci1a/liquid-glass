"""Freeze conditional Mail inputs and an unfitted neutral-transmission baseline."""
from pathlib import Path
import os,sys,json,copy,hashlib,shutil
import cv2,numpy as np
from PIL import Image
from scipy.optimize import least_squares
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from crowned_footprint import field
from extended_fit import Study
from vector_revision import composite
from source_support import masks,confidence_at
from publish import pair
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/mail-toolbar-round');assert not(R/'baseline.json').exists();old=json.loads((R/'source-review.json').read_text());g=json.loads((R/'geometry-source-review.json').read_text());vectors=json.loads((R/'original-vector-review.json').read_text())['candidates'];points=np.load(R/'contour-landmarks.npz');train=points['points'][points['train']]
# Reuse existing crowned-family softness.1 as a declared prior; data improvement.04px cannot identify softness robustly.
def res(v):
 cx,cy,a,b=v;t,gx,gy=field(train[:,0]-cx,train[:,1]-cy,[a,b],.1);return(t-1)/np.maximum(np.hypot(gx,gy),1e-10)
fit=least_squares(res,g['geometry']['capsule']['parameters'],bounds=([650,698,296,79.5],[657,705,306,85.5]),loss='soft_l1',f_scale=.5,max_nfev=100);cx,cy,major,L=[float(q)for q in fit.x];folder=R/'a';folder.mkdir();shutil.copyfile('/evidence/apple-matches/219-100.png',folder/'target.png');T=np.asarray(Image.open(folder/'target.png'));H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];co_source=np.asarray(old['source_coefficients_rgb']);D=np.stack([np.ones_like(xx),(xx-653.5)/300,(yy-701.5)/82.5],-1);source=D@co_source;defined=(xx>=250)&(xx<=1310)&(yy>=420)&(yy<=890);rgb=np.uint8(np.rint(np.clip(np.where(defined[...,None],source,0),0,1)*255));Image.fromarray(rgb).save(folder/'source.png');Image.fromarray(np.uint8(defined)*255).save(folder/'known.png');Image.fromarray(np.zeros_like(defined,dtype='uint8')).save(folder/'observed.png');Image.fromarray(np.ones_like(defined,dtype='uint8')*255).save(folder/'target-visible.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();layers=[]
for v in vectors:
 name=v['name'];bb=next(t['dark_bbox']for t in old['glyph_bounds']if t['name']==name);box=[bb[0]-7,bb[1]-7,bb[2]+7,bb[3]+7];asset=name+'-outline.svg';shutil.copyfile(R/asset,folder/asset);layers.append({'mode':'mask','box':box,'color':[0,0,0],'threshold':.3,'vector_asset':asset,'vector_box':v['placement'],'vector_sha256':v['svg_sha256'],'opacity':1.})
case={'id':'mail-three-action-single-a','category':'Mail three-action toolbar, conditional material study','radial':False,'center':[cx,cy],'half':[major,L],'radius':L,'crop':[315,590,995,815],'foreground':[l['box']for l in layers],'foreground_layers':layers,'source_observation_mask':'observed.png','target_observation_mask':'target-visible.png','allow_estimated_background':True,'background_estimate':{'kind':'Affine RGB field from fixed uncovered upper/right/lower bands; quadratic failed predeclared independent-lower requirement','basis':old['source_basis'],'coefficient_rgb':old['source_coefficients_rgb'],'source_defined_domain':[250,420,1311,891],'controls':old['controls'],'observed_hidden_fraction':0,'uncertainty':'Parent-panel curvature/shadow/extrapolation unresolved. Rectangle is modeled domain, not panel segmentation. No texture recovery or optical identifiability from smooth field.'},'pose_provenance':{'method':'Fixed.1 shared crowned prior; image gradient normal-projection pose fit','softness_not_identified':'Capsuleheld.469px vsfreecrown.429px, improvement.041px below.1px decision margin','free_crown':g['geometry']['crown']},'reference':{'video':'219','seconds':100},'foreground_provenance':vectors};case['source_sha256']={n:sha(folder/n)for n in ['source.png','target.png','known.png','observed.png','target-visible.png']};(folder/'case.json').write_text(json.dumps(case,indent=2)+'\n')
nav=Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/music-navigation/review-round/pass-03.json');p=copy.deepcopy(json.loads(nav.read_text())['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.,crown_softness=.1)
for name in ['shape_dx','shape_dy','half_x_delta','half_y_delta','radius_delta']:p[name]=0.
p['shadow']['opacity']=0.
material=np.zeros(23);material[:3]=material[-3:]=1.
record={'parameters':p,'material':material.tolist(),'model':'neutral transmission C=tau*S+(1-tau)*1 in encodedRGB; baseline tau1','tau':1.,'stage':'INPUT_BASELINE_PROPOSAL_ZERO_VERIFIED_PASSES','geometry_seed':{'file':str(nav.name),'sha256':sha(nav),'scope':'Reused dimensionless Study geometry-field coefficients only; source/post blur, gamma, old lighting/material and shadow discarded. Source cannot identify map/blur; prior not calibrated to this Mail image.'},'case_sha256':{'a':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()},'vector_sha256':{'a':{l['vector_asset']:l['vector_sha256']for l in layers}},'large':False};(R/'baseline-recipe.json').write_text(json.dumps(record,indent=2)+'\n');s=Study(folder);M=s.render(p,material);C=composite(s,p,M);alpha=s.shape_coverage(p);scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']));yc,xc=np.mgrid[590:815,315:995];fg=np.zeros(s.valid.shape,bool)
for l in layers:a,b,c,d=l['box'];fg|=(xc>=a)&(xc<c)&(yc>=b)&(yc<d)
near=(s.sd>0)&(s.sd<=.35);full=s.sd>0
for name,m in [('glyph',fg),('exterior',near),('full_visible_exterior',full)]:scores[name]={'pixels':int(m.sum()),'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2)))}
np.savez_compressed(R/'baseline-arrays.npz',material=M,complete=C,alpha=alpha,glass_mask=s.valid,rim_mask=s.rim,glyph_mask=fg,exterior_mask=near)
# Source has no filters: finite native2x2 emitted WHOLE and ALLscored, including post footprint0.
defd,observed=masks(s);counts={'whole':0,'scored':0,'whole_bad':0,'scored_bad':0};bounds=[1e9,1e9,-1e9,-1e9]
for row,bottom,W,x,y in s.raster_tiles():
 X,Y,d,J=s.geometry_field(x,y,p);rx=(X*L+cx).astype('float32');ry=(Y*L+cy).astype('float32');q=confidence_at(defd,rx,ry);whole=s.shape(x,y,p)[-1][0]<=0;scored=np.repeat(np.repeat(s.valid[row:bottom],2,0),2,1)
 for name,m in [('whole',whole),('scored',scored)]:counts[name]+=int(m.sum());counts[name+'_bad']+=int((q[m]<.999999).sum())
 m=whole|scored
 if m.any():bounds=[min(bounds[0],float(rx[m].min())),min(bounds[1],float(ry[m].min())),max(bounds[2],float(rx[m].max())),max(bounds[3],float(ry[m].max()))]
assert counts['whole_bad']==counts['scored_bad']==0
A=np.uint8(np.rint(s.target_crop*255));B=np.uint8(np.rint(np.clip(C,0,1)*255));pair(cv2.resize(A,(720,238),interpolation=cv2.INTER_LANCZOS4),cv2.resize(B,(720,238),interpolation=cv2.INTER_LANCZOS4),('Apple source','Unfitted neutral transmission'),font_size=24).save(R/'baseline-comparison.png');out={'status':'SOURCE_POSE_VECTOR_NATIVE_BASELINE_READY_FOR_PEER_REVIEW','scores':scores,'source_support':{'counts':counts,'bounds':bounds,'ordinary_blur':0,'observed_hidden_fraction':0,'limits':'Modeled plane definedness only, no recovered hidden RGB/physical solid/optical validation'},'fits':0,'verified_passes':0,'neutral_material_scope':'Only prospective scalar tau in[0,1], material rim/core gains=tau equally inRGB, offsets=1-tau equally, all lightingcoeffs0. No RGBcast/clipping fit; no adaptivecontrast claim. Rays/shape/source/SVG frozen.'};(R/'baseline.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
