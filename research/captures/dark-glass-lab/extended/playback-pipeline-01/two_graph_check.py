import time,json
from pathlib import Path
import numpy as np
from geometric_optics import RadialCurvatureBack,trace_flat_front_orthographic,trace_closed_orthographic
from two_graph_control import TwoGraphCircle
D=Path('/evidence/extended/playback-pipeline-01/refraction-03');D.mkdir(exist_ok=True);started=time.time();p=np.load('/evidence/extended/geometric-playback-inverse/geometry-513.npz');back=RadialCurvatureBack(p['nodes'],p['curvature'])
xx,yy=np.meshgrid(np.linspace(-.999,.999,45),np.linspace(-.999,.999,45));r=np.hypot(xx,yy);inside=r<.999;xx=xx[inside];yy=yy[inside];rows=[];total=0
for a in [0.,.003,.006]:
 s=TwoGraphCircle(back,a);q=trace_closed_orthographic(s,xx,yy,1.5,2);total+=xx.size;assert total<=20000;assert q['complete'].all();assert np.nanmax(q['intersection_bracket'])<=1e-11
 p0=q['entry'];p1=q['exit'];f0,n0=s.level_gradient(p0);f1,n1=s.level_gradient(p1);assert np.max(abs(f0))<1e-10 and np.max(abs(f1))<1e-10
 # Actual level gradients at the regular physical entry and exit, not selector ridges.
 e=1e-7;errors=[]
 for pp in [p0,p1]:
  for ax in range(3):
   dv=np.zeros_like(pp);dv[...,ax]=e;fd=(s.level_gradient(pp+dv)[0]-s.level_gradient(pp-dv)[0])/(2*e);actual=s.level_gradient(pp)[1][...,ax];errors.append(float(abs(fd-actual).max()))
 assert max(errors)<1e-7
 row={'front_sag':a,'rays':xx.size,'complete':True,'max_level_residual':float(abs(f1).max()),'gradient_FD_error':max(errors),'min_Snell_discriminant':float(q['discriminant'].min()),'maximum_bracket':float(np.nanmax(q['intersection_bracket']))}
 if a==0:
  old=trace_flat_front_orthographic(back,xx,yy,1.5,2);total+=xx.size;err=float(np.maximum(abs(old['X']-q['X']),abs(old['Y']-q['Y'])).max());assert err<1e-10;row['zero_front_flat_comparator_error_L']=err
 rows.append(row)
np.savez(D/'checkpoint-rays.npz',x=xx,y=yy,**q)
(D/'checkpoint.json').write_text(json.dumps({'status':'PASS_GEOMETRY_ONLY','rows':rows,'total_checkpoint_rays':total,'elapsed_seconds':time.time()-started,'images':0,'fits':0},indent=2)+'\n');print((D/'checkpoint.json').read_text())
