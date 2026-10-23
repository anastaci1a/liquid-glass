from pathlib import Path
import sys,json,datetime,time,hashlib,os
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent;R=ROOT.parents[2]
sys.path.insert(0,str(R/'reconstruction'));sys.path.insert(0,str(ROOT))
from harmonic_crowned_back import HarmonicCrownedBack
from geometric_optics import trace_flat_front_orthographic
# Load only the already validated translation adapter from its frozen file.
import importlib.util
sp=importlib.util.spec_from_file_location('frozen_pose',ROOT/'checkpoint.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);PosedSurface=module.PosedSurface
os.umask(0o002)
proto=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(proto['checkpoint_deadline_utc'].replace('Z','+00:00')).timestamp()
assert time.time()<end and not (P/'checkpoint.json').exists()
proposal=json.loads((ROOT/'proposal.json').read_text());rows=[];count=0;arrays={}
for pin in proposal['code']:assert hashlib.sha256((R/pin['file']).read_bytes()).hexdigest()==pin['sha256']
for item in proposal['cases']:
 a,b=item['corrected_half_over_L'];base=HarmonicCrownedBack((a,b),.15,.4,.08);assert .5>base.maximum_height
 dx=(item['corrected_center'][0]-item['center'][0])/item['L'];dy=(item['corrected_center'][1]-item['center'][1])/item['L'];s=PosedSurface(base,dx,dy)
 yy,xx=np.meshgrid(np.linspace(-.95*b,.95*b,9),np.linspace(-.95*a,.95*a,9),indexing='ij');x=xx+dx;y=yy+dy
 count+=162;assert count<=1024
 q=trace_flat_front_orthographic(s,x,y,1.5,.5);old=trace_flat_front_orthographic(s,x,y,1.5,2.)
 assert q['complete'].all() and old['complete'].all()
 for k in ['inside','back','outward_normal','exit_direction']:assert np.array_equal(q[k],old[k],equal_nan=True),k
 actual=q['inside'];assert np.all(q['exit_direction'][actual,2]<0);assert np.all(q['path_length']>0)
 expected_x=old['X']-1.5*q['exit_direction'][...,0]/(-q['exit_direction'][...,2]);expected_y=old['Y']-1.5*q['exit_direction'][...,1]/(-q['exit_direction'][...,2]);err=max(float(abs(q['X']-expected_x).max()),float(abs(q['Y']-expected_y).max()));assert err<1e-12
 rows.append(dict(case=item['key'],maximum_height=base.maximum_height,minimum_background_clearance=.5-base.maximum_height,minimum_discriminant=float(q['discriminant'].min()),complete=True,unchanged_geometry_normal_direction=True,linear_propagation_error=err))
 for k in ['X','Y','inside','back','outward_normal','exit_direction','path_length','complete']:arrays[item['key']+'_'+k]=q[k]
assert time.time()<end
np.savez_compressed(P/'fixture-paths.npz',**arrays)
(P/'checkpoint.json').write_text(json.dumps(dict(status='PASS_FIXED_DISTANCE_GEOMETRY',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),charged_fixture_rays=count,rows=rows,RGB_queries=0,new_native_rays=0),indent=2)+'\n')
print((P/'checkpoint.json').read_text())
