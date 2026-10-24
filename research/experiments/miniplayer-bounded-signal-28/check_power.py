from pathlib import Path
import sys,json,datetime
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from geometric_optics import refract,fresnel_components
from environment_radiance import two_interface_power
P=json.loads((OUT/'protocol.json').read_text());start=datetime.datetime.fromisoformat(P['start'].replace('Z','+00:00'));records=[];count=0;worst=0.
for index in [1.,1.5]:
 incoming=[];front=[];internal=[];normal=[];expected=[]
 for alpha in [0.,35.,70.]:
  nf=np.array([np.sin(np.deg2rad(alpha)),0.,np.cos(np.deg2rad(alpha))]);i=np.array([0.,0.,-1.]);v,blocked,_=refract(i,nf,1.,index);assert not blocked;s=np.cross(i,nf)
  if np.linalg.norm(s)==0:s=np.array([0.,1.,0.])
  s/=np.linalg.norm(s);p=np.cross(s,v)
  for beta in [0.,30.,60.]:
   for phi in [0.,40.,90.]:
    b=np.deg2rad(beta);f=np.deg2rad(phi);nq=np.cos(b)*v+np.sin(b)*(np.cos(f)*p+np.sin(f)*s);r0=fresnel_components(np.array([-i@nf]),1.,index)[0];r1=fresnel_components(np.array([v@nq]),index,1.)[0];J=.5*(1-r0[0])*np.outer(s,s)+.5*(1-r0[1])*np.outer(p,p);s1=np.cross(v,nq)
    if np.linalg.norm(s1)<1e-15:s1=s
    s1/=np.linalg.norm(s1);p1=np.cross(s1,v);ws=s1@J@s1;wp=p1@J@p1;expected.append([r0.mean(),ws*(1-r1[0])+wp*(1-r1[1]),ws*r1[0]+wp*r1[1]]);incoming.append(i);front.append(nf);internal.append(v);normal.append(nq)
 vectors=list(map(np.array,[incoming,front,internal,normal]));q=two_interface_power(*vectors,index);count+=len(incoming);array=np.stack([q['front'],q['primary'],q['tail']],-1);error=float(np.max(abs(array-expected)));assert error<1e-12;worst=max(worst,error)
 axis=np.array([1.,2.,3.]);axis/=np.linalg.norm(axis);theta=.731;K=np.array([[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]]);rot=np.cos(theta)*np.eye(3)+(1-np.cos(theta))*np.outer(axis,axis)+np.sin(theta)*K;q2=two_interface_power(*[v@rot.T for v in vectors],index);count+=len(incoming)
 assert max(np.max(abs(q2[k]-q[k])) for k in ['front','primary','tail'])<1e-12
 records.append({'index':index,'tensor_error_max':error,'rigid_covariance':True,'vector_evaluations':2*len(incoming)})
assert count<=128 and datetime.datetime.now(datetime.timezone.utc)<start+datetime.timedelta(minutes=7),'Original checkpoint deadline'
(OUT/'checkpoint.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_TWO_INTERFACE_TENSOR_AND_COVARIANCE','synthetic_vectors':count,'tensor_error_max':worst,'records':records,'native_internal_launches':0},indent=2)+'\n')
