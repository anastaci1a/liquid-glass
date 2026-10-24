from pathlib import Path
import json,datetime,atexit,sys,os
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parents[2];WORK=ROOT/'.evidence-working/music-search-baseline-01'
sys.path.insert(0,str(ROOT/'reconstruction'))
from geometric_optics import HarmonicCircularBack,trace_flat_front_orthographic
from extended_fit import Study
os.umask(0o002);cv2.setNumThreads(1)
p=json.loads((P/'protocol.json').read_text());par=p['parameters']
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,x):(P/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def gate(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(p['checkpoint_deadline' if checkpoint else 'deadline'].replace('Z','+00:00')),'Original deadline'
ledger=json.loads((P/'ledger.json').read_text()) if (P/'ledger.json').exists() else dict(graph=0,adapter_height_nested=0,adapter_boundary_nested=0,mask_geometry=0,fixture_rays=0,native_rays=0,RGB_queries=0,candidate_images=0,incident_fields=0,known_mask_erosions=0,source_audit_subrays=0,bilinear_mask_lookups=0,foreground_controls=0)
atexit.register(lambda:save('ledger.json',ledger))
def charge(key,n):
 n=int(n);assert ledger['graph']+n<=p['caps']['graph'],'Persistent nested call limit';ledger['graph']+=n;ledger[key]+=n;save('ledger.json',ledger)
class RadiusBack:
 def __init__(self):self.base=HarmonicCircularBack(depth=.15,crown_depth=.4);self.R=par['R']
 @property
 def maximum_height(self):return self.base.maximum_height
 @property
 def slope_bound(self):return self.base.slope_bound/self.R
 def height_gradient(self,x,y):
  n=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size;charge('adapter_height_nested',8*n)
  h,hx,hy,inside=self.base.height_gradient(np.asarray(x)/self.R,np.asarray(y)/self.R)
  return h,hx/self.R,hy/self.R,inside
 def boundary_mask(self,x,y):
  n=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size;charge('adapter_boundary_nested',4*n)
  return self.base.boundary_mask(np.asarray(x)/self.R,np.asarray(y)/self.R)
def trace(f,x,y,n=1.5,D=2,native=False):
 N=np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size;k='native_rays' if native else 'fixture_rays';assert ledger[k]+N<=p['caps'][k];assert ledger['graph']+14*N<=p['caps']['graph'];ledger[k]+=int(N);save('ledger.json',ledger);return trace_flat_front_orthographic(f,x,y,n,D)
def study(k,charge_masks=False):
 if charge_masks:charge('mask_geometry',240*235)
 return Study(WORK/k)
