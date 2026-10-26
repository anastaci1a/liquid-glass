from pathlib import Path
import datetime,json,traceback
import numpy as np
from shoulder_core_coordinate import ShoulderCoreCoordinate
from miniplayer_refinement_effects import pixel_rule_batch,saturated_rim,extent_at
OUT=Path(__file__).parent
record={'start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':{'quadrature_nodes':200000,'boundary_inversions':200000,'color_inputs':5000},'ledger':{'quadrature_nodes':0,'boundary_inversions':0,'color_inputs':0}}
def save():(OUT/'effects-controls.json').write_text(json.dumps(record,indent=2)+'\n')
def charge(k,n):
 assert record['ledger'][k]+n<=record['caps'][k];record['ledger'][k]+=int(n)
save()
try:
 c=ShoulderCoreCoordinate((7.24,1.0125),.9902,.0113)
 pts=np.array([[0,0],[0,1.0125],[7.24,0],[7.5,0],[-7.24,0],[0,-1.0125]])
 masses=[]
 for order in [8,16,32]:
  p,w,owner=pixel_rule_batch(pts,c,order,charge)
  assert (c.boundary_distance(p[:,0],p[:,1])[0]<1e-10).all()
  assert np.max(abs(p-pts[owner]))<.5000000001
  masses.append(np.bincount(owner,weights=w,minlength=len(pts)).tolist())
 assert max(abs(np.array(masses[-1])-np.array(masses[-2])))<1e-7
 assert abs(masses[-1][0]-1)<1e-12
 colors=np.array([[0.,0.,0.],[1.,1.,1.],[.95,.89,.38],[.98,.94,.52],[.4,.2,.01]])
 responses=[]
 for chroma in [1.,1.35,1.7]:
  for alpha in [0.,.5,1.]:
   charge('color_inputs',len(colors));v=saturated_rim(colors,colors,np.full(len(colors),alpha),chroma=chroma)
   assert np.isfinite(v).all() and v.min()>=0 and v.max()<=1
   assert np.array_equal(v[1],colors[1])
   if alpha==0:assert np.array_equal(v,colors)
   responses.append(dict(chroma=chroma,alpha=alpha,output=v.tolist()))
 record.update(passed=True,masses=masses,response=responses,finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print('EFFECT CONTROLS PASS',flush=True)
except Exception as e:record.update(passed=False,error=repr(e),traceback=traceback.format_exc());save();raise
