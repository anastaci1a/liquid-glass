"""One unfitted pair. Shared rays, cached-coordinate native integration only."""
from pathlib import Path
import sys,json,time,datetime,hashlib,os
import numpy as np,cv2
P=Path(__file__).resolve().parent.parent;R=P.parents[2];sys.path.insert(0,str(R/'reconstruction'));sys.path.insert(0,str(P))
from checkpoint import PosedSurface
import native_surface
from native_surface import RaisedBack
from geometric_optics import trace_flat_front_orthographic
from geometric_render import incident_source_filter,render_rows
from extended_fit import Study
cv2.setNumThreads(1);os.umask(0o002)
O=P/'raised-native-06';schedule=json.loads((O/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(schedule['deadline_utc'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Original subpass deadline reached'
def save(name,obj):(O/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def main():
 gate();assert not (O/'native-started.json').exists(),'Inspect partial artifacts; do not restart'
 approved=json.loads((P/'raised-back-05/geometry-result.json').read_text());assert approved['status']=='RAISED_BACK_PRIMARY_GEOMETRY_CHECKPOINT_PASS';checkpoint={'charged_fixture_rays':0};assert native_surface.height_evaluations==0 and native_surface.footprint_evaluations==0;save('phase-armed.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),graph_limit=8000000,prior_geometry_height_evaluations=9350,height_counter_initial=0,footprint_counter_initial=0));save('native-started.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),native_ray_cap=3736800,images_cap=2))
 proposal=json.loads((P/'proposal.json').read_text());states={};proofs=[];total=0
 for item in proposal['cases']:
  gate();key=item['key'];s=Study(P/'baseline/inputs'/key);L=s.L;x0,y0,x1,y1=s.crop;H,W=y1-y0,x1-x0
  assert not s.foreground_layers and not s.transmission_layers
  for cohort,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim)]:assert int(mask.sum())==item['original_scores'][cohort]['pixels']
  ext=(s.sd>0)&(s.sd<.35);assert int(ext.sum())==item['original_scores']['shadow']['pixels']
  safe_ssim=cv2.erode(s.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0
  required=s.valid|ext|(cv2.dilate(safe_ssim.astype(np.uint8),np.ones((11,11),np.uint8))>0)
  known=cv2.imread(str(s.folder/'known.png'),0)>0;observed=cv2.imread(str(s.folder/'observed.png'),0)>0;r=item['finite_kernel_radius_px'];kernel=np.ones((2*r+1,2*r+1),np.uint8);ksafe=cv2.erode(known.astype(np.uint8),kernel,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;osafe=cv2.erode(observed.astype(np.uint8),kernel,borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  base=RaisedBack(tuple(item['corrected_half_over_L']),softness=.08);dx=(item['corrected_center'][0]-s.case['center'][0])/L;dy=(item['corrected_center'][1]-s.case['center'][1])/L;surface=PosedSurface(base,dx,dy)
  X=np.empty((2*H,2*W),float);Y=np.empty_like(X);inside=np.empty(X.shape,bool);support=np.empty(X.shape,bool);obs=np.empty(X.shape,bool);complete=np.empty(X.shape,bool);row_stats=[];paths={k:np.empty(X.shape+(3,),float) for k in ["entry","entry_normal","exit","exit_normal","internal_direction","exit_direction"]};paths.update({k:np.empty(X.shape,float) for k in ["path_length","discriminant"]});paths.update({k:np.empty(X.shape,bool) for k in ["boundary_unresolved","zero_thickness_unresolved"]})
  for row in range(0,H,24):
   gate();stop=min(H,row+24);yy,xx=np.mgrid[y0+row:y0+stop:.5,x0:x1:.5];x=(xx-.25-s.case['center'][0])/L;y=(yy-.25-s.case['center'][1])/L;total+=x.size;assert total<=3736800;save('ray-ledger.json',dict(native_attempted=total,fixture_comparator=checkpoint['charged_fixture_rays'],rgb_integrations=0))
   q=trace_flat_front_orthographic(surface,x,y,1.5,2.);assert q['complete'].all(),'Unresolved native branch';sx=q['X']*L+s.case['center'][0];sy=q['Y']*L+s.case['center'][1];assert np.isfinite(sx).all() and np.isfinite(sy).all();i=np.floor(sx).astype(int);j=np.floor(sy).astype(int);assert ((i>=0)&(j>=0)&(i+1<known.shape[1])&(j+1<known.shape[0])).all(),'Undefined native bilinear coordinate'
   ok=np.ones(x.shape,bool);ob=np.ones_like(ok)
   for u,v in [(0,0),(1,0),(0,1),(1,1)]:ok&=np.where(q['inside'],ksafe[j+v,i+u],known[j+v,i+u]);ob&=np.where(q['inside'],osafe[j+v,i+u],observed[j+v,i+u])
   req=np.repeat(np.repeat(required[row:stop],2,0),2,1);assert ok[q['inside']|req].all(),'Required finite source footprint undefined';assert ok.all(),'This baseline requires full native image support'
   sl=np.s_[2*row:2*stop];entry=np.stack([x,y,np.zeros_like(x)],axis=-1);front_normal=np.zeros_like(entry);front_normal[...,2]=1.;internal=-front_normal;paths['entry'][sl]=np.where(q['inside'][...,None],entry,np.nan);paths['entry_normal'][sl]=np.where(q['inside'][...,None],front_normal,np.nan);paths['internal_direction'][sl]=np.where(q['inside'][...,None],internal,np.nan);paths['exit'][sl]=q['back'];paths['exit_normal'][sl]=q['outward_normal'];paths['exit_direction'][sl]=q['exit_direction'];
   for field in ['path_length','discriminant','boundary_unresolved','zero_thickness_unresolved']:paths[field][sl]=q[field]
   X[sl]=sx;Y[sl]=sy;inside[sl]=q['inside'];support[sl]=ok;obs[sl]=ob;complete[sl]=q['complete'];row_stats.append(dict(row=row,stop=stop,rays=int(x.size),minimum_discriminant=float(q['discriminant'].min())))
  np.savez_compressed(O/f'{key}-paths.npz',**paths);old_z=np.load(P/f'baseline/{key}-coordinates.npz');
  for field,new in [('inside',inside),('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim),('exterior',ext),('required',required)]:assert np.array_equal(old_z[field],new),field
  np.savez_compressed(O/f'{key}-coordinates.npz',source_X=X,source_Y=Y,inside=inside,support=support,observed=obs,complete=complete,glass=s.valid,rim=s.rim,held=s.held,interior=s.valid&~s.rim,exterior=ext,ssim_safe=safe_ssim,required=required)
  req=np.repeat(np.repeat(required,2,0),2,1);proof=dict(case=key,rays=int(X.size),whole=int(inside.sum()),required_subrays=int(req.sum()),whole_or_required=int((inside|req).sum()),undefined_required=0,unresolved=0,minimum_defined=1,whole_observed_fraction=float(obs[inside].mean()),required_observed_fraction=float(obs[req].mean()),source_kernel_radius=r,rows=row_stats,original_mask_counts={k:int(m.sum()) for k,m in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim),('exterior',ext)]});proofs.append(proof);states[key]=(s,item,surface,X,Y,inside,known,ksafe,ext)
 gate();assert total==3736800;save('source-proof-FIRST.json',dict(status='PASS_BOTH_CASES_BEFORE_RGB',observations=proofs,native_rays=total,source_confidence='Modeled hidden track; defined support is not photographic observation',utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 integrate(states,checkpoint,total)
def integrate(states,checkpoint,total):
 results=[];parity_count=0
 for key,(s,item,surface,X,Y,inside,known,ksafe,ext) in states.items():
  gate();incident,filter_safe,radius=incident_source_filter(s.source,known,item['proposed_incident_sigma_px']);assert radius==item['finite_kernel_radius_px'] and np.array_equal(filter_safe,ksafe)
  # Reuse every certified coordinate. No new native trace is made here.
  samples=cv2.remap(s.source,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR)
  yy,xx=np.nonzero(inside)
  for lo in range(0,len(yy),16000):
   gate();rr=yy[lo:lo+16000];cc=xx[lo:lo+16000];samples[rr,cc]=cv2.remap(incident,X[rr,cc].astype(np.float32)[None],Y[rr,cc].astype(np.float32)[None],cv2.INTER_LINEAR)[0]
  assert np.isfinite(samples).all()
  H,W=s.valid.shape;C=samples.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);coverage=inside.reshape(H,2,W,2).mean((1,3));lens=(samples*inside[...,None]).reshape(H,2,W,2,3).mean((1,3));clear=(samples*(~inside)[...,None]).reshape(H,2,W,2,3).mean((1,3));lens_color=np.divide(lens,coverage[...,None],out=np.zeros_like(lens),where=coverage[...,None]>0)
  # Tiny parity controls cover one central patch and one partial-edge patch.
  partial=np.argwhere((coverage>0)&(coverage<1));edge=partial[len(partial)//2];patches=[(H//2,W//2),(int(edge[0]),max(0,min(W-4,int(edge[1]))))];errors=[]
  for py,px in patches:
   gate();py=min(py,H-4);px=min(px,W-4);case={**s.case,'crop':[s.crop[0]+px,s.crop[1]+py,s.crop[0]+px+4,s.crop[1]+py+4]};parity_count+=64;assert checkpoint['charged_fixture_rays']+parity_count<=256
   actual,_=render_rows(s.source,case,{},surface,1.5,2.,0,4,raw_transmission=True,samples_per_axis=2,source_known=known,required_pixels=np.ones((4,4),bool),incident_source=incident,incident_known=filter_safe);expected=C[py:py+4,px:px+4];errors.append(float(abs(actual-expected).max()));assert np.array_equal(actual,expected),'Integrator parity mismatch'
  old_arrays=np.load(P/f'baseline/{key}-native.npz');assert np.array_equal(coverage,old_arrays['coverage']);assert np.array_equal(clear,old_arrays['clear_premultiplied']);old_scores=next(z['scores'] for z in json.loads((P/'baseline/result.json').read_text())['observations'] if z['case']==key);scores=s.scores(C);scores['E']=float(np.sqrt(scores['loss']));scores['exterior']=dict(pixels=int(ext.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2))));baseline=item['original_scores'];guards={k:scores[k]['rmse']<=baseline[k]['rmse'] for k in ['glass','rim','held','interior']};guards.update(E=scores['E']<=baseline['E'],ssim=scores['ssim']>=baseline['ssim'],exterior=scores['exterior']['rmse']<=baseline['shadow']['rmse']);v=samples;clips=dict(below_zero=int((v<0).sum()),above_one=int((v>1).sum()))
  np.savez_compressed(O/f'{key}-native.npz',sampled_rgb=samples,lens_premultiplied=lens,clear_premultiplied=clear,coverage=coverage,lens_color=lens_color,pre_foreground=C,complete=C)
  # Native-size saved diagnostic only; no extra optical raster or fitting.
  from PIL import Image,ImageDraw
  width=W;sheet=Image.new('RGB',(2*width+2,H+48),'white');sheet.paste(Image.fromarray(np.uint8(np.rint(s.target_crop*255))),(0,48));sheet.paste(Image.fromarray(np.uint8(np.rint(np.clip(C,0,1)*255))),(width+2,48));d=ImageDraw.Draw(sheet);d.text((8,16),'Apple reference',fill='black');d.text((width+10,16),'Fixed raised back D2; modeled source',fill='black');sheet.save(O/f'{key}-comparison.png')
  result=dict(case=key,scores=scores,historical_guards=guards,parity_max_difference=errors,raw_clip_counts=clips,images=1,versus_D2={k:scores[k]['rmse']<=old_scores[k]['rmse'] for k in ['glass','rim','held','interior','exterior']},unchanged_coverage=True,unchanged_clear_contribution=True);results.append(result);save('partial-result.json',results);print(json.dumps(result),flush=True)
 gate();save('result.json',dict(status='RAISED_BACK_NATIVE_PAIR_READY_FOR_REVIEW',observations=results,native_rays=total,fixture_comparator_rays=checkpoint['charged_fixture_rays']+parity_count,full_native_images=2,fits=0,accepted_passes=0,cumulative_native_rays=7473600+total,cumulative_fixture_comparator_rays=9704+parity_count,cumulative_native_images=6,new_height_evaluations=native_surface.height_evaluations,new_footprint_evaluations=native_surface.footprint_evaluations,new_graph_evaluations=native_surface.height_evaluations+native_surface.footprint_evaluations,raised_height_evaluations_cumulative=9350+native_surface.height_evaluations,raised_checkpoint_plus_parity=1522+parity_count,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),limitations='Modeled source, observed confidence zero; no lighting, shadow or spectral operator. Mathematical paths are not identified Apple optics. No historical mask/recipe/count change.'))
if __name__=='__main__':main()
