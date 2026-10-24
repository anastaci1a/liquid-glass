from pathlib import Path
import sys,json,datetime
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from closed_power_surface import ClosedPowerSurface
from geometric_optics import ClosedCircularOval,trace_closed_orthographic,reflect_direction,fresnel_components
from music_miniplayer_family import load_working_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
class Counted(ClosedPowerSurface):
 def level_gradient(self,p):
  n=np.asarray(p).size//3;charge('level_points',n);charge('adapter_points',n);charge('adapter_units',20*n);return super().level_gradient(p)
 def front_height(self,x,y):
  n=np.asarray(x).size;charge('adapter_points',n);charge('adapter_units',20*n);return super().front_height(x,y)
 def boundary_mask(self,x,y):
  n=np.asarray(x).size;charge('adapter_points',n);charge('adapter_units',20*n);return super().boundary_mask(x,y)
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});F=load_working_family();g=F['geometry'];L=F['length_unit_native_pixels'];rec=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());model=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/back-profile.json').read_text());Hf=rec['depth'];Hb=model['heights'][0];power=rec['power'];D=F['optics']['background_distance'];rng=np.random.default_rng(5801)
# Physical gradient FD at declared regular interior points, away from z=0.
solid=Counted((F['members']['expanded']['major_half'],g['minor_half']),g['corner_radius'],Hf,Hb,power);pts=np.array([[0,.5*g['minor_half'],Hf*.3],[solid.half[0]-.3,0,-Hb*.3],[solid.half[0]-.6,.4,Hf*.7]])
charge('fixture_level_points',len(pts)*7);f,grad=solid.level_gradient(pts);fd=[]
for j in range(3):
 step=np.zeros(3);step[j]=1e-7;fd.append((solid.level_gradient(pts+step)[0]-solid.level_gradient(pts-step)[0])/2e-7)
err=float(np.max(abs(grad-np.stack(fd,-1))));assert err<1e-5
# Algebraic same-level true-circle fixture, no extra traced comparators.
circle=Counted((1,1),1,.15,.15,2);v=rng.uniform(-.7,.7,(8,3));v[:,2]*=.15;charge('fixture_level_points',16);fa,ga=circle.level_gradient(v);fb,gb=ClosedCircularOval(.15,0).level_gradient(v-np.array([0,0,.15]));assert np.max(abs(fa-fb))<1e-12 and np.max(abs(ga-gb))<1e-12
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gradient_FD_max':err,'true_circle_level_and_gradient_pass':True,'ledger':dict(ledger)})
records=[];arrays={};source_rows=[];pending=[];sections={}
for member in ['expanded','compact']:
 a=F['members'][member]['major_half'];b=g['minor_half'];r=g['corner_radius'];s=Counted((a,b),r,Hf,Hb,power);rho=np.tile(np.array([.9,.97,.99,.999,.9999,.999999]),3);names=np.repeat(['upper_body','right_cap','upper_right_arc'],6);x=np.r_[np.zeros(6),a-r+r*rho[6:12],a-r+r*rho[12:]/np.sqrt(2)];y=np.r_[-(b-r+r*rho[:6]),np.zeros(6),-(b-r+r*rho[12:]/np.sqrt(2))]
 for index in [1.,1.5]:
  charge('launches',len(x));q=trace_closed_orthographic(s,x,y,index,D);assert q['regular_entry'].all() and not q['boundary_unresolved'].any();arrays[f'{member}_n{index}_X']=q['X'];arrays[f'{member}_n{index}_Y']=q['Y']
  if index==1:assert q['complete'].all() and np.max(abs(q['X']-x))<1e-9 and np.max(abs(q['Y']-y))<1e-9
  for key in ['entry','exit','entry_normal','exit_normal','internal_direction','exit_direction','complete','blocked','intersection_bracket','exit_level_residual']:arrays[f'{member}_n{index}_{key}']=q[key]
  records.append({'member':member,'index':index,'complete_primary':int(q['complete'].sum()),'TIR_or_critical':int(q['blocked'].sum()),'other_primary_incomplete':int((~q['complete']&~q['blocked']).sum())})
  if index==1.5:
   charge('front_Fresnel_points',len(x));R=fresnel_components(q['entry_normal'][:,2],1,1.5).mean(-1);camera=np.zeros_like(q['entry']);camera[:,2]=-1;charge('front_reflection_points',len(x));direction=reflect_direction(camera,q['entry_normal']);assert np.all(np.sum(direction*q['entry_normal'],axis=-1)>0);down=direction[:,2]<0;t=np.full(len(x),np.nan);t[down]=(-D-q['entry'][down,2])/direction[down,2];hit=q['entry']+t[:,None]*direction;arrays[member+'_front_R']=R;arrays[member+'_front_reflection']=direction;arrays[member+'_downward_hit']=hit
   work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');case=json.loads((work/'a/case.json').read_text());center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
   if member=='compact':
    prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
   for k in ['a','b']:
    known=cv2.imread(str(work/k/'known.png'),0)>0
    for j in np.flatnonzero(down):
     X,Y=hit[j,:2]*L+center;a0,b0=int(np.floor(X)),int(np.floor(Y));supported=0<=a0<known.shape[1]-1 and 0<=b0<known.shape[0]-1
     if supported:charge('known_mask_lookups',4);supported=bool(known[b0,a0]&known[b0+1,a0]&known[b0,a0+1]&known[b0+1,a0+1])
     source_rows.append({'member':member,'reference':k,'section':str(names[j]),'rho':float(rho[j]),'front_R':float(R[j]),'reflected_dz':float(direction[j,2]),'X':float(X),'Y':float(Y),'raw_backdrop_supported':supported,'source_RGB_evaluated':False})
   records.append({'member':member,'front_reflection_R':R.tolist(),'rho':rho.tolist(),'section':names.tolist(),'downward':int(down.sum()),'upward_or_horizontal':int((~down).sum())})
 # Same-F sections, no decorative geometry.
 for axis,extent in [('x',a),('y',b)]:
  v=np.linspace(-extent,extent,201);front,back=s.section(v,axis);valid=np.isfinite(front).all(1)&np.isfinite(back).all(1);charge('fixture_level_points',2*int(valid.sum()));assert max(np.max(abs(s.level_gradient(front[valid])[0])),np.max(abs(s.level_gradient(back[valid])[0])))<1e-9;arrays[f'{member}_{axis}_front_section']=front;arrays[f'{member}_{axis}_back_section']=back
save('source-role.json',{'status':'SPARSE_CONDITIONAL_RAW_BACKDROP_SUPPORT_ONLY','records':source_rows,'no_RGB':True,'whole_source_proof':False,'unobserved_upward_environment':True});np.savez_compressed(OUT/'paths-sections.npz',**arrays);save('result.json',{'status':'ONE_CLOSED_GRAZING_SURFACE_SPARSE_DISCRIMINATOR_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical':{'front_height':Hf,'back_height':Hb,'power':power,'index':1.5,'D':D},'records':records,'ledger':ledger,'full_image':False,'selected_model_changed':False});print(json.dumps({'status':'COMPLETE','records':records[:2],'ledger':ledger}),flush=True)
