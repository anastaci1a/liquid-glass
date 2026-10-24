from pathlib import Path
import sys,datetime,json
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from polarization_transport import polarized_interface
from environment_radiance import two_interface_power
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def call(d,n,nf,nt,B,C):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 for k in ['interface_points','Snell_points','reflection_points','complex_Fresnel_points']:
  ledger[k]+=len(d);assert ledger[k]<=P['caps'][k]
 save('ledger.json',ledger);return polarized_interface(d,n,nf,nt,B,C)
def global_matrix(B,C):return np.swapaxes(B,-1,-2)@C@B
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});rows=[];saved={};maxclosure=0.;maxcov=0.
for nf,nt in [(1.,1.5),(1.5,1.),(1.,1.)]:
 for angle in [0,20,40,60,80]:
  theta=np.deg2rad(angle);d=np.array([[np.sin(theta),0,-np.cos(theta)]]);n=np.array([[0,0,1.]]);s=np.array([[0,1.,0]]);B=np.stack([s,np.cross(s,d)],-2)
  for name,C in [('unpolarized',np.eye(2)[None]/2),('circular',np.array([[[.5,.5j],[-.5j,.5]]]))]:
   q=call(d,n,nf,nt,B,C);a=.37;U=np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]]);Br=U@B;Cr=U@C@U.T;qr=call(d,n,nf,nt,Br,Cr);closure=float(q['closure_error'].max());maxclosure=max(maxclosure,closure);assert closure<P['tolerances']['closure'];assert np.linalg.eigvalsh(q['reflected_density']).min()>-P['tolerances']['PSD'] and np.linalg.eigvalsh(q['transmitted_density']).min()>-P['tolerances']['PSD']
   errors=[]
   for branch in ['reflected','transmitted']:
    if branch=='transmitted' and q['blocked'].all():assert np.isnan(q['transmitted_direction']).all() and not q['transmitted_density'].any();continue
    errors.append(float(np.max(abs(global_matrix(q[branch+'_basis'],q[branch+'_density'])-global_matrix(qr[branch+'_basis'],qr[branch+'_density'])))))
   err=max(errors);maxcov=max(maxcov,err);assert err<P['tolerances']['basis_covariance'];assert np.max(abs(abs(q['amplitudes'])**2-q['component_power']))<5e-13
   if angle==0 and nf!=nt:
    expected=((nf-nt)/(nf+nt))**2;assert abs(q['reflected_power'][0]-expected)<5e-13;assert np.max(abs(global_matrix(q['reflected_basis'],q['reflected_density'])-expected*global_matrix(B,C)))<5e-13
   if nf==nt:assert not q['reflected_density'].any() and np.max(abs(global_matrix(q['transmitted_basis'],q['transmitted_density'])-global_matrix(B,C)))<5e-13
   if not (OUT/'checkpoint.json').exists():save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_normal_dielectric_pass':True,'closure':closure,'basis_covariance_error':err,'ledger':dict(ledger)})
   rows.append({'n_from':nf,'n_to':nt,'angle_degrees':angle,'state':name,'blocked':bool(q['blocked'][0]),'reflected_power':float(q['reflected_power'][0]),'transmitted_power':float(q['transmitted_power'][0]),'closure':closure,'basis_covariance_error':err});key=f'{nf}_{nt}_{angle}_{name}';saved[key+'_reflected_density']=q['reflected_density'];saved[key+'_amplitudes']=q['amplitudes']
# Reuse retained actual58 entry/exit geometry; no new boundary trace.
z=np.load(ROOT/'research/experiments/miniplayer-grazing-solid-58/paths-sections.npz');comparisons=[]
for member in ['expanded','compact']:
 valid=z[f'{member}_n1.5_complete'];nf=z[f'{member}_n1.5_entry_normal'][valid];nb=z[f'{member}_n1.5_exit_normal'][valid];internal=z[f'{member}_n1.5_internal_direction'][valid];d=np.zeros_like(internal);d[:,2]=-1;s=np.zeros_like(d);s[:,0]=1;B=np.stack([s,np.cross(s,d)],-2);C=np.broadcast_to(np.eye(2)/2,(len(d),2,2)).copy();q=call(d,nf,1.,1.5,B,C);assert not q['blocked'].any();r=call(q['transmitted_direction'],-nb,1.5,1.,q['transmitted_basis'],q['transmitted_density']);assert not r['blocked'].any();ledger['shared_power_comparator_points']+=2*len(d);assert ledger['shared_power_comparator_points']<=P['caps']['shared_power_comparator_points'];expected=two_interface_power(d,nf,internal,nb,1.5);error=float(np.max(abs(r['transmitted_power']-expected['primary'])));assert error<P['tolerances']['old_two_interface_power'];comparisons.append({'member':member,'completed_events':len(d),'max_old_two_interface_error':error})
np.savez_compressed(OUT/'coherence-fixtures.npz',**saved);save('ledger.json',ledger);save('result.json',{'status':'LOSSLESS_POLARIZED_INTERFACE_CONTROLS_PASS','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'existing_two_interface_comparison':comparisons,'closure_max':maxclosure,'basis_covariance_max':maxcov,'ledger':ledger,'source_or_scene_validated':False});print(json.dumps({'status':'PASS','comparisons':comparisons,'ledger':ledger}),flush=True)
