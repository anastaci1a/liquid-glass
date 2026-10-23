"""Independent unoccluded icon registration; no lens/image fitting."""
import os,json,cv2,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
os.umask(0o002);cv2.setNumThreads(1)
D=Path('/evidence/extended/blue-slider-short-round');S=D/'sequence';a=cv2.imread(str(S/'frame-00.png'));b=cv2.imread(str(S/'frame-07.png'));assert a.shape==b.shape
ma=np.zeros(a.shape[:2],np.uint8);mb=np.zeros_like(ma)
for x0,y0,x1,y1 in [(420,510,528,590),(1425,510,1535,590)]:ma[y0:y1,x0:x1]=255
for x0,y0,x1,y1 in [(380,510,484,590),(1410,510,1520,590)]:mb[y0:y1,x0:x1]=255
sift=cv2.SIFT_create(nfeatures=600);ka,da=sift.detectAndCompute(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),ma);kb,db=sift.detectAndCompute(cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),mb);assert da is not None and db is not None
pairs=[(m.queryIdx,m.trainIdx) for m,n in cv2.BFMatcher().knnMatch(da,db,k=2) if m.distance<.7*n.distance]
P=np.array([ka[i].pt for i,j in pairs]);Q=np.array([kb[j].pt for i,j in pairs]);assert len(P)>=8
train=np.arange(len(P))%3!=0;scale=np.array([1920.,1080.]);center=np.array([960.,540.]);X=(P-center)/scale;Y=(Q-center)/scale
f=lambda v:((X*v[:2]+v[2:])-Y)
opt=least_squares(lambda v:f(v)[train].ravel(),[1,1,-.02,0],loss='soft_l1',f_scale=.5/1920,max_nfev=100)
pred=(X*opt.x[:2]+opt.x[2:])*scale+center;err=pred-Q;rmse=lambda mask:float(np.sqrt(np.mean(np.sum(err[mask]**2,axis=1))))
# Entire gray-end cap is unoccluded at the far right in B; reserve it as a
# separate semantic control rather than fit the hidden left endpoint.
luma=b.mean(2);row=luma[545:555].mean(0);edge=np.where(np.diff(row[1300:1410])>1)[0]+1300
result=dict(scope='Observation-only Arest1090.5 to gray-min B1091.55, original video; no proposed source adopted or optical render',matches=len(P),left_matches=int((P[:,0]<900).sum()),right_matches=int((P[:,0]>900).sum()),axis_affine=dict(scale=opt.x[:2].tolist(),translation_px=(center-opt.x[:2]*center+opt.x[2:]*scale).tolist()),all_rmse=rmse(np.ones(len(P),bool)),train_rmse=rmse(train),held_rmse=rmse(~train),controls=[dict(source=p.tolist(),observed=q.tolist(),predicted=v.tolist(),error=e.tolist(),held=bool(not t)) for p,q,v,e,t in zip(P,Q,pred,err,train)],predicted_source_track_start=float((579.5-center[0])*opt.x[0]+opt.x[2]*scale[0]+center[0]),predicted_source_track_right=float((1377.5-center[0])*opt.x[0]+opt.x[2]*scale[0]+center[0]),unoccluded_gray_cap_candidate_edges=edge.tolist(),limits='A/B active shape and full control layout change under the minimum-bound interaction. Icon registration cannot establish hidden track endpoint/value or refractive geometry. No lensed boundary was used to fit registration. Global affine support must also be checked against independent gray-cap geometry; no automatic paired-reference/source approval.')
(D/'background-controls.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k not in ['controls']},flush=True)
