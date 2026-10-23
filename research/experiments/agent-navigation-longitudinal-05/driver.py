"""Navigation-only fixed two-sign observation; shared math and cached integrator."""
from pathlib import Path
import sys,os,json,datetime,hashlib,atexit,argparse
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parents[2];Q=P.parent/'agent-navigation-spline-03';PRIMARY=ROOT.parent/'liquid-glass';CACHE=PRIMARY/'research/experiments/navigation-geometry-01';WORK=PRIMARY/'.evidence-working/navigation-geometry-01'
sys.path.insert(0,str(ROOT/'reconstruction'))
from longitudinal_height import LongitudinalHeight
from spline_height_back import SplineFootprintBack
from geometric_optics import trace_flat_front_orthographic
from geometric_render import render_rows,incident_source_filter
from extended_fit import Study
os.umask(0o002);cv2.setNumThreads(1)
protocol=json.loads((P/'protocol.json').read_text());limits=protocol['limits'];fit=json.loads((ROOT/'research/experiments/expanded-spline-height-01/inference.json').read_text());bounds=json.loads((Q/'native-reservation.json').read_text())['bounds'];params=json.loads((ROOT/'reconstruction/studies/music-navigation/review-round/pass-03.json').read_text())['parameters']
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['checkpoint' if checkpoint else 'deadline'].replace('Z','+00:00')),'Original wall cap reached'
ledger=json.loads((P/'ledger.json').read_text()) if (P/'ledger.json').exists() else dict(graph=0,wrapper_height=0,wrapper_boundary=0,base_height=0,base_boundary=0,footprint=0,fixture_rays=0,native_rays=0,RGB_queries=0,candidate_composites=0,source_audit_subrays=0,mask_corner_lookups=0,incident_filters=0,known_mask_erosions=0)
atexit.register(lambda:save('ledger.json',ledger))
def charge(key,n):
 n=int(n);assert ledger['graph']+n<=limits['graph'];ledger['graph']+=n;ledger[key]+=n;save('ledger.json',ledger)
def npoints(x,y):return np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size
class BaseCount(SplineFootprintBack):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);coord=self.coordinate
  class Coord:
   def footprint(self,x,y):charge('footprint',npoints(x,y));return coord.footprint(x,y)
   def __getattr__(self,k):return getattr(coord,k)
  self.coordinate=Coord()
 def height_gradient(self,x,y):charge('base_height',npoints(x,y));return super().height_gradient(x,y)
 def boundary_mask(self,x,y):charge('base_boundary',npoints(x,y));return super().boundary_mask(x,y)
class WrapperCount(LongitudinalHeight):
 def height_gradient(self,x,y):charge('wrapper_height',npoints(x,y));return super().height_gradient(x,y)
 def boundary_mask(self,x,y):charge('wrapper_boundary',npoints(x,y));return super().boundary_mask(x,y)
def setup(strength,scale=1):return WrapperCount(BaseCount(tuple(np.array(bounds['half'])*scale),bounds['radius']*scale,fit['breaks'],np.array(fit['best']['heights'])*scale,cap_join_width=0),strength)
def trace(s,x,y,native=False,D=2.1):
 n=npoints(x,y);key='native_rays' if native else 'fixture_rays';assert ledger[key]+n<=limits[key];assert ledger['graph']+8*n<=limits['graph'];ledger[key]+=int(n);save('ledger.json',ledger);return trace_flat_front_orthographic(s,x,y,1.5,D)
def pin():
 prior=json.loads((Q/'code-pin.json').read_text());out=[]
 for row in prior['files']:
  digest=hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest();assert digest==row['sha256'],row['file'];out.append(row)
 f=ROOT/'reconstruction/longitudinal_height.py';digest=hashlib.sha256(f.read_bytes()).hexdigest();assert digest==protocol['wrapper_sha256'];out.append(dict(file='reconstruction/longitudinal_height.py',sha256=digest));assert json.loads((Q/'contract-result.json').read_text())['status']=='PASS'
 # Reuse the exact cached compositor prerequisite only under unchanged code,
 # input and vector hashes. No baseline composite or optical query is repeated.
 integrity=json.loads((Q/'input-integrity.json').read_text());save('code-pin.json',dict(shared_commit=protocol['shared_commit'],files=out,cached_compositor_proof_sha256=hashlib.sha256((Q/'contract-result.json').read_bytes()).hexdigest(),root_tests_reused=True));return integrity

def checkpoint():
 gate(True);assert not (P/'checkpoint.json').exists();pin();rows=[]
 for e in protocol['strengths']:
  f=setup(e);a=f.half[0];r=bounds['radius'];x=np.linspace(-.9*a,.9*a,32);y=.4*r*np.sin(np.arange(32)*.47);h,hx,hy,inside=f.height_gradient(x,y);assert inside.all() and (h>0).all();d=1e-6;fdx=(f.height_gradient(x+d,y)[0]-f.height_gradient(x-d,y)[0])/(2*d);fdy=(f.height_gradient(x,y+d)[0]-f.height_gradient(x,y-d)[0])/(2*d);err=max(abs(fdx-hx).max(),abs(fdy-hy).max());assert err<1e-8
  q=trace(f,x,y);mirror=trace(f,-x,-y);assert q['complete'].all();np.testing.assert_allclose(mirror['X'],-q['X'],rtol=0,atol=3e-14);np.testing.assert_allclose(mirror['Y'],-q['Y'],rtol=0,atol=3e-14)
  scaled=trace(setup(e,3),x*3,y*3,D=6.3);np.testing.assert_allclose(scaled['X'],q['X']*3,rtol=0,atol=3e-13);np.testing.assert_allclose(scaled['Y'],q['Y']*3,rtol=0,atol=3e-13)
  c=np.array(bounds['center'])+[13.,-17.];posed=trace(f,((x*bounds['L']+c[0])-c[0])/bounds['L'],((y*bounds['L']+c[1])-c[1])/bounds['L']);np.testing.assert_allclose(posed['X'],q['X'],rtol=0,atol=3e-14);np.testing.assert_allclose(posed['Y'],q['Y'],rtol=0,atol=3e-14)
  crease=trace(f,np.array([0.,0.]),np.array([r,-r]));assert not crease['complete'].any() and np.isnan(crease['X']).all()
  hh,gx,gy,ii=f.height_gradient(np.array([-a/3,a/3]),np.zeros(2));assert np.all(np.sign(gx)==np.sign(e*np.array([-1,1])))
  sub=(1.5**2-1)*f.slope_bound**2;assert sub<1 and f.maximum_height<2.1
  np.savez_compressed(P/('plus-fixtures.npz' if e>0 else 'minus-fixtures.npz'),**q)
  rows.append(dict(strength=e,maximum_height=f.maximum_height,slope_bound=f.slope_bound,subcritical=sub,clearance_rate_bound=float(np.sqrt(1-sub)),gradient_error=float(err),mirrors=True,scale=True,pose=True,crease_unresolved=True,sign_control=True))
 gate(True);save('checkpoint.json',dict(status='PASS',utc=utc(),records=rows,ledger=ledger.copy()));print('CHECKPOINT',rows,ledger,flush=True)

def prepare_masks():
 gate();assert not (P/'audit-masks.json').exists();records=[]
 for key in ['a','b']:
  oldproof=next(r for r in json.loads((Q/'source-preflight.json').read_text())['rows'] if r['case']==key)
  for name,digest in oldproof['input_hashes'].items():assert hashlib.sha256((WORK/key/name).read_bytes()).hexdigest()==digest
  known=cv2.imread(str(WORK/key/'known.png'),0)>0;ledger['known_mask_erosions']+=1;save('ledger.json',ledger)
  safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;np.savez_compressed(P/f'{key}-audit-mask.npz',safe=safe);records.append(dict(case=key,source_hash=oldproof['input_hashes']['source.png'],known_hash=oldproof['input_hashes']['known.png'],sigma=6.75,radius=21,kernel=[43,43],reason='Original filter field was not retained; one unchanged field is constructed and reused for both signs. Clear raw samples are retained and reused.'))
 save('audit-masks.json',dict(records=records,utc=utc(),ledger=ledger.copy()))

def preflight(label,e):
 gate();folder=P/label;folder.mkdir(exist_ok=True);assert not (folder/'reservation.json').exists();f=setup(e);oldq=np.load(Q/'native-paths.npz');x,y=oldq['x'],oldq['y'];N=x.size;assert ledger['graph']+8*N<=limits['graph'];assert ledger['native_rays']+N<=limits['native_rays'];(folder/'reservation.json').write_text(json.dumps(dict(utc=utc(),rays=N,nested_per_ray=8,graph_reserved=8*N,prior_graph=ledger['graph']),indent=2)+'\n')
  # The wrapper's unchanged footprint gives identical view coordinates, not identical refracted coordinates.
 q=trace(f,x,y,native=True);gate();X=q['X']*bounds['L']+bounds['center'][0];Y=q['Y']*bounds['L']+bounds['center'][1];entry=np.where(q['inside'][...,None],np.stack([x,y,np.zeros_like(x)],-1),np.nan);np.savez_compressed(folder/'paths.npz',source_X=X,source_Y=Y,x=x,y=y,entry=entry,front_outward_normal=np.array([0.,0.,1.]),**q)
 assert q['complete'].all(),'Incomplete primary path stops family';assert np.array_equal(q['inside'],oldq['inside']);H,W=335,1080;cov=q['inside'].reshape(H,2,W,2).mean((1,3));rows=[]
 for key in ['a','b']:
  gate();sp0=np.load(Q/f'{key}-support.npz');required_pixels=sp0['required_pixels'];required=q['inside']|np.repeat(np.repeat(required_pixels,2,0),2,1);assert np.array_equal(cov,sp0['coverage']);known=cv2.imread(str(WORK/key/'known.png'),0)>0;safe=np.load(P/f'{key}-audit-mask.npz')['safe'];assert np.isfinite(X).all() and np.isfinite(Y).all();a=np.floor(X).astype(int);b=np.floor(Y).astype(int);inbounds=(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);ii,jj=np.nonzero(inbounds);base=np.zeros_like(inbounds);lens=np.zeros_like(inbounds)
  ledger['source_audit_subrays']+=int(N);ledger['mask_corner_lookups']+=8*len(ii);save('ledger.json',ledger)
  for out,mask in [(base,known),(lens,safe)]:out[ii,jj]=mask[b[ii,jj],a[ii,jj]]&mask[b[ii,jj]+1,a[ii,jj]]&mask[b[ii,jj],a[ii,jj]+1]&mask[b[ii,jj]+1,a[ii,jj]+1]
  support=np.where(q['inside'],lens,base);bad=required&~support;np.savez_compressed(folder/f'{key}-support.npz',support=support,required_pixels=required_pixels,coverage=cov);row=dict(case=key,whole=int(q['inside'].sum()),required=int(required.sum()),unsupported_required=int(bad.sum()),unknown_unscored=int((~support&~required).sum()),audit_subrays=N,mask_lookups=8*len(ii),coverage_exact=True,source_kernel_radius=21);rows.append(row)
  if bad.any():row['first_bad']=np.argwhere(bad)[:16].tolist()
 status='PASS' if not any(r['unsupported_required'] for r in rows) else 'STOP_REQUIRED_SOURCE'
 (folder/'source-proof.json').write_text(json.dumps(dict(status=status,utc=utc(),records=rows,ledger=ledger.copy()),indent=2)+'\n');print(label,'SOURCE',status,ledger,flush=True);return status=='PASS'

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['checkpoint','masks','plus-source','minus-source']);args=ap.parse_args()
 if args.stage=='checkpoint':checkpoint()
 elif args.stage=='masks':prepare_masks()
 else:preflight('plus' if args.stage=='plus-source' else 'minus',.1 if args.stage=='plus-source' else -.1)
