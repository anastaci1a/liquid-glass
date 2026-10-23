"""Retained-array three-proposal comparison. No surface calls or RGB remapping."""
from pathlib import Path
import json,time,datetime,os
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parent;end=datetime.datetime.fromisoformat(json.loads((P/'protocol.json').read_text())['deadline_utc'].replace('Z','+00:00')).timestamp();assert time.time()<end;os.umask(0o002)
variants=[('D2',ROOT/'baseline'),('D0.5',ROOT/'distance-03'),('Raised D2',P)];crops=json.loads((ROOT/'frozen-records/review-round--pass-09-crops.json').read_text());measurements=[json.loads((ROOT/'correspondence-02/measurements.json').read_text()),json.loads((ROOT/'distance-03/measurements.json').read_text()),json.loads((P/'measurements.json').read_text())];allcrops=[];sections=[];audits=[];guards=[]
for index,key in enumerate(['a','b']):
 assert time.time()<end
 case=json.loads((ROOT/'baseline/inputs'/key/'case.json').read_text());L=min(case['half']);cx,cy=case['center'];x0,y0,x1,y1=case['crop'];target=cv2.cvtColor(cv2.imread(str(ROOT/'baseline/inputs'/key/'target.png')),cv2.COLOR_BGR2RGB).astype(float)/255;target=target[y0:y1,x0:x1];native=[np.load(folder/f'{key}-native.npz') for _,folder in variants];z=np.load(P/f'{key}-coordinates.npz');paths=np.load(P/f'{key}-paths.npz');inside=z['inside'];exit=paths['exit'][inside];direction=paths['exit_direction'][inside];dest=exit+paths['path_length'][inside,None]*direction
 errors=dict(source_x=float(abs(dest[:,0]-(z['source_X'][inside]-cx)/L).max()),source_y=float(abs(dest[:,1]-(z['source_Y'][inside]-cy)/L).max()),background_plane=float(abs(dest[:,2]+2).max()),normal_length=float(abs(np.linalg.norm(paths['exit_normal'][inside],axis=1)-1).max()))
 assert max(errors.values())<1e-12 and np.isnan(paths['entry'][~inside]).all() and np.isnan(paths['exit'][~inside]).all()
 orientation=[]
 for (name,folder),n in zip(variants,native):
  q=np.load(folder/f'{key}-coordinates.npz');assert np.array_equal(q['inside'],inside);assert np.array_equal(n['coverage'],native[0]['coverage']);assert np.array_equal(n['clear_premultiplied'],native[0]['clear_premultiplied']);X=q['source_X'];Y=q['source_Y'];Xy,Xx=np.gradient(X,.5,.5);Yy,Yx=np.gradient(Y,.5,.5);det=Xx*Yy-Xy*Yx;safe=cv2.erode(inside.astype(np.uint8),np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  orientation.append(dict(variant=name,full_lens_stencil_subrays=int(safe.sum()),negative_orientation_subrays=int((det[safe]<0).sum()),negative_fraction=float((det[safe]<0).mean()),minimum_det=float(det[safe].min()),maximum_det=float(det[safe].max()),limits='Finite differences of saved maps, not a new ray test or a no-fold acceptance criterion. Reference correspondence is needed to judge a reversal.'))
 audits.append(dict(case=key,retained_path_errors=errors,coverage_clear_exact=True,orientation=orientation))
 rows=[];metrics={}
 for name,record in crops['observations'][index]['states'][-1].items():
  l,t,r,b=record['bounds_pixels'];w=r-l;width=min(2*w,max(w,720));height=round((b-t)*width/w);sheet=Image.new('RGB',(4*width+6,height+48),'white');draw=ImageDraw.Draw(sheet);values={};ref=target[t:b,l:r]
  for col,(label,full) in enumerate([('Apple',target)]+[(label,n['complete']) for (label,_),n in zip(variants,native)]):
   tile=full[t:b,l:r];im=Image.fromarray(np.uint8(np.rint(np.clip(tile,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS);sheet.paste(im,(col*(width+2),48));draw.text((col*(width+2)+5,12),label+' / '+name,fill='black')
   if col:
    d=(tile-ref)*255;y=d@np.array([.2126,.7152,.0722]);ch=d-y[...,None];values[label]=dict(rgb_rmse=float(np.sqrt(np.mean(d*d))),luma_rmse=float(np.sqrt(np.mean(y*y))),chroma_rmse=float(np.sqrt(np.mean(ch*ch))),signed_RGB=d.mean((0,1)).tolist())
  metrics[name]=dict(bounds_pixels=record['bounds_pixels'],width_per_image=width,metrics=values,raised_minus_D2={m:values['Raised D2'][m]-values['D2'][m] for m in ['rgb_rmse','luma_rmse','chroma_rmse']},raised_minus_D05={m:values['Raised D2'][m]-values['D0.5'][m] for m in ['rgb_rmse','luma_rmse','chroma_rmse']});rows.append(sheet)
 canvas=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+8*(len(rows)-1)),'white');y=0
 for row in rows:canvas.paste(row,(0,y));y+=row.height+8
 canvas.save(P/f'{key}-three-proposal-crops.png');allcrops.append(dict(case=key,crops=metrics))
 for j,now in enumerate(measurements[2]['cases'][index]['sections']):
  previous=[m['cases'][index]['sections'][j] for m in measurements[:2]]
  for prev in previous:assert now['target_landmarks']==prev['target_landmarks'] and now['fixed_integer_coordinate']==prev['fixed_integer_coordinate'] and now['original_glass_pixels']==prev['original_glass_pixels']
  sections.append(dict(case=key,axis=now['axis'],offset=now['offset'],target_landmarks_exact=True,variants={name:dict(regions=s['kernel_regions'],mean_luma=s['guard_mean_luma']) for name,s in zip(['D2','D0.5','Raised D2'],previous+[now])}))
 scores=[next(o['scores'] for o in json.loads((folder/'result.json').read_text())['observations'] if o['case']==key) for _,folder in variants]
 def nonreg(a,b):return {**{m:a[m]['rmse']<=b[m]['rmse'] for m in ['glass','rim','held','interior','exterior']},'E':a['E']<=b['E'],'ssim':a['ssim']>=b['ssim']}
 guards.append(dict(case=key,scores={name:s for (name,_),s in zip(variants,scores)},raised_vs_D2=nonreg(scores[2],scores[0]),raised_vs_D05=nonreg(scores[2],scores[1])))
assert time.time()<end
for name,obj in [('three-proposal-crops.json',dict(advisory_only=True,observations=allcrops)),('section-comparison.json',sections),('retained-path-orientation.json',audits),('three-proposal-guards.json',guards)]: (P/name).write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps(audits));print(json.dumps(guards))
