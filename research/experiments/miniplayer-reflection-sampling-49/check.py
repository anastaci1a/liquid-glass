"""Finite sampling of the actual direct-reflection component only."""
from pathlib import Path
import datetime,json,sys,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from bevel_footprint_back import BevelFootprintBack
from geometric_optics import reflect_direction,fresnel_components
from environment_radiance import planar_annular_emitter
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());recipe=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());L=F['length_unit_native_pixels'];g=F['geometry'];records=[];profiles=[];arrays={}
for member in ['expanded','compact']:
 a=F['members'][member]['major_half'];b=g['minor_half'];surface=BevelFootprintBack(RoundedRectangleHarmonicBack((a,b),g['corner_radius'],cap_join_width=0),recipe['depth'],recipe['power']);work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');case=json.loads((work/'a/case.json').read_text());x0,y0,x1,y1=case['crop'];center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 q=np.load(ROOT/f'research/experiments/miniplayer-shallow-native-42/{member}-paths.npz');inside=q['inside'];cached=np.zeros_like(inside,float);panel=np.load(ROOT/f'research/experiments/miniplayer-finite-emitter-48/{member}-panel-paths.npz')['unit_radiance'];cached[inside]=4*q['front_reflection_power'][inside]*panel
 tiles=[('upper',center[0],center[1]-b*L),('lower',center[0],center[1]+b*L),('right_cap',center[0]+a*L,center[1])]
 for name,cx,cy in tiles:
  left=int(np.floor(cx+.5))-12;top=int(np.floor(cy+.5))-12;assert x0<=left<left+24<=x1 and y0<=top<top+24<=y1
  results={};subray_error=None
  for s in P['levels']:
   yy,xx=np.mgrid[top:top+24:1/s,left:left+24:1/s];phase=(s-1)/(2*s);x=(xx-phase-center[0])/L;y=(yy-phase-center[1])/L;charge('camera_front_points',x.size);charge('conservative_adapter_units',20*x.size);h,hx,hy,mask=surface.height_gradient(x,y);assert not (mask&(h==0)).any(),'Exact boundary sample';N=int(mask.sum());charge('reflection_points',N);charge('Fresnel_points',N);nf=np.stack([-hx[mask],-hy[mask],np.ones(N)],-1);nf/=np.linalg.norm(nf,axis=-1)[:,None];camera=np.zeros_like(nf);camera[:,2]=-1;direction=reflect_direction(camera,nf);power=fresnel_components(nf[:,2],1.,1.5).mean(-1);positions=np.c_[x[mask]*L+center[0],y[mask]*L+center[1],h[mask]*L];charge('panel_intersections',N);emitter=planar_annular_emitter(positions,direction,panel_z=1770.,center_xy=(960.,540.));assert emitter['reaches_panel'].all();signal=np.zeros_like(x);signal[mask]=4*power*emitter['unit_radiance'];pixel=signal.reshape(24,s,24,s).mean((1,3));results[s]=pixel;arrays[f'{member}_{name}_AA{s}']=pixel
   if s==2:
    old=cached[2*(top-y0):2*(top-y0+24),2*(left-x0):2*(left-x0+24)];oldmask=inside[2*(top-y0):2*(top-y0+24),2*(left-x0):2*(left-x0+24)];charge('cached_identity_points',old.size);assert np.array_equal(mask,oldmask);subray_error=float(np.max(abs(signal-old)));assert subray_error<1e-14
    if not (OUT/'checkpoint.json').exists():save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_AA2_subray_error':subray_error,'membership_exact':True,'ledger':ledger})
  row=dict(member=member,tile=name,bounds_native=[left,top,left+24,top+24],AA2_identity_max_error=subray_error,AA2_to_AA4_max=float(np.max(abs(results[2]-results[4]))),AA4_to_AA8_max=float(np.max(abs(results[4]-results[8]))),AA2_to_AA8_max=float(np.max(abs(results[2]-results[8]))));records.append(row)
  for s,v in results.items():profiles.append({'member':member,'tile':name,'samples_per_axis':s,'linear_signal':(v.mean(0) if name=='right_cap' else v.mean(1)).tolist()})
np.savez_compressed(OUT/'reflection-tiles.npz',**arrays);save('profiles.json',{'scope':'Reflected linear component only; no Apple target profile or full reconstruction','records':profiles});save('result.json',{'status':'FIXED_SAMPLING_COMPONENT_DIAGNOSTIC_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'score_epoch_changed':False});print(json.dumps({'status':'PASS','records':records,'ledger':ledger}),flush=True)
