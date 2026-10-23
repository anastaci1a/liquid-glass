"""Numeric/analytic controls for the private playback study; no fitting rerun."""
import ast,json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
root=Path('/evidence/apple-matches');out=root/'review-pass05-playback'
r=json.loads((out/'diagnostics.json').read_text());z=r['geometry']
A=z['amplitude_px'];b=z['original_band_px'];p=z['original_power'];R=z['radius'];LUMA=np.array([.2126,.7152,.0722])
tree=ast.parse((root/'playback-pass05.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['smooth5','displacement','response','ordered_response','shared_curve_response']],type_ignores=[]),'study-functions','exec'))
checks={}
domain=np.linspace(-b,3*b,10001)
expected=A*np.clip(1-domain/b,0,1)**p
checks['baseline_max_error_px']=float(np.max(abs(displacement(domain,1,1,p)-expected)))
assert checks['baseline_max_error_px']<1e-10
outer=np.linspace(0,b/4,1001);reference=A*(1-outer/b)**p
maximum_outer=maximum_slope=maximum_second=maximum_scale=0.
for width in [1,1.5,2,2.5,3,3.5,4]:
    for gain in [.75,1,1.25]:
        maximum_outer=max(maximum_outer,float(np.max(abs(displacement(outer,width,gain)-reference))))
        # Independent one-sided cubic interpolation at the two splice joins.
        h=1e-4*b
        for at in [b/4,b/2]:
            jets=[]
            for sign in [-1,1]:
                q=sign*np.arange(4,dtype=float)
                values=displacement(at+h*q,width,gain)
                co=np.polynomial.polynomial.polyfit(q,values,3)
                jets.append([co[1]/h,2*co[2]/h**2])
            maximum_slope=max(maximum_slope,abs(jets[0][0]-jets[1][0]))
            maximum_second=max(maximum_second,abs(jets[0][1]-jets[1][1]))
        # Analytic entry jets of the new tail equal the original jets times
        # gain, independently of end-power and tail width.
        w0=b/2;w=width*w0;q=4
        ld=(-q+q-p*width)/w
        ldd=(-q+q-p*width**2)/w**2
        assert abs(ld+p/w0)<1e-12 and abs(ldd+p/w0**2)<1e-12
        end=b/2+w
        assert displacement(np.array([end,end+1]),width,gain).max()==0
        assert np.isfinite(displacement(domain,width,gain)).all()
        saved=(A,b);v=displacement(domain,width,gain)
        A,b=3*A,3*b
        maximum_scale=max(maximum_scale,float(np.max(abs(displacement(3*domain,width,gain)-3*v))))
        A,b=saved
checks.update(outer_map_preservation_max_error_px=maximum_outer,splice_first_derivative_mismatch=maximum_slope,splice_second_derivative_mismatch=maximum_second,scale_covariance_max_error_px=maximum_scale)
assert maximum_outer<1e-10 and maximum_slope<1e-5 and maximum_second<.001 and maximum_scale<1e-9
# Scalar radial maps commute with rotation and have symmetric Jacobians away
# from the origin. This tests image-map integrability, not physical-body optics.
def mapping(x,y):
    rad=np.hypot(x,y);a=displacement(R-rad,1.5,1)
    scale=np.divide(rad-a,rad,out=np.ones_like(rad),where=rad>0)
    return x*scale,y*scale
rng=np.random.default_rng(5005);theta=rng.uniform(0,2*np.pi,100)
rad=rng.uniform(R-35,R-.1,100);x=rad*np.cos(theta);y=rad*np.sin(theta)
angle=.73;c,s=np.cos(angle),np.sin(angle);X,Y=mapping(x,y);XX,YY=mapping(c*x-s*y,s*x+c*y)
checks['rotation_max_error_px']=float(max(np.max(abs(XX-(c*X-s*Y))),np.max(abs(YY-(s*X+c*Y)))))
h=1e-4
dxy=(mapping(x,y+h)[0]-mapping(x,y-h)[0])/(2*h)
dyx=(mapping(x+h,y)[1]-mapping(x-h,y)[1])/(2*h)
checks['mixed_jacobian_mismatch']=float(np.max(abs(dxy-dyx)))
assert checks['rotation_max_error_px']<1e-9 and checks['mixed_jacobian_mismatch']<1e-6
for entry in r['geometry_trials']:assert entry['radial_derivative_sign_changes']==1
for entry in [r['icon_models']['white_plateau'],r['icon_models']['plateau_chroma']]:
    v=np.array(entry['parameters']);white=response(v,np.ones((10,3)))
    assert np.all(white==1)
    a=rng.uniform(0,1,(1000,3));C=response(v,a)
    assert C.min()>=0 and C.max()<=1 and np.isfinite(C).all()
checks['icon_white_plateau_and_output_bounds']='pass'
v=np.array(r['icon_ordered_model']['parameters'])
warm=np.sort(rng.uniform(0,1,(100000,3)),axis=-1)[:,::-1]
C=ordered_response(v,warm)
assert (np.diff(C,axis=-1)<=1e-12).all()
assert (ordered_response(v,np.ones((10,3)))==1).all()
assert (ordered_response(v,np.zeros((10,3)))==1-v[0]).all()
checks['ordered_icon_color']='100,000 warm RGB samples retain R>=G>=B; black input stays neutral; white stays white'
v=np.array(r['icon_shared_model']['parameters'])
C=shared_curve_response(v,warm)
assert (np.diff(C,axis=-1)<=1e-12).all() and (C>=0).all() and (C<=1).all()
gray=np.repeat(np.linspace(0,1,10001)[:,None],3,axis=-1)
C=shared_curve_response(v,gray)
assert np.max(abs(C[:,0]-C[:,1]))==0 and np.max(abs(C[:,1]-C[:,2]))==0
assert np.diff(C[:,0]).min()>=-1e-12 and (C[-1]==1).all()
checks['shared_icon_curve']='monotone on 10,001 gray samples; neutral grays and 100,000 warm color orderings preserved; white endpoint'
checks['grid_single_radial_fold']='all 21 tested profiles; not a universal guarantee'
checks['endpoint_continuity']='Inner exponent 4: a and its first three derivatives vanish at the inner join. Outer/middle splice only claims C2.'
(out/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2));print('PASS playback profile and icon controls')
