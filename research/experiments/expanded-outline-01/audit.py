"""Same-solid reflected-path audit with rigorous s/p intensity intervals."""
from pathlib import Path
import datetime,json
import cv2,numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from parabolic_front_solid import ParabolicFrontHeightSolid
from geometric_optics import fresnel_components,reflect_direction,refract,next_convex_boundary
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['first_checkpoint_deadline']);assert not (OUT/'result.json').exists()
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];back=RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius']);solid=ParabolicFrontHeightSolid(back,0);solid.maximum_level_points=p['budgets']['level_points']
case=json.loads((WORK/'a/case.json').read_text());L=min(case['half']);x0,y0,x1,y1=case['crop'];yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];xx=(xx-.25-scene['center'][0])/L;yy=(yy-.25-scene['center'][1])/L;old=np.load(WORK/'h1-a-paths.npz');inside=old['inside'];a,b=back.half;r=back.radius
regions=[(yy<-.8*b)&(abs(xx)<a-2*r),(yy>.8*b)&(abs(xx)<a-2*r),xx<-a+r,xx>a-r,(yy<-.6*b)&(yy>=-.8*b)&(abs(xx)<a-2*r),(yy>.6*b)&(yy<=.8*b)&(abs(xx)<a-2*r),(abs(yy)<.2*b)&(abs(xx)<a-2*r),(abs(abs(xx)-(a-r))<.15*r)&(abs(yy)>.6*b)]
selected=[]
for mask in regions:
 ids=np.flatnonzero(mask&inside);ids=ids[~np.isin(ids,np.asarray(selected,dtype=int))];assert len(ids)>=32;selected.extend(ids[np.linspace(0,len(ids)-1,32,dtype=int)].tolist())
assert len(selected)==p['budgets']['launches'];rr,cc=np.unravel_index(selected,xx.shape);x=xx[rr,cc];y=yy[rr,cc];h,hx,hy,valid=back.height_gradient(x,y);assert valid.all() and (h>0).all()
normal=-np.stack([hx,hy,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1)[:,None];incident=np.zeros_like(normal);incident[:,2]=-1;outgoing,tir,k=refract(incident,-normal,1.5,1);assert not tir.any()
primary_distance=(2-h)/-outgoing[:,2];expectedX=(x+primary_distance*outgoing[:,0])*L+scene['center'][0];expectedY=(y+primary_distance*outgoing[:,1])*L+scene['center'][1];assert max(abs(expectedX-old['X'][rr,cc]).max(),abs(expectedY-old['Y'][rr,cc]).max())<1e-7
front=fresnel_components(np.ones(len(x)),1.,1.5).mean(-1);R=fresnel_components(np.sum(incident*normal,-1),1.5,1);initial_reflected=(1-front)*R.mean(-1);bg_lower=(1-front)*(1-R.mean(-1));bg_upper=bg_lower.copy();env_lower=front.copy();env_upper=front.copy();lower=initial_reflected.copy();upper=lower.copy();point=np.stack([x,y,-h],-1);direction=reflect_direction(incident,normal);encounters=2*len(x);epsilon=1e-6
source_masks={key:cv2.erode((cv2.imread(str(WORK/key/'known.png'),0)>0).astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0 for key in ['a','b']}
secondary=[];events=[];records={};status='COMPLETE_TO_POWER_BOUND';unresolved=np.zeros(len(x),bool)
for number in range(2,64):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 ids=np.flatnonzero((upper>epsilon)&~unresolved)
 if not len(ids):break
 encounters+=len(ids);assert encounters<=p['budgets']['total_interface_encounters']
 event=next_convex_boundary(solid,point[ids],direction[ids],1e-11,64);regular=event['complete'];records[f'{number:02d}_ids']=ids;records[f'{number:02d}_point']=event['point'];records[f'{number:02d}_normal']=event['outward_normal'];records[f'{number:02d}_upper_in']=upper[ids].copy()
 if not regular.all():unresolved[ids[~regular]]=True;status='STOP_UNRESOLVED_GEOMETRIC_BOUNDARY';break
 q=event['point'];n=event['outward_normal'];inc=direction[ids];R=fresnel_components(np.sum(inc*n,-1),1.5,1);loR=R.min(-1);hiR=R.max(-1);loT=lower[ids]*(1-hiR);hiT=upper[ids]*(1-loR);air,tir,_=refract(inc,-n,1.5,1);down=(~tir)&(air[:,2]<0);up=(~tir)&~down
 bg_lower[ids[down]]+=loT[down];bg_upper[ids[down]]+=hiT[down];env_lower[ids[up]]+=loT[up];env_upper[ids[up]]+=hiT[up]
 if down.any():
  travel=(-2-q[down,2])/air[down,2];hit=q[down]+travel[:,None]*air[down];X=hit[:,0]*L+scene['center'][0];Y=hit[:,1]*L+scene['center'][1];safe_by_case={}
  for key,mask in source_masks.items():
   finite=np.isfinite(X)&np.isfinite(Y);u=np.floor(np.where(finite,X,-1)).astype(int);v=np.floor(np.where(finite,Y,-1)).astype(int);safe=finite&(travel>0)&(u>=0)&(v>=0)&(u+1<mask.shape[1])&(v+1<mask.shape[0]);j=np.flatnonzero(safe);safe[j]&=mask[v[j],u[j]]&mask[v[j]+1,u[j]]&mask[v[j],u[j]+1]&mask[v[j]+1,u[j]+1];safe_by_case[key]=safe.tolist()
  secondary.append(dict(encounter=number,launch_ids=ids[down].tolist(),X=X.tolist(),Y=Y.tolist(),power_lower=loT[down].tolist(),power_upper=hiT[down].tolist(),source_supported=safe_by_case))
 lower[ids]*=loR;upper[ids]*=hiR;point[ids]=q;direction[ids]=reflect_direction(inc,n);events.append(dict(encounter=number,active=len(ids),TIR=int(tir.sum()),background=int(down.sum()),environment=int(up.sum()),maximum_bracket=float(event['bracket'].max())))
assert np.all(bg_lower+env_lower+lower<=1+1e-12) and np.all(bg_upper+env_upper+upper>=1-1e-12)
if np.any(upper>epsilon) and status=='COMPLETE_TO_POWER_BOUND':status='STOP_RESIDUAL_POWER_AFTER_ENCOUNTER_CAP'
np.savez_compressed(OUT/'paths.npz',selected_native_indices=np.array(selected),x=x,y=y,point=point,direction=direction,background_lower=bg_lower,background_upper=bg_upper,environment_lower=env_lower,environment_upper=env_upper,residual_lower=lower,residual_upper=upper,unresolved=unresolved,**records)
result=dict(status=status,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),launches=len(x),interface_encounters=encounters,level_points=solid.level_point_evaluations,new_RGB_queries=0,native_images=0,fits=0,initial_nonprimary_power_range=[float((front+initial_reflected).min()),float((front+initial_reflected).max())],residual_upper_max=float(upper.max()),residual_above_tolerance=int((upper>epsilon).sum()),unresolved_geometric_paths=int(unresolved.sum()),secondary_background_events=sum(len(z['X']) for z in secondary),unsupported_secondary_events={key:sum(sum(not a for a in z['source_supported'][key]) for z in secondary) for key in ['a','b']},front_environment_observations=0,events=events,secondary=secondary,limits=['Sparse launch/source audit, not full native reflection support.','Later intensity intervals bound any polarization state; sums are not falsely called exact scalar conservation.','Unobserved environment and incomplete/source-unsupported paths prohibit an RGB reflection image.'])
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','launches','interface_encounters','level_points','initial_nonprimary_power_range','residual_upper_max','residual_above_tolerance','unresolved_geometric_paths','secondary_background_events','unsupported_secondary_events']}))
