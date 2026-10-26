"""Independent area from Steiner's formula plus support perturbation."""
from pathlib import Path
import json,datetime,traceback
import numpy as np
from scipy.integrate import quad
from scipy.special import ellipe
from shoulder_core_coordinate import ShoulderCoreCoordinate
from miniplayer_refinement_effects import pixel_rule_batch
P=Path(__file__).parent;caps={'quadrature_nodes':3000000,'boundary_inversions':200000,'support_points':20000};ledger=dict.fromkeys(caps,0);partial={}
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def charge(k,n):
 assert ledger[k]+n<=caps[k],k;ledger[k]+=int(n)
save('area-refined-start.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'reason':'Uniform angular trapezoid comparison failed before pixel integration. Use independent analytic Steiner base with a separately bounded scalar correction. Original failure remains unchanged.'})
try:
 c=ShoulderCoreCoordinate((7.24,1.0125),.9902,.0113);a,b=np.array(c.half)-c.original_radius;R=c.original_radius;delta=c.shoulder
 base=np.pi*a*b+4*R*a*ellipe(1-(b/a)**2)+np.pi*R*R
 def density(t):
  charge('support_points',1);e=np.hypot(a*np.cos(t),b*np.sin(t));return (a*a*b*b/e**3)*np.sin(2*t)**2
 value,error=quad(density,0,np.pi/2,epsabs=1e-12,epsrel=1e-12,points=[np.pi/2-10*b/a,np.pi/2-b/a],limit=128)
 area=base-delta*(np.pi*R+4*value)-13*np.pi*delta*delta/8
 partial.update(independent_area=float(area),scalar_error_bound=float(4*delta*error),base=float(base));save('area-refined-progress.json',partial)
 yy,xx=np.mgrid[-2:3,-8:9];pixels=np.stack([xx.ravel(),yy.ravel()],1);mass=[]
 for order in [16,32]:
  nodes,weights,owners=pixel_rule_batch(pixels,c,order,charge);actual=float(weights.sum());mass.append(actual);partial['pixel_weight_sums']=mass;save('area-refined-progress.json',partial)
  assert abs(actual-area)<1e-8,(order,actual,area)
  assert np.max(abs(nodes-pixels[owners]))<=.5000000001 and (weights>0).all()
 save('area-refined-result.json',dict(passed=True,ledger=ledger,**partial));print('INDEPENDENT AREA PASS',mass,area)
except Exception as e:save('area-refined-failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'ledger':ledger,'partial':partial});raise
