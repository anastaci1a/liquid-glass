"""Compare continuous crowned footprints against the frozen Apple rim.

Read-only shape experiment. Photometric fitting and optical acceptance separate.
"""
import sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import least_squares
from scipy.special import expit
from render import geometry
from PIL import Image,ImageDraw

folder=Path('/evidence/extended/active-segmented-selector')
out=folder/'crown-review';out.mkdir(exist_ok=True)

def crown(x,a,b,w):
    # q is even/convex, zero only at the center; no straight body interval.
    # Normalize q(a)=b, so the measured cardinal bounds stay fixed.
    e=w*b;neck=a-b
    base=np.logaddexp(0,(e-neck)/e)
    root=np.sqrt(x*x+e*e)
    raw=np.logaddexp(0,(root-neck)/e)-base
    den=np.logaddexp(0,(np.hypot(a,e)-neck)/e)-base
    return b*raw/den,b/den*expit((root-neck)/e)*x/(e*root)

def implicit(points,v,kind):
    cx,cy,a,b,k=v;x=points[:,0]-cx;y=points[:,1]-cy
    if kind=='capsule':return geometry(x,y,[a,b],min(a,b)*k)[0]
    if kind=='crown':
        q,qd=crown(x,a,b,k);r=np.hypot(q,y);grad=np.hypot(q*qd,y)
        return (r*r-b*b)/(2*np.maximum(grad,b*.2))
    # Implicit gradient-normalized superellipse residual; only contour fit.
    u=np.abs(x)/a;z=np.abs(y)/b;f=u**k+z**k-1
    g=np.hypot(k*u**(k-1)/a,k*z**(k-1)/b)
    return f/np.maximum(g,.001)

results=[]
for label,root in [('A',folder),('B',folder/'second-observation')]:
    case=json.loads((root/'case.json').read_text());target=cv2.imread(str(root/'target.png'))[:,:,::-1]
    cx,cy=case['center'];a,b=case['half'];theta=np.linspace(-np.pi/2,np.pi/2,256)
    right=np.column_stack((cx+a-b+b*np.cos(theta),cy+b*np.sin(theta)))
    left=np.column_stack((cx-a+b-b*np.cos(theta),cy+b*np.sin(theta)))
    xs=np.linspace(cx-a+b,cx+a-b,256)
    pp=np.vstack([right,left,np.column_stack((xs,np.full(256,cy-b))),np.column_stack((xs,np.full(256,cy+b)))])
    nn=np.vstack([np.column_stack((np.cos(theta),np.sin(theta))),np.column_stack((-np.cos(theta),np.sin(theta))),np.tile([0,-1],(256,1)),np.tile([0,1],(256,1))])
    offsets=np.linspace(-9,9,145);positions=pp[:,None,:]+nn[:,None,:]*offsets[None,:,None]
    value=cv2.remap(target.mean(2).astype(np.float32),positions[:,:,0].astype(np.float32),positions[:,:,1].astype(np.float32),cv2.INTER_LINEAR)
    chosen=np.argmax(value-.015*offsets[None,:]**2,axis=1)
    points=positions[np.arange(len(pp)),chosen]
    support=(value.max(1)>248)&(np.ptp(value,axis=1)>2)
    points=points[support];indices=np.arange(len(points));train=indices%3!=0;hold=~train
    fits=[]
    for kind,start,limits in [('capsule',.95,(.4,1.)),('crown',.25,(.025,.85)),('superellipse',3.8,(2.01,7.))]:
        bounds=([cx-8,cy-8,a-10,b-10,limits[0]],[cx+8,cy+8,a+10,b+10,limits[1]])
        fit=least_squares(lambda v:implicit(points[train],v,kind),[cx,cy,a,b,start],bounds=bounds,loss='soft_l1',f_scale=.5,max_nfev=150)
        row=dict(kind=kind,parameters=fit.x.tolist(),train_rmse=float(np.sqrt(np.mean(implicit(points[train],fit.x,kind)**2))),held_rmse=float(np.sqrt(np.mean(implicit(points[hold],fit.x,kind)**2))))
        fits.append(row)
    # Show fixed native crops at4x for contour inspection, not extra source detail.
    x0,y0,x1,y1=case['crop'];crop=Image.fromarray(target[y0:y1,x0:x1]);sheet=Image.new('RGB',(crop.width*3,crop.height+45),'#151922');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(fits):
        panel=crop.copy();D=ImageDraw.Draw(panel);cx1,cy1,a1,b1,k=row['parameters'];xx=np.linspace(-a1,a1,1500)
        if row['kind']=='capsule':yy=np.sqrt(np.maximum((b1*k)**2-np.maximum(np.abs(xx)-(a1-b1*k),0)**2,0))+(b1-b1*k)
        elif row['kind']=='crown':yy=np.sqrt(np.maximum(b1*b1-crown(xx,a1,b1,k)[0]**2,0))
        else:yy=b1*np.maximum(1-(np.abs(xx)/a1)**k,0)**(1/k)
        for sign in [-1,1]:D.line(list(zip(xx+cx1-x0,sign*yy+cy1-y0)),fill=(0,150,255),width=1)
        sheet.paste(panel,(i*crop.width,45));draw.text((i*crop.width+12,12),f"{row['kind']} held {row['held_rmse']:.4f}px",fill='white')
    sheet.save(out/f'contours-{label}.png')
    np.save(out/f'contour-points-{label}.npy',points)
    results.append(dict(observation=label,target_sha256=hashlib.sha256((root/'target.png').read_bytes()).hexdigest(),points=len(points),fits=fits))
(out/'report.json').write_text(json.dumps(dict(experiment='Fixed-ridge silhouette comparison',results=results,accepted_optical_pass=False,limits='White ridge is not necessarily the exact material boundary. All models use the same sampled points and held-out every third point. Residual is gradient-normalized implicit approximation except capsule SDF. No optical score or source mutation.'),indent=2)+'\n')
print(json.dumps(results),flush=True)
