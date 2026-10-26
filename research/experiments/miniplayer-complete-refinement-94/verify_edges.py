from pathlib import Path
import json,datetime,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from ellipse_core_coordinate import EllipseCoreSplineBack
from hermite_height_back import HermiteFootprintBack
from raised_front_optics import VerticalScaleBack,trace_raised_front_orthographic
P=json.loads((OUT/'plan.json').read_text());F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());g=F['geometry'];ledger=json.loads((OUT/'geometry-control-ledger.json').read_text())
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['geometry_deadline']);assert ledger[k]+n<=P['geometry_caps'][k];ledger[k]+=int(n)
rows=[]
for member in ['expanded','compact']:
 A=F['members'][member]['major_half'];B=g['minor_half'];R=g['corner_radius'];a,b=A-R,B-R
 base=EllipseCoreSplineBack((A,B),R,g['breaks'],g['height_controls'],charge);back=HermiteFootprintBack(base,json.loads((ROOT/g['back_profile']).read_text()));front=VerticalScaleBack(base,g['front_scale'])
 t=np.arange(8)*np.pi/4;n=np.stack([np.cos(t),np.sin(t)],-1);z=np.hypot(a*n[:,0],b*n[:,1]);e=np.stack([a*a*n[:,0]/z,b*b*n[:,1]/z],-1)
 pts=np.concatenate([e+rho*R*n for rho in [.9,.99,.999]])
 for index in [1.,1.5]:
  charge('fixture_rays',len(pts));q=trace_raised_front_orthographic(back,*pts.T,1.,index,F['optics']['background_distance'],lambda k,n:charge('height_point_queries',n),front_surface=front)
  assert q['complete'].all();assert np.max(abs(q['back_residual']))<2e-11
  if index==1:assert max(np.max(abs(q['X']-pts[:,0])),np.max(abs(q['Y']-pts[:,1])))<1e-9
  rows.append({'member':member,'index':index,'rays':len(pts),'min_outgoing_clearance':float(np.nanmin(q['outgoing_back_clearance'])),'min_raw_front_clearance':float(np.nanmin(q['reflection_front_clearance'])),'monotone_escape':bool(q['front_reflection_escape_certified'].all())})
(OUT/'edge-controls.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'cumulative_ledger':ledger},indent=2)+'\n');print(json.dumps(rows))
