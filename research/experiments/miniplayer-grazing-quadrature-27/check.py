from pathlib import Path
import sys,json,datetime,warnings
import numpy as np
from scipy.integrate import quad,IntegrationWarning
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from closed_crowned_surface import ClosedRoundedSurface
from geometric_optics import fresnel_components
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));START=datetime.datetime.fromisoformat(P['start'].replace('Z','+00:00'));F=json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text());old=json.loads((ROOT/'research/experiments/miniplayer-closed-perimeter-25/protocol.json').read_text())['parameters'];ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});data=[]
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');case=json.loads((work/'a/case.json').read_text());cx,cy=case['center']
 if member=='expanded':cx,cy=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 else:
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];cx+=88.5*prior['shape_dx'];cy+=88.5*prior['shape_dy']
 s=ClosedRoundedSurface((F['members'][member]['major_half'],F['geometry']['minor_half']),F['geometry']['corner_radius'],old['eta'],old['z_offset'],0.);cached=np.load(ROOT/f'research/experiments/miniplayer-native-front-26/{member}-pixel-power.npz')['total_reflectance'];x0,y0,_,_=case['crop'];b=F['geometry']['minor_half'];L=88.5
 def reflectance(pixel_y,s=s,cy=cy):
  charge('callback_points',1);charge('geometry_delegate_units',20);y=(pixel_y-cy)/88.5;z,inside=s.front_height(np.array([0.]),np.array([y]))
  if s.boundary_mask(np.array([0.]),np.array([y]))[0]:return 1.
  if not inside[0]:return 0.
  point=np.array([[0.,y,z[0]]]);f,g=s.level_gradient(point);assert abs(f[0])<1e-10;cos=g[0,2]/np.linalg.norm(g[0]);charge('Fresnel_points',1);return float(fresnel_components(np.array([cos]),1.,1.5).mean())
 for side,edge in [('upper',cy-b*L),('lower',cy+b*L)]:
  for row in range(round(edge)-1,round(edge)+2):
   charge('native_AA2_identity_pixels',1);aa2=sum(reflectance(row+v) for v in [-.25,.25])/2;expected=float(cached[row-y0,round(cx)-x0]);assert abs(aa2-expected)<1e-12,'AA2 cached discrepancy';data.append(dict(member=member,side=side,row=row,edge=edge,AA2=aa2,callback=reflectance,lower=cy-b*L,upper=cy+b*L))
assert datetime.datetime.now(datetime.timezone.utc)<START+datetime.timedelta(minutes=3),'Checkpoint deadline';save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all12_AA2_identities_match':True,'before_adaptive_integration':True,'ledger':ledger})
records=[]
for d in data:
 callback=d['callback'];row=d['row'];charge('AA8_pixels',1);aa8=sum(callback(row+(i+.5)/8-.5) for i in range(8))/8;lo=max(row-.5,d['lower']);hi=min(row+.5,d['upper']);charge('pixel_integrals',1)
 if hi<=lo:value,error=0.,0.
 else:
  with warnings.catch_warnings():
   warnings.simplefilter('error',IntegrationWarning);value,error=quad(callback,lo,hi,epsabs=1e-10,epsrel=1e-7,limit=128)
 assert error<1e-7,'Quadrature uncertainty';records.append({k:v for k,v in d.items() if k not in ['callback','lower','upper']}|dict(AA8=aa8,adaptive=value,estimated_error=error,AA2_error=abs(d['AA2']-value),AA8_error=abs(aa8-value)))
save('result.json',{'status':'STRAIGHT_EDGE_UNIT_REFLECTANCE_QUADRATURE_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'source_RGB_queries_internal_traces_fits':0,'AA2_protocol_unchanged':True,'optical_acceptance':False})
