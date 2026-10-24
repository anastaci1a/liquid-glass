"""Fixed known-area controls followed by fixed direct-signal convergence."""
from pathlib import Path
import datetime,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from pixel_quadrature import rounded_rectangle_pixel_rule
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
def rule(pixel,half,r,center=(0,0),order=16,width=1):
 z=rounded_rectangle_pixel_rule(pixel,half,r,center=center,order=order,pixel_width=width);charge('quadrature_nodes',len(z['weights']));points=z['points'];weights=z['weights'];assert np.all(weights>0);assert weights.sum()<=1+1e-12
 if len(points):
  q=np.maximum(abs(points-np.array(center))-(np.array(half)-r),0);assert np.all(np.linalg.norm(q,axis=1)<r),'Strict inside nodes'
 return z
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
fixtures=[]
for pixel,half,r,expected in [((0,0),(2,2),1,1),((0,2),(4,2),1,.5),((0,2.2),(4,2),1,.3),((0,3),(4,2),1,0),((0,2.5),(4,2),1,0),((0,0),(.5,.5),.5,np.pi/4)]:
 charge('analytic_geometry_fixtures',1);z=rule(pixel,half,r);err=abs(z['weights'].sum()-expected);assert err<2e-12;fixtures.append({'pixel':pixel,'mass':float(z['weights'].sum()),'expected':expected,'error':float(err)})
for pixel in [(1.75,1.75),(2.35,.2),(.1,1.8)]:
 charge('analytic_geometry_fixtures',1);z=rule(pixel,(2.5,2),1);mass=z['weights'].sum()
 for v,c,h,r,w in [(np.array(pixel)+[7.3,-3.2],(7.3,-3.2),(2.5,2),1,1),(-np.array(pixel),(0,0),(2.5,2),1,1),(np.array(pixel)[::-1],(0,0),(2,2.5),1,1),(np.array(pixel)*3,(0,0),(7.5,6),3,3)]:
  charge('analytic_geometry_fixtures',1);q=rule(v,h,r,c,width=w);assert abs(q['weights'].sum()-mass)<2e-12
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'AREA_POSITIVITY_MEMBERSHIP_COVARIANCE_PASS','fixtures':fixtures,'ledger':dict(ledger)})
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from bevel_footprint_back import BevelFootprintBack
from geometric_optics import reflect_direction,fresnel_components
from environment_radiance import planar_annular_emitter
F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());rec=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());L=F['length_unit_native_pixels'];g=F['geometry'];rows=[]
for member in ['expanded','compact']:
 a=F['members'][member]['major_half'];b=g['minor_half'];surface=BevelFootprintBack(RoundedRectangleHarmonicBack((a,b),g['corner_radius'],cap_join_width=0),rec['depth'],rec['power']);case=json.loads((ROOT/('.evidence-working/expanded-geometry-02/a/case.json' if member=='expanded' else '.evidence-working/compact-geometry-01/a/case.json')).read_text());center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 for side in [-1,1]:
  ycenter=int(np.floor(center[1]+side*b*L+.5));xcenter=int(np.floor(center[0]+.5))
  for offset in [-1,0,1]:
   pixel=(xcenter,ycenter+offset);values={};masses={}
   for order in [8,16,32]:
    z=rule(pixel,(a*L,b*L),g['corner_radius']*L,center,order);points=z['points'];w=z['weights'];masses[order]=float(w.sum());n=len(w)
    if not n:values[order]=0.;continue
    charge('camera_front_points',n);charge('adapter_units',20*n);h,hx,hy,inside=surface.height_gradient((points[:,0]-center[0])/L,(points[:,1]-center[1])/L);assert inside.all() and (h>0).all();nf=np.c_[-hx,-hy,np.ones(n)];nf/=np.linalg.norm(nf,axis=1)[:,None];inc=np.zeros_like(nf);inc[:,2]=-1
    charge('reflection_points',n);d=reflect_direction(inc,nf);charge('Fresnel_points',n);power=fresnel_components(nf[:,2],1,1.5).mean(-1);charge('panel_intersections',n);em=planar_annular_emitter(np.c_[points,h*L],d,panel_z=1770,center_xy=(960,540));assert em['reaches_panel'].all();values[order]=float(np.dot(w,4*power*em['unit_radiance']))
   rows.append({'member':member,'side':side,'pixel':pixel,'signal':values,'area':masses,'difference_8_16':abs(values[8]-values[16]),'difference_16_32':abs(values[16]-values[32])})
save('result.json',{'status':'GEOMETRIC_AREA_AND_FIXED_SIGNAL_CHECK_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'ledger':ledger,'scope':'Straight-body selected pixels only, not full cap/full RGB convergence or an optical improvement.'});print(json.dumps({'records':rows,'ledger':ledger}),flush=True)
