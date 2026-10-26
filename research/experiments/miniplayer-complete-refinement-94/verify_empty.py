from pathlib import Path
import sys,json,datetime
import numpy as np
ROOT=Path(__file__).resolve().parents[3];O=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from ellipse_core_coordinate import EllipseCoreSplineBack
from hermite_height_back import HermiteFootprintBack
from raised_front_optics import trace_raised_front_orthographic,VerticalScaleBack
F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());g=F['geometry'];s=EllipseCoreSplineBack((F['members']['expanded']['major_half'],g['minor_half']),g['corner_radius'],g['breaks'],g['height_controls']);b=HermiteFootprintBack(s,json.loads((ROOT/g['back_profile']).read_text()));f=VerticalScaleBack(s,.5)
x=np.linspace(-8,8,60);y=np.full(60,2.);q=trace_raised_front_orthographic(b,x,y,1,1.5,2.1,front_surface=f);assert q['complete'].all() and not q['inside'].any();assert np.array_equal(q['X'],x) and np.array_equal(q['Y'],y);assert np.isnan(q['front']).all() and np.isnan(q['primary_power']).all()
x=np.array([s.half[0],-s.half[0],0,0]);y=np.array([0,0,s.half[1],-s.half[1]]);q=trace_raised_front_orthographic(b,x,y,1,1.5,2.1,front_surface=f);assert q['boundary_unresolved'].all() and not q['complete'].any() and np.isnan(q['X']).all()
(O/'empty-controls.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'launches':64,'regular_interface_events':0,'clear_identity_and_boundary_nan_contract':'PASS'},indent=2)+'\n');print('PASS empty clear and unresolved boundary contract')
