"""Bounded local finite-camera compatibility screen of the frozen switch map.
No image fitting, source replacement, camera identification or no-root proof.
"""
import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np
from extended_fit import Study
from perspective_back_surface import projected_height_gradient
root=Path('/evidence/extended/active-switch');out=root/'rev6-finite-camera';out.mkdir(exist_ok=True);recipe=json.loads((root/'rev5-joint-existing/candidate.json').read_text());p=recipe['parameters'];records=[]

def gradient(points,H,F,C,G,n):
    """Strict public equation on individually admissible rows; others unresolved."""
    H=np.broadcast_to(H,points.shape[:-1]);m=points/C;a=np.sqrt(n*n+(n*n-1)*np.sum(m*m,axis=-1));w=m/a[...,None]
    t=np.concatenate([w,-np.ones((*H.shape,1))],-1);t/=np.linalg.norm(t,axis=-1)[...,None]
    q=points+H[...,None]*w;v=np.concatenate([(1+G/C)*F-q,-(G-H)[...,None]],-1);v/=np.linalg.norm(v,axis=-1)[...,None]
    normal=n*t-v;valid=(normal[...,2]<-1e-8)&(n*np.sum(t*v,axis=-1)>1+1e-8)
    result=np.full_like(points,np.nan)
    if valid.any():result[valid]=projected_height_gradient(points[valid],H[valid],F[valid],C,G,n)
    return result,valid


def condition(points,H,fields,step,C,G,n):
    B,valid=gradient(points,H,fields[0],C,G,n);derivatives=[]
    for axis in range(2):
        shift=np.eye(2)[axis]*step;plus,vp=gradient(points+shift,H,fields[1+2*axis],C,G,n);minus,vm=gradient(points-shift,H,fields[2+2*axis],C,G,n);valid&=vp&vm;derivatives.append((plus-minus)/(2*step))
    plus,vp=gradient(points,H+step,fields[0],C,G,n);minus,vm=gradient(points,H-step,fields[0],C,G,n);valid&=vp&vm;dh=(plus-minus)/(2*step)
    c=derivatives[0][...,1]-derivatives[1][...,0]+B[...,0]*dh[...,1]-B[...,1]*dh[...,0]
    return c,valid

for name in ['a','b']:
    s=Study(root/'paired'/name);half=s.half+np.array([p['half_x_delta'],p['half_y_delta']]);x,y=np.meshgrid(np.linspace(-half[0]+.01,half[0]-.01,71),np.linspace(-half[1]+.01,half[1]-.01,51));origin=np.array([p['shape_dx'],p['shape_dy']]);positions=np.stack([x,y],-1);sd=s.shape(x+origin[0],y+origin[1],p)[-1][0];inside=sd<-.01;points=positions[inside]
    def mapping(q):
        X,Y,_,_=s.geometry_field(q[...,0]+origin[0],q[...,1]+origin[1],p);return np.stack([X-origin[0],Y-origin[1]],-1)
    field_sets=[]
    for step in [2e-4,1e-4]:
        fields=[mapping(points)]
        for axis in np.eye(2):fields.extend([mapping(points+axis*step),mapping(points-axis*step)])
        field_sets.append(fields)
    rows=[]
    for C in [3.,10.,30.]:
        for G in [2.,4.]:
            for n in [1.2,1.5]:
                samples=[]
                for fraction in np.linspace(.05,.95,19):
                    H=np.full(len(points),G*fraction);a,va=condition(points,H,field_sets[0],2e-4,C,G,n);b,vb=condition(points,H,field_sets[1],1e-4,C,G,n);reliable=va&vb&np.isfinite(a)&np.isfinite(b)
                    tolerance=np.maximum(1e-7,100*abs(a-b));nearzero=reliable&(abs(b)<=tolerance);signed=np.where(reliable&~nearzero,np.sign(b),0)
                    samples.append((reliable,signed,nearzero,b))
                any_valid=np.logical_or.reduce([r[0] for r in samples]);nearzero=np.logical_or.reduce([r[2] for r in samples]);bracket=np.logical_or.reduce([(a[1]*b[1]<0)&a[0]&b[0] for a,b in zip(samples,samples[1:])])
                row=dict(camera_over_L=C,gap_over_L=G,index=n,inside_nodes=len(points),some_admissible_sample=int(any_valid.sum()),stable_sign_change_between_sampled_heights=int(bracket.sum()),nearzero_or_step_uncertain=int(nearzero.sum()),no_sampled_root_bracket=int((any_valid&~bracket&~nearzero).sum()),no_admissible_sample=int((~any_valid).sum()),height_fractions=[.05,.95],height_samples=19);rows.append(row)
                print(name,C,G,n,'brackets',row['stable_sign_change_between_sampled_heights'],'near',row['nearzero_or_step_uncertain'],'valid',row['some_admissible_sample'],flush=True)
    records.append(dict(observation=name.upper(),rows=rows))
report=dict(method=__doc__,recipe='Accepted switch6',observations=records,derivative_steps=[.0002,.0001],sign_threshold='max1e-7 or100times step disagreement; nearzero includes unresolved derivatives',limits='Finite grid and sampled heights/camera parameters ONLY. Sign brackets need continuous branch/root refinement; no sampled bracket is NOT proof no root exists. Local compatibility does not recover a globally integrable height or complete solid. No image score, source, epoch, count or Apple camera claim.')
with (out/'local-screen.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
