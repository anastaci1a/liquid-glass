"""Read frozen arrays only. No transport, RGB remap, raster output or fitting."""
from pathlib import Path
import json,datetime,time,hashlib,csv
import numpy as np,cv2
P=Path(__file__).resolve().parent;B=P;config=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(config['deadline_utc'].replace('Z','+00:00')).timestamp()
assert time.time()<end
cv2.setNumThreads(1)
coeff=np.array([.2126,.7152,.0722]);summary=[]
def intervals(values,selected):
 out=[];on=None
 for v,b in zip(values,selected):
  if b and on is None:on=int(v)
  if not b and on is not None:out.append([on,int(v)-1]);on=None
 if on is not None:out.append([on,int(values[-1])])
 return out
def landmarks(coord,lum,mask,center):
 output=[]
 grad=np.diff(lum);ok=mask[:-1]&mask[1:]
 for side,selector in [('negative',coord<=center),('positive',coord>center)]:
  ids=np.where(mask&selector)[0]
  if not len(ids):continue
  maxidx=ids[np.argmax(lum[ids])];candidates=np.where(ok&selector[:-1])[0];order=candidates[np.argsort(-abs(grad[candidates]))];chosen=[]
  for i in order:
   if all(abs(coord[i]-coord[j])>=4 for j in chosen):chosen.append(int(i))
   if len(chosen)==3:break
  output.append(dict(side=side,brightest_integer_pixel=int(coord[maxidx]),luma_levels=float(lum[maxidx]),gradient_landmarks=[dict(between_pixels=[int(coord[i]),int(coord[i+1])],signed_levels=float(grad[i])) for i in chosen]))
 return output
for key in ['a','b']:
 assert time.time()<end
 case=json.loads((P.parent/'baseline/inputs'/key/'case.json').read_text());proposal=next(x for x in json.loads((P.parent/'proposal.json').read_text())['cases'] if x['key']==key)
 z=np.load(B/f'{key}-coordinates.npz');n=np.load(B/f'{key}-native.npz');source=cv2.cvtColor(cv2.imread(str(P.parent/'baseline/inputs'/key/'source.png')),cv2.COLOR_BGR2RGB).astype(float)/255;target=cv2.cvtColor(cv2.imread(str(P.parent/'baseline/inputs'/key/'target.png')),cv2.COLOR_BGR2RGB).astype(float)/255
 x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;cx,cy=proposal['corrected_center'];L=proposal['L'];half=proposal['corrected_half_over_L'][0]*L
 bg=source[0,0];track=source[round(case['center'][1]),round(case['center'][0])];assert np.linalg.norm(track-bg)>.05
 # Region labels for the already modeled source; never sample RGB at ray coordinates.
 region=np.sum((source-track)**2,axis=-1)<np.sum((source-bg)**2,axis=-1)
 r=proposal['finite_kernel_radius_px'];kernel=np.ones((2*r+1,2*r+1),np.uint8)
 all_track=cv2.erode(region.astype(np.uint8),kernel,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 all_bg=cv2.erode((~region).astype(np.uint8),kernel,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 target=target[y0:y1,x0:x1];C=n['complete'];lum=target@coeff*255;pred=C@coeff*255
 sections=[];csvrows=[]
 for axis,offsets in [('horizontal',[-.6,0,.6]),('vertical',[-.6,0,.6])]:
  for offset in offsets:
   if axis=='horizontal':
    fixed=int(round(cy+offset*L));row=fixed-y0;assert 0<=row<H;coord=np.arange(x0,x1);X=z['source_X'][2*row:2*row+2].reshape(2,W,2).transpose(1,0,2).reshape(W,4);Y=z['source_Y'][2*row:2*row+2].reshape(2,W,2).transpose(1,0,2).reshape(W,4);inside=z['inside'][2*row:2*row+2].reshape(2,W,2).transpose(1,0,2).reshape(W,4);tl=lum[row];pl=pred[row];mask=z['glass'][row];center=cx;viewX=coord[:,None]+np.array([-.25,.25,-.25,.25]);viewY=np.full((W,1),fixed)+np.array([-.25,-.25,.25,.25])
   else:
    fixed=int(round(cx+offset*half));col=fixed-x0;assert 0<=col<W;coord=np.arange(y0,y1);X=z['source_X'][:,2*col:2*col+2].reshape(H,4);Y=z['source_Y'][:,2*col:2*col+2].reshape(H,4);inside=z['inside'][:,2*col:2*col+2].reshape(H,4);tl=lum[:,col];pl=pred[:,col];mask=z['glass'][:,col];center=cy;viewX=np.full((H,1),fixed)+np.array([-.25,.25,-.25,.25]);viewY=coord[:,None]+np.array([-.25,-.25,.25,.25])
   i=np.floor(X).astype(int);j=np.floor(Y).astype(int);rt=np.ones_like(inside);rb=np.ones_like(inside)
   for dx,dy in [(0,0),(0,1),(1,0),(1,1)]:rt &= all_track[j+dy,i+dx];rb &= all_bg[j+dy,i+dx]
   mixed=~rt&~rb;nt=inside.sum();dX=X-viewX;dY=Y-viewY;valid=mask&inside.any(axis=1)
   entry=dict(axis=axis,offset=offset,fixed_integer_coordinate=fixed,inside_subrays=int(nt),original_glass_pixels=int(mask.sum()),source_X_range=[float(X[inside].min()),float(X[inside].max())],source_Y_range=[float(Y[inside].min()),float(Y[inside].max())],displacement_x_range=[float(dX[inside].min()),float(dX[inside].max())],displacement_y_range=[float(dY[inside].min()),float(dY[inside].max())],kernel_regions={name:dict(count=int((m&inside).sum()),fraction=float((m&inside).sum()/nt)) for name,m in [('track_only',rt),('background_only',rb),('mixed',mixed)]},target_landmarks=landmarks(coord,tl,mask,center),predicted_landmarks=landmarks(coord,pl,mask,center),guard_mean_luma=dict(target=float(tl[mask].mean()),predicted=float(pl[mask].mean())),mixed_footprint_integer_intervals=intervals(coord,mixed.any(axis=1)&valid),track_only_integer_intervals=intervals(coord,(rt|~inside).all(axis=1)&valid))
   sections.append(entry)
   for a in range(len(coord)):csvrows.append([axis,offset,fixed,int(coord[a]),int(mask[a]),int(inside[a].sum()),float(tl[a]),float(pl[a]),*map(float,[X[a].min(),X[a].max(),Y[a].min(),Y[a].max()]),int((rt[a]&inside[a]).sum()),int((rb[a]&inside[a]).sum()),int((mixed[a]&inside[a]).sum())])
 with (P/f'{key}-sections.csv').open('w') as f:
  writer=csv.writer(f,lineterminator="\n");writer.writerow(['axis','offset','fixed_coordinate','varying_coordinate','original_glass','inside_subrays','target_luma','cached_complete_luma','source_x_min','source_x_max','source_y_min','source_y_max','track_only','background_only','mixed']);writer.writerows(csvrows)
 summary.append(dict(case=key,source_anchors=dict(background=bg.tolist(),track=track.tolist()),source_track_bounds=dict(x=[int(np.where(region)[1].min()),int(np.where(region)[1].max())],y=[int(np.where(region)[0].min()),int(np.where(region)[0].max())]),retained_coordinate_keys=z.files,retained_path_keys=np.load(P/f'{key}-paths.npz').files,has_cached_exit_height_or_direction=True,sections=sections))
assert time.time()<end
result=dict(status='SAVED_ARRAY_DIAGNOSTIC_COMPLETE',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases=summary,new_rays=0,new_RGB_sampling_queries=0,new_images=0,fits=0,parameter_trials=0)
(P/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
for case in summary:
 print('CASE',case['case'],'source bounds',case['source_track_bounds'],'anchors',case['source_anchors'])
 for sec in case['sections']:print(sec['axis'],sec['offset'],sec['fixed_integer_coordinate'],'regions',sec['kernel_regions'],'mean',sec['guard_mean_luma'],'mixed',sec['mixed_footprint_integer_intervals'],'target',sec['target_landmarks'])
