from pathlib import Path
import numpy as np,cv2,json,datetime,time,os
P=Path(__file__).resolve().parent;ROOT=P.parent;os.umask(0o002);cv2.setNumThreads(1)
protocol=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['deadline_utc'].replace('Z','+00:00')).timestamp()
assert time.time()<deadline and not (P/'started.json').exists()
(P/'started.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
crops=json.loads((ROOT/'frozen-records/review-round--pass-09-crops.json').read_text());luma=np.array([.2126,.7152,.0722]);rows=[]
for index,key in enumerate(['a','b']):
 assert time.time()<deadline
 case=json.loads((ROOT/f'baseline/inputs/{key}/case.json').read_text());x0,y0,x1,y1=case['crop'];target=cv2.cvtColor(cv2.imread(str(ROOT/f'baseline/inputs/{key}/target.png')),cv2.COLOR_BGR2RGB).astype(np.float32)/255;target=target[y0:y1,x0:x1]
 z=np.load(ROOT/f'baseline/{key}-coordinates.npz');old=np.load(ROOT/f'baseline/{key}-native.npz');new=np.load(ROOT/f'neutral-colour-08/0p5-{key}-native.npz');arrays={'Apple':target,'H1 unit':old['complete'],'H1 tone':new['complete']};H,W=target.shape[:2];inside=z['inside'];raw=old['sampled_rgb'];cohorts={}
 for name,crop in crops['observations'][index]['states'][-1].items():
  l,t,r,b=crop['bounds_pixels'];mask=z['glass'][t:b,l:r];values={}
  for label,full in arrays.items():
   tile=full[t:b,l:r].astype(float)*255;ref=target[t:b,l:r].astype(float)*255;v=tile[mask];yy=v@luma;cc=v-yy[:,None];delta=(tile-ref)[mask];dl=delta@luma;dc=delta-dl[:,None];dx=np.diff(tile,axis=1);dy=np.diff(tile,axis=0);mx=mask[:,1:]&mask[:,:-1];my=mask[1:]&mask[:-1];grad=np.concatenate([dx[mx],dy[my]],axis=0);gl=grad@luma;gc=grad-gl[:,None]
   values[label]={'glass_pixels':int(mask.sum()),'mean_RGB':v.mean(0).tolist(),'mean_luma':float(yy.mean()),'chroma_rms':float(np.sqrt(np.mean(cc*cc))),'signed_RG_BG':[(float((v[:,0]-v[:,1]).mean())),float((v[:,2]-v[:,1]).mean())],'luma_gradient_rms':float(np.sqrt(np.mean(gl*gl))),'chroma_gradient_rms':float(np.sqrt(np.mean(gc*gc))),'RGB_error':float(np.sqrt(np.mean(delta*delta))),'luma_error':float(np.sqrt(np.mean(dl*dl))),'chroma_error':float(np.sqrt(np.mean(dc*dc))),'signed_RGB_error':delta.mean(0).tolist()}
  sub=inside[2*t:2*b,2*l:2*r];samples=raw[2*t:2*b,2*l:2*r][sub].astype(float)*255;sv=samples@luma
  values['retained_incident_samples']={'inside_samples':int(sub.sum()),'mean_RGB':samples.mean(0).tolist(),'chroma_rms':float(np.sqrt(np.mean((samples-sv[:,None])**2))),'observed_confidence':'Zero for hidden incident model; source-availability proof is not photographic evidence.'}
  cohorts[name]={'bounds_pixels':crop['bounds_pixels'],'measurements':values}
 rows.append({'case':key,'source_track_RGB':case['background_estimate']['track_color'],'source_background_RGB':case['background_estimate']['background_color'],'cohorts':cohorts,'limits':'The two frames have different pose, size and transition state. Channel/luma derivatives combine source structure, geometry, blur, lighting and encoding. They are not spectral source correspondences.'})
assert time.time()<deadline
result={'status':'SPECTRAL_DIRECTION_NOT_IDENTIFIED','observations':rows,'conclusion':'Chromatic residuals exist, but the retained modeled source and unresolved achromatic returns do not identify a common physically coupled index direction. This is not evidence that dispersion is absent. No spectral evaluation or adoption.','required_evidence':'Independent incident texture with identifiable neutral edges under the same material/transition state, or a specified measured illumination/background spectral model, before attributing channel offsets to index dispersion.','new_rays':0,'new_source_queries':0,'new_filters':0,'new_composites':0,'new_fits':0,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(P/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(result['status'],result['finished_utc'])
