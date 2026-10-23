"""Saved-array consistency and presentation only; no new optical rays or sampling."""
from pathlib import Path
import json,datetime,time,hashlib,os
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parent;end=datetime.datetime.fromisoformat(json.loads((P/'protocol.json').read_text())['deadline_utc'].replace('Z','+00:00')).timestamp();assert time.time()<end;os.umask(0o002)
old=json.loads((ROOT/'correspondence-02/measurements.json').read_text());new=json.loads((P/'measurements.json').read_text());crops=json.loads((ROOT/'frozen-records/review-round--pass-09-crops.json').read_text());proposal=json.loads((ROOT/'proposal.json').read_text());audits=[];regions=[];section_changes=[]
for index,key in enumerate(['a','b']):
 assert time.time()<end
 item=proposal['cases'][index];case=json.loads((ROOT/'baseline/inputs'/key/'case.json').read_text());L=item['L'];cx,cy=case['center'];z=np.load(P/f'{key}-coordinates.npz');paths=np.load(P/f'{key}-paths.npz');inside=z['inside'];n=np.load(P/f'{key}-native.npz');old_n=np.load(ROOT/f'baseline/{key}-native.npz');a=n['complete'];b=old_n['complete'];target=cv2.cvtColor(cv2.imread(str(ROOT/'baseline/inputs'/key/'target.png')),cv2.COLOR_BGR2RGB).astype(float)/255;x0,y0,x1,y1=case['crop'];target=target[y0:y1,x0:x1]
 # Validate the stored primary path without a call to any surface or tracer.
 entry=paths['entry'][inside];exit=paths['exit'][inside];directions=paths['exit_direction'][inside];length=paths['path_length'][inside];projected=exit+length[:,None]*directions
 errors=dict(entry_front_z=float(abs(entry[:,2]).max()),entry_exit_xy=float(abs(entry[:,:2]-exit[:,:2]).max()),source_X=float(abs(projected[:,0]-(z['source_X'][inside]-cx)/L).max()),source_Y=float(abs(projected[:,1]-(z['source_Y'][inside]-cy)/L).max()),background_z=float(abs(projected[:,2]+.5).max()),exit_normal_norm=float(abs(np.linalg.norm(paths['exit_normal'][inside],axis=1)-1).max()),exit_direction_norm=float(abs(np.linalg.norm(directions,axis=1)-1).max()))
 assert max(errors.values())<1e-12
 assert np.isnan(paths['entry'][~inside]).all() and np.isnan(paths['exit'][~inside]).all();assert np.isnan(paths['entry_normal'][~inside]).all() and np.isnan(paths['exit_normal'][~inside]).all()
 assert (exit[:,2]<0).all() and (directions[:,2]<0).all();assert np.array_equal(n['coverage'],old_n['coverage']) and np.array_equal(n['clear_premultiplied'],old_n['clear_premultiplied'])
 audits.append(dict(case=key,errors=errors,entry_normal_plus_z=bool(np.array_equal(paths['entry_normal'][inside],np.tile([0.,0.,1.],(len(entry),1)))),minimum_actual_exit_clearance=float((.5+exit[:,2]).min()),missing_interfaces_are_NaN_on_clear_misses=True,paths_complete=bool(z['complete'].all()),coverage_exact=True,clear_premultiplied_exact=True,units='Positions are original-L coordinates relative to original case center; +z viewer, front0/background-.5. Normals are outward. Clear misses have no physical interface.'))
 rows=[];metrics={};maxw=0
 for name,record in crops['observations'][index]['states'][-1].items():
  l,t,r,bot=record['bounds_pixels'];nativew=r-l;width=min(2*nativew,max(nativew,720));height=round((bot-t)*width/nativew);maxw=max(maxw,width);row=Image.new('RGB',(3*width+4,height+48),'white');draw=ImageDraw.Draw(row)
  vals={};ref=target[t:bot,l:r];
  for c,(label,v) in enumerate([('Apple',target),('Physical D2',b),('Physical D0.5',a)]):
   tile=v[t:bot,l:r];im=Image.fromarray(np.uint8(np.rint(np.clip(tile,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS);row.paste(im,(c*(width+2),48));draw.text((c*(width+2)+6,10),label+' / '+name,fill='black')
   if c:
    d=(tile-ref)*255;lum=d@np.array([.2126,.7152,.0722]);chroma=d-lum[...,None];vals[label]=dict(rgb_rmse=float(np.sqrt(np.mean(d*d))),luma_rmse=float(np.sqrt(np.mean(lum*lum))),chroma_rmse=float(np.sqrt(np.mean(chroma*chroma))),signed_RGB=d.mean((0,1)).tolist())
  metrics[name]=dict(bounds_pixels=record['bounds_pixels'],presentation_width_per_image=width,metrics=vals,change_D05_minus_D2={m:vals['Physical D0.5'][m]-vals['Physical D2'][m] for m in ['rgb_rmse','luma_rmse','chroma_rmse']});rows.append(row)
 sheet=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+8*(len(rows)-1)),'white');y=0
 for row in rows:sheet.paste(row,(0,y));y+=row.height+8
 sheet.save(P/f'{key}-fixed-crops.png');regions.append(dict(case=key,crops=metrics))
 for s,o in zip(new['cases'][index]['sections'],old['cases'][index]['sections']):
  assert s['axis']==o['axis'] and s['offset']==o['offset'] and s['fixed_integer_coordinate']==o['fixed_integer_coordinate'] and s['target_landmarks']==o['target_landmarks'] and s['original_glass_pixels']==o['original_glass_pixels']
  section_changes.append(dict(case=key,axis=s['axis'],offset=s['offset'],track_only=[o['kernel_regions']['track_only']['fraction'],s['kernel_regions']['track_only']['fraction']],background_only=[o['kernel_regions']['background_only']['fraction'],s['kernel_regions']['background_only']['fraction']],target_landmarks_exact=True,mean_luma=dict(target=s['guard_mean_luma']['target'],D2=o['guard_mean_luma']['predicted'],D05=s['guard_mean_luma']['predicted'])))
assert time.time()<end
(P/'saved-path-audit.json').write_text(json.dumps(dict(status='PASS_SAVED_PATH_CONSISTENCY',cases=audits,new_rays=0,new_RGB_queries=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
(P/'crop-diagnostics.json').write_text(json.dumps(dict(advisory_only=True,scoring_masks_changed=False,observations=regions),indent=2)+'\n')
(P/'section-comparison.json').write_text(json.dumps(section_changes,indent=2)+'\n')
print(json.dumps(audits));print(json.dumps(regions))
