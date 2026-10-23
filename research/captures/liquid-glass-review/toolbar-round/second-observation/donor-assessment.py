import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image,ImageDraw
from reproduce import frame
root=Path('/tmp/agent-toolbar-second-observation');B=np.asarray(Image.open(root/'frame-714.png')).astype(np.float32)/255;source_root=Path('/evidence/apple-matches')
allowed=np.full((1080,1920),255,np.uint8);allowed[280:960,440:1480]=0;sift=cv2.SIFT_create(nfeatures=10000);kb,db=sift.detectAndCompute(cv2.cvtColor(np.uint8(B*255),cv2.COLOR_RGB2GRAY),allowed)
y,x=np.mgrid[:1080,:1920];qx=np.maximum(np.abs(x-960)-(392-170),0);inside=qx*qx+(y-542)**2<170**2;union=np.zeros((1080,1920),bool);records=[];sheet=Image.new('RGB',(1280,792),'#202020');draw=ImageDraw.Draw(sheet)
for i,t in enumerate([724,726,728,730]):
    rgb,meta=frame(source_root,'219',t);rgb8=np.uint8(rgb*255);Image.fromarray(rgb8).save(root/f'frame-{t}.png');draw.text(((i%2)*640+8,(i//2)*396+8),f'{t}s | frame{meta["frame_index"]} | PTS{meta["presentation_seconds"]:.6f}',fill='white');sheet.paste(Image.fromarray(rgb8).resize((640,360)),((i%2)*640,(i//2)*396+36))
    ka,da=sift.detectAndCompute(cv2.cvtColor(rgb8,cv2.COLOR_RGB2GRAY),allowed);pairs=[m for m,n in cv2.BFMatcher().knnMatch(da,db,k=2) if m.distance<.7*n.distance];r={**meta,'rgb_sha256':hashlib.sha256(rgb8.tobytes()).hexdigest(),'matches':len(pairs)}
    if len(pairs)>=20:
        P=np.array([ka[m.queryIdx].pt for m in pairs]);Q=np.array([kb[m.trainIdx].pt for m in pairs]);M,inlier=cv2.estimateAffinePartial2D(P,Q,method=cv2.RANSAC,ransacReprojThreshold=1,maxIters=5000);good=inlier[:,0]>0
        r['inliers']=int(good.sum());r['matrix']=M.tolist();r['registration_rms']=float(np.sqrt(np.mean(np.sum((P[good]@M[:,:2].T+M[:,2]-Q[good])**2,axis=1))))
        if good.sum()>=20:
            known=cv2.warpAffine(allowed//255,M,(1920,1080))>0;union|=known;r['conservative_coverage_fraction']=float(known[inside].mean());r['role']='background donor proposal only; no source pixels promoted'
        else:r['role']='rejected as insufficient registration evidence'
    else:r['role']='rejected as insufficient feature matches'
    records.append(r);print('DONOR',t,r,flush=True)
sheet.save(root/'later-donors-overview.png');(root/'later-donors.json').write_text(json.dumps({'records':records,'union_provisional_B_coverage':float(union[inside].mean()),'limits':'outside conservative donor control/shadow exclusion, not proof of photographic shadow-free RGB. A input/epoch remain untouched; paired stage not begun.'},indent=2)+'\n')
