from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from closed_power_surface import ClosedPowerSurface
from geometric_optics import next_convex_boundary
from polarization_transport import polarized_interface
from music_miniplayer_family import load_working_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
class Counted(ClosedPowerSurface):
 @property
 def half_extents(self):charge('bound_reads',1);return super().half_extents
 def level_gradient(self,p):
  n=np.asarray(p).size//3;charge('level_points',n);charge('adapter_units',20*n);return super().level_gradient(p)
def interface(d,n,nf,nt,B,C):
 for k in ['interface_points','interface_encounters','Snell_points','reflection_points','complex_Fresnel_points']:charge(k,1)
 return polarized_interface(d[None],n[None],nf,nt,B[None],C[None])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});F=load_working_family();L=F['length_unit_native_pixels'];g=F['geometry'];phys=json.loads((ROOT/'research/experiments/miniplayer-grazing-solid-58/result.json').read_text())['physical'];z=np.load(ROOT/'research/experiments/miniplayer-grazing-solid-58/paths-sections.npz');known={};safe={};centers={};bindings={};cv2.setNumThreads(1)
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');case=json.loads((work/'a/case.json').read_text());center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 centers[member]=np.array(center)
 for ref in ['a','b']:
  file=work/ref/'known.png';c=json.loads((work/ref/'case.json').read_text());assert sha(file)==c['source_sha256']['known.png'];bindings[str(file.relative_to(ROOT))]=sha(file);m=cv2.imread(str(file),0)>0;charge('decoded_known_cells',m.size);known[(member,ref)]=m;charge('known_erosions',1);safe[(member,ref)]=cv2.erode(m.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
save('known-inputs-FIRST.json',bindings);events=[];endpoints=[];launches=[];arrays={};endpointarrays=[]
def endpoint(member,launch,event,point,direction,B,C,direct):
 power=float(np.trace(C).real);down=direction[2]<0;row={'member':member,'launch':launch,'event':event,'power':power,'role':'direct_front_raw' if direct else 'through_glass_finite21','direction':direction.tolist(),'downward':bool(down),'support':{}}
 if down:
  t=(-phys['D']-point[2])/direction[2];assert t>0;hit=point+t*direction;X,Y=hit[:2]*L+centers[member];row['backdrop_XY']=[float(X),float(Y)]
  for ref in ['a','b']:
   mask=known[(member,ref)] if direct else safe[(member,ref)];a,b=int(np.floor(X)),int(np.floor(Y));ok=0<=a<mask.shape[1]-1 and 0<=b<mask.shape[0]-1
   if ok:charge('known_mask_lookups',4);ok=bool(mask[b,a]&mask[b+1,a]&mask[b,a+1]&mask[b+1,a+1])
   row['support'][ref]=ok
 else:row['environment']='UNOBSERVED_UPWARD_OR_LATERAL';row['support']={'a':False,'b':False}
 endpoints.append(row);endpointarrays.append((point,direction,B,C));return power
for member in ['expanded','compact']:
 surface=Counted((F['members'][member]['major_half'],g['minor_half']),g['corner_radius'],phys['front_height'],phys['back_height'],phys['power'])
 for j in [2,3,4,8,9,10]:
  charge('launches',1);p=z[f'{member}_n1.5_entry'][j];nf=z[f'{member}_n1.5_entry_normal'][j];back=z[f'{member}_n1.5_exit'][j];nb=z[f'{member}_n1.5_exit_normal'][j]
  f,grad=surface.level_gradient(np.array([p,back]));assert abs(f).max()<P['tolerances']['cached_level'];norm=grad/np.linalg.norm(grad,axis=1)[:,None];assert np.max(abs(norm-np.array([nf,nb])))<P['tolerances']['cached_normal_direction']
  d=np.array([0.,0.,-1.]);B=np.array([[1.,0.,0.],[0.,1.,0.]]);C=np.eye(2,dtype=complex)/2;v=interface(d,nf,1.,1.5,B,C);assert not v['blocked'][0];assert np.max(abs(v['transmitted_direction'][0]-z[f'{member}_n1.5_internal_direction'][j]))<P['tolerances']['cached_normal_direction'];emitted=endpoint(member,j,1,p,v['reflected_direction'][0],v['reflected_basis'][0],v['reflected_density'][0],True);d=v['transmitted_direction'][0];B=v['transmitted_basis'][0];C=v['transmitted_density'][0];blocked=0;maxres=0.
  for event in range(2,P['encounters']+1):
   if event==2:point,normal=back,nb;bracket=float(z[f'{member}_n1.5_intersection_bracket'][j]);residual=float(z[f'{member}_n1.5_exit_level_residual'][j])
   else:
    charge('new_segments',1);nxt=next_convex_boundary(surface,point[None],d[None],P['tolerances']['next_boundary_bracket'],64);assert nxt['complete'].all();point=nxt['point'][0];normal=nxt['outward_normal'][0];bracket=float(nxt['bracket'][0]);residual=float(nxt['residual'][0])
   v=interface(d,-normal,1.5,1.,B,C);assert v['closure_error'].max()<P['tolerances']['power_closure'];isblocked=bool(v['blocked'][0]);blocked+=int(isblocked)
   if not isblocked:emitted+=endpoint(member,j,event,point,v['transmitted_direction'][0],v['transmitted_basis'][0],v['transmitted_density'][0],False)
   events.append({'member':member,'launch':j,'event':event,'blocked':isblocked,'input_power':float(np.trace(C).real),'emitted_power':float(v['transmitted_power'][0]),'retained_power':float(v['reflected_power'][0]),'bracket':bracket,'residual':residual,'closure':float(v['closure_error'][0])});key=f'{member}_{j}_{event}';arrays[key+'_point']=point;arrays[key+'_direction_in']=d;arrays[key+'_normal']=normal;arrays[key+'_retained_density']=v['reflected_density'][0];arrays[key+'_reflected_basis']=v['reflected_basis'][0];arrays[key+'_emitted_density']=v['transmitted_density'][0];d=v['reflected_direction'][0];B=v['reflected_basis'][0];C=v['reflected_density'][0];assert np.dot(d,normal)<0;maxres=max(maxres,abs(residual))
  tail=float(np.trace(C).real);closure=abs(emitted+tail-1);assert closure<P['tolerances']['power_closure'];launches.append({'member':member,'launch':j,'encounters':P['encounters'],'blocked_transmissions':blocked,'emitted_power':emitted,'retained_tail':tail,'closure':closure,'maximum_exit_level_residual':maxres});arrays[f'{member}_{j}_tail_density']=C
  if not (OUT/'checkpoint.json').exists():save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_launch_complete_with_tail':launches[-1],'ledger':dict(ledger)})
for i,(point,d,B,C) in enumerate(endpointarrays):arrays[f'endpoint_{i}_point']=point;arrays[f'endpoint_{i}_direction']=d;arrays[f'endpoint_{i}_basis']=B;arrays[f'endpoint_{i}_density']=C
summary=[]
for member in ['expanded','compact']:
 for ref in ['a','b']:
  e=[e for e in endpoints if e['member']==member];l=[x for x in launches if x['member']==member];summary.append({'member':member,'reference':ref,'launches':len(l),'equal_launch_supported_backdrop_power':sum(x['power'] for x in e if x['downward'] and x['support'][ref])/len(l),'equal_launch_unsupported_backdrop_power':sum(x['power'] for x in e if x['downward'] and not x['support'][ref])/len(l),'equal_launch_unknown_environment_power':sum(x['power'] for x in e if not x['downward'])/len(l),'equal_launch_tail':sum(x['retained_tail'] for x in l)/len(l)})
np.savez_compressed(OUT/'branch-arrays.npz',**arrays);save('endpoints.json',{'records':endpoints,'role':'Model power/support only, no radiance or RGB value.'});save('events.json',{'records':events});save('result.json',{'status':'SPARSE_POLARIZED_CLOSED_BRANCH_AUDIT_COMPLETE_SCENE_INCOMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'launches':launches,'summary':summary,'ledger':ledger,'full_image':False,'source_RGB_evaluated':False,'claim':'Equal selected-launch power means, not pixel-area/radiance or whole-image weights.'});print(json.dumps({'summary':summary,'ledger':ledger}),flush=True)
