import cv2,numpy as np,json
from pathlib import Path
root=Path('/evidence/apple-matches')
results={}
for name,source,target,roi in [('media','219-180.png','219-190.png',(650,250,1260,840)),('regular','219-720.png','219-710.png',(520,335,1400,760))]:
 s=cv2.imread(str(root/source));t=cv2.imread(str(root/target));sg=cv2.cvtColor(s,cv2.COLOR_BGR2GRAY);tg=cv2.cvtColor(t,cv2.COLOR_BGR2GRAY)
 mask=np.full(sg.shape,255,np.uint8);x0,y0,x1,y1=roi;mask[y0:y1,x0:x1]=0
 sift=cv2.SIFT_create(nfeatures=10000);k1,d1=sift.detectAndCompute(sg,mask);k2,d2=sift.detectAndCompute(tg,mask)
 pairs=cv2.BFMatcher().knnMatch(d1,d2,k=2);good=[a for a,b in pairs if a.distance<.7*b.distance]
 a=np.array([k1[m.queryIdx].pt for m in good]);b=np.array([k2[m.trainIdx].pt for m in good]);mat,inliers=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=1,maxIters=5000)
 w=cv2.warpAffine(s,mat,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(219,219,219))
 cv2.imwrite(str(root/(name+'-registered.png')),w)
 valid=cv2.warpAffine(np.full(sg.shape,255,np.uint8),mat,(1920,1080));valid&=mask
 diff=np.abs(w.astype(float)-t.astype(float));results[name]={'matches':len(good),'inliers':int(inliers.sum()),'affine':mat.tolist(),'exterior_mae':float(diff[valid>250].mean())}
 if name=='regular':
  # Surface in the later source frame must never become the new background.
  smask=np.zeros(sg.shape,np.uint8);smask[350:780,500:1410]=255
  contaminated=cv2.warpAffine(smask,mat,(1920,1080))>0
  w[contaminated]=(219,219,219)
  # Target's uniformly lit page estimate: sampled outside text and glass.
  cv2.imwrite(str(root/(name+'-registered.png')),w)
 print(name,results[name])
(root/'registration.json').write_text(json.dumps(results,indent=2))
