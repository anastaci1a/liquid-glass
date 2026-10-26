"""Independent support-maximum checks; no optical or source work."""
from pathlib import Path
import json,datetime,traceback
import numpy as np
from scipy.optimize import minimize_scalar
from shoulder_core_coordinate import ShoulderCoreCoordinate
O=Path(__file__).parent;ledger={'support_points':0,'coordinate_points':0};caps={'support_points':150000,'coordinate_points':128};rows=[]
def save(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
def charge(k,n):
 assert ledger[k]+n<=caps[k];ledger[k]+=int(n)
save('projection-global-start.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'deadline':'2026-10-26T06:02:24+00:00','scientific_scope':'Independent geometric maximum only; no optical events, sources or images.'})
try:
 for major in [7.24,4.92]:
  c=ShoulderCoreCoordinate((major,1.0125),.9902,.0113);t=np.linspace(.001,np.pi/2-.001,16);h,hp,_=c.support(t);n=np.stack([np.cos(t),np.sin(t)],1);q=h[:,None]*n+hp[:,None]*np.stack([-np.sin(t),np.cos(t)],1)
  pts=np.concatenate([q+shift*n for shift in [-.04,-.001,.001,.2]])
  charge('coordinate_points',len(pts));d,_,_=c.distance_gradient(pts[:,0],pts[:,1]);grid=np.linspace(0,np.pi/2,1025);normals=np.stack([np.cos(grid),np.sin(grid)],1)
  for i,p in enumerate(pts):
   charge('support_points',len(grid));v=normals@p-c.support(grid)[0];j=int(np.argmax(v));lo=grid[max(j-1,0)];hi=grid[min(j+1,1024)]
   def f(theta):
    charge('support_points',1);return float(c.support(theta)[0]-p[0]*np.cos(theta)-p[1]*np.sin(theta))
   opt=minimize_scalar(f,bounds=(lo,hi),method='bounded',options={'xatol':1e-14});expected=max(0.,float(v[j]),-opt.fun);err=abs(float(d[i])-expected);assert err<1e-9,(major,i,err)
   rows.append(dict(major=major,point=p.tolist(),distance=float(d[i]),independent=expected,error=err))
 save('projection-global-result.json',{'passed':True,'maximum_error':max(r['error'] for r in rows),'ledger':ledger,'rows':rows,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()});print('GLOBAL SUPPORT CHECK PASS',ledger)
except Exception as e:save('projection-global-failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'ledger':ledger,'rows':rows});raise
