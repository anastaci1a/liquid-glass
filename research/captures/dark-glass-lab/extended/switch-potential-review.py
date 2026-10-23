"""Project an empirical map onto an integrable family, then measure native RGB."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from switch_potential_model import PotentialStudy,components
root=Path('/evidence/extended/active-switch');out=root/'potential-review';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text());p=old['parameters'];S=[Study(root/'paired'/n) for n in ['a','b']];P=[PotentialStudy(s.folder) for s in S];co=np.asarray(old['material']);rows=[]
for k in [-.8,-.4,0.,.4,.8]:
    designs=[];targets=[]
    for s in S:
        yy,xx=np.mgrid[-.98:.98:61j,-1.49:1.49:91j];*_,(sd,_,_)=s.shape(xx,yy,p);mask=sd<-.004;x=xx[mask];y=yy[mask]
        bx,by,fx,fy=components(s,x,y,p,k);X,Y,*_=s.geometry_field(x,y,p)
        designs.extend([np.c_[fx,-bx,np.zeros_like(bx)],np.c_[fy,np.zeros_like(by),-by]])
        targets.extend([X-x,Y-y])
    A=np.concatenate(designs);b=np.concatenate(targets);v=np.linalg.lstsq(A,b,rcond=None)[0]
    q=copy.deepcopy(p);q['potential_profile']=dict(longitudinal_weight=k,coefficients=v[:7].tolist(),core=v[7:].tolist())
    sc=[s.scores(s.render(q,co),include_ssim=False) for s in P];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,old['scores'])]
    # Independent finite differences on a strictly interior grid.
    s=P[0];y,x=np.mgrid[-.85:.85:39j,-1.3:1.3:59j];h=1e-5
    Xpy=s.geometry_field(x,y+h,q)[0];Xmy=s.geometry_field(x,y-h,q)[0];Ypx=s.geometry_field(x+h,y,q)[1];Ymx=s.geometry_field(x-h,y,q)[1]
    *_,(sd,_,_)=s.shape(x,y,q);mask=sd<-.03;curl=(Xpy-Xmy-Ypx+Ymx)/(2*h)
    row=dict(parameters=q,material=co.tolist(),scores=sc,ratios=ratios,map_projection_rmse=float(np.sqrt(np.mean((A@v-b)**2))),maximum_interior_curl=float(np.max(abs(curl[mask]))),accepted=False);rows.append(row)
    print('POTENTIAL',k,ratios,'curl',row['maximum_interior_curl'],flush=True)
    (out/'review.json').write_text(json.dumps(dict(trials=rows,model=__doc__,limits='Least-squares projection fits the prior coordinate map, not target pixels. Native scores remain authoritative. Integrability is necessary for this thin-element model, not proof of a valid thick solid or Apple parity.'),indent=2)+'\n')
