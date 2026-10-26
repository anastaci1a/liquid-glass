"""Independent whole-contour area and pixel normalization control."""
from pathlib import Path
import numpy as np,json,datetime,traceback
from shoulder_core_coordinate import ShoulderCoreCoordinate
from miniplayer_refinement_effects import pixel_rule_batch
P=Path(__file__).parent;caps={'quadrature_nodes':3000000,'boundary_inversions':200000,'support_points':30000};ledger=dict.fromkeys(caps,0)
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def charge(k,n):
 assert ledger[k]+n<=caps[k],k;ledger[k]+=int(n)
save('area-check-start.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'no_optics_or_images':True})
try:
 c=ShoulderCoreCoordinate((7.24,1.0125),.9902,.0113);areas=[]
 for count in [4096,8192]:
  t=np.arange(count)*2*np.pi/count;charge('support_points',count);h,hp,_=c.support(t);h=h+c.radius;areas.append(float(np.pi*np.mean(h*h-hp*hp)))
 assert abs(areas[-1]-areas[-2])<1e-9
 yy,xx=np.mgrid[-2:3,-8:9];pixels=np.stack([xx.ravel(),yy.ravel()],1);mass=[]
 for order in [16,32]:
  nodes,weights,owners=pixel_rule_batch(pixels,c,order,charge);a=float(weights.sum());assert abs(a-areas[-1])<1e-8;mass.append(a)
  assert np.max(abs(nodes-pixels[owners]))<=.5000000001 and (weights>0).all()
 save('area-check-result.json',{'passed':True,'support_integral':areas,'pixel_weight_sums':mass,'normalization':'Full pixel area; no occupied-area normalization','ledger':ledger,'maximum_error':max(abs(a-areas[-1]) for a in mass)});print('WHOLE AREA PASS',mass,areas)
except Exception as e:save('area-check-failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'ledger':ledger});raise
