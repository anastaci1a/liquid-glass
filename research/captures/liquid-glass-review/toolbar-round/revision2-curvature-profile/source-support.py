"""Read-only native ray support; never a new mask/source/scoring epoch.

Observed here means outside the documented donor lens-removal rectangle. It is a
conservative provenance diagnostic, not proof that all remaining RGB is accurate.
The frozen input contains estimated paper within that transformed rectangle.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
import toolbar_curvature_profile as model
cv2.setNumThreads(1)
package=Path('/tmp/agent-toolbar-evidence-package')
p=json.loads(Path('/tmp/agent-toolbar-revision2-curvature-fit/best-feasible/recipe.json').read_text());case=p['case']
audit=json.loads(Path('/tmp/agent-toolbar-input-audit.json').read_text())
A=np.array(audit['registration']['matrix']);H,W=1080,1920
estimated=np.zeros((H,W),np.uint8);estimated[350:790,490:1420]=1
estimated=cv2.warpAffine(estimated,A,(W,H))>0
observed=(~estimated).astype(np.float32)
sigmas=[11.]
supports={}
for sigma in sigmas:
    radius=int(np.ceil(3*sigma))+1
    supports[str(sigma)]={'radius':radius,'mask':cv2.erode(observed,np.ones((2*radius+1,2*radius+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)}
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
x0,y0,x1,y1=case['crop'];nh,nw=y1-y0,x1-x0;L=min(case['half'])
regions={'glass':masks['glass'],'rim':masks['rim']}
yy,xx=np.mgrid[:nh,:nw]
for name,(a,b,c,d) in {'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
    regions[name]=masks['glass']&(xx+x0>=a)&(xx+x0<c)&(yy+y0>=b)&(yy+y0<d)
rows={name:{'rays':0,'center_outside_estimated':0,'kernel_outside_estimated':{k:0 for k in supports}} for name in regions}
extrema=[np.inf,np.inf,-np.inf,-np.inf]
for top in range(0,nh,16):
    bot=min(top+16,nh);yy,xx=np.mgrid[top*4:bot*4,0:nw*4]
    x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L
    X,Y=model.mapping(x,y,p);X=(X*L+case['center'][0]).astype(np.float32);Y=(Y*L+case['center'][1]).astype(np.float32)
    inside=model.baseline.boundary(x,y,p)[0]<=0
    center=cv2.remap(observed,X,Y,cv2.INTER_LINEAR)>.999
    safe={k:cv2.remap(v['mask'],X,Y,cv2.INTER_LINEAR)>.999 for k,v in supports.items()}
    for name,mask in regions.items():
        valid=np.repeat(np.repeat(mask[top:bot],4,axis=0),4,axis=1)&inside
        row=rows[name];row['rays']+=int(valid.sum());row['center_outside_estimated']+=int((valid&center).sum())
        for k in safe:row['kernel_outside_estimated'][k]+=int((valid&safe[k]).sum())
        if name=='glass' and valid.any():
            extrema=[min(extrema[0],float(X[valid].min())),min(extrema[1],float(Y[valid].min())),max(extrema[2],float(X[valid].max())),max(extrema[3],float(Y[valid].max()))]
for row in rows.values():
    row['center_outside_estimated_fraction']=row['center_outside_estimated']/row['rays']
    row['kernel_outside_estimated_fraction']={k:v/row['rays'] for k,v in row['kernel_outside_estimated'].items()}
report={'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','sampling':'native4x4 rays in fixed destination masks AND actual silhouette','source_ray_extrema_xyxy':extrema,'sigma_native_pixels':sigmas,'conservative_3sigma_plus_bilinear_radii':{k:v['radius'] for k,v in supports.items()},'regions':rows,'limits':['No source RGB/masks/registration/score changes; no gain or new experiment','Outside replaced rectangle does not prove all RGB or registration accurate; inside is estimated paper','3sigma proxy truncates Gaussian tails; not an exhaustive optical kernel proof','Foreground boxes excluded by frozen destination masks; filters never applied to solid glyphs','HQ source-domain proof still required for a qualifying candidate']}
out=Path('/tmp/agent-toolbar-revision2-curvature-source-support.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
