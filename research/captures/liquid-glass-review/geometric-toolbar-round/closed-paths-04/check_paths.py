"""Fixed closed-path transfer through the CURRENT pinned lead-owned tracer."""
import sys,json,time,traceback
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'code'))
from geometric_optics import trace_closed_orthographic,ClosedCircularOval
from closed_crowned_surface import ClosedCrownedSurface
cfg=json.loads((P/'experiment.json').read_text());deadline=cfg['deadline_unix']
R={'status':'RUNNING','rays':0,'images':0,'fits':0,'source_work':0,'checks':{},'toolbar':{}}
def save():(P/'report.json').write_text(json.dumps(R,indent=2,allow_nan=False))
def check(name,ok,details):
    R['checks'][name]={'pass':bool(ok),'details':details};save()
    if not ok:raise AssertionError(name)
    if time.time()>deadline:raise TimeoutError('Original five-minute deadline')
def trace(s,x,y):
    if time.time()>deadline:raise TimeoutError('Original five-minute deadline')
    R['rays']+=int(np.broadcast_arrays(x,y)[0].size)
    if R['rays']>12000:raise RuntimeError('Original ray cap')
    return trace_closed_orthographic(s,x,y,1.5,2.)
def compare(a,b):
    if a.dtype==bool:return bool(np.array_equal(a,b)),0.
    finite=np.isfinite(a)&np.isfinite(b)
    same=bool(np.array_equal(np.isnan(a),np.isnan(b)))
    error=float(abs(a[finite]-b[finite]).max()) if finite.any() else 0.
    return same and error<2e-10,error
try:
    # True radial circle fixture: same kappa0 field, no softened equal-half crown.
    cx,cy=np.meshgrid(np.linspace(-1,1,21),np.linspace(-1,1,21))
    own=trace(ClosedCrownedSurface(half=(1.,1.),eta=.15,kappa=0.,radial_fixture=True),cx,cy)
    lead=trace(ClosedCircularOval(depth=.15,kappa=0.),cx,cy)
    comparisons={k:compare(own[k],lead[k]) for k in own}
    check('circle_fixture_shared_tracer_equality',all(a for a,b in comparisons.values()),{'maximum_errors':{k:b for k,(a,b) in comparisons.items()},'all_status_and_NaN_patterns_exact':all(np.array_equal(own[k],lead[k]) for k in own if own[k].dtype==bool),'scope':'True radial kappa0; root owns anisotropic circle kappa1/3 fixture. No new toolbar set.'})
    np.savez(P/'circle-fixture-paths.npz',x=cx,y=cy,**own)
    for k in [0.,1/3]:
        s=ClosedCrownedSurface(eta=.15,kappa=k);a,b=s.half
        x,y=np.meshgrid(np.linspace(-a,a,71),np.linspace(-b,b,71))
        out=trace(s,x,y);inside=out['inside'];complete=out['complete'];tir=inside&out['blocked'];boundary=out['boundary_unresolved']
        finite_out=np.isfinite(out['exit_direction']).all(axis=-1)
        nondown=inside&~tir&finite_out&(out['exit_direction'][...,2]>=0)
        other=inside&~complete&~tir&~nondown
        miss=~inside&~boundary
        no_replacement=~complete
        check(f'incomplete_nan_{k}',np.isnan(out['X'][no_replacement]).all() and np.isnan(out['Y'][no_replacement]).all(),'No background replacements on TIR, exact tangent, non-downward or other incomplete paths')
        check(f'clear_miss_identity_{k}',np.array_equal(out['X'][miss],x[miss]) and np.array_equal(out['Y'][miss],y[miss]),'Clear misses are straight; not counted as transmitted solid paths')
        entry=out['entry'][inside];exit=out['exit'][inside];fe,ge=s.level_gradient(entry);fx,gx=s.level_gradient(exit)
        maxentry=float(abs(fe).max());maxexit=float(abs(fx).max());bracket=float(out['intersection_bracket'][inside].max())
        expected_e=ge/np.linalg.norm(ge,axis=-1)[:,None];expected_x=gx/np.linalg.norm(gx,axis=-1)[:,None]
        normal_error=max(float(abs(expected_e-out['entry_normal'][inside]).max()),float(abs(expected_x-out['exit_normal'][inside]).max()))
        check(f'actual_F_roots_normals_{k}',maxentry<1e-10 and maxexit<2e-9 and bracket<=1e-11 and normal_error<1e-12,{'entry_level_max':maxentry,'exit_level_max':maxexit,'exit_bracket_max':bracket,'normal_max_error':normal_error,'shared_tolerance':1e-11})
        # Advisory numerical fold evidence only where the complete interior stencil is valid.
        valid=inside&complete
        stencil=valid[1:-1,1:-1]&valid[:-2,1:-1]&valid[2:,1:-1]&valid[1:-1,:-2]&valid[1:-1,2:]
        U,V=out['X'],out['Y'];dx=2*a/70;dy=2*b/70
        ux=(U[1:-1,2:]-U[1:-1,:-2])/(2*dx);uy=(U[2:,1:-1]-U[:-2,1:-1])/(2*dy)
        vx=(V[1:-1,2:]-V[1:-1,:-2])/(2*dx);vy=(V[2:,1:-1]-V[:-2,1:-1])/(2*dy)
        det=ux*vy-uy*vx;fold=stencil&(det<0)
        transmitted=inside&complete
        r={'grid':[71,71],'grid_rays':int(x.size),'strict_inside':int(inside.sum()),'clear_miss':int(miss.sum()),'exact_projected_tangent':int(boundary.sum()),'transmitted_background':int(transmitted.sum()),'TIR_or_critical':int(tir.sum()),'non_downward_finite_exit':int(nondown.sum()),'other_incomplete':int(other.sum()),'fold_evidence_valid_stencils':int(stencil.sum()),'negative_Jacobian_stencils':int(fold.sum()),'Jacobian_determinant_range':[float(det[stencil].min()),float(det[stencil].max())],'fold_limit':'71x71 centered differences on complete strict-interior stencils; numerical orientation-reversal evidence, not a rigorous global caustic certificate.','transmitted_source_XY_bounds':[[float(U[transmitted].min()),float(V[transmitted].min())],[float(U[transmitted].max()),float(V[transmitted].max())]],'source_support':'NOT evaluated; geometry coordinates only, no RGB/input inspected'}
        R['toolbar'][str(k)]=r
        tag='0' if k==0 else 'one-third'
        np.savez(P/f'paths-{tag}.npz',x=x,y=y,fold_stencil=fold,valid_fold_stencil=stencil,jacobian_determinant=det,**out)
        save();print(json.dumps(r),flush=True)
    R['status']='PASS_MATHEMATICAL_TRANSFER_WITH_INCOMPLETE_BRANCHES';R['finished_unix']=time.time();save()
    print(json.dumps({'status':R['status'],'rays':R['rays']}),flush=True)
except Exception as ex:
    R['status']='STOP_FIRST_FAILURE';R['error']=repr(ex);R['traceback']=traceback.format_exc();save();raise
