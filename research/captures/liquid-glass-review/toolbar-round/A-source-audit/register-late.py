"""Source-only A-page registrations from exposed controls; no optical fits."""
import json,hashlib,time
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw
cv2.setNumThreads(1);cv2.setRNGSeed(14)
root=Path('/tmp/agent-toolbar-A-source-audit');meta=json.loads((root/'late-screen/frame-provenance.json').read_text());meta['frames']=[f for f in meta['frames'] if f['requested_seconds']==724.5];out=root/'late-registration';out.mkdir(exist_ok=True)
A=np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png').convert('RGB'))
H,W=A.shape[:2];allowed=np.full((H,W),255,np.uint8);allowed[330:820,490:1430]=0
sift=cv2.SIFT_create(nfeatures=10000);ka,da=sift.detectAndCompute(cv2.cvtColor(A,cv2.COLOR_RGB2GRAY),allowed)
query=np.array([[640.,444.],[1280.,444.],[640.,640.],[1280.,640.],[960.,542.]])
def similarity(x,y):
    M=np.zeros((2*len(x),4));b=y.ravel();M[0::2,0]=x[:,0];M[0::2,1]=-x[:,1];M[0::2,2]=1;M[1::2,0]=x[:,1];M[1::2,1]=x[:,0];M[1::2,3]=1
    v=np.linalg.lstsq(M,b,rcond=None)[0];return np.array([[v[0],-v[1],v[2]],[v[1],v[0],v[3]]])
def warp_points(M,x):return x@M[:,:2].T+M[:,2]
def stats(values):
    return {'n':len(values),'rms':float(np.sqrt(np.mean(values**2))),'median':float(np.median(values)),'p95':float(np.quantile(values,.95)),'max':float(np.max(values))} if len(values) else {'n':0}
records=[]
for frame in meta['frames']:
    began=time.time();t=frame['requested_seconds'];raw=(root/frame['local_file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==frame['png_sha256'];S=np.asarray(Image.open(root/frame['local_file']).convert('RGB'));assert S.shape==A.shape
    rgb_hash=hashlib.sha256(S.tobytes()).hexdigest();assert rgb_hash==frame['rgb_sha256']
    ks,ds=sift.detectAndCompute(cv2.cvtColor(S,cv2.COLOR_RGB2GRAY),allowed);bf=cv2.BFMatcher();forward={m.queryIdx:m for m,n in bf.knnMatch(ds,da,k=2) if m.distance<.7*n.distance};backward={m.queryIdx:m for m,n in bf.knnMatch(da,ds,k=2) if m.distance<.7*n.distance};matches=[m for i,m in forward.items() if m.trainIdx in backward and backward[m.trainIdx].trainIdx==i]
    src=np.array([ks[m.queryIdx].pt for m in matches]);dst=np.array([ka[m.trainIdx].pt for m in matches]);block=(dst//128).astype(int);hold=(block[:,0]+3*block[:,1])%4==0;train=~hold
    record={'requested_seconds':t,'presentation_seconds':frame['presentation_seconds'],'frame_index':frame['frame_index'],'png_sha256':frame['png_sha256'],'mutual_ratio_matches':len(matches),'train_matches':int(train.sum()),'heldout_matches':int(hold.sum()),'source_and_target_control_regions_excluded':[490,330,1430,820]}
    if train.sum()<8:
        record['status']='insufficient independent exposed controls';records.append(record);continue
    M,consensus=cv2.estimateAffinePartial2D(src[train],dst[train],method=cv2.RANSAC,ransacReprojThreshold=1.,maxIters=5000,confidence=.999)
    if M is None or consensus.sum()<6:
        record['status']='no robust exterior registration';records.append(record);continue
    inliers=np.flatnonzero(train)[consensus.ravel()>0];M=similarity(src[inliers],dst[inliers]);residual=np.linalg.norm(warp_points(M,src)-dst,axis=1);held=residual[hold];trainres=residual[inliers]
    inverse=cv2.invertAffineTransform(M);source_query=warp_points(inverse,query);inlierblocks=(dst[inliers]//128).astype(int);labels=np.unique(inlierblocks,axis=0);rng=np.random.default_rng(14000+int(1000*t));samples=[]
    for _ in range(200):
        chosen=rng.integers(len(labels),size=len(labels));indices=np.concatenate([inliers[np.all(inlierblocks==labels[i],axis=1)] for i in chosen])
        if len(indices)<4:continue
        boot=similarity(src[indices],dst[indices]);samples.append(warp_points(boot,source_query)-query)
    samples=np.array(samples);radii=np.linalg.norm(samples,axis=2);q95=np.quantile(radii,.95,axis=0)
    heldgood=held[held<=1.5];record.update({'status':'registered-provisional-source-evidence','matrix':M.tolist(),'scale':float(np.hypot(M[0,0],M[1,0])),'rotation_radians':float(np.arctan2(M[1,0],M[0,0])),'train_inliers':len(inliers),'train_inlier_residual_px':stats(trainres),'heldout_ALL_candidate_residual_px':stats(held),'heldout_fraction_below1_5px':float((held<=1.5).mean()) if len(held) else None,'heldout_below1_5px_SELECTED_residual':stats(heldgood),'training_spatial_blocks':len(labels),'train_control_span_xy':np.ptp(dst[inliers],axis=0).tolist(),'bootstrap_samples':len(samples),'query_A_native_xy':query.tolist(),'bootstrap_conditional_q95_displacement_px':q95.tolist(),'bootstrap_mean_displacement_xy':samples.mean(0).tolist(),'uncertainty_limits':'Conditional on inlier correspondences and similarity model; not a complete error bound. All heldout candidates/outliers reported, not removed from primary heldout RMS.'})
    record['source_confidence_erosion_px']=int(np.ceil(float(q95.max())+(float(np.sqrt(np.mean(heldgood**2))) if len(heldgood) else 1.5)+1.))
    record['registration_evidence_sufficient']=bool(len(inliers)>=20 and len(held)>=8 and (held<=1.5).mean()>=.7 and q95.max()<2 and np.ptp(dst[inliers],axis=0).min()>80)
    warped=cv2.warpAffine(S,M,(W,H));Image.fromarray(warped).save(out/f'{t}-registered-RAW-NOT-CLEAN.png')
    diagnostic=Image.fromarray(A.copy());draw=ImageDraw.Draw(diagnostic)
    for i,(x,y) in enumerate(dst):
        color='cyan' if hold[i] else ('green' if i in inliers else 'red');draw.ellipse((x-3,y-3,x+3,y+3),outline=color,width=2)
    draw.rectangle((490,330,1430,820),outline='yellow',width=3);diagnostic.save(out/f'{t}-exterior-controls.png')
    np.savez_compressed(out/f'{t}-controls.npz',source_xy=src,target_xy=dst,train=train,heldout=hold,train_inliers=inliers,all_residual=residual,bootstrap_displacements=samples)
    record['seconds']=time.time()-began;records.append(record);(out/'registrations.json').write_text(json.dumps({'records':records,'no_source_pixels_promoted':True,'no_optical_fit_or_epoch_change':True},indent=2)+'\n');print('REGISTERED',t,len(inliers),stats(held),record['registration_evidence_sufficient'],flush=True)
(out/'registrations.json').write_text(json.dumps({'records':records,'no_source_pixels_promoted':True,'no_optical_fit_or_epoch_change':True},indent=2)+'\n');print('SOURCE REGISTRATIONS COMPLETE',flush=True)
