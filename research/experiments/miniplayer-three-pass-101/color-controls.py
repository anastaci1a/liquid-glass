from pathlib import Path
import numpy as np,json,datetime
from miniplayer_color_refinement import interior_chroma,bright_colored_rim
from environment_radiance import decode_srgb
from outline_response import cap_strength
B=Path(__file__).parent
samples=np.array([[0,0,0],[1,1,1],[.95,.85,.3],[.2,.4,.8],[.4,.4,.4],[.9,.2,.1]],float)
weights=np.array([.2126,.7152,.0722]);rows=[]
for k in [1.,1.15,1.5]:
 z=interior_chroma(samples,k);err=float(np.max(abs(decode_srgb(z)@weights-decode_srgb(samples)@weights)));assert err<1e-14 and z.min()>=-1e-14 and z.max()<=1+1e-14
 rows.append(dict(chroma=k,luminance_error=err,outputs=z.tolist()))
for exposure,sat in [(1,1),(1.8,1),(1.8,1.8)]:
 z=bright_colored_rim(samples,samples,np.ones(6),exposure,sat);assert np.array_equal(z[1],[1,1,1]) and z[0].min()>0 and z.min()>=-1e-14 and z.max()<=1+1e-14
 assert np.array_equal(bright_colored_rim(samples,samples,np.zeros(6),exposure,sat),samples)
 rows.append(dict(exposure=exposure,saturation=sat,outputs=z.tolist()))
a=dict(start=-45,minimum=30,hold=60,recover=85);t=np.linspace(30,60,17)*np.pi/180
x=5+np.cos(t);y=-np.sin(t);v=cap_strength(x,y,(6,1),1,(0,0),a);vm=cap_strength(-x,-y,(6,1),1,(0,0),a)
assert np.array_equal(v,vm) and (v==0).all()
(B/'color-controls.json').write_text(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),fixed_color_samples=36,angular_samples=34,rows=rows,opposing_gaps_exact_zero=True),indent=2)+'\n')
print('COLOR AND ANGULAR CONTROLS PASS')
