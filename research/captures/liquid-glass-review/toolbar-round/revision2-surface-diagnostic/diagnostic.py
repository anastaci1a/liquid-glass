"""Bounded finite-gap SURFACE diagnostic of accepted map; no target-image fit."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
import toolbar_candidate as empirical
cv2.setNumThreads(1)
out=Path('/tmp/agent-toolbar-surface-diagnostic');out.mkdir(exist_ok=True)
p=json.loads(Path('/tmp/agent-toolbar-evidence-package/recipe.json').read_text())
half=p['shape']['half'];h0=.5
configs=[{'n':n,'g':g,'h0':h0,'G':h0+g} for n in [1.33,1.5,1.8] for g in [.5,2.,8.]]

def accepted_v(x,y):
    X,Y=empirical.mapping(x,y,p);return np.stack([X-x,Y-y],axis=-1)

def inverse(v,s,n):
    R=np.sqrt(np.sum(v*v,axis=-1)+s*s);D=n*R-s
    q=v/D[...,None]
    outgoing_normal=s-np.sum(q*v,axis=-1)
    K=1-n*n*(1-1/(1+np.sum(q*q,axis=-1)))
    valid=(s>0)&(D>0)&(outgoing_normal>1e-12)&(K>1e-12)&np.all(np.isfinite(q),axis=-1)
    return q,valid,R,D,K

def forward(h,grad,G,n):
    a=1/np.sqrt(1+np.sum(grad*grad,axis=-1));K=1-n*n*(1-a*a);normal=-np.concatenate([grad,np.ones((*h.shape,1))],axis=-1)*a[...,None]
    factor=np.sqrt(np.maximum(K,0))-n*a
    V=factor[...,None]*normal;V[...,2]-=n
    valid=(h>0)&(G-h>0)&(K>1e-12)&(V[...,2]<-1e-12)&np.all(np.isfinite(V),axis=-1)
    displacement=(G-h)[...,None]*V[...,:2]/(-V[...,2,None]);displacement=np.where(valid[...,None],displacement,np.nan)
    return displacement,valid,K

def paths(x,y,cfgs,step,vfun=accepted_v):
    n=np.array([c['n'] for c in cfgs])[:,None];g=np.array([c['g'] for c in cfgs])[:,None]
    results=[]
    for order in [(0,1),(1,0)]:
        s=np.broadcast_to(g,(len(cfgs),len(x))).copy();alive=np.ones_like(s,bool);cx=np.zeros_like(x);cy=np.zeros_like(y)
        for axis in order:
            length=x if axis==0 else y;steps=max(1,int(np.ceil(np.max(np.abs(length))/step)));dt=1/steps
            def rhs(t,clearance):
                xx=cx+t*length if axis==0 else cx;yy=cy+t*length if axis==1 else cy
                v=vfun(xx,yy)[None,...];q,valid,*_=inverse(v,clearance,n)
                # Invalid branches do not become rays. Carry NaN and validity.
                return np.where(valid,-q[...,axis]*length[None,:],np.nan),valid
            for k in range(steps):
                t=k*dt;k1,a1=rhs(t,s);k2,a2=rhs(t+dt/2,s+dt*k1/2);k3,a3=rhs(t+dt/2,s+dt*k2/2);k4,a4=rhs(t+dt,s+dt*k3)
                alive&=a1&a2&a3&a4;s+=dt*(k1+2*k2+2*k3+k4)/6
            if axis==0:cx=x
            else:cy=y
        heights=np.array([c['G'] for c in cfgs])[:,None]-s
        positive=heights>0
        results.append({'h':heights,'inverse_branch_valid':alive,'positive_height':positive})
    return results

def stats(x):
    x=np.asarray(x);x=x[np.isfinite(x)]
    return {'n':len(x),'rms':float(np.sqrt(np.mean(x*x))),'median':float(np.median(x)),'p95_abs':float(np.quantile(np.abs(x),.95)),'max_abs':float(np.max(np.abs(x)))} if len(x) else {'n':0}

def invariant_checks():
    x=np.linspace(-1.8,1.8,29);y=np.linspace(-.8,.8,17);yy,xx=np.meshgrid(y,x,indexing='ij');X=xx.ravel();Y=yy.ravel();cfg=[{'n':1.5,'g':2.,'h0':.5,'G':2.5}]
    ident=paths(X,Y,cfg,.02,lambda x,y:np.zeros((*np.broadcast(x,y).shape,2)))
    assert np.max(np.abs(ident[0]['h']-.5))==0 and np.array_equal(ident[0]['h'],ident[1]['h'])
    ax,ay=.01,.02
    def vfun(x,y):
        h=.5+ax*x*x+ay*y*y;grad=np.stack([2*ax*x,2*ay*y],axis=-1)
        v,valid,_=forward(h,grad,2.5,1.5);assert np.all(valid);return v
    v=vfun(X,Y);truth=.5+ax*X*X+ay*Y*Y;q,valid,*_=inverse(v,2.5-truth,1.5);gradient=np.stack([2*ax*X,2*ay*Y],axis=-1)
    qerr=float(np.max(np.abs(q-gradient)));assert np.all(valid) and qerr<1e-12
    known=paths(X,Y,cfg,.02,vfun);herror=max(float(np.max(np.abs(r['h'][0]-truth))) for r in known);patherror=float(np.max(np.abs(known[0]['h']-known[1]['h'])));assert herror<1e-8 and patherror<1e-8
    # Finite-gap physical map can itself have nonzero displacement curl.
    eps=1e-4;vx=(vfun(X+eps,Y)-vfun(X-eps,Y))/(2*eps);vy=(vfun(X,Y+eps)-vfun(X,Y-eps))/(2*eps);c=vx[:,1]-vy[:,0];K=v[:,1]*np.sum(v*vx,axis=-1)-v[:,0]*np.sum(v*vy,axis=-1);R=np.sqrt(np.sum(v*v,axis=-1)+(2.5-truth)**2);D=1.5*R-(2.5-truth);compat=(D*c-1.5*K/R)/D**2
    assert np.max(np.abs(compat))<1e-8
    # Too lateral a requested ray is an invalid inverse branch even if the
    # algebraic inverse gradient has a nonnegative Snell discriminant.
    _,invalid,*_=inverse(np.array([[1.,0.]]),np.array([.1]),1.5);assert not invalid[0]
    report={'identity_exact':True,'known_quadratic_inverse_gradient_max_error':qerr,'known_quadratic_integrated_height_max_error':herror,'known_quadratic_path_difference_max':patherror,'known_surface_map_curl_max_abs':float(np.max(np.abs(c))),'known_surface_compatibility_max_abs':float(np.max(np.abs(compat))),'invalid_inverse_exit_branch_rejected':True,'scope':'Numerical/physical equation checks, not toolbar fit or universal solid validity'}
    (out/'invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('INVARIANTS',report,flush=True)

def run_grid(spacing,step,cfgs,label):
    xs=np.arange(-int(np.floor(half[0]/spacing)),int(np.floor(half[0]/spacing))+1)*spacing;ys=np.arange(-int(np.floor(half[1]/spacing)),int(np.floor(half[1]/spacing))+1)*spacing
    y,x=np.meshgrid(ys,xs,indexing='ij');sd=empirical.boundary(x,y,p)[0];inside=sd<=0;ids=np.flatnonzero(inside);pointsx=x.ravel()[ids];pointsy=y.ravel()[ids]
    v=accepted_v(x,y);vx_y,vx_x=np.gradient(v[...,0],spacing,spacing,edge_order=2);vy_y,vy_x=np.gradient(v[...,1],spacing,spacing,edge_order=2);curl=vy_x-vx_y;K=v[...,1]*(v[...,0]*vx_x+v[...,1]*vy_x)-v[...,0]*(v[...,0]*vx_y+v[...,1]*vy_y)
    solutions=paths(pointsx,pointsy,cfgs,step);hfields=[];branches=[];positive=[]
    for sol in solutions:
        H=np.full((len(cfgs),*x.shape),np.nan);B=np.zeros(H.shape,bool);P=np.zeros(H.shape,bool)
        H.reshape(len(cfgs),-1)[:,ids]=sol['h'];B.reshape(len(cfgs),-1)[:,ids]=sol['inverse_branch_valid'];P.reshape(len(cfgs),-1)[:,ids]=sol['positive_height'];hfields.append(H);branches.append(B);positive.append(P)
    baseinterior=cv2.erode(inside.astype(np.uint8),np.ones((3,3),np.uint8))>0
    reports=[]
    for i,cfg in enumerate(cfgs):
        H1,H2=hfields[0][i],hfields[1][i];both=inside&branches[0][i]&branches[1][i];row={'configuration':cfg,'spacing_L':spacing,'RK_max_step_L':step,'inside_points':int(inside.sum()),'path_common_inverse_valid_points':int(both.sum()),'path_height_difference_L':stats((H1-H2)[both]),'paths':[]}
        for k,H in enumerate([H1,H2]):
            valid=inside&branches[k][i]&positive[k][i];stencil=(cv2.erode(valid.astype(np.uint8),np.ones((3,3),np.uint8))>0)&baseinterior
            hy,hx=np.gradient(H,spacing,spacing,edge_order=2);grad=np.stack([hx,hy],axis=-1);s=cfg['G']-H;q,branch,R,D,_=inverse(v,s,cfg['n']);pde=grad-q
            comp=(D*curl-cfg['n']*K/R)/D**2
            fwd,forwardvalid,Q=forward(H,grad,cfg['G'],cfg['n']);score=stencil&forwardvalid;error=np.linalg.norm(fwd-v,axis=-1)
            row['paths'].append({'order':'x-then-y' if k==0 else 'y-then-x','inverse_branch_invalid_points':int((inside&~branches[k][i]).sum()),'nonpositive_height_points':int((inside&np.isfinite(H)&(H<=0)).sum()),'undefined_height_points':int((inside&~np.isfinite(H)).sum()),'valid_interior_stencil_points':int(stencil.sum()),'height_range_L':[float(np.nanmin(H)),float(np.nanmax(H))] if np.any(np.isfinite(H)) else None,'PDE_gradient_error_norm':stats(np.linalg.norm(pde,axis=-1)[stencil]),'compatibility_residual':stats(comp[stencil]),'forward_invalid_interior_points':int((stencil&~forwardvalid).sum()),'forward_TIR_or_critical_interior_points':int((stencil&(Q<=1e-12)).sum()),'forward_map_vector_error_L':stats(error[score]),'forward_map_vector_error_native_px':stats(error[score]*170),'no_global_slope_clearance_certificate':True})
        reports.append(row);print('SURFACE',label,cfg,'path',row['path_height_difference_L'],'mapPx',[r['forward_map_vector_error_native_px'].get('rms') for r in row['paths']],flush=True)
    np.savez_compressed(out/(label+'-fields.npz'),x=x,y=y,inside=inside,displacement=v,map_curl=curl,K=K,h_xy=hfields[0],h_yx=hfields[1],branch_xy=branches[0],branch_yx=branches[1])
    (out/(label+'.json')).write_text(json.dumps({'label':label,'accepted_recipe':'revision2/pass-02','configs':reports,'target_pixels_used':0,'optical_passes':0},indent=2)+'\n');return reports

if __name__=='__main__':
    if '--reuse-invariants' in sys.argv:
        assert (out/'invariants.json').exists()
        print('REUSED completed equation invariant checks; no repeat',flush=True)
    else:invariant_checks()
    if '--invariants-only' in sys.argv:sys.exit(0)
    coarse=run_grid(.08,.02,configs,'coarse-08');fine=run_grid(.04,.02,configs,'fine-04');refine=run_grid(.04,.01,[configs[4]],'fine-04-RK01')
    report={'coarse':'coarse-08.json','fine':'fine-04.json','RK_refinement':'fine-04-RK01.json','equation':'grad(h)=v/(n*sqrt(|v|²+(G-h)²)-(G-h)); unknown h, fixed planeG','necessary_local_compatibility':'D*curl(v)-(n/R)*(v_y*v dot dxv-v_x*v dot dyv)=0','native_input_or_output_score_changes':False,'new_optical_fits':0,'counted_passes':0,'limitations':['Two integration paths are diagnostics, not a least-squares best surface or global impossibility proof','Near-boundary stencil and nonpositive-height/invalid branches kept separate','No camera/IOR/gap/thickness inferred from footage; finite grid cannot certify surface clearance or sidewall exclusion','Source shading/blur/spectral response unchanged and not identified by map geometry']}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print('SURFACE DIAGNOSTIC COMPLETE',flush=True)
