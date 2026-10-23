"""Only changed-core regression/status checks; original unchanged tests reused."""
import sys,json,time
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'code'))
from crowned_bevel import CrownedBevel
from geometric_optics import CircularBevel,refract,trace_flat_front_orthographic
R={'status':'RUNNING','additional_rays':0,'checks':{},'prior_rays':9403,'deadline_unix':1792640797.369}
def save():
    R['total_rays']=R['prior_rays']+R['additional_rays'];(P/'report.json').write_text(json.dumps(R,indent=2))
def check(name,ok,detail):
    R['checks'][name]={'pass':bool(ok),'details':detail};save()
    if not ok:raise AssertionError(name)
    if time.time()>R['deadline_unix']:raise TimeoutError('Original deadline exceeded')
def trace(s,x,y):
    R['additional_rays']+=np.broadcast_arrays(x,y)[0].size
    if R['prior_rays']+R['additional_rays']>50000:raise RuntimeError('Original ray budget exceeded')
    return trace_flat_front_orthographic(s,x,y,1.5,2.)
try:
    if '--remaining' not in sys.argv:
        for depth in [.02,.04]:
            # Fixed radial samples now deliberately include exact crease points.
            x=np.r_[np.linspace(-.99,.99,301),1.,-1.,0.,0.]
            y=np.r_[np.zeros(301),0.,0.,1.,-1.]
            c=CrownedBevel(half=(1.,1.),depth=depth,radial_fixture=True)
            b=CircularBevel(core=0,depth=depth,power=3,edge=0)
            check(f'circle_height_exact_{depth}',all(np.array_equal(a,z) for a,z in zip(c.height_gradient(x,y),b.height_gradient(x,y))),'Unchanged same-profile gradient/height circle equivalence')
            a=trace(c,x,y);z=trace(b,x,y)
            check(f'circle_trace_exact_{depth}',all(np.array_equal(a[k],z[k],equal_nan=True) for k in a),'All new-core outputs exact, including unresolved exact crease')
        R['status']='UPDATED_CORE_CIRCLE_CHECKPOINT_PASS';save();(P/'checkpoint.json').write_text(json.dumps(R,indent=2))
        print(json.dumps({'checkpoint':R['status'],'total_rays':R['total_rays']}),flush=True)
        sys.exit(0)
    R=json.loads((P/'checkpoint.json').read_text())
    for depth in [.02,.04]:
        s=CrownedBevel(depth=depth);old=np.load(P.parent/f'geometry-depth-{depth}.npz')
        a=trace(s,old['x'],old['y'])
        check(f'regular_toolbar_unchanged_{depth}',all(np.array_equal(a[k],old[k],equal_nan=True) for k in old.files if k in a),'All old tracer arrays unchanged at 700 strict-interior points; no new geometry/source candidates')
        check(f'regular_status_{depth}',np.all(a['complete']) and not np.any(a['boundary_unresolved']),'All regular transmitted paths complete')
        x=np.array([s.half[0],-s.half[0],0.,0.,s.half[0]+.01]);y=np.array([0.,0.,1.,-1.,0.])
        out=trace(s,x,y)
        check(f'exact_crease_unresolved_{depth}',np.all(s.level(x[:4],y[:4])[0]==1) and np.all(out['boundary_unresolved'][:4]) and not np.any(out['complete'][:4]) and np.isnan(out['X'][:4]).all() and np.isnan(out['Y'][:4]).all() and np.isnan(out['outward_normal'][:4]).all() and np.isnan(out['back'][:4]).all(),'T==1 only; NaN source/back/normal, complete=False; auxiliary direction fields not valid rays')
        check(f'clear_miss_{depth}',out['complete'][4] and not out['boundary_unresolved'][4] and out['X'][4]==x[4] and out['Y'][4]==y[4],'Clear miss retains straight source coordinates')
    # eta1 and tangent incidence yield exactly k0 with exact floating values.
    d,tir,k=refract(np.array([[1.,0.,0.]]),np.array([[0.,0.,1.]]),1.,1.);R['additional_rays']+=1
    check('critical_k_exact_zero',k[0]==0 and tir[0] and np.isnan(d).all(),'Critical grazing is non-transmitting; no replacement direction')
    R['status']='PASS_UPDATED_BOUNDARY_CORE';R['finished_unix']=time.time();save()
    print(json.dumps({'status':R['status'],'total_rays':R['total_rays'],'additional_checks':len(R['checks'])}))
except Exception as e:
    R['status']='STOP_FIRST_FAILURE';R['error']=repr(e);save();raise
