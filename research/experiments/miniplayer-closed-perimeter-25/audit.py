"""One closed same-footprint geometry; sparse transport and support only."""
from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from closed_crowned_surface import ClosedRoundedSurface
from geometric_optics import ClosedCircularOval,trace_closed_orthographic,reflect_direction,fresnel_components
from music_miniplayer_family import load_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));START=datetime.datetime.fromisoformat(P['start'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};F=load_family();p=P['parameters'];cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
class Counted:
 def __init__(self,shape):self.shape=shape
 def __getattr__(self,k):return getattr(self.shape,k)
 def level_gradient(self,x):
  n=np.asarray(x).shape[:-1];n=int(np.prod(n));charge('level_points',n);charge('conservative_delegate_units',6*n);return self.shape.level_gradient(x)
 def front_height(self,x,y):
  charge('conservative_delegate_units',12*np.broadcast_arrays(x,y)[0].size);return self.shape.front_height(x,y)
 def boundary_mask(self,x,y):
  charge('conservative_delegate_units',4*np.broadcast_arrays(x,y)[0].size);return self.shape.boundary_mask(x,y)
def trace(s,x,y,n,fixture=False):
 count=np.broadcast_arrays(x,y)[0].size;charge('fixture_rays' if fixture else 'sparse_grid_rays',count);charge('conservative_delegate_units',4*count);return trace_closed_orthographic(Counted(s),x,y,n,2.1)
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});proof=[]
for member in ['expanded','compact']:
 a=F['members'][member]['major_half'];b=F['geometry']['minor_half'];R=F['geometry']['corner_radius'];s=ClosedRoundedSurface((a,b),R,p['eta'],p['z_offset'],0.);test=np.array([[0.,0.,p['z_offset']],[.25*a,.3*b,p['z_offset']-.04],[a-.2*R,.25*b,p['z_offset']-.07]])
 charge('level_points',7*len(test));charge('conservative_delegate_units',6*7*len(test));val,g=s.level_gradient(test);fd=[]
 for axis in range(3):
  e=np.zeros(3);e[axis]=1e-6;fd.append((s.level_gradient(test+e)[0]-s.level_gradient(test-e)[0])/(2e-6))
 error=float(np.max(abs(np.stack(fd,-1)-g)));assert error<1e-7
 top,bottom=s.sheet_heights(np.array([0.]),np.array([0.]));assert abs(top[0]-p['z_offset'])<1e-15 and abs(bottom[0]-(p['z_offset']-2*p['eta']))<1e-15
 xp=np.array([a,-a,0,0]);yp=np.array([0,0,b,-b]);assert s.boundary_mask(xp,yp).all() and not s.front_height(xp,yp)[1].any()
 proof.append({'member':member,'gradient_FD_max':error,'center_front_back_exact':True,'four_projected_poles_excluded':True,'convexity':'Squared distance to convex inner rectangle plus positive z square; global convexity for kappa0.','normal_bound':s.regular_gradient_lower_bound})
X,Y=np.meshgrid(np.linspace(-.75,.75,5),np.linspace(-.75,.75,5));new=ClosedRoundedSurface((1.,1.),1.,p['eta'],0.,0.);old=ClosedCircularOval(p['eta'],0.)
for index in [1.,1.5]:
 q=trace(new,X,Y,index,True);z=trace(old,X,Y,index,True)
 for k in ['inside','projected_inside','regular_entry','boundary_unresolved','complete','blocked']:assert np.array_equal(q[k],z[k]),k
 assert np.array_equal(np.isnan(q['X']),np.isnan(z['X'])) and np.array_equal(np.isnan(q['Y']),np.isnan(z['Y']))
 for k in ['X','Y','entry','exit','entry_normal','exit_normal','internal_direction','exit_direction']:
  assert np.nanmax(abs(q[k]-z[k]))<1e-9,k
assert datetime.datetime.now(datetime.timezone.utc)<START+datetime.timedelta(minutes=5),'Checkpoint deadline'
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'geometry':proof,'circle_contract_parity':True,'source_RGB_queries':0,'ledger':ledger})
records=[]
for member in ['expanded','compact']:
 a=F['members'][member]['major_half'];b=F['geometry']['minor_half'];R=F['geometry']['corner_radius'];s=ClosedRoundedSurface((a,b),R,p['eta'],p['z_offset'],0.);X,Y=np.meshgrid(np.linspace(-1.01*a,1.01*a,65),np.linspace(-1.01*b,1.01*b,33));X=np.r_[X.ravel(),a,-a,0,0];Y=np.r_[Y.ravel(),0,0,b,-b];q=trace(s,X,Y,1.5);np.savez_compressed(OUT/f'{member}-paths.npz',**q);reg=q['regular_entry'];miss=~q['projected_inside'];assert np.array_equal(q['X'][miss],X[miss]) and np.array_equal(q['Y'][miss],Y[miss]);assert np.isnan(q['X'][q['boundary_unresolved']]).all()
 normals=q['entry_normal'][reg];charge('front_interface_points',len(normals));charge('conservative_delegate_units',3*len(normals));camera=np.zeros_like(normals);camera[:,2]=-1;d=reflect_direction(camera,normals);Rf=fresnel_components(normals[:,2],1.,1.5).mean(-1);entry=q['entry'][reg];down=d[:,2]<0;up=d[:,2]>0;front_source=np.full((len(d),2),np.nan);t=(-2.1-entry[down,2])/d[down,2];assert (t>0).all();front_source[down]=entry[down,:2]+t[:,None]*d[down,:2];np.savez_compressed(OUT/f'{member}-front-roles.npz',entry=entry,direction=d,power=Rf,downward=down,source_XY=front_source)
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');source_rows=[]
 for ref in ['a','b']:
  case=json.loads((work/ref/'case.json').read_text());center=np.array(case['center'],float)
  if member=='expanded':center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
  else:
   prev=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center+=88.5*np.array([prev['shape_dx'],prev['shape_dy']])
  known=cv2.imread(str(work/ref/'known.png'),0)>0;charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  def support(coords,mask):
   xy=coords*88.5+center;charge('source_audit_points',len(xy));ok=np.isfinite(xy).all(-1);aa=np.floor(np.where(ok,xy[:,0],0)).astype(int);bb=np.floor(np.where(ok,xy[:,1],0)).astype(int);bounds=ok&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);ids=np.flatnonzero(bounds);charge('bilinear_mask_lookups',4*len(ids));result=np.zeros(len(coords),bool);result[ids]=mask[bb[ids],aa[ids]]&mask[bb[ids]+1,aa[ids]]&mask[bb[ids],aa[ids]+1]&mask[bb[ids]+1,aa[ids]+1];return result
  complete=q['inside']&q['complete'];primary=np.stack([q['X'][complete],q['Y'][complete]],-1);supported=support(primary,safe);fr=support(front_source[down],known);source_rows.append({'reference':ref,'primary_transmitted':len(primary),'primary_supported':int(supported.sum()),'primary_unsupported':int((~supported).sum()),'front_downward':int(down.sum()),'front_raw_supported':int(fr.sum()),'front_raw_unsupported':int((~fr).sum()),'RGB_queries':0})
 angles=np.rad2deg(np.arccos(normals[:,2]));row={'member':member,'sampled_rays':len(X),'regular_entries':int(reg.sum()),'primary_transmitted':int((q['inside']&q['complete']).sum()),'blocked_TIR':int(q['blocked'].sum()),'other_incomplete_regular':int((reg&~q['complete']&~q['blocked']).sum()),'projected_tangencies':int(q['boundary_unresolved'].sum()),'front_incidence_max_degrees':float(angles.max()),'front_incidence_over45':int((angles>45).sum()),'front_reflected_down':int(down.sum()),'front_reflected_up':int(up.sum()),'front_reflectance_min':float(Rf.min()),'front_reflectance_max':float(Rf.max()),'source_rows':source_rows,'full_native_source_certificate':False};records.append(row)
 # Same-F sections and actual internal segments; vertical magnification explicit.
 sections=[]
 for axis,extent in [('x',a),('y',b)]:
  v=np.linspace(-extent,extent,257);zero=np.zeros_like(v);x,y=(v,zero) if axis=='x' else (zero,v);charge('section_points',2*len(v));top,bot=s.sheet_heights(x,y);points=np.r_[np.stack([x,y,top],-1),np.stack([x,y,bot],-1)];charge('level_points',len(points));charge('conservative_delegate_units',6*len(points));assert np.nanmax(abs(s.level_gradient(points)[0]))<1e-10;sections.append({'axis':axis,'coordinate':v.tolist(),'front':top.tolist(),'back':bot.tolist()})
 save(f'{member}-sections.json',{'same_F':True,'sections':sections});print(json.dumps(row),flush=True)
save('result.json',{'status':'CLOSED_GEOMETRY_SPARSE_PATH_AND_ROLE_AUDIT_ONLY','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'RGB_images_fits':0,'selected_changed':False})
