"""Closed-form intersections of saved exit lines with a frozen modeled capsule."""
from pathlib import Path
import json,time,datetime,math,os
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent;D=ROOT/'distance-03';proto=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(proto['deadline_utc'].replace('Z','+00:00')).timestamp();assert time.time()<deadline;os.umask(0o002)
H=.10909090909090907
# No renderer, image decoder, sampler, optimizer or surface is imported.
def intersections(a,b,seg,radius):
 roots=[]
 for side in [-1,1]:
  if b[1]!=0:
   t=(side*radius-a[1])/b[1];x=a[0]+t*b[0]
   if abs(x)<=seg+1e-12:roots.append(dict(D=float(t),boundary='top' if side<0 else 'bottom',signed_crossing=float(side*b[1]),boundary_residual=float(abs(a[1]+t*b[1]-side*radius))))
  q=a-np.array([side*seg,0.]);A=float(b@b);B=float(2*q@b);C=float(q@q-radius*radius);disc=B*B-4*A*C
  if A>0 and disc>=0:
   sq=math.sqrt(disc);v=-.5*(B+math.copysign(sq,B));vals=[v/A,C/v] if v!=0 else [-B/(2*A)]
   for t in vals:
    pt=a+t*b
    if side*pt[0]>=seg-1e-12:
     n=pt-np.array([side*seg,0.]);roots.append(dict(D=float(t),boundary='left_cap' if side<0 else 'right_cap',signed_crossing=float(n@b/radius),boundary_residual=float(abs(np.linalg.norm(n)-radius))))
 for q in roots:q['valid_plane']=q['D']>H;q['event']='enter_track' if q['signed_crossing']<0 else ('leave_track' if q['signed_crossing']>0 else 'tangent')
 return sorted(roots,key=lambda q:q['D'])
def interval_events(a,b,seg,radius):return intersections(a,b,seg,radius)
allcases=[];proposal=json.loads((ROOT/'proposal.json').read_text())
for item in proposal['cases']:
 assert time.time()<deadline
 key=item['key'];case=json.loads((ROOT/'baseline/inputs'/key/'case.json').read_text());paths=np.load(D/f'{key}-paths.npz');coords=np.load(D/f'{key}-coordinates.npz');L=item['L'];cx,cy=item['corrected_center'];hx=item['corrected_half_over_L'][0]*L;x0,y0,x1,y1=case['crop'];track=case['background_estimate'];center=np.array(track['track_center_over_L']);halfx,r=track['track_half_over_L'];seg=halfx-r;rho=math.sqrt(2)*(item['finite_kernel_radius_px']+1.5)/L;rows=[]
 for axis in ['horizontal','vertical']:
  for offset in [-.6,0,.6]:
   for along in [-.6,0,.6]:
    px=int(round(cx+(along if axis=='horizontal' else offset)*hx));py=int(round(cy+(offset if axis=='horizontal' else along)*L));ix=px-x0;iy=py-y0
    for sy in [0,1]:
     for sx in [0,1]:
      j=2*iy+sy;i=2*ix+sx;inside=bool(coords['inside'][j,i]);row=dict(section_axis=axis,section_offset=offset,along_offset=along,pixel=[px,py],AA_subray=[sx,sy],inside=inside)
      if inside:
       e=paths['exit'][j,i];u=paths['exit_direction'][j,i];assert u[2]<0;b=u[:2]/(-u[2]);a=e[:2]+e[2]*b-center
       roots=intersections(a,b,seg,r);inner=intersections(a,b,seg,r-rho);outer=intersections(a,b,seg,r+rho)
       # Replay algebra only at the already-rendered plane, never an alternative map.
       predicted=a+.5*b+center;stored=np.array([(coords['source_X'][j,i]-case['center'][0])/L,(coords['source_Y'][j,i]-case['center'][1])/L]);assert abs(predicted-stored).max()<1e-12
       row.update(exit=e.tolist(),exit_direction=u.tolist(),affine_origin_relative_track=a.tolist(),slope=b.tolist(),roots=roots,finite_enclosure=dict(radius=r,rho=rho,eroded_roots=inner,dilated_roots=outer),closest_valid_plane_coordinate_relative_track=(a+H*b).tolist(),stationary=bool((b==0).all()))
      rows.append(row)
 allcases.append(dict(case=key,source_track_center_over_L=center.tolist(),capsule_halfx=halfx,capsule_radius=r,segment_half_length=seg,conservative_kernel_rho=rho,selected_saved_ray_records=len(rows),rows=rows))
assert time.time()<deadline
result=dict(status='ANALYTIC_SAVED_PATH_CROSSINGS_COMPLETE',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),valid_plane_D_strictly_greater_than=H,cases=allcases,new_rays=0,RGB_queries=0,images=0,fits=0,cumulative_native_rays=7473600,cumulative_fixture_comparator_rays=8182,cumulative_images=4)
(P/'crossings.json').write_text(json.dumps(result,indent=2)+'\n')
for case in allcases:
 print('CASE',case['case'])
 for row in case['rows']:
  if row['AA_subray']!=[0,0]:continue
  print(row['section_axis'],row['section_offset'],row['along_offset'],row['pixel'],[(round(t['D'],5),t['boundary'],t['event'],t['valid_plane']) for t in row.get('roots',[])])
