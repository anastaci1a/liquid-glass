from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from closed_crowned_surface import ClosedRoundedSurface
from geometric_optics import reflect_direction,fresnel_components
from music_miniplayer_family import load_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));START=datetime.datetime.fromisoformat(P['start'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};F=load_family();old=json.loads((ROOT/'research/experiments/miniplayer-closed-perimeter-25/protocol.json').read_text())['parameters'];L=F['length_unit_native_pixels']
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});bindings={};data={}
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');items=[]
 for ref in ['a','b']:
  case=json.loads((work/ref/'case.json').read_text());center=np.array(case['center'],float)
  if member=='expanded':center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
  else:
   prev=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center+=L*np.array([prev['shape_dx'],prev['shape_dy']])
  knownfile=work/ref/'known.png';bindings[str(knownfile.relative_to(ROOT))]=sha(knownfile);bindings[str((work/ref/'case.json').relative_to(ROOT))]=sha(work/ref/'case.json');items.append(dict(case=case,center=center,known=cv2.imread(str(knownfile),0)>0,reference=ref))
 assert np.array_equal(items[0]['center'],items[1]['center']);data[member]=items
for file in ['reconstruction/closed_crowned_surface.py','reconstruction/geometric_optics.py','reconstruction/families/music-mini-player.json']:
 bindings[file]=sha(ROOT/file)
save('bindings-FIRST.json',bindings);records=[]
for member,items in data.items():
 a=F['members'][member]['major_half'];b=F['geometry']['minor_half'];R=F['geometry']['corner_radius'];s=ClosedRoundedSurface((a,b),R,old['eta'],old['z_offset'],0.);case=items[0]['case'];center=items[0]['center'];x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;Y,X=np.mgrid[y0:y1:.5,x0:x1:.5];X=(X-.25-center[0])/L;Y=(Y-.25-center[1])/L;charge('native_front_launches',X.size);charge('footprint_points',3*X.size);charge('conservative_delegate_units',16*X.size);z,inside=s.front_height(X,Y);boundary=s.boundary_mask(X,Y);reg=inside&~boundary;ids=np.flatnonzero(reg);entry=np.stack([X[reg],Y[reg],z[reg]],-1);charge('level_points',len(ids));charge('front_interface_points',len(ids));charge('conservative_delegate_units',9*len(ids));f,g=s.level_gradient(entry);assert np.max(abs(f))<1e-10;normal=g/np.linalg.norm(g,axis=-1)[:,None];camera=np.zeros_like(normal);camera[:,2]=-1;direction=reflect_direction(camera,normal);assert np.all(np.sum(direction*normal,axis=-1)>0);power=fresnel_components(normal[:,2],1.,1.5).mean(-1);down=direction[:,2]<0;up=direction[:,2]>0;source=np.full((len(ids),2),np.nan);t=(-2.1-entry[down,2])/direction[down,2];assert np.all(t>0);source[down]=entry[down,:2]+t[:,None]*direction[down,:2];np.savez_compressed(OUT/f'{member}-first-front.npz',flat_ids=ids,inside=inside,boundary=boundary,entry=entry,outward_normal=normal,reflected_direction=direction,reflectance=power,downward=down,source_XY=source)
 fields={};field=np.zeros(X.shape);field[boundary]=np.nan;field[reg]=power;fields['total_reflectance']=field.reshape(H,2,W,2).mean((1,3));env=np.zeros(X.size);env[ids[up]]=power[up];fields['unknown_upward_power']=env.reshape(H,2,W,2).mean((1,3));role_rows=[]
 for item in items:
  xy=source[down]*L+center;charge('source_endpoint_checks',len(xy));known=item['known'];aa=np.floor(xy[:,0]).astype(int);bb=np.floor(xy[:,1]).astype(int);valid=np.isfinite(xy).all(-1)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);ii=np.flatnonzero(valid);charge('raw_mask_lookups',4*len(ii));supported=np.zeros(len(xy),bool);supported[ii]=known[bb[ii],aa[ii]]&known[bb[ii]+1,aa[ii]]&known[bb[ii],aa[ii]+1]&known[bb[ii]+1,aa[ii]+1];good=np.zeros(X.size);bad=np.zeros(X.size);downids=ids[down];good[downids[supported]]=power[down][supported];bad[downids[~supported]]=power[down][~supported];fields[item['reference']+'_known_downward_power']=good.reshape(H,2,W,2).mean((1,3));fields[item['reference']+'_unsupported_downward_power']=bad.reshape(H,2,W,2).mean((1,3));role_rows.append({'reference':item['reference'],'downward_endpoints':len(xy),'supported':int(supported.sum()),'unsupported':int((~supported).sum()),'sum_downward_power':float(power[down].sum()),'sum_unsupported_downward_power':float(power[down][~supported].sum()),'RGB_queries':0})
 angles=np.rad2deg(np.arccos(normal[:,2]));record={'member':member,'regular_entries':len(ids),'boundary_unresolved':int(boundary.sum()),'max_front_angle_degrees':float(angles.max()),'front_angles_above45':int((angles>45).sum()),'front_angles_above80':int((angles>80).sum()),'reflectance_max':float(power.max()),'front_reflectance_above_half':int((power>=.5).sum()),'front_downward':int(down.sum()),'front_upward':int(up.sum()),'role_rows':role_rows,'pixel_reflectance_max':float(np.nanmax(fields['total_reflectance']))};records.append(record);np.savez_compressed(OUT/f'{member}-pixel-power.npz',**fields)
 width=min(W,1080);height=round(H*width/W);im=Image.fromarray(np.uint8(np.rint(255*np.nan_to_num(fields['total_reflectance'],nan=.5)))).convert('RGB').resize((width,height),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(width,height+64),'white');canvas.paste(im,(0,64));ImageDraw.Draw(canvas).text((8,20),'Unit first-front reflectance, linear0..1; not a radiance/RGB reconstruction',fill='black',font=ImageFont.load_default(size=15));canvas.save(OUT/f'{member}-unit-reflectance.png')
 if member=='expanded':
  assert datetime.datetime.now(datetime.timezone.utc)<START+datetime.timedelta(minutes=5),'Original checkpoint';save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_full_member':record,'source_RGB_queries':0,'ledger':ledger})
 print(json.dumps(record),flush=True)
assert all(sha(ROOT/file)==digest for file,digest in bindings.items());save('bindings-LAST.json',bindings);save('result.json',{'status':'FULL_NATIVE_FIRST_INTERFACE_COMPLETE_SCENE_UNOBSERVED','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'RGB_queries_filters_fits_internal_rays':0,'radiance_or_fidelity_acceptance':False,'selected_changed':False})
