"""Saved-array crop and fixed-section diagnostics; zero rays or RGB remaps."""
from pathlib import Path
import json,time,datetime,os
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parent;os.umask(0o002)
deadline=datetime.datetime.fromisoformat(json.loads((P/'protocol.json').read_text())['deadline_utc'].replace('Z','+00:00')).timestamp()
assert time.time()<deadline
crops=json.loads((ROOT/'frozen-records/review-round--pass-09-crops.json').read_text());sections=json.loads((ROOT/'correspondence-02/measurements.json').read_text());results=[];luma=np.array([.2126,.7152,.0722])
for index,key in enumerate(['a','b']):
 case=json.loads((ROOT/f'baseline/inputs/{key}/case.json').read_text());x0,y0,x1,y1=case['crop'];target=cv2.cvtColor(cv2.imread(str(ROOT/f'baseline/inputs/{key}/target.png')),cv2.COLOR_BGR2RGB).astype(float)/255;target=target[y0:y1,x0:x1]
 arrays={'H1 seed':np.load(ROOT/f'baseline/{key}-native.npz')['complete'],'0.75':np.load(P/f'narrow-{key}-native.npz')['complete'],'1.25':np.load(P/f'wide-{key}-native.npz')['complete']};z=np.load(ROOT/f'baseline/{key}-coordinates.npz');rows=[];metrics={}
 for name,record in crops['observations'][index]['states'][-1].items():
  l,t,r,b=record['bounds_pixels'];w=r-l;width=min(2*w,max(w,720));height=round((b-t)*width/w);sheet=Image.new('RGB',(4*width+6,height+48),'white');draw=ImageDraw.Draw(sheet);ref=target[t:b,l:r];values={}
  for col,(label,full) in enumerate([('Apple',target)]+list(arrays.items())):
   tile=full[t:b,l:r];sheet.paste(Image.fromarray(np.uint8(np.rint(np.clip(tile,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS),(col*(width+2),48));draw.text((col*(width+2)+5,12),label+' / '+name,fill='black');y=tile@luma*255;dx=np.diff(y,axis=1);dy=np.diff(y,axis=0);detail=float(np.sqrt((np.mean(dx*dx)+np.mean(dy*dy))/2));entry=dict(luma_adjacent_difference_rms=detail)
   if col:
    delta=(tile-ref)*255;yd=delta@luma;cd=delta-yd[...,None];entry.update(rgb_rmse=float(np.sqrt(np.mean(delta*delta))),luma_rmse=float(np.sqrt(np.mean(yd*yd))),chroma_rmse=float(np.sqrt(np.mean(cd*cd))),signed_RGB=delta.mean((0,1)).tolist(),max_change_from_seed=float(np.max(np.abs((tile-arrays['H1 seed'][t:b,l:r])*255))))
   values[label]=entry
  metrics[name]=dict(bounds_pixels=record['bounds_pixels'],width_per_image=width,values=values);rows.append(sheet)
 canvas=Image.new('RGB',(max(x.width for x in rows),sum(x.height for x in rows)+8*(len(rows)-1)),'white');yy=0
 for row in rows:canvas.paste(row,(0,yy));yy+=row.height+8
 canvas.save(P/f'{key}-fixed-crops.png');section_results=[]
 for record in sections['cases'][index]['sections']:
  horizontal=record['axis']=='horizontal';coord=record['fixed_integer_coordinate']-(y0 if horizontal else x0);mask=z['glass'][coord,:] if horizontal else z['glass'][:,coord];measure={}
  for label,full in [('Apple',target)]+list(arrays.items()):
   line=full[coord,:] if horizontal else full[:,coord];v=line@luma*255;d=np.diff(v);adj=mask[:-1]&mask[1:];measure[label]=dict(mean_luma=float(v[mask].mean()),max_luma=float(v[mask].max()),adjacent_difference_rms=float(np.sqrt(np.mean(d[adj]**2))))
  section_results.append(dict(axis=record['axis'],offset=record['offset'],fixed_integer_coordinate=record['fixed_integer_coordinate'],original_glass_pixels=int(mask.sum()),values=measure))
 results.append(dict(case=key,crops=metrics,sections=section_results))
assert time.time()<deadline
(P/'diagnostic.json').write_text(json.dumps(dict(advisory_only=True,limits='Fixed native rectangles and sections. Adjacent differences combine boundaries, material and illumination; they do not identify a geometry or physical PSF. No new RGB remapping or rays.',observations=results),indent=2)+'\n')
print('Saved diagnostics complete')
