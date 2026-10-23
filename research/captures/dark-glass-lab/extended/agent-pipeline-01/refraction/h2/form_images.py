"""Private case driver: integrate certified shared-tracer coordinates only.
No tracing, empirical map, fitted shading, source repair or new framework.
"""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h2';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
from PIL import Image,ImageDraw
proof=json.loads((O/'source-preflight.json').read_text());assert proof['status']=='PASS_REQUIRED_SOURCE'
assert time.time()<1792655400.,'Original H2 deadline'
protocol=json.loads((O/'protocol.json').read_text());records={}
for key in ['a','b']:
 st=Study(P/f'inputs/{key}');assert not st.transmission_layers,'No hidden foreground calibration'
 q=np.load(O/f'{key}-native-paths.npz');X=q['X'];Y=q['Y'];supported=q['support']&q['complete'];C=np.full((*X.shape,3),np.nan,np.float64)
 # Access only certified supported RGB texels. Never call remap's boundary extension.
 from geometric_render import render_rows
 from expanded_surface import ExpandedHarmonicBack
 geo=json.loads((O/'geometry-checkpoint.json').read_text())['scene'];surface=ExpandedHarmonicBack(tuple(geo['surface_half']),geo['surface_radius']);scene={**st.case,'center':geo['center']};known=cv2.imread(str(P/f'inputs/{key}/known.png'),0)>0;masks=np.load(P/f'historical-{key}-masks.npz');required=masks['glass']|masks['exterior'];H,W=st.valid.shape
 for layer in st.case['foreground_layers']:
  a,b,c,d=layer['box'];x0,y0,_,_=st.crop;required[b-y0:d-y0,a-x0:c-x0]=True
 material=np.empty((H,W,3),np.float32)
 for row in range(0,H,12):
  assert time.time()<1792655400.,'H2 deadline';bottom=min(row+12,H)
  material[row:bottom],bounds,mask=render_rows(st.source,scene,{},surface,1.5,.5,row,bottom,True,True,samples_per_axis=2,source_known=known,required_pixels=required,return_support=True)
 complete=st.apply_foreground(material.copy())
 display_support=np.isfinite(complete).all(2);assert np.isfinite(complete[st.valid]).all()
 masks=np.load(P/f'historical-{key}-masks.npz');assert np.isfinite(complete[masks['exterior']]).all()
 scores=st.scores(complete);err=(complete-st.target_crop)*255
 fg=[]
 for layer in st.case['foreground_layers']:
  a,b,c,d=layer['box'];x0,y0,_,_=st.crop;m=err[b-y0:d-y0,a-x0:c-x0];assert np.isfinite(m).all();fg.append({'box':layer['box'],'rmse':float(np.sqrt(np.mean(m*m)))})
 scores['exterior']={'pixels':int(masks['exterior'].sum()),'rmse':float(np.sqrt(np.mean(err[masks['exterior']]**2)))}
 scores['E']=float(np.sqrt(scores['loss']));scores['foreground']=fg
 crops={}
 for name,(a,b,c,d) in protocol['reference_crops'].items():
  x0,y0,_,_=st.crop;m=np.zeros((H,W),bool);m[max(0,b-y0):min(H,d-y0),max(0,a-x0):min(W,c-x0)]=True;m&=st.valid
  if m.any():crops[name]={'original_glass_pixels':int(m.sum()),'rmse':float(np.sqrt(np.mean(err[m]**2))),'signed_RGB':err[m].mean(0).tolist()}
 np.save(O/f'{key}-material.npy',material);np.save(O/f'{key}-complete.npy',complete);np.save(O/f'{key}-presentation-support.npy',display_support)
 def rgba(arr):
  ok=np.isfinite(arr).all(2);rgb=np.uint8(np.round(np.clip(np.nan_to_num(arr),0,1)*255));return np.dstack([rgb,ok.astype(np.uint8)*255])
 Image.fromarray(rgba(complete),'RGBA').save(O/f'{key}-candidate.png')
 hist=np.load(P/f'historical-{key}-material.npy');hist=st.apply_foreground(hist.copy())
 panels=[st.target_crop,hist,complete];sheet=Image.new('RGBA',(W*3,H+48),(255,255,255,0));dr=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip(panels,['Apple reference','Historical pass03 (different nuisances)','H2 raw geometric diagnostic; exterior unavailable transparent'])):
  sheet.paste(Image.fromarray(rgba(im),'RGBA'),(i*W,48));dr.text((i*W+8,8),label,fill=(0,0,0,255))
 sheet.save(O/f'{key}-comparison.png')
 # Advisory exact crop rectangles; no recrop/scoring change.
 for name,(a,b,c,d) in protocol['reference_crops'].items():
  x0,y0,_,_=st.crop;cropbox=(a-x0,b-y0,c-x0,d-y0);w=c-a;h=d-b;tile=Image.new('RGBA',(w*3,h+28),(255,255,255,0));draw=ImageDraw.Draw(tile)
  for i,(im,label) in enumerate(zip(panels,['Apple','Historical','H2 raw'])):tile.paste(Image.fromarray(rgba(im),'RGBA').crop(cropbox),(i*w,28));draw.text((i*w+2,4),label,fill=(0,0,0,255))
  tile.save(O/f'{key}-crop-{name}.png')
 records[key]={'scores':scores,'advisory_crops':crops,'supported_pixels':int(display_support.sum()),'unavailable_presentation_pixels':int((~display_support).sum()),'RGB_supported_subrays_sampled':int(supported.sum()),'new_native_images':1,'path_cache_sha256':hashlib.sha256((O/f'{key}-native-paths.npz').read_bytes()).hexdigest()}
result={'status':'FORMED_TWO_FIXED_NATIVE_DIAGNOSTICS','new_shared_render_path_evaluations':2720000,'native_images':2,'AA':2,'bilinear':'exact 4texel','nuisance':'unit transmission; zero added optical blur, lighting, outline, shadow; fixed foreground styles/artwork','historical_comparison':'different nuisances, NOT a same-nuisance gain claim','cases':records,'finished_unix':time.time()};(O/'image-result.json').write_text(json.dumps(result,indent=2,allow_nan=False));print(json.dumps(result))
