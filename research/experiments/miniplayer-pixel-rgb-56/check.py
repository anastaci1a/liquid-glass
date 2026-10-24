"""Complete finite-pixel RGB controls; no target fit or full reconstruction."""
from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from music_miniplayer_family import load_working_family,surface_for_member
from pixel_quadrature import rounded_rectangle_pixel_rule
from hermite_height_back import HermiteFootprintBack
from bevel_footprint_back import BevelFootprintBack
from raised_front_optics import trace_raised_front_orthographic
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,planar_annular_emitter
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
def count(label,n):charge('surface_points',n);charge('adapter_units',20*n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
F=load_working_family();L=F['length_unit_native_pixels'];g=F['geometry'];previous=json.loads((ROOT/'research/experiments/miniplayer-cap-quadrature-55/result.json').read_text());model=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/back-profile.json').read_text());recipe=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());preserved=json.loads((ROOT/'research/experiments/miniplayer-shared-transfer-06/preservation.json').read_text())['rows'];data={};first={}
for row in preserved:
 member,k=row['member'],row['reference'];work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');assert sha(work/k/'case.json')==row['case_sha256']
 for n,d in row['hashes'].items():assert sha(work/k/n)==d;first[str((work/k/n).relative_to(ROOT))]=d
 charge('Study_mask_points',1360*250 if member=='expanded' else 920*240);s=Study(work/k);known=cv2.imread(str(work/k/'known.png'),0)>0;charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;data[(member,k)]={'s':s,'known':known,'safe':safe}
save('inputs-FIRST.json',first)
def audit(X,Y,mask):
 X,Y=np.asarray(X),np.asarray(Y);charge('source_audit_points',X.size);a=np.floor(X).astype(int);b=np.floor(Y).astype(int);assert np.isfinite(X).all() and np.isfinite(Y).all() and ((a>=0)&(b>=0)&(a+1<mask.shape[1])&(b+1<mask.shape[0])).all();charge('bilinear_mask_lookups',4*X.size);assert (mask[b,a]&mask[b,a+1]&mask[b+1,a]&mask[b+1,a+1]).all(),'Unsupported contributing source'
def sample(field,X,Y):
 charge('RGB_queries',len(X));a=np.floor(X).astype(int);b=np.floor(Y).astype(int);wx=(X-a)[:,None];wy=(Y-b)[:,None];return (field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
geometry={};proof=[]
for member in ['expanded','compact']:
 old=surface_for_member(member);back=HermiteFootprintBack(old,model);front=BevelFootprintBack(old.coordinate,recipe['depth'],recipe['power']);case=data[(member,'a')]['s'].case
 center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 rows=[r for r in previous['records'] if r['member']==member];pixels=np.array([r['pixel'] for r in rows]);clearpoints=np.concatenate([p+np.array([[-.25,-.25],[.25,-.25],[-.25,.25],[.25,.25]]) for p in pixels]);geometry[(member,'clear')]=clearpoints
 for k in ['a','b']:audit(clearpoints[:,0],clearpoints[:,1],data[(member,k)]['known'])
 for order in [8,16,32]:
  zz=[rounded_rectangle_pixel_rule(p,(old.half[0]*L,old.half[1]*L),old.radius*L,center=center,order=order) for p in pixels];points=np.concatenate([z['points'] for z in zz]);weights=np.concatenate([z['weights'] for z in zz]);indices=np.concatenate([np.full(len(z['weights']),i,int) for i,z in enumerate(zz)]);charge('quadrature_nodes',len(weights));charge('native_rays',len(weights));q=trace_raised_front_orthographic(back,(points[:,0]-center[0])/L,(points[:,1]-center[1])/L,1,1.5,F['optics']['background_distance'],count,front_surface=front);assert q['inside'].all() and q['complete'].all() and not q['boundary_unresolved'].any();X=q['X']*L+center[0];Y=q['Y']*L+center[1]
  for k in ['a','b']:
   audit(X,Y,data[(member,k)]['safe']);audit(points[:,0],points[:,1],data[(member,k)]['known']);proof.append({'member':member,'reference':k,'order':order,'inside_paths':len(weights),'unsupported':0,'kernel_radius':21})
  charge('panel_intersections',len(weights));panel=planar_annular_emitter(q['front']*L+np.array([*center,0]),q['front_reflection_direction'],panel_z=1770,center_xy=(960,540));assert panel['reaches_panel'].all();geometry[(member,order)]=(points,weights,indices,q,X,Y,panel['unit_radiance'],pixels)
save('source-FIRST.json',{'status':'ALL_MEMBERS_REFERENCES_ORDERS_PASS_BEFORE_RGB','records':proof,'observed_truth':False});save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_paths_complete':True,'all_source_gates_pass_before_RGB':True,'ledger':dict(ledger)})
records=[];arrays={}
for (member,k),d in data.items():
 charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(d['s'].source,d['known'],6.75);assert r==21 and np.array_equal(safe,d['safe']);cp=geometry[(member,'clear')];fullclear=sample(d['s'].source,cp[:,0],cp[:,1]).reshape(-1,4,3).mean(1);colors={};masses={}
 for order in [8,16,32]:
  points,w,idx,q,X,Y,panel,pixels=geometry[(member,order)];raw=sample(field,X,Y);clear=sample(d['s'].source,points[:,0],points[:,1]);graded=neutral_color_response(raw,gain=F['material']['gain'],bias=F['material']['bias']);lin=q['primary_power'][:,None]*decode_srgb(graded)+4*(q['front_reflection_power']*panel)[:,None];encoded=encode_srgb(lin);charge('preclip_channels',encoded.size);clips=int(((encoded<0)|(encoded>1)).sum());glass=np.clip(encoded,0,1);value=fullclear.copy();np.add.at(value,idx,w[:,None]*(glass-clear));mass=np.zeros(len(pixels));np.add.at(mass,idx,w);colors[order]=value;masses[order]=mass;arrays[f'{member}_{k}_order{order}']=value
  assert np.isfinite(value).all();records.append({'member':member,'reference':k,'order':order,'clipped_channels':clips,'pixels':pixels.tolist(),'pre_foreground_RGB':value.tolist(),'covered_area':mass.tolist()})
 records.append({'member':member,'reference':k,'max_RGB_difference_8_16':float(np.max(abs(colors[8]-colors[16]))),'max_RGB_difference_16_32':float(np.max(abs(colors[16]-colors[32]))),'units':'normalized encodedRGB, not8bit levels'})
np.savez_compressed(OUT/'pixel-colors.npz',**arrays);save('result.json',{'status':'FIXED_COMPLETE_PIXEL_RGB_INTEGRATION_CHECK_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'full_image_convergence':False,'source_support':'Conditional original mosaic, observed hidden truth zero.'});print(json.dumps({'status':'COMPLETE','ledger':ledger,'differences':[r for r in records if 'max_RGB_difference_16_32' in r]}),flush=True)
