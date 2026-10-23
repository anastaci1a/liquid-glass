import json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
root=Path('/tmp/agent-toolbar-second-observation')
def read(t):return np.asarray(Image.open(root/f'frame-{t}.png')).astype(np.float32)/255
A=read(710);B=read(714);donor=read(720)
def measurement(image):
    gray=cv2.cvtColor(np.uint8(image*255),cv2.COLOR_RGB2GRAY);roi=gray[440:650,650:1270];count,labels,stats,centers=cv2.connectedComponentsWithStats(np.uint8(roi<90))
    candidates=[i for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>700 and stats[i,cv2.CC_STAT_HEIGHT]>60];candidates=sorted(candidates,key=lambda i:stats[i,cv2.CC_STAT_AREA],reverse=True)[:2];glyphs=[]
    for i in sorted(candidates,key=lambda i:centers[i][0]):
        x,y,w,h,area=map(int,stats[i]);glyphs.append({'bbox':[x+650,y+440,x+w+650,y+h+440],'area':area,'centroid':[float(centers[i][0]+650),float(centers[i][1]+440)]})
    smooth=cv2.GaussianBlur(gray.astype(np.float32),(0,0),1.2)
    horizontal=smooth[536:548].mean(0);vertical=smooth[:,900:1020].mean(1);dx=np.gradient(horizontal);dy=np.gradient(vertical)
    # Signed-edge diagnostic only: source text, rims and shadow are confounds.
    bounds={'left':int(520+np.argmax(dx[520:640])),'right':int(1280+np.argmin(dx[1280:1400])),'top':int(330+np.argmax(dy[330:430])),'bottom':int(660+np.argmin(dy[660:780]))}
    return {'glyph_components':glyphs,'signed_luma_edge_hypothesis':bounds,'limits':'edge peaks are provisional, not an accepted silhouette fit; glyph scale may include pose/state changes'}
def register(source,target):
    allowed=np.full((1080,1920),255,np.uint8);allowed[280:960,440:1480]=0
    sift=cv2.SIFT_create(nfeatures=10000);a=cv2.cvtColor(np.uint8(source*255),cv2.COLOR_RGB2GRAY);b=cv2.cvtColor(np.uint8(target*255),cv2.COLOR_RGB2GRAY);ka,da=sift.detectAndCompute(a,allowed);kb,db=sift.detectAndCompute(b,allowed)
    pairs=[m for m,n in cv2.BFMatcher().knnMatch(da,db,k=2) if m.distance<.7*n.distance];P=np.array([ka[m.queryIdx].pt for m in pairs]);Q=np.array([kb[m.trainIdx].pt for m in pairs]);M,inlier=cv2.estimateAffinePartial2D(P,Q,method=cv2.RANSAC,ransacReprojThreshold=1,maxIters=5000);good=inlier[:,0]>0;reproj=P@M[:,:2].T+M[:,2];rms=float(np.sqrt(np.mean(np.sum((reproj[good]-Q[good])**2,axis=1))));warped=cv2.warpAffine(source,M,(1920,1080))
    return M,{'matrix':M.tolist(),'matches':len(pairs),'inliers':int(good.sum()),'inlier_reprojection_rms_native_px':rms,'scale':float(np.hypot(M[0,0],M[1,0])),'limits':'registration from exposed page text only, no optical score; same-video development evidence, not blind validation'},warped
ma=measurement(A);mb=measurement(B);Mab,regAB,_=register(A,B);Mdb,regDB,warp=register(donor,B)
known=np.ones((1080,1920),np.uint8);known[280:960,440:1480]=0;warped_known=cv2.warpAffine(known,Mdb,(1920,1080))>0
# Use OLD canonical shape only as an explicit provisional B footprint for feasibility.
y,x=np.mgrid[:1080,:1920];qx=np.maximum(np.abs(x-960)-(392-170),0);inside=(qx*qx+(y-542)**2)<170**2
fraction=float(warped_known[inside].mean());known_img=np.repeat((warped_known*255)[:,:,None],3,axis=2).astype(np.uint8);known_img[~inside]=np.uint8(B[~inside]*255)
Image.fromarray(known_img).save(root/'B-donor-coverage-proposal.png');Image.fromarray(np.uint8(np.clip(warp,0,1)*255)).save(root/'donor-720-registered-to-B-NOT-CLEAN.png')
result={'chosen_B_seconds':714,'selection':'posthoc same-control/active-style and changed text location from overview, no reconstruction fit or score used','A_measurements':ma,'B_measurements':mb,'A_to_B_page_registration':regAB,'donor720_to_B_page_registration':regDB,'conservative_donor_coverage_fraction_of_provisional_B_footprint':fraction,'coverage_limits':'rectangular exclusion covers donor control/nearby context conservatively but is not a certification of shadow-free photographic RGB. No source was promoted; raw registered donor contains its old control elsewhere. Use observed text plus independently documented paper/source recovery; preserve uncertainty.','pair_stage':'proposal only, cannot begin paired fits before20 qualifying singles. Existing A input/epoch unchanged.'}
(root/'assessment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
