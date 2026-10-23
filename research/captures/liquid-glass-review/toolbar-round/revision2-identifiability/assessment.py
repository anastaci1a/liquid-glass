"""Queue7: residual/source identifiability; no fit, score epoch or source edit."""
import sys,json
from pathlib import Path
from collections import OrderedDict
sys.path.insert(0,'/tmp/agent-toolbar-evidence-package/code')
import numpy as np
import cv2
from PIL import Image
import crowned_tensor as model
import grazing_reflection
from render import case_geometry
cv2.setNumThreads(1)
package=Path('/tmp/agent-toolbar-evidence-package')
out=Path('/tmp/agent-toolbar-revision2-identifiability');out.mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text());case=p['case'];L=min(case['half'])
x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0
source=np.asarray(Image.open(package/'inputs/source.png'),float)/255
T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255
C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy')
joint=np.load('/tmp/agent-toolbar-joint-native-continuation/material.npy')
blur=np.load('/tmp/agent-toolbar-revision2-blur/best-raw/material.npy')
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
audit=json.loads(Path('/tmp/agent-toolbar-input-audit.json').read_text())
estimated=np.zeros(source.shape[:2],np.uint8);estimated[350:790,490:1420]=1
estimated=(cv2.warpAffine(estimated,np.array(audit['registration']['matrix']),(1920,1080))>0).astype(np.uint8)
registered_valid=cv2.warpAffine(np.ones(source.shape[:2],np.uint8),np.array(audit['registration']['matrix']),(1920,1080))>0
radius=int(np.ceil(3*p['source_sigma']*L))+1;kernel=np.ones((2*radius+1,2*radius+1),np.uint8)
obs_safe=cv2.erode((((1-estimated)>0)&registered_valid).astype(np.uint8),kernel,borderType=cv2.BORDER_CONSTANT,borderValue=0).astype(np.float32)
est_safe=cv2.erode(estimated,kernel,borderType=cv2.BORDER_CONSTANT,borderValue=0).astype(np.float32)
n=np.zeros((H,W),int);obs=np.zeros_like(n);est=np.zeros_like(n)
for top in range(0,H,16):
    bot=min(top+16,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4]
    x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L
    X,Y=model.mapping(x,y,p);X=(X*L+case['center'][0]).astype(np.float32);Y=(Y*L+case['center'][1]).astype(np.float32)
    inside=model.boundary(x,y,p)[0]<=0
    safe_obs=(cv2.remap(obs_safe,X,Y,cv2.INTER_LINEAR)>.999)&inside
    safe_est=(cv2.remap(est_safe,X,Y,cv2.INTER_LINEAR)>.999)&inside
    shape=(bot-top,4,W,4)
    n[top:bot]=inside.reshape(shape).sum((1,3));obs[top:bot]=safe_obs.reshape(shape).sum((1,3));est[top:bot]=safe_est.reshape(shape).sum((1,3))
# Include the fixed output filter in conservative cohort support. Outside sharp
# glass coverage contributes zero to normalized color filtering, so it is neutral.
post_radius=int(np.ceil(3*p['post_sigma']*L))+1
K=np.ones((2*post_radius+1,2*post_radius+1),np.uint8)
wholly_observed=cv2.erode(((obs==n)|(n==0)).astype(np.uint8),K,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
wholly_estimated=cv2.erode(((est==n)|(n==0)).astype(np.uint8),K,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
cohorts={'all':masks['glass'],'observed_kernel_proxy':masks['glass']&wholly_observed,'estimated_kernel_proxy':masks['glass']&wholly_estimated,'mixed_or_uncertain':masks['glass']&~wholly_observed&~wholly_estimated}
np.savez(out/'support-cohorts.npz',**cohorts,inside_samples=n,observed_samples=obs,estimated_samples=est)
yy,xx=np.mgrid[:H,:W];xs=xx+x0;ys=yy+y0;x=(xs-case['center'][0])/L;y=(ys-case['center'][1])/L
depth=-case_geometry(case,xs-case['center'][0],ys-case['center'][1])[0]
residual=(C-T)*255;desired=-residual
light=model.lighting(x,y,p)

class ReflectionAdapter:
    def __init__(self):
        self.crop=case['crop'];self.case=case;self.L=L;self.source=source;self.cache=OrderedDict();self.backdrop_shift=[0.,0.]
    def shape(self,x,y,q):return None,model.boundary(x,y,q)
adapter=ReflectionAdapter()
directions={'tested_inner_tangent':(joint-C)*255,'tested_ordinary_blur':(blur-C)*255}
for name,direction in [('grazing_down',[0.,1.]),('grazing_up',[0.,-1.])]:
    q={**p,'grazing_reflection':{'strength':1.,'width':p['rim_width'],'angular_power':2.,'source_sigma':p['source_sigma'],'direction':direction}}
    weight,environment=grazing_reflection.layers(adapter,q)
    directions[name]=(environment-C)*weight[...,None]*255
# Existing neutral even rim terms. Center-sampled basis is diagnostic only;
# clipping, native averaging and post filtering prevent calling it an exact J.
for name,index in [('neutral_thin',0),('neutral_rim',3),('neutral_wide_rim',6)]:
    directions[name]=np.broadcast_to(light[...,index,None]*255,C.shape)

def stats(mask):
    count=int(mask.sum())
    if not count:return {'pixels':0}
    R=residual[mask].astype(float)
    return {'pixels':count,'rmse':float(np.sqrt(np.mean(R**2))),'signed_RGB_mean':R.mean(0).tolist(),'signed_luma_mean':float((R@np.array([.2126,.7152,.0722])).mean())}

def projection(mask,D):
    if not mask.any():return {'pixels':0}
    a=D[mask].astype(float).ravel();b=desired[mask].astype(float).ravel();dot=float(a@b);aa=float(a@a);bb=float(b@b)
    return {'pixels':int(mask.sum()),'direction_rms':float(np.sqrt(aa/a.size)),'cosine_to_desired':dot/np.sqrt(aa*bb) if aa*bb>1e-20 else None,'signed_sensitivity':dot/aa if aa>1e-20 else None,'note':'Projection only, no parameter applied or optical fit; sensitivities across different bases have different units'}

regions={'full-glass':None,'upper-rim':[650,369,1270,435],'d-stroke':[960,450,1120,550],'underside':[650,650,1270,726]}
reports={}
for name,box in regions.items():
    region=np.ones((H,W),bool) if box is None else (xs>=box[0])&(xs<box[2])&(ys>=box[1])&(ys<box[3])
    data={}
    for cohort,mask in cohorts.items():
        valid=region&mask
        data[cohort]={'residual':stats(valid),'directions':{name:projection(valid,D) for name,D in directions.items()},'depth_profile':[]}
        for lo,hi in [(.75,2),(2,4),(4,8),(8,16),(16,34),(34,68),(68,170)]:
            selected=valid&(depth>=lo)&(depth<hi)
            data[cohort]['depth_profile'].append({'inward_native_px':[lo,hi],**stats(selected)})
    reports[name]={'box':box,'cohorts':data}
report={'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch_unchanged':True,'assessment_not_a_fit_or_pass':True,'source_confidence_proxy':{'native_ray_samples_per_axis':4,'source_kernel_radius':radius,'post_kernel_radius':post_radius,'observed_definition':'All contributing rays outside documented source-estimated rectangle under conservative3sigma+bilinear kernel proxy','estimated_definition':'All contributing source kernels inside documented estimated rectangle; mixed separately retained'},'regions':reports,'limits':['Confidence truncates Gaussian tails and is conservative; outside estimated rectangle does not prove all RGB correct','Source pixels/masks/registration/epoch and accepted baseline remain unchanged','Reflection layers are an existing empirical unrefracted source-environment proxy, not Apple reflection rays','Geometry/filter directions use saved rejected SAME-baseline native material arrays, no reruns or new fits','Neutral basis projections are center-sampled diagnostic proxies, not fitted colors or exact native derivatives','Crops and cohort splits are advisory; they never replace full native gates or exclude bad score pixels','Projection signs/correlations cannot uniquely identify optics; compare cohort sample sizes and mixed support']}
(out/'assessment.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({r:{k:{'pixels':v['residual']['pixels'],'signed_luma_mean':v['residual'].get('signed_luma_mean'),'direction_cosines':{n:s.get('cosine_to_desired') for n,s in v['directions'].items()}} for k,v in row['cohorts'].items()} for r,row in reports.items()},indent=2),flush=True)
