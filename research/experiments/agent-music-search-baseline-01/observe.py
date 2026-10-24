from common import *
from geometric_render import render_rows
from PIL import Image,ImageDraw,ImageFont
import hashlib
assert json.loads((P/'source-preflight.json').read_text())['status']=='PASS_BOTH_BEFORE_RGB'
assert not (P/'RGB-started.json').exists(),'No repeated RGB pair';gate()
crops={'upper_rim':[1440,576,1580,620],'left_cap':[1418,630,1455,718],'lower_return':[1440,728,1580,764],'glyph':[1467,626,1563,722]}
save('RGB-started.json',dict(utc=utc(),fixed_original_frame_crops=crops,settings=par,maximum_pairs=1,case_epoch_scope='Prospective approved verification-protocol cases; historical recipe fingerprint remains unresolved, no same-epoch acceptance comparison.',source_gate='Both preflights passed before any RGB'))
q=np.load(P/'native-paths.npz');X=q['source_X'];Y=q['source_Y'];inside=q['inside'];center=np.asarray(par['center']);rows=[];parity=[]
def reserve_RGB(n):
 assert ledger['RGB_queries']+n<=500000;ledger['RGB_queries']+=int(n);save('ledger.json',ledger)
def metrics(s,im,C,m):
 z=s.scores(im);z['E']=float(np.sqrt(z['loss']));e=(C-s.target_crop)*255;z['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));z['foreground_RMSE']=float(np.sqrt(np.mean(e[m['foreground']]**2)));return z
for key in ['a','b']:
 gate();s=study(key);case=json.loads((P/'cases'/f'{key}.json').read_text());assert s.case==case
 for file,h in case['source_sha256'].items():assert hashlib.sha256((WORK/key/file).read_bytes()).hexdigest()==h
 for layer in case['foreground_layers']:assert hashlib.sha256((WORK/key/layer['vector_asset']).read_bytes()).hexdigest()==layer['vector_sha256']
 sp=np.load(P/f'{key}-support.npz');m=np.load(P/f'{key}-masks.npz');support=sp['support'];required=sp['required_pixels'];alpha=sp['coverage'];known=sp['known'];safe=sp['incident_known'];x0,y0,x1,y1=s.crop;H,W=y1-y0,x1-x0
 assert ledger['incident_fields']<2;ledger['incident_fields']+=1;save('ledger.json',ledger)
 filtered=cv2.GaussianBlur(s.source,(43,43),6.75,borderType=cv2.BORDER_CONSTANT)
 raw=np.full(X.shape+(3,),np.nan,float);reserve_RGB(int(support.sum()))
 # Identical approved shared exact-bilinear expression and operation order.
 for mask,texture in [(support&~inside,s.source),(support&inside,filtered)]:
  rr,cc=np.nonzero(mask)
  for first in range(0,len(rr),65536):
   ri=rr[first:first+65536];ci=cc[first:first+65536];a=np.floor(X[ri,ci]).astype(int);b=np.floor(Y[ri,ci]).astype(int);fx=(X[ri,ci]-a)[:,None];fy=(Y[ri,ci]-b)[:,None]
   raw[ri,ci]=(texture[b,a]*(1-fx)+texture[b,a+1]*fx)*(1-fy)+(texture[b+1,a]*(1-fx)+texture[b+1,a+1]*fx)*fy
 f=RadiusBack()
 for name,mask in [('lens',(alpha==1)&m['glass']),('straight_miss',(alpha==0)&m['exterior']),('partial',(alpha>0)&(alpha<1)&required)]:
  coords=np.argwhere(mask);assert len(coords);rr,cc=coords[len(coords)//2];top=int(min(max(rr-1,0),H-2));left=int(min(max(cc-1,0),W-2));sub=(slice(top*2,(top+2)*2),slice(left*2,(left+2)*2));pc={**s.case,'center':center.tolist(),'crop':[x0+left,y0+top,x0+left+2,y0+top+2]};N=16
  assert ledger['fixture_rays']+N<=3000 and ledger['graph']+12*N<=6000000;ledger['fixture_rays']+=N;reserve_RGB(int(support[sub].sum())+int((support[sub]&inside[sub]).sum()))
  im,bounds,ps,layers=render_rows(s.source,pc,{},f,1.5,2,0,2,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,required_pixels=required[top:top+2,left:left+2],return_support=True,return_layers=True,return_samples=True,incident_source=filtered,incident_known=safe)
  expected=raw[sub].reshape(2,2,2,2,3).mean((1,3)).astype(np.float32);record=dict(case=key,cohort=name,patch=[left,top,left+2,top+2],pre_foreground_exact=bool(np.array_equal(im,expected,equal_nan=True)),raw_samples_exact=bool(np.array_equal(layers['sample_rgb'],raw[sub],equal_nan=True)),source_coordinates_exact=bool(np.array_equal(layers['source_X'],X[sub]) and np.array_equal(layers['source_Y'],Y[sub])),inside_exact=bool(np.array_equal(layers['sample_inside'],inside[sub])),support_exact=bool(np.array_equal(ps,support[sub].reshape(2,2,2,2).all((1,3)))))
  parity.append(record);save('parity.json',dict(records=parity,ledger=ledger.copy()));assert all(record[k] for k in ['pre_foreground_exact','raw_samples_exact','source_coordinates_exact','inside_exact','support_exact']),'Parity failure; stop without precision change'
 pre=raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);lens=np.where(inside[...,None],raw,0).reshape(H,2,W,2,3).mean((1,3));clear=np.where((~inside)[...,None],raw,0).reshape(H,2,W,2,3).mean((1,3));lenscolor=np.divide(lens,alpha[...,None],out=np.zeros_like(lens),where=alpha[...,None]>0)
 assert np.isfinite(pre[required]).all();assert ledger['candidate_images']<2;ledger['candidate_images']+=1;save('ledger.json',ledger)
 C=s.apply_foreground(pre.copy());assert np.isfinite(C[required]).all();original=metrics(s,pre,C,m);complete=metrics(s,C,C,m);partial=m['glass']&(alpha<1);partial_result=dict(pixels=int(partial.sum()),pre_foreground_RMSE=float(np.sqrt(np.mean(((pre-s.target_crop)[partial]*255)**2))),complete_RMSE=float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2))))
 fg=m['foreground'];assert np.array_equal(C[~fg],pre[~fg],equal_nan=True)
 np.savez_compressed(P/f'{key}-candidate.npz',sample_before_response=raw,raw_lens_samples=np.where(inside[...,None],raw,np.nan),raw_clear_samples=np.where((~inside)[...,None],raw,np.nan),inside=inside,support=support,coverage=alpha,lens_premultiplied=lens,clear_premultiplied=clear,lens_color=lenscolor,pre_foreground=pre,complete=C)
 local={};luma=np.array([.2126,.7152,.0722])
 for name,(a,b,c,d) in crops.items():
  tile=C[b-y0:d-y0,a-x0:c-x0].astype(float);target=s.target_crop[b-y0:d-y0,a-x0:c-x0].astype(float);valid=np.isfinite(tile).all(2);err=(tile-target)[valid]*255;dy=err@luma;dc=err-dy[:,None];local[name]=dict(original_frame_bounds=crops[name],finite_pixels=int(valid.sum()),total_pixels=int(valid.size),RGB_RMSE=float(np.sqrt(np.mean(err**2))),luma_RMSE=float(np.sqrt(np.mean(dy**2))),chroma_RMSE=float(np.sqrt(np.mean(dc**2))),signed_RGB=err.mean(0).tolist(),scope='Advisory only; unavailable pixels counted, no scoring mask changed')
 row=dict(reference=key,original_mask_scores_on_physical_pre_foreground=original,completed_image_scores=complete,partial_boundary=partial_result,fixed_crops=local,required_complete_pixels_finite=True,outside_foreground_exact=True,raw_sample_clips=[int((raw[support]<0).sum()),int((raw[support]>1).sum())],clear_unfiltered=True,source_sigma=6.75,source_radius=21,body='unit neutral, before original foreground',historical_comparison='Different declared operator and unresolved historical fingerprint; no same-epoch acceptance guard or numerical gain claimed')
 rows.append(row);save(f'{key}-result.json',row)
 width=480;height=round(H*width/W);canvas=Image.new('RGB',(width*2+2,height+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=17)
 for col,(label,image) in enumerate([('Apple reference',s.target_crop),('Unfitted physical baseline',C)]):
  finite=np.isfinite(image).all(2);yy,xx=np.indices(finite.shape);view=np.where(finite[...,None],image,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS),(col*(width+2),64));draw.text((col*(width+2)+8,20),label,fill='black',font=font)
 canvas.save(P/f'{key}-comparison.png');gate();print(key,original['E'],complete['E'],flush=True)
save('result.json',dict(status='COUNT_ZERO_UNFITTED_PAIRED_BASELINE',utc=utc(),records=rows,ledger=ledger.copy(),fits=0,historical_replacement=False,epoch_scope='Prospective approved current verification-protocol cases; historical receipt mismatch unresolved',ordering_deviation='Mask counts were verified after fixtures but before native/RGB; preserved and primary acknowledged.'))
