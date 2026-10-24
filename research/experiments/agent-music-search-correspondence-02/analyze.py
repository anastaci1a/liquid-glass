from pathlib import Path
import numpy as np,cv2,json,csv,hashlib,datetime
P=Path(__file__).resolve().parent; B=P.parent/'agent-music-search-baseline-01';W=P.parents[2]/'.evidence-working/music-search-baseline-01/b'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert not (P/'result.json').exists()
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-24T01:03:21.699+00:00')
files=[W/'source.png',W/'target.png',W/'known.png',B/'native-paths.npz',B/'b-candidate.npz',B/'cached-sections.csv',B/'RGB-started.json']
hashes={str(f.relative_to(P.parents[2])):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
source=cv2.imread(str(W/'source.png'))[...,::-1];target=cv2.imread(str(W/'target.png'))[...,::-1];known=cv2.imread(str(W/'known.png'),0)>0
S=source[560:795,1395:1635];K=known[560:795,1395:1635];white=(S.min(2)/255>=.85)&K
n,lab,stats,cent=cv2.connectedComponentsWithStats(white.astype(np.uint8),8)
components=[dict(id=i,box=[int(stats[i,0]+1395),int(stats[i,1]+560),int(stats[i,0]+stats[i,2]+1395),int(stats[i,1]+stats[i,3]+560)],pixels=int(stats[i,4]),centroid=(cent[i]+[1395,560]).tolist()) for i in range(1,n)]
def runs(a):
 out=[];start=0
 for i in range(1,len(a)+1):
  if i==len(a) or a[i]!=a[start]:out.append(dict(y_start=560+start,y_end_exclusive=560+i,classification=a[start]));start=i
 return out
strips=[];boundary_rows=[]
for name,x0,x1 in [('left',1395,1400),('right',1620,1635)]:
 yy,xx=np.mgrid[560:660,x0:x1];outside=np.hypot(xx-1511.2043368857017,yy-672.8753258356955)>88.75191176648384+1.5
 valid=known[560:660,x0:x1]&outside;rgb=source[560:660,x0:x1];wh=rgb.min(2)/255>=.85;labels=[];rowdata=[]
 for j in range(100):
  v=valid[j];nw=int((v&wh[j]).sum());nv=int(v.sum());label='unavailable' if nv==0 else 'all_white' if nw==nv else 'no_white' if nw==0 else 'mixed'
  labels.append(label);rowdata.append(dict(y=560+j,valid=nv,white=nw,mean_RGB=rgb[j][v].mean(0).tolist() if nv else None))
 changes=[dict(between_rows=[559+j,560+j],from_class=labels[j-1],to_class=labels[j]) for j in range(1,100) if labels[j]!=labels[j-1]]
 for a in changes:
  if a['from_class']!='unavailable' and a['to_class']!='unavailable':boundary_rows+=a['between_rows']
 strips.append(dict(name=name,valid_pixels=int(valid.sum()),outside_margin_native=1.5,minimum_circle_clearance=float((np.hypot(xx-1511.2043368857017,yy-672.8753258356955)-88.75191176648384).min()),runs=runs(labels),changes=changes,rows=rowdata))
q0=np.load(B/'native-paths.npz');q={k:q0[k] for k in ['source_X','source_Y','inside','complete','back','exit_direction','x','y']};c0=np.load(B/'b-candidate.npz');raw=c0['sample_before_response'];coverage=c0['coverage'];inside=q['inside'];X=q['source_X'];Y=q['source_Y'];crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops']
# Conditional feature bounds from fixed threshold components, not a new source mask.
upper_ids=[i['id'] for i in components if i['box'][1]<660];lower_ids=[i['id'] for i in components if i['box'][3]>700]
regions={'upper_white':white&(np.indices(white.shape)[0]+560<660),'lower_letter_white':white&(np.indices(white.shape)[0]+560>=700)}
# Integer integral counts are diagnostic mask reductions, never optical source lookup.
ints={k:np.pad(v.astype(np.int64).cumsum(0).cumsum(1),((1,0),(1,0))) for k,v in regions.items()}
def envelopes(ids):
 sx=X[ids];sy=Y[ids];lx=np.floor(sx).astype(int)-21;rx=np.floor(sx).astype(int)+22;ly=np.floor(sy).astype(int)-21;ry=np.floor(sy).astype(int)+22
 a=np.maximum(lx,1395)-1395;b=np.minimum(rx+1,1635)-1395;d=np.maximum(ly,560)-560;e=np.minimum(ry+1,795)-560
 ok=(a<b)&(d<e);a=np.clip(a,0,240);b=np.clip(b,0,240);d=np.clip(d,0,235);e=np.clip(e,0,235)
 counts={name:np.where(ok,v[e,b]-v[d,b]-v[e,a]+v[d,a],0) for name,v in ints.items()}
 return dict(rays=len(sx),source_bounds=[float(sx.min()),float(sy.min()),float(sx.max()),float(sy.max())],envelopes_outside_diagnostic_crop=int(((lx<1395)|(rx>=1635)|(ly<560)|(ry>=795)).sum()),upper_possible=int((counts['upper_white']>0).sum()),lower_possible=int((counts['lower_letter_white']>0).sum()),both_possible=int(((counts['upper_white']>0)&(counts['lower_letter_white']>0)).sum()),neither_in_crop=int(((counts['upper_white']==0)&(counts['lower_letter_white']==0)).sum()),cached_samples_mean=raw[ids].mean(0).tolist(),cached_samples_white=int((raw[ids].min(1)>=.85).sum()))
local={}
for name,(x0,y0,x1,y1) in crops.items():
 mask=np.zeros(inside.shape,bool);mask[(y0-560)*2:(y1-560)*2,(x0-1395)*2:(x1-1395)*2]=True;ids=np.nonzero(mask&inside&q['complete']);local[name]=envelopes(ids);tt=target[y0:y1,x0:x1];local[name]['target_native_white_pixels']=int((tt.min(2)/255>=.85).sum());local[name]['target_pixels']=tt.shape[0]*tt.shape[1]
sections=list(csv.DictReader((B/'cached-sections.csv').open()));groups={n:[r for r in sections if r['section']==n] for n in sorted({r['section'] for r in sections})};selected=[]
for name,rows in groups.items():
 chosen=rows[::32]+([rows[-1]] if rows[-1] is not rows[::32][-1] else [])
 for r in chosen:
  i,j=int(r['subray_row']),int(r['subray_column']);back=q['back'][i,j];di=q['exit_direction'][i,j];v=float(di[1]/di[2]);roots=[]
  for yb in sorted(set(boundary_rows)):
   yn=(yb-672.8753258356955)/89
   D=None if v==0 else float((back[1]-yn)/v-back[2]);z='stationary' if D is None else 'negative' if D<0 else 'invalid_plane' if D<=.10909090909090907 else 'valid_plane_only'
   # Finite kernel straddles this line when floor(sourceY) lies in [yb-22,yb+21]. Conservative continuous band adds one pixel.
   ends=[] if v==0 else [float((back[1]-(yb+s-672.8753258356955)/89)/v-back[2]) for s in [-22,22]]
   roots.append(dict(boundary_y=yb,D_original_L=D,status=z,near_stationary=abs(v)<1e-6,finite_band_D=sorted(ends)))
  selected.append(dict(section=name,row=i,col=j,x_original_L=float(q['x'][i,j]),y_original_L=float(q['y'][i,j]),dsourceY_dD_native=float(-89*v),cached_source=[float(X[i,j]),float(Y[i,j])],roots=roots))
summary={name:dict(count=len(rows),actual_fixed_coordinate_original_L=float(rows[0]['y_original_L' if name.startswith('horizontal') else 'x_original_L']),envelopes=envelopes((np.array([int(r['subray_row']) for r in rows]),np.array([int(r['subray_column']) for r in rows])))) for name,rows in groups.items()}
save('source-feature-diagnostic.json',dict(criterion='minRGB>=0.85, known, eight-connected',components=components,strips=strips,upper_white_pixels=int(regions['upper_white'].sum()),lower_white_pixels=int(regions['lower_letter_white'].sum()),scope='Conditional source mosaic only; no photographic observation or adopted mask'))
save('saved-correspondence.json',dict(crops=local,sections=summary,selected_roots=selected,boundary_rows=sorted(set(boundary_rows)),maximum_back_depth=.10909090909090907,root_validity='D must exceed maximum complete back height; line intersection alone is not whole support or correspondence.'))
assert all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[str(f.relative_to(P.parents[2]))] for f in files)
save('result.json',dict(status='SAVED_DIAGNOSTIC_COMPLETE',utc=now(),input_hashes=hashes,source_crop_pixels=56400,control_strip_pixels=2000,target_fixed_crop_pixels=sum((r[2]-r[0])*(r[3]-r[1]) for r in crops.values()),retained_section_rows=len(sections),selected_root_rays=len(selected),image_plane_analysis=True,new_photographic_observations=0,new_rays=0,height_evaluations=0,optical_RGB_remaps=0,filters=0,fields=0,images=0,fits=0))
print(json.dumps(dict(components=components,strip_runs=[(x['name'],x['runs']) for x in strips],crops=local,sections=summary,boundary_rows=sorted(set(boundary_rows))),indent=2))
