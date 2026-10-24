from pathlib import Path
import json,datetime,hashlib,zipfile,struct,ast,math
O=Path(__file__).parent;ROOT=O.parents[2];P=json.loads((O/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));CP=datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'))
def gate(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<(CP if checkpoint else END)
def save(f,v):(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files={};headers=[];plans=[];pixels=0;payload=0;channels=0
for k in ['a','b']:
 folder=ROOT/'.evidence-working/music-search-baseline-01'/k;case=json.loads((folder/'case.json').read_text());assert case['crop']==[1395,560,1635,795]
 files[str((folder/'case.json').relative_to(ROOT))]=sha(folder/'case.json')
 for name,path in [('original_target',folder/'target.png'),('selected_Search_complete',ROOT/f'research/experiments/agent-music-search-neutral-05/full-{k}-candidate.npz'),('transfer34_complete',ROOT/f'research/experiments/agent-search-working-transfer-34/{k}-candidate.npz')]:
  gate();files[str(path.relative_to(ROOT))]=sha(path)
  if path.suffix=='.png':
   with path.open('rb') as f:h=f.read(33)
   assert h[:8]==b'\x89PNG\r\n\x1a\n' and h[12:16]==b'IHDR';W,H,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',h[16:29]);assert depth==8 and color==2 and compression==0 and filtering==0
   shape=(H,W,3);dtype='uint8';nbytes=H*W*3;member=None
  else:
   with zipfile.ZipFile(path) as z:
    assert len(z.namelist())==len(set(z.namelist())) and 'complete.npy' in z.namelist()
    with z.open('complete.npy') as f:
     assert f.read(6)==b'\x93NUMPY';version=tuple(f.read(2));assert version in [(1,0),(2,0)];size=struct.unpack('<H' if version==(1,0) else '<I',f.read(2 if version==(1,0) else 4))[0];assert size<=4096;raw=f.read(size);header=ast.literal_eval(raw.decode('latin1'));shape=header['shape'];dtype=header['descr'];assert shape==(235,240,3) and dtype=='<f4' and not header['fortran_order'];nbytes=math.prod(shape)*4;assert z.getinfo('complete.npy').file_size==6+2+(2 if version==(1,0) else 4)+size+nbytes
   member='complete.npy'
  pixels+=shape[0]*shape[1];channels+=math.prod(shape);payload+=nbytes;headers.append({'reference':k,'field':name,'path':str(path.relative_to(ROOT)),'shape':shape,'dtype':dtype,'member':member,'decoded_payload_bytes':nbytes});plans.append((k,name,path,shape))
assert pixels<=P['caps']['decoded_spatial_pixel_cells'] and payload<=P['caps']['decoded_payload_bytes']
assert P['center_native']==[1511.2043368857017,672.8753258356955] and P['radius_native']==88.75191176648384
receipt=ROOT/'research/experiments/agent-search-family-forward-29/common.py';text=receipt.read_text();assert '1511.2043368857017,672.8753258356955' in text and 'L=89' in text;files[str(receipt.relative_to(ROOT))]=sha(receipt)
# Radius in native units is the accepted normalized radius times original L89.
assert abs(.9972124917582454*89-P['radius_native'])<1e-12
save('first-hashes.json',files);gate(True);save('checkpoint.json',{'status':'PASS_HEADERS_GEOMETRY_FIXED_PLAN_BEFORE_DECODE','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headers':headers,'reserved':{'decoded_spatial_pixel_cells':pixels,'channel_entries':channels,'decoded_payload_bytes':payload,'profiles':24,'selected_pixel_observations':408},'only_NPY_member_complete':True})
print('CHECKPOINT',pixels,payload,flush=True)
import numpy as np
from PIL import Image
records=[];observations=0;actual_pixels=0;actual_payload=0
for k,name,path,shape in plans:
 gate()
 if path.suffix=='.png':
  with Image.open(path) as image:
   assert image.mode=='RGB' and image.size==(shape[1],shape[0]);arr=np.asarray(image);assert arr.shape==shape and arr.dtype==np.uint8
 else:
  with np.load(path,allow_pickle=False) as z:arr=z['complete']
  assert arr.shape==shape and arr.dtype==np.float32
 actual_pixels+=shape[0]*shape[1];actual_payload+=arr.nbytes
 for direction,(dx,dy) in P['directions'].items():
  samples=[]
  for offset in P['radial_offsets_native']:
   gate();radius=P['radius_native']+offset;x=P['center_native'][0]+dx*radius;y=P['center_native'][1]+dy*radius;px=math.floor(x+.5);py=math.floor(y+.5);a,b=(px,py) if name=='original_target' else (px-1395,py-560);assert 0<=a<arr.shape[1] and 0<=b<arr.shape[0];v=arr[b,a];observations+=1;rgb=[float(t)/255 if name=='original_target' else float(t) for t in v];finite=all(math.isfinite(t) for t in rgb);lum=sum(c*t for c,t in zip([.2126,.7152,.0722],rgb)) if finite else None
   samples.append({'offset_native':offset,'requested_xy':[x,y],'selected_native_xy':[px,py],'actual_radius_offset_native':math.hypot(px-P['center_native'][0],py-P['center_native'][1])-P['radius_native'],'RGB':[t if math.isfinite(t) else None for t in rgb],'finite':finite,'encoded_luminance':lum})
  differences=[];extrema=[]
  for i in range(16):
   aa=samples[i];bb=samples[i+1];differences.append({'from_offset':aa['offset_native'],'to_offset':bb['offset_native'],'delta_luminance':bb['encoded_luminance']-aa['encoded_luminance'] if aa['finite'] and bb['finite'] else None,'delta_RGB':[v-u for u,v in zip(aa['RGB'],bb['RGB'])] if aa['finite'] and bb['finite'] else None})
  for i in range(1,16):
   a,b,c=[samples[j]['encoded_luminance'] for j in [i-1,i,i+1]]
   if None in [a,b,c]:continue
   if b>=a and b>=c:extrema.append({'offset':samples[i]['offset_native'],'kind':'local_maximum_including_plateau','luminance':b})
   if b<=a and b<=c:extrema.append({'offset':samples[i]['offset_native'],'kind':'local_minimum_including_plateau','luminance':b})
  seen=set();duplicates=[]
  for s in samples:
   key=tuple(s['selected_native_xy'])
   if key in seen:duplicates.append(s['offset_native'])
   seen.add(key)
  records.append({'reference':k,'field':name,'direction':direction,'samples':samples,'duplicate_offsets':duplicates,'finite_differences':differences,'local_extrema':extrema,'endpoint_extrema_not_inferred':True})
 del arr
assert observations==408 and len(records)==24 and actual_pixels==pixels and actual_payload==payload
last={f:sha(ROOT/f) for f in files};assert last==files;save('last-hashes.json',last);save('profiles.json',{'status':'FIXED_SAVED_CARDINAL_PROFILES_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':{'profiles':24,'selected_pixel_observations':observations,'decoded_spatial_pixel_cells':actual_pixels,'decoded_channel_entries':channels,'decoded_payload_bytes':actual_payload,'optical_work':0,'new_images_or_exports':0},'selected_state_changed':False})
print('PROFILES_COMPLETE',observations,flush=True)
